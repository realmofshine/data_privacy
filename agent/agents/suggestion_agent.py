"""SuggestionAgent — provides security recommendations based on incidents."""
import re
import json
import time
import operator
from typing import Annotated, Sequence
from datetime import date, datetime
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD


INCIDENT_PATTERN = re.compile(r"\bINC-[0-9a-fA-F-]{6,}\b")


def extract_json(text: str):
    text = re.sub(r"^```[a-zA-Z]*\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("["), text.rfind("]") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON array found")
    return json.loads(text[start:end])


def to_json_safe(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj


class SuggestionAgentState(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    incident_id: str | None


def _get_driver():
    from neo4j import GraphDatabase
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


class SuggestionAgent:
    """Security recommendation agent — contextual (incident-based) or generic."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        self.contextual_chain = self._build_contextual_chain()
        self.generic_chain = self._build_generic_chain()

        graph = StateGraph(SuggestionAgentState)
        graph.add_node("prevent", self.run)
        graph.add_edge("prevent", END)
        graph.set_entry_point("prevent")
        self.graph = graph.compile()

    def _fetch_incident_context(self, incident_id: str):
        try:
            driver = _get_driver()
            with driver.session() as session:
                record = session.run(
                    """
                    MATCH (i:Incident {id: $incident_id})
                    OPTIONAL MATCH (i)-[:HAS_BREACH]->(b:DataBreach)
                    OPTIONAL MATCH (b)-[:IMPACTED_THIRDPARTY]->(tp:ThirdParty)
                    OPTIONAL MATCH (tp)-[:PROVIDES]->(s:Service)
                    OPTIONAL MATCH (tp)-[:IMPLEMENTS]->(c:Control)
                    RETURN
                        properties(i) AS incident,
                        collect(DISTINCT properties(b)) AS breaches,
                        collect(DISTINCT tp.name) AS impacted_third_parties,
                        collect(DISTINCT s.name) AS services,
                        collect(DISTINCT c.name) AS controls
                    """,
                    incident_id=incident_id,
                ).single()
            driver.close()
            if not record:
                return None
            return {
                "incident": dict(record["incident"]),
                "breaches": [dict(b) for b in record["breaches"]],
                "impacted_third_parties": list(record["impacted_third_parties"]),
                "services": list(record["services"]),
                "existing_controls": list(record["controls"]),
            }
        except Exception:
            return None

    def _build_contextual_chain(self):
        prompt = ChatPromptTemplate.from_template("""
You are a security risk and compliance advisor.

Based on the Incident Context below, recommend preventive measures to reduce similar incidents.
Tie each recommendation to specific elements in the context (breach type, services, data types).
Rank by impact: High / Medium / Low. Explain WHY in one sentence.
Return ONLY valid JSON:
[
  {{
    "measure": "...",
    "impact": "High|Medium|Low",
    "reason": "..."
  }}
]

Incident Context:
{context}
""")
        return (
            RunnableParallel({"context": RunnablePassthrough()})
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def _build_generic_chain(self):
        prompt = ChatPromptTemplate.from_template("""
You are a security risk and compliance advisor.

User question: {question}

If it's a greeting, return:
[{{"message": "..."}}]

If it's a cybersecurity question, return preventive measures as JSON:
[
  {{
    "measure": "...",
    "impact": "High|Medium|Low",
    "reason": "..."
  }}
]

Return ONLY valid JSON.
""")
        return prompt | self.llm | StrOutputParser()

    def run(self, state: SuggestionAgentState):
        raw_input = (state.get("incident_id") or "").strip()
        match = INCIDENT_PATTERN.search(raw_input)
        incident_id = match.group(0) if match else None

        if not incident_id:
            llm_output = self.generic_chain.invoke({"question": raw_input})
            try:
                final_text = json.dumps(extract_json(llm_output), indent=2)
            except Exception:
                final_text = llm_output
            return {"messages": [AIMessage(content=final_text)]}

        ctx = self._fetch_incident_context(incident_id)
        if not ctx:
            return {"messages": [AIMessage(content=f"No incident found for id={incident_id}")]}

        safe_ctx = json.dumps(ctx, default=to_json_safe, indent=2)
        llm_output = self.contextual_chain.invoke(safe_ctx)
        try:
            final_text = json.dumps(extract_json(llm_output), indent=2)
        except Exception:
            final_text = llm_output
        return {"messages": [AIMessage(content=final_text)]}

    async def stream(self, query: str) -> dict:
        state = {
            "messages": [HumanMessage(content=query or "")],
            "incident_id": query or None,
        }
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "SuggestionAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
