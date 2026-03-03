"""AccessControlAgent — IAM review, over-privileged user detection, least privilege analysis."""
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY


class AccessState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class AccessControlAgent:
    """Reviews access controls, detects over-privileged accounts, and enforces least privilege."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(AccessState)
        graph.add_node("access_control", self.run)
        graph.add_edge("access_control", END)
        graph.set_entry_point("access_control")
        self.graph = graph.compile()

    def run(self, state: AccessState):
        user_msg = state["messages"][-1].content if state["messages"] else ""
        prompt = f"""You are an Identity and Access Management (IAM) security expert.

Analyze the following access control request:

REQUEST: {user_msg}

Provide your response as:

ACCESS CONTROL REVIEW:

1. OVER-PRIVILEGED ACCOUNTS:
For each finding:
- User/Account: [name]
- Department: [current dept]
- Current Permissions: [list]
- Required Permissions: [list]
- Excess Permissions: [what should be removed]
- Risk Level: CRITICAL/HIGH/MEDIUM
- Last Activity: [date]
- Recommendation: [action]

2. ZOMBIE ACCOUNTS (terminated employees):
| Account | Last Login | Status | Systems | Action Needed |

3. SERVICE ACCOUNTS:
| Account | Purpose | Privilege Level | Last Rotated | Risk |

4. ROLE-BASED ACCESS MATRIX:
| Role | System | Read | Write | Admin | Delete |

5. ANOMALOUS BEHAVIOR:
- Unusual login patterns
- Off-hours access
- Geographic anomalies
- Failed login attempts

6. LEAST PRIVILEGE RECOMMENDATIONS:
For each over-privileged account:
- Current state → Recommended state
- Impact of change
- Implementation steps

7. COMPLIANCE STATUS:
- SOX compliance: [status]
- PCI-DSS Req 7 (Restrict access): [status]
- ISO 27001 A.9 (Access control): [status]

Generate realistic simulated findings. Mark as SIMULATED DATA."""

        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    async def stream(self, message: str, metadata: dict = None) -> dict:
        state = {"messages": [HumanMessage(content=message)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "AccessControlAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
