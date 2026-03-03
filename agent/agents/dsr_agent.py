"""DSRAgent — handles Data Subject Rights requests (access, erasure, portability)."""
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY


class DSRState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class DSRAgent:
    """Processes GDPR data subject requests: access, erasure, portability, rectification."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(DSRState)
        graph.add_node("dsr", self.run)
        graph.add_edge("dsr", END)
        graph.set_entry_point("dsr")
        self.graph = graph.compile()

    def run(self, state: DSRState):
        user_msg = state["messages"][-1].content if state["messages"] else ""
        prompt = f"""You are a Data Subject Rights specialist handling GDPR requests.

Process the following Data Subject Request:

REQUEST: {user_msg}

Provide your response in this structure:

DSR PROCESSING REPORT:

1. REQUEST CLASSIFICATION:
- Type: (Access Art.15 / Erasure Art.17 / Portability Art.20 / Rectification Art.16 / Restriction Art.18 / Objection Art.21)
- Data Subject ID:
- Deadline: (30 days from receipt)
- Priority:

2. IDENTITY VERIFICATION:
- Verification method required
- Status: PENDING/VERIFIED

3. SYSTEMS INVENTORY:
| System | Data Found | Records | Data Types | Can Delete? | Retention Obligation |

4. LEGAL EXCEPTIONS:
- Legal obligations preventing deletion (tax records, fraud prevention)
- Legitimate interest overrides
- Contract performance requirements

5. EXECUTION PLAN:
☐ Step 1: [action on specific system]
☐ Step 2: [action on specific system]
☐ Step 3: [verification step]

6. RESPONSE LETTER (draft):
Dear [Data Subject],
Re: Your request under GDPR Article [X]
[Professional response confirming actions taken]

7. AUDIT LOG:
- Request received: [date]
- Verification completed: [date]
- Actions executed: [date]
- Response sent: [date]

Be specific with system names and realistic data types."""

        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    async def stream(self, message: str, metadata: dict = None) -> dict:
        state = {"messages": [HumanMessage(content=message)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "DSRAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
