"""DataMappingAgent — maps data flows and classifies data sensitivity."""
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY


class DataMapState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class DataMappingAgent:
    """Maps PII data flows between internal systems and vendors (GDPR Art.30)."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(DataMapState)
        graph.add_node("data_map", self.run)
        graph.add_edge("data_map", END)
        graph.set_entry_point("data_map")
        self.graph = graph.compile()

    def run(self, state: DataMapState):
        user_msg = state["messages"][-1].content if state["messages"] else ""
        prompt = f"""You are a Data Protection Officer specializing in data flow mapping and GDPR Article 30 compliance.

Analyze the following request and provide a comprehensive data mapping:

REQUEST: {user_msg}

Provide your response in this structure:

DATA FLOW MAP:

1. PROCESSING ACTIVITIES (ROPA):
| Activity | Purpose | Legal Basis | Data Categories | Data Subjects | Recipients | Retention | Transfer |

2. DATA CLASSIFICATION:
| Data Element | Classification | Sensitivity | Regulation |
Where Classification = PII/PHI/PCI/IP/Public
Sensitivity = Restricted/Confidential/Internal/Public

3. DATA FLOW DIAGRAM:
Internal System → Data Type → Third Party Vendor
(List all flows)

4. CROSS-BORDER TRANSFERS:
- Source country and destination country
- Transfer mechanism (SCCs, BCRs, Adequacy)
- Risk assessment

5. DATA LINEAGE:
For key data elements, trace: Collection Point → Storage → Processing → Sharing → Archival/Deletion

6. GAPS IDENTIFIED:
- Missing consent for specific processing
- Inadequate retention policies
- Undocumented transfers
- Missing DPIAs

7. RECOMMENDATIONS:
- Immediate actions needed
- Policy updates required
- Technical controls to implement

Be specific and use realistic examples based on the context provided."""

        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    async def stream(self, message: str, metadata: dict = None) -> dict:
        state = {"messages": [HumanMessage(content=message)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "DataMappingAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
