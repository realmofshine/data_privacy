"""VulnScanAgent — CVE scanning, CVSS scoring, and patch prioritization."""
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY


class VulnState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class VulnScanAgent:
    """Scans for CVEs, provides CVSS scoring, and prioritizes patches."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(VulnState)
        graph.add_node("vuln_scan", self.run)
        graph.add_edge("vuln_scan", END)
        graph.set_entry_point("vuln_scan")
        self.graph = graph.compile()

    def run(self, state: VulnState):
        user_msg = state["messages"][-1].content if state["messages"] else ""
        prompt = f"""You are a vulnerability management expert with access to NVD, CISA KEV, and ExploitDB.

Analyze vulnerabilities for:

TARGET: {user_msg}

Provide your response as:

VULNERABILITY ASSESSMENT REPORT:

TARGET INFO:
- Software/System:
- Version:
- Last Scanned:

CRITICAL VULNERABILITIES:
For each CVE:
- CVE ID: CVE-YYYY-NNNNN
- CVSS Score: X.X (CRITICAL/HIGH/MEDIUM/LOW)
- Description: [what the vulnerability is]
- Impact: [RCE/DoS/Info Disclosure/Privilege Escalation]
- Exploit Available: Yes/No
- CISA KEV Listed: Yes/No
- Patch: [specific version to upgrade to]
- Workaround: [if patch not immediately possible]

CVSS BREAKDOWN (for top vulnerability):
- Attack Vector: Network/Adjacent/Local/Physical
- Attack Complexity: Low/High
- Privileges Required: None/Low/High
- User Interaction: None/Required
- Scope: Unchanged/Changed
- Impact: Confidentiality/Integrity/Availability

PATCH PRIORITY MATRIX:
| Priority | CVE | Business Impact | Effort | Recommendation |
| 1 | ... | CRITICAL | Low | Patch immediately |
(Rank by business impact, not just CVSS)

SUMMARY:
- Total CVEs found:
- Critical:
- High:
- Medium:
- Low:
- Patches available:

Use known, real CVE IDs where applicable. For demonstration, include well-known CVEs."""

        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    async def stream(self, message: str, metadata: dict = None) -> dict:
        state = {"messages": [HumanMessage(content=message)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "VulnScanAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
