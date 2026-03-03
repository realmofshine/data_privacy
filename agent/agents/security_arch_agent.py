"""SecurityArchAgent — Zero Trust assessment, security posture scoring, BCP/DR planning."""
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY


class SecArchState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class SecurityArchAgent:
    """Assesses Zero Trust maturity, security posture, and business continuity planning."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(SecArchState)
        graph.add_node("sec_arch", self.run)
        graph.add_edge("sec_arch", END)
        graph.set_entry_point("sec_arch")
        self.graph = graph.compile()

    def run(self, state: SecArchState):
        user_msg = state["messages"][-1].content if state["messages"] else ""
        prompt = f"""You are a Chief Security Architect with expertise in Zero Trust, NIST CSF, and business continuity.

Analyze the following request:

REQUEST: {user_msg}

Provide your response as:

SECURITY ARCHITECTURE ASSESSMENT:

1. ZERO TRUST MATURITY (CISA Model):
| Pillar | Current Level | Target Level | Gap | Priority |
| Identity | Level X/5 | Level Y/5 | Z | HIGH/MED/LOW |
| Devices | ... | ... | ... | ... |
| Networks | ... | ... | ... | ... |
| Applications | ... | ... | ... | ... |
| Data | ... | ... | ... | ... |

Overall Score: X.X / 5.0
Industry Benchmark: X.X / 5.0

2. SECURITY POSTURE SCORE:
| Category | Score | Weight | Weighted Score |
| Prevention | X/100 | 25% | ... |
| Detection | X/100 | 25% | ... |
| Response | X/100 | 25% | ... |
| Recovery | X/100 | 25% | ... |
Overall: X/100

3. NIST CSF ALIGNMENT:
| Function | Maturity | Key Gaps |
| Identify | Tier X | ... |
| Protect | Tier X | ... |
| Detect | Tier X | ... |
| Respond | Tier X | ... |
| Recover | Tier X | ... |

4. BUSINESS CONTINUITY:
- RTO (Recovery Time Objective): [current vs target]
- RPO (Recovery Point Objective): [current vs target]
- Last BCP Test: [date]
- Test Result: Pass/Fail/Partial

5. GAP ANALYSIS:
| Gap | Risk Impact | Effort | Priority |
(Top 5 gaps ranked by risk)

6. IMPROVEMENT ROADMAP:
Phase 1 (0-3 months): [quick wins]
Phase 2 (3-6 months): [major improvements]
Phase 3 (6-12 months): [strategic initiatives]

Generate realistic but clearly simulated assessment data."""

        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    async def stream(self, message: str, metadata: dict = None) -> dict:
        state = {"messages": [HumanMessage(content=message)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "SecurityArchAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
