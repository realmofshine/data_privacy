"""ComplianceAgent — assesses regulatory obligations (GDPR, CCPA, HIPAA, PCI-DSS)."""
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY


class ComplianceState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class ComplianceAgent:
    """Analyzes incidents against GDPR, CCPA, HIPAA, PCI-DSS, SOX regulations."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(ComplianceState)
        graph.add_node("compliance", self.run)
        graph.add_edge("compliance", END)
        graph.set_entry_point("compliance")
        self.graph = graph.compile()

    def run(self, state: ComplianceState):
        user_msg = state["messages"][-1].content if state["messages"] else ""
        prompt = f"""You are a Data Privacy Compliance Expert with deep knowledge of GDPR, CCPA, HIPAA, PCI-DSS, and SOX.

Analyze the following query/incident and provide a compliance assessment:

QUERY: {user_msg}

Provide your response in this structure:

COMPLIANCE ASSESSMENT:

1. APPLICABLE REGULATIONS:
   For each regulation that applies:
   - Regulation name and specific articles
   - Why it applies to this situation
   - Notification requirements and deadlines
   - Maximum penalties

2. NOTIFICATION REQUIREMENTS:
   - Who must be notified (DPA, users, board, insurance, law enforcement)
   - Deadline for each notification
   - Required content of each notification

3. DOCUMENTATION REQUIREMENTS:
   - What records must be maintained
   - What evidence must be preserved
   - Retention periods

4. RISK OF NON-COMPLIANCE:
   - Estimated fine range
   - Reputational impact
   - Legal exposure

5. RECOMMENDED ACTIONS:
   - Immediate actions (within 24 hours)
   - Short-term actions (within 72 hours)
   - Long-term actions (within 30 days)

Be specific, cite actual regulation articles, and provide actionable guidance."""

        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    async def stream(self, message: str, metadata: dict = None) -> dict:
        state = {"messages": [HumanMessage(content=message)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "ComplianceAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
