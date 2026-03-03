"""ExecutiveReportAgent — generates board reports, regulatory filings, and KPI dashboards."""
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY


class ReportState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class ExecutiveReportAgent:
    """Generates executive board reports, regulatory filings, and security metrics."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(ReportState)
        graph.add_node("report", self.run)
        graph.add_edge("report", END)
        graph.set_entry_point("report")
        self.graph = graph.compile()

    def run(self, state: ReportState):
        user_msg = state["messages"][-1].content if state["messages"] else ""
        prompt = f"""You are a CISO preparing reports for the board and regulators.

Generate a report based on:

REQUEST: {user_msg}

Provide your response as:

EXECUTIVE REPORT:
Classification: CONFIDENTIAL

1. EXECUTIVE SUMMARY:
[3-4 sentence overview for board members]

2. KEY METRICS:
| Metric | Current | Previous | Trend |
| Total Incidents | X | Y | ↑↓ |
| Critical Incidents | X | Y | ↑↓ |
| Avg Response Time | X hours | Y hours | ↑↓ |
| GDPR Compliance | X% | Y% | ↑↓ |
| Vendors Assessed | X | Y | ↑↓ |
| DSR Requests Completed | X | Y | ↑↓ |
| Open Vulnerabilities | X | Y | ↑↓ |
| Patch Compliance | X% | Y% | ↑↓ |

3. NOTABLE INCIDENTS:
For each significant incident:
- Date:
- Type:
- Impact:
- Status:
- Financial Impact:

4. RISK SUMMARY:
- Top 3 risks and mitigation status
- Risk trend (improving/stable/deteriorating)

5. COMPLIANCE STATUS:
| Regulation | Status | Score | Next Audit |
| GDPR | Compliant/Partial | X% | [date] |

6. VENDOR RISK OVERVIEW:
- Vendors assessed:
- High-risk vendors:
- New vendors onboarded:

7. RECOMMENDATIONS FOR BOARD:
1. [Budget/resource request]
2. [Policy approval needed]
3. [Strategic direction]

8. NEXT QUARTER PRIORITIES:
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

Generate realistic simulated data. Mark as SIMULATED REPORT."""

        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    async def stream(self, message: str, metadata: dict = None) -> dict:
        state = {"messages": [HumanMessage(content=message)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "ExecutiveReportAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
