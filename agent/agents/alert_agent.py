"""AlertAgent — generates RED / ORANGE / YELLOW alerts from risk scores."""
import operator
from typing import Annotated, Sequence, Optional, Dict
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD


class AlertState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    alerts: dict


def _get_db():
    """Get Neo4jGraph for querying."""
    try:
        from langchain_community.graphs import Neo4jGraph
        return Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD)
    except Exception:
        return None


class AlertAgent:
    """Classifies third-party risk into RED / ORANGE / YELLOW alerts."""

    def __init__(self, risk_threshold: float = 0.40):
        self.threshold = risk_threshold
        self.graph_db = _get_db()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )

        graph = StateGraph(AlertState)
        graph.add_node("alert", self.run)
        graph.add_edge("alert", END)
        graph.set_entry_point("alert")
        self.graph = graph.compile()

    def _get_thirdparty_name(self, element_id: str) -> Optional[str]:
        if not self.graph_db:
            return None
        try:
            records = self.graph_db.query(
                "MATCH (t:ThirdParty) WHERE elementId(t) = $element_id RETURN t.name AS name LIMIT 1",
                {"element_id": element_id},
            )
            return records[0]["name"] if records else None
        except Exception:
            return None

    def _get_thirdparty_domain_id(self, element_id: str) -> Optional[str]:
        if not self.graph_db:
            return None
        try:
            records = self.graph_db.query(
                "MATCH (tp:ThirdParty) WHERE elementId(tp) = $element_id RETURN tp.id AS id LIMIT 1",
                {"element_id": element_id},
            )
            return records[0]["id"] if records else None
        except Exception:
            return None

    def _get_red_alert_reason(self, thirdparty_id: str, incident_id: str) -> Optional[dict]:
        if not self.graph_db:
            return None
        try:
            records = self.graph_db.query(
                """
                MATCH (:Incident {id: $incident_id})-[:HAS_BREACH]->(db:DataBreach)
                    -[:IMPACTED_THIRDPARTY]->(tp:ThirdParty)
                WHERE tp.id = $thirdparty_id
                MATCH (ip:InternalProcess)-[r:SHARED_DATA_WITH|USES]->(tp)
                RETURN
                    ip.processName AS process,
                    type(r) AS relation_type,
                    r.isPIIShared AS pii_shared,
                    db.severity AS severity,
                    db.breachType AS breach_type
                LIMIT 1
                """,
                {"incident_id": incident_id, "thirdparty_id": thirdparty_id},
            )
            if not records:
                return None
            rec = records[0]
            return {
                "exposure_type": "DIRECT_OPERATIONAL_DEPENDENCY",
                "internal_process": rec.get("process"),
                "relationship": rec.get("relation_type"),
                "pii_shared": rec.get("pii_shared"),
                "incident_severity": rec.get("severity"),
                "breach_type": rec.get("breach_type"),
            }
        except Exception:
            return None

    def run(self, state: AlertState):
        alerts = state["alerts"]
        prompt = f"""You are a cybersecurity alerting system for an executive audience.

Summarize the following security alerts. Be concise, factual, and business-focused.
Keep total response under 400 words. Avoid technical jargon.

Alert colors:
- RED = Critical confirmed high-risk third party
- ORANGE = Elevated risk (predictive signals)
- YELLOW = Advisory risk (similar companies nearby)

For each RED alert: include company name, risk score, and 1-2 line explanation.
For ORANGE/YELLOW: mention only at high level.

ALERT DATA:
{alerts}

Output format:
Executive Summary
[4-6 line paragraph]

RED Alerts Breakdown
For each RED alert:
- Company Name: ...
- Risk Score: ...
- Reason for Alert: ...

Incident Profile (if incident_article exists)
- Organization:
- Industry:
- Date Reported:
- Impact:
- Data Exposed:
- Attack Vector:
- Location:
- Consequences:
"""
        response = self.llm.invoke(prompt)
        alerts["summary"] = response.content
        return {"messages": [AIMessage(content=str(alerts))]}

    async def stream(self, metadata: Dict) -> dict:
        risk_predictions = metadata.get("RiskAgent", [])
        nlp_block = metadata.get("NLPAgent", {})
        incident_obj = nlp_block.get("Incident", {})
        incident_text = incident_obj.get("description", "")
        incident_id = incident_obj.get("id", "")

        red_alerts = []
        orange_alerts = []

        for p in risk_predictions:
            element_id = p.get("thirdPartyId")
            risk_score = p.get("riskScore")
            if not element_id or risk_score is None:
                continue

            name = p.get("companyName") or self._get_thirdparty_name(element_id) or "UNKNOWN"
            thirdparty_id = self._get_thirdparty_domain_id(element_id)

            entry = {
                "thirdparty_element_id": element_id,
                "thirdparty_id": thirdparty_id or element_id,
                "company_name": name,
                "risk_score": risk_score,
            }

            if risk_score >= self.threshold:
                entry["alert_type"] = "RED"
                entry["priority"] = "CRITICAL"
                if thirdparty_id and incident_id:
                    entry["reason"] = self._get_red_alert_reason(thirdparty_id, incident_id)
                red_alerts.append(entry)
            else:
                entry["alert_type"] = "ORANGE"
                entry["priority"] = "HIGH"
                orange_alerts.append(entry)

        yellow_list = metadata.get("SimilarCompanyAgent", [])
        yellow_alerts = [
            {"company_name": y, "alert_type": "YELLOW", "priority": "MEDIUM"}
            for y in yellow_list
        ]

        alert_payload = {
            "threshold": self.threshold,
            "red_alerts": red_alerts,
            "orange_alerts": orange_alerts,
            "yellow_alerts": yellow_alerts,
            "incident_article": incident_text,
        }

        state = {
            "messages": [HumanMessage(content="Generate alerts + narrative")],
            "alerts": alert_payload,
        }
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )

        return {
            "agent_name": "AlertAgent",
            "agent_message": final_msg.content if final_msg else "No result",
            "alerts": alert_payload,
        }
