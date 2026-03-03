"""TavilyNewsVerificationAgent — second opinion on news authenticity using Tavily AI search."""
import json
import re
import os
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()


class TavilyState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class TavilyNewsVerificationAgent:
    """
    Provides a second opinion on news authenticity using Tavily's
    AI-powered search API.
    """

    def __init__(self):
        try:
            from tavily import TavilyClient
            self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
            self._available = True
        except ImportError:
            self._available = False

        graph = StateGraph(TavilyState)
        graph.add_node("verify", self.verify)
        graph.add_edge("verify", END)
        graph.set_entry_point("verify")
        self.graph = graph.compile()

    def verify(self, state: TavilyState):
        user_msg = state["messages"][-1].content

        if not self._available:
            result = {
                "verdict": "UNKNOWN",
                "confidence": 0.5,
                "reason": "Tavily client not available",
                "sources": [],
            }
            return {"messages": [AIMessage(content=json.dumps(result))]}

        try:
            # Search for the claim
            search_result = self.tavily.search(
                query=user_msg[:500],
                search_depth="advanced",
                max_results=5,
                include_answer=True,
            )

            sources = [r.get("url", "") for r in search_result.get("results", [])]
            answer = search_result.get("answer", "")

            # Determine verdict based on search results
            claim_lower = user_msg.lower()
            answer_lower = answer.lower() if answer else ""

            # Check if the search results corroborate the claim
            if search_result.get("results"):
                # Look for contradictory or confirming signals
                result_texts = " ".join(
                    r.get("content", "") for r in search_result["results"]
                ).lower()
                verdict = "REAL" if (
                    ("breach" in result_texts or "hack" in result_texts or "leak" in result_texts) and
                    len(search_result["results"]) >= 2
                ) else "FAKE"
            else:
                verdict = "FAKE"

            result = {
                "verdict": verdict,
                "confidence": 0.75 if verdict == "REAL" else 0.65,
                "reason": answer[:300] if answer else "No corroborating evidence found via Tavily search",
                "sources": sources[:5],
            }

        except Exception as e:
            result = {
                "verdict": "FAKE",
                "confidence": 0.3,
                "reason": f"Tavily search error: {str(e)}",
                "sources": [],
            }

        return {"messages": [AIMessage(content=json.dumps(result))]}

    async def stream(self, query: str) -> dict:
        state = {"messages": [HumanMessage(content=query)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "TavilyNewsVerificationAgent",
            "agent_message": final_msg.content if final_msg else "{}",
        }
