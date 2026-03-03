"""ThreatModelAgent — performs STRIDE/DREAD analysis and MITRE ATT&CK mapping."""
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from agent.configs import GOOGLE_API_KEY


class ThreatModelState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class ThreatModelAgent:
    """Performs STRIDE threat analysis and MITRE ATT&CK mapping for systems."""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        graph = StateGraph(ThreatModelState)
        graph.add_node("threat_model", self.run)
        graph.add_edge("threat_model", END)
        graph.set_entry_point("threat_model")
        self.graph = graph.compile()

    def run(self, state: ThreatModelState):
        user_msg = state["messages"][-1].content if state["messages"] else ""
        prompt = f"""You are a senior security architect specializing in threat modeling.

Perform a comprehensive threat analysis for:

SYSTEM: {user_msg}

Provide your response as:

THREAT MODEL REPORT:

SYSTEM OVERVIEW:
- Components identified
- Trust boundaries
- Data flows
- Entry points

STRIDE ANALYSIS:
| Category | Threat | Risk Level | Description | Mitigation |
| Spoofing | ... | HIGH/MED/LOW | ... | ... |
| Tampering | ... | ... | ... | ... |
| Repudiation | ... | ... | ... | ... |
| Info Disclosure | ... | ... | ... | ... |
| Denial of Service | ... | ... | ... | ... |
| Elevation of Privilege | ... | ... | ... | ... |

DREAD SCORING:
For the top 3 threats:
| Threat | Damage | Reproducibility | Exploitability | Affected Users | Discoverability | Total |
(Scale 1-10 for each)

MITRE ATT&CK MAPPING:
| Tactic | Technique | ID | Description |
| Initial Access | Phishing | T1566 | ... |
(Map all identified threats to ATT&CK)

ATTACK TREE:
Root Goal: Compromise [system]
├── Path 1: [description]
│   ├── Step 1.1: [technique]
│   └── Step 1.2: [technique]
├── Path 2: [description]
└── Path 3: [description]

TOP RECOMMENDATIONS:
1. [Most critical mitigation]
2. [Second priority]
3. [Third priority]

Be specific and actionable."""

        response = self.llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}

    async def stream(self, message: str, metadata: dict = None) -> dict:
        state = {"messages": [HumanMessage(content=message)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "ThreatModelAgent",
            "agent_message": final_msg.content if final_msg else "No result",
        }
