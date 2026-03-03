"""NLPAgent — extracts cybersecurity events from news text and ingests into Neo4j."""
import uuid
import operator
from typing import Annotated, Sequence, Optional, List, Tuple
from datetime import datetime

from typing_extensions import TypedDict
from pydantic import BaseModel

from langchain_core.messages import (
    BaseMessage, HumanMessage, SystemMessage, ToolMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE


# ─── Pydantic Models ────────────────────────────────────────────────

class DataBreach(BaseModel):
    breachType: Optional[str] = None
    description: Optional[str] = None
    detectedAt: Optional[str] = None
    impact: Optional[str] = None
    severity: Optional[int] = None
    location: Optional[str] = None
    impactedThirdParty: Optional[str] = None
    impactedControlServices: Optional[list] = []
    piiImpacted: bool = False
    status: str = "active"


class Incident(BaseModel):
    type: Optional[str] = None
    status: str = "active"
    description: Optional[str] = None
    responseTime: str = ""
    resolutionTime: str = ""
    source: str = ""
    createdDate: Optional[str] = None


class CyberSecurityEvent(BaseModel):
    Incident: Incident
    DataBreach: list[DataBreach]


class ImpactedServicesParser(BaseModel):
    impacted_services: list[str]


# ─── Neo4j Utilities ────────────────────────────────────────────────

def _get_driver():
    from neo4j import GraphDatabase
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def check_thirdparty_in_neo4j(third_party_name: str) -> bool:
    try:
        driver = _get_driver()
        with driver.session(database=NEO4J_DATABASE) as session:
            record = session.run(
                "MATCH (n:ThirdParty) WHERE toLower(n.name) CONTAINS toLower($name) RETURN COUNT(n) > 0 AS exists",
                name=third_party_name,
            ).single()
            return record["exists"] if record else False
    except Exception:
        return False
    finally:
        driver.close()


def get_services_from_neo4j(impacted_third_party: str) -> Tuple[List[str], Optional[str]]:
    empty_response: Tuple[List[str], Optional[str]] = ([], None)
    if not impacted_third_party or not impacted_third_party.strip():
        return empty_response
    try:
        driver = _get_driver()
        query = """
            MATCH (n:ThirdParty)-[:PROVIDES]-(s:Service)-[]->(c:Control)
            WHERE toLower(n.name) CONTAINS toLower($company_name)
            WITH collect(c.accessedServices) AS services, n
            RETURN n.id AS thirdPartyId,
                   reduce(all = [], s IN services | all + s) AS service_list
        """
        with driver.session(database=NEO4J_DATABASE) as session:
            records = [dict(r) for r in session.run(query, company_name=impacted_third_party.strip())]
        if not records:
            return empty_response
        all_services: List[str] = []
        third_party_id = None
        for record in records:
            third_party_id = record.get("thirdPartyId")
            service_list = record.get("service_list") or []
            all_services.extend(s for s in service_list if s)
        return list(dict.fromkeys(all_services)), third_party_id
    except Exception:
        return empty_response
    finally:
        driver.close()


def get_related_thirdparty(name: str) -> list:
    try:
        driver = _get_driver()
        query = """
            CALL db.index.fulltext.queryNodes("thirdPartyNames", $name + "~")
            YIELD node, score
            RETURN node.name AS matched_name
            ORDER BY score DESC LIMIT 3
        """
        with driver.session(database=NEO4J_DATABASE) as session:
            return [r["matched_name"] for r in session.run(query, name=name)]
    except Exception:
        return []
    finally:
        driver.close()


# ─── Extraction Logic ────────────────────────────────────────────────

def assign_unique_ids(data: dict) -> dict:
    data["Incident"]["id"] = f"INC-{uuid.uuid4()}"
    for breach in data.get("DataBreach", []):
        breach["id"] = f"BRE-{uuid.uuid4()}"
    return data


def extract_event(event_text: str, model: ChatGoogleGenerativeAI) -> dict:
    """Extract structured cybersecurity event from raw text and enrich with Neo4j data."""
    try:
        parser = PydanticOutputParser(pydantic_object=CyberSecurityEvent)
        prompt = f"""Extract a CyberSecurityEvent from this text.

{event_text}

{parser.get_format_instructions()}
"""
        response = model.invoke(prompt)
        parsed_data = parser.parse(response.content).model_dump()

        valid_breaches = []
        missing_third_parties = []

        for breach in parsed_data.get("DataBreach", []):
            third_party = breach.get("impactedThirdParty")
            if not third_party or not check_thirdparty_in_neo4j(third_party):
                missing_third_parties.append({
                    "impacted_third_party": third_party,
                    "similar_company_names": get_related_thirdparty(third_party) if third_party else [],
                })
                continue

            services, third_party_id = get_services_from_neo4j(third_party)
            if services:
                svc_parser = PydanticOutputParser(pydantic_object=ImpactedServicesParser)
                svc_prompt = f"""Which of these services are impacted by the breach?
Third party: {third_party}
Available services: {services}
Event: {event_text[:500]}
{svc_parser.get_format_instructions()}"""
                svc_response = model.invoke(svc_prompt)
                svc_data = svc_parser.parse(svc_response.content).model_dump()
                breach["impactedControlServices"] = svc_data.get("impacted_services", [])

            breach["impactedThirdPartyId"] = third_party_id
            breach["createdAt"] = datetime.utcnow().isoformat()
            valid_breaches.append(breach)

        parsed_data = assign_unique_ids(parsed_data)
        parsed_data["DataBreach"] = valid_breaches
        parsed_data["missing_third_parties"] = missing_third_parties
        return parsed_data

    except Exception as e:
        return {"error": str(e)}


def ingest_to_neo4j(payload: dict) -> bool:
    """Ingest extracted cybersecurity event into Neo4j."""
    cypher_query = """
        MERGE (i:Incident {id: $incident.id})
        SET i.type = $incident.type,
            i.status = $incident.status,
            i.description = $incident.description,
            i.responseTime = $incident.responseTime,
            i.resolutionTime = $incident.resolutionTime,
            i.source = $incident.source,
            i.createdDate = datetime($incident.createdDate)

        WITH i
        UNWIND $dataBreaches AS breach

        MERGE (b:DataBreach {id: breach.id})
        SET b.breachType = breach.breachType,
            b.description = breach.description,
            b.detectedAt = datetime(breach.detectedAt),
            b.impact = breach.impact,
            b.severity = breach.severity,
            b.location = breach.location,
            b.piiImpacted = breach.piiImpacted,
            b.status = breach.status,
            b.impactedThirdParty = breach.impactedThirdParty,
            b.impactedThirdPartyId = breach.impactedThirdPartyId,
            b.impactedControlServices = breach.impactedControlServices

        MERGE (i)-[:HAS_BREACH]->(b)

        WITH b, breach
        WHERE breach.impactedThirdPartyId IS NOT NULL
        AND breach.impactedThirdPartyId <> ""

        MERGE (t:ThirdParty {id: breach.impactedThirdPartyId})
        MERGE (b)-[r:IMPACTED_THIRDPARTY {directed: true}]->(t)
        SET r.impactedAt = datetime(breach.detectedAt)
        SET r.createdAt = datetime(breach.createdAt)
    """
    try:
        driver = _get_driver()
        with driver.session(database=NEO4J_DATABASE) as session:
            session.run(
                cypher_query,
                {"incident": payload["Incident"], "dataBreaches": payload["DataBreach"]},
            )
        return True
    except Exception:
        return False
    finally:
        driver.close()


# ─── LangGraph Agent ────────────────────────────────────────────────

class NLPAgentState(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    extracted_data: dict


class NLPAgent:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model=GOOGLE_API_KEY and "gemini-2.0-flash" or "gemini-2.0-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )

        graph = StateGraph(NLPAgentState)
        graph.add_node("extract", self.extract_node)
        graph.add_node("ingest", self.ingest_node)
        graph.add_edge("extract", "ingest")
        graph.add_edge("ingest", END)
        graph.set_entry_point("extract")
        self.graph = graph.compile()

    def extract_node(self, state: NLPAgentState):
        text = state["messages"][-1].content
        data = extract_event(text, self.model)
        return {
            "messages": [ToolMessage(tool_call_id="extract", name="extract_tool", content=str(data))],
            "extracted_data": data,
        }

    def ingest_node(self, state: NLPAgentState):
        data = state.get("extracted_data")
        if not data:
            return {"messages": [ToolMessage(tool_call_id="ingest", name="ingest_tool", content="No data extracted")]}

        valid_breaches = [b for b in data.get("DataBreach", []) if b.get("impactedThirdPartyId")]
        if not valid_breaches:
            return {
                "messages": [ToolMessage(tool_call_id="ingest", name="ingest_tool", content="No valid third-party found for ingestion")],
                "extracted_data": data,
            }

        data["DataBreach"] = valid_breaches
        success = ingest_to_neo4j(data)
        msg = "Extraction and ingestion successful" if success else "Ingestion failed"
        return {
            "messages": [ToolMessage(tool_call_id="ingest", name="ingest_tool", content=msg)],
            "extracted_data": data,
        }

    async def stream(self, event_text: str) -> dict:
        state = {
            "messages": [
                SystemMessage(content="You are a cybersecurity extraction + ingestion agent."),
                HumanMessage(content=event_text),
            ]
        }
        result = self.graph.invoke(state)
        return {
            "agent_name": "NLPAgent",
            "agent_message": result["messages"][-1].content,
            "agent_metadata": result.get("extracted_data", {}),
        }
