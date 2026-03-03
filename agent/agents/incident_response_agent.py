"""IncidentResponseAgent — generates IR playbooks, notifications, and remediation steps."""
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY


class IRState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class IncidentResponseAgent:
    """Generates step-by-step IR playbooks based on incident type."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(IRState)
        graph.add_node("ir", self.run)
        graph.add_edge("ir", END)
        graph.set_entry_point("ir")
        self.graph = graph.compile()

    def run(self, state: IRState):
        user_msg = state["messages"][-1].content if state["messages"] else ""
        prompt = f"""You are a Senior Incident Response Manager with 20+ years experience in cybersecurity.

Generate a detailed Incident Response Playbook for the following:

INCIDENT: {user_msg}

Structure your response as:

INCIDENT RESPONSE PLAYBOOK:

INCIDENT CLASSIFICATION:
- Type: (Ransomware/Phishing/Insider Threat/Supply Chain/DDoS/Data Exfiltration)
- Severity: (CRITICAL/HIGH/MEDIUM/LOW)
- Estimated Impact:

PHASE 1 — CONTAIN (Hour 0-1):
☐ Step 1: [specific action]
☐ Step 2: [specific action]
☐ Step 3: [specific action]
Owner: [role]

PHASE 2 — ASSESS (Hour 1-4):
☐ Step 1: [specific action]
☐ Step 2: [specific action]
Owner: [role]

PHASE 3 — NOTIFY (Hour 4-24):
☐ Step 1: [specific action]
Notification Matrix:
| Recipient | Deadline | Method | Template |
Owner: [role]

PHASE 4 — REMEDIATE (Hour 24-72):
☐ Step 1: [specific technical action]
☐ Step 2: [specific patch or config change]
Owner: [role]

PHASE 5 — RECOVER (Day 3-7):
☐ Step 1: [specific action]
Owner: [role]

PHASE 6 — POST-INCIDENT (Week 2-4):
☐ Lessons learned workshop
☐ Update IR plan
☐ Policy revisions
Owner: [role]

MITRE ATT&CK MAPPING:
- Tactic: [name] | Technique: [ID and name]

Be very specific with actions — no generic advice. Include actual commands, tools, and procedures."""

        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    async def stream(self, message: str, metadata: dict = None) -> dict:
        state = {"messages": [HumanMessage(content=message)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "IncidentResponseAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
