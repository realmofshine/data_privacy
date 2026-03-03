"""SimilarCompanyAgent — finds companies similar to those affected by the breach."""
import operator
from typing import Annotated, Sequence, Dict, List
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

from agent.configs import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE


class SimilarCompanyState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


def _get_driver():
    from neo4j import GraphDatabase
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def find_similar_companies(affected_companies: List[str], top_k: int = 10) -> List[str]:
    """Find companies similar to affected ones using vector similarity or industry matching."""
    similar = set()
    try:
        driver = _get_driver()
        with driver.session(database=NEO4J_DATABASE) as session:
            for company in affected_companies:
                # Try vector similarity search first
                try:
                    result = session.run(
                        """
                        MATCH (t:ThirdParty)
                        WHERE toLower(t.name) CONTAINS toLower($name)
                        WITH t LIMIT 1
                        CALL db.index.vector.queryNodes("thirdPartyEmbeddings", $k, t.embedding)
                        YIELD node, score
                        WHERE node.name <> t.name AND score > 0.7
                        RETURN node.name AS name
                        ORDER BY score DESC LIMIT $k
                        """,
                        name=company, k=top_k,
                    )
                    for r in result:
                        similar.add(r["name"])
                except Exception:
                    # Fallback: same industry search
                    result = session.run(
                        """
                        MATCH (t:ThirdParty)
                        WHERE toLower(t.name) CONTAINS toLower($name)
                        WITH t LIMIT 1
                        MATCH (t2:ThirdParty)
                        WHERE t2.industry = t.industry AND t2.name <> t.name
                        RETURN t2.name AS name LIMIT $k
                        """,
                        name=company, k=top_k,
                    )
                    for r in result:
                        similar.add(r["name"])
        driver.close()
    except Exception:
        pass
    return list(similar)[:top_k]


class SimilarCompanyAgent:
    def __init__(self):
        graph = StateGraph(SimilarCompanyState)
        graph.add_node("find_similar", self.run)
        graph.add_edge("find_similar", END)
        graph.set_entry_point("find_similar")
        self.graph = graph.compile()

    def run(self, state: SimilarCompanyState):
        # Extract company names from message metadata
        last_msg = state["messages"][-1]
        metadata = getattr(last_msg, "additional_kwargs", {}).get("metadata", {})

        affected_companies: List[str] = []

        # Companies from RiskAgent predictions
        for pred in metadata.get("RiskAgent", []):
            name = pred.get("companyName", "")
            if name:
                affected_companies.append(name)

        # Also include companies from NLP DataBreach
        nlp_data = metadata.get("NLPAgent", {})
        for breach in nlp_data.get("DataBreach", []):
            tp = breach.get("impactedThirdParty", "")
            if tp:
                affected_companies.append(tp)

        similar = find_similar_companies(list(set(affected_companies)))

        return {"messages": [AIMessage(content=str(similar))]}

    async def stream(self, query: str, metadata: Dict) -> dict:
        state = {
            "messages": [HumanMessage(
                content=query,
                additional_kwargs={"metadata": metadata},
            )]
        }
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        msg_content = final_msg.content if final_msg else "[]"

        # Try to parse as list
        try:
            import ast
            similar_list = ast.literal_eval(msg_content)
        except Exception:
            similar_list = []

        return {
            "agent_name": "SimilarCompanyAgent",
            "agent_message": msg_content,
            "similar_companies": similar_list,
        }
