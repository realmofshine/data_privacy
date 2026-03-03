"""ForensicsAgent — digital forensics, log analysis, and timeline reconstruction."""
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY


class ForensicsState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class ForensicsAgent:
    """Performs digital forensics analysis, log correlation, and timeline reconstruction."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(ForensicsState)
        graph.add_node("forensics", self.run)
        graph.add_edge("forensics", END)
        graph.set_entry_point("forensics")
        self.graph = graph.compile()

    def run(self, state: ForensicsState):
        user_msg = state["messages"][-1].content if state["messages"] else ""
        prompt = f"""You are a senior digital forensics investigator with expertise in incident reconstruction.

Analyze the following evidence:

EVIDENCE: {user_msg}

Provide your response as:

FORENSIC ANALYSIS REPORT:

1. ATTACK CLASSIFICATION:
- Attack Type: [Brute Force/Phishing/Malware/Insider/APT/Supply Chain]
- Confidence: [percentage]
- Sophistication: Low/Medium/High/APT-Level

2. RECONSTRUCTED TIMELINE:
| Timestamp | Event | Category | Severity | MITRE ATT&CK |
| HH:MM:SS | [what happened] | [recon/initial access/execution/...] | [CRITICAL/HIGH/...] | [T-ID] |

3. INDICATORS OF COMPROMISE (IOCs):
- IP Addresses: [list with GeoIP]
- Domains: [list]
- File Hashes: [MD5/SHA256]
- Email Addresses: [list]
- User Accounts: [compromised accounts]
- Tools Used: [attacker tools identified]

4. ATTACK CHAIN ANALYSIS:
Step 1: [Initial Access] → [how attacker got in]
Step 2: [Execution] → [what attacker ran]
Step 3: [Persistence] → [how attacker maintained access]
Step 4: [Exfiltration] → [what was stolen and how]

5. EVIDENCE PRESERVATION:
☐ Memory dump captured
☐ Disk images preserved
☐ Network logs secured
☐ Chain of custody documented

6. ROOT CAUSE:
[What underlying weakness allowed this attack]

7. RECOMMENDATIONS:
- Immediate containment actions
- Evidence to preserve for legal proceedings
- Prevention measures

Be very specific with technical details."""

        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    async def stream(self, message: str, metadata: dict = None) -> dict:
        state = {"messages": [HumanMessage(content=message)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "ForensicsAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
