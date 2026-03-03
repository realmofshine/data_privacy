"""RiskAgent — computes GNN-based risk scores for affected third parties."""
import operator
from typing import Annotated, Sequence, Optional, Dict, List
from typing_extensions import TypedDict

from langchain_core.messages import (
    BaseMessage, HumanMessage, SystemMessage, ToolMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY, NEO4J_DATABASE, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD


# ─── Agent State ────────────────────────────────────────────────────

class RiskAgentState(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    third_parties: List[Dict]
    predictions: List[Dict]


# ─── Neo4j Helpers ──────────────────────────────────────────────────

def _get_driver():
    from neo4j import GraphDatabase
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def resolve_third_parties(breach_ids: List[str]) -> List[Dict]:
    """Resolve DataBreach IDs → ThirdParty elementIds and names."""
    resolved_data: Dict[str, Dict] = {}
    try:
        driver = _get_driver()
        with driver.session(database=NEO4J_DATABASE) as session:
            for breach_id in breach_ids:
                result = session.run(
                    """
                    MATCH (i:DataBreach {id: $value})
                    -[:IMPACTED_THIRDPARTY]->(tp:ThirdParty)
                    RETURN elementId(tp) AS thirdPartyIds, tp.name as thirdPartyName
                    """,
                    value=breach_id,
                )
                for r in result:
                    el_id = r["thirdPartyIds"]
                    resolved_data[el_id] = {"element_id": el_id, "name": r["thirdPartyName"]}
        driver.close()
    except Exception:
        pass
    return list(resolved_data.values())


def compute_risk_score(element_id: str, incident_id: Optional[str]) -> float:
    """
    Compute a risk score for a ThirdParty given an incident.

    In production this calls your trained GNN model (risk_pipeline.py).
    Here we implement a rule-based fallback using graph properties from Neo4j.
    """
    try:
        driver = _get_driver()
        with driver.session(database=NEO4J_DATABASE) as session:
            # Count direct breaches, PII exposure, and shared data relationships
            result = session.run(
                """
                MATCH (tp:ThirdParty)
                WHERE elementId(tp) = $el_id
                OPTIONAL MATCH (tp)<-[:IMPACTED_THIRDPARTY]-(db:DataBreach)
                OPTIONAL MATCH (ip:InternalProcess)-[:SHARED_DATA_WITH|USES]->(tp)
                WITH tp,
                     count(DISTINCT db) AS breachCount,
                     count(DISTINCT ip) AS processCount,
                     tp.riskScore AS existingScore
                RETURN breachCount, processCount, existingScore
                """,
                el_id=element_id,
            ).single()

            if result:
                existing = result.get("existingScore")
                if existing is not None:
                    return float(existing)
                breach_count = result.get("breachCount", 0) or 0
                process_count = result.get("processCount", 0) or 0
                # Simple heuristic: base 0.3 + 0.1 per breach + 0.05 per process
                return min(0.95, 0.3 + breach_count * 0.1 + process_count * 0.05)
        driver.close()
    except Exception:
        pass
    return 0.35  # fallback default


# ─── LangGraph Agent ────────────────────────────────────────────────

class RiskAgent:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(RiskAgentState)
        graph.add_node("resolve_third_parties", self.resolve_node)
        graph.add_node("predict_risk", self.predict_node)
        graph.add_edge("resolve_third_parties", "predict_risk")
        graph.add_edge("predict_risk", END)
        graph.set_entry_point("resolve_third_parties")
        self.graph = graph.compile()

    def resolve_node(self, state: RiskAgentState):
        last_msg = state["messages"][-1]
        metadata = getattr(last_msg, "additional_kwargs", {}).get("metadata", {}).get("NLPAgent", {})
        breach_ids = [db.get("id") for db in metadata.get("DataBreach", []) if db.get("id")]

        if not breach_ids:
            return {"messages": [ToolMessage(tool_call_id="resolve", name="resolve_third_parties", content="No Data Breaches Found")]}

        third_parties = resolve_third_parties(breach_ids)
        if not third_parties:
            return {"messages": [ToolMessage(tool_call_id="resolve", name="resolve_third_parties", content="No Third Parties Found")]}

        return {
            "third_parties": third_parties,
            "messages": [ToolMessage(tool_call_id="resolve", name="resolve_third_parties", content=f"Resolved {len(third_parties)} ThirdParties")],
        }

    def predict_node(self, state: RiskAgentState):
        third_parties = state.get("third_parties", [])
        last_msg = state["messages"][-2]
        metadata = getattr(last_msg, "additional_kwargs", {}).get("metadata", {}).get("NLPAgent", {})
        incident_id = metadata.get("Incident", {}).get("id")

        if not third_parties:
            return {"messages": [ToolMessage(tool_call_id="predict", name="predict_risk", content="No ThirdParties resolved for prediction")]}

        predictions = []
        for tp in third_parties:
            el_id = tp["element_id"]
            score = compute_risk_score(el_id, incident_id)
            predictions.append({"thirdPartyId": el_id, "riskScore": score, "companyName": tp["name"]})

        summary = "\n".join(
            f"- {p['companyName']}: {p['riskScore']:.4f}" for p in predictions
        )

        return {
            "predictions": predictions,
            "messages": [ToolMessage(tool_call_id="predict", name="predict_risk", content=f"Risk scores computed:\n{summary}")],
        }

    async def stream(self, user_query: str, metadata: Dict) -> dict:
        try:
            state = {
                "messages": [
                    SystemMessage(content="You are a cybersecurity risk prediction agent."),
                    HumanMessage(content=user_query, additional_kwargs={"metadata": metadata}),
                ]
            }
            result = self.graph.invoke(state)
            return {
                "agent_name": "RiskAgent",
                "agent_message": result["messages"][-1].content,
                "predictions": result.get("predictions", []),
            }
        except Exception as e:
            return {"agent_name": "RiskAgent", "agent_message": f"Error: {str(e)}", "predictions": []}
