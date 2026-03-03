"""DarkWebMonitorAgent — scans for leaked credentials and brand mentions."""
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY


class DarkWebState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class DarkWebMonitorAgent:
    """Simulates dark web monitoring for leaked credentials and brand mentions."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(DarkWebState)
        graph.add_node("darkweb", self.run)
        graph.add_edge("darkweb", END)
        graph.set_entry_point("darkweb")
        self.graph = graph.compile()

    def run(self, state: DarkWebState):
        user_msg = state["messages"][-1].content if state["messages"] else ""
        prompt = f"""You are a Cyber Threat Intelligence analyst specializing in dark web monitoring.

Analyze the following request and generate a realistic dark web scan report:

REQUEST: {user_msg}

Provide your response as:

DARK WEB SCAN REPORT:

SCAN SUMMARY:
- Target: [domain/email/organization]
- Scan Date: March 2025
- Sources Checked: [list of dark web sources]
- Total Findings: [number]

CRITICAL FINDINGS:
For each finding:
- Credential/Data: [what was found]
- Source: [where it was found — forum name, paste site, database dump]
- Date Discovered: [when]
- Exposure Level: CRITICAL/HIGH/MEDIUM/LOW
- Data Type: (Password/API Key/PII/Financial/Source Code)
- Recommended Action: [specific action]

BRAND MENTIONS:
- Forum/Channel: [name]
- Context: [threat discussion summary]
- Sentiment: Hostile/Neutral/Informational
- Credibility: High/Medium/Low

CREDENTIAL ANALYSIS:
- Total compromised credentials: [number]
- Unique passwords: [number]
- Password reuse detected: Yes/No
- Most common password patterns: [list]

RECOMMENDATIONS:
1. Immediate actions (within 24 hours)
2. Short-term actions (within 1 week)
3. Monitoring improvements

Generate realistic but clearly simulated findings. Mark it as SIMULATED DATA."""

        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    async def stream(self, message: str, metadata: dict = None) -> dict:
        state = {"messages": [HumanMessage(content=message)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "DarkWebMonitorAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
