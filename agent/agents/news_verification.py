"""NewsVerificationAgent — verifies news using Google Search grounding (Gemini)."""
import json
import re
import os
import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class NewsVerificationState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


class NewsVerificationAgent:
    """
    Verifies whether a news article is REAL or FAKE using
    Google Search grounding via Gemini.
    """

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.grounding_tool = types.Tool(google_search=types.GoogleSearch())

        graph = StateGraph(NewsVerificationState)
        graph.add_node("verify", self.verify)
        graph.add_edge("verify", END)
        graph.set_entry_point("verify")
        self.graph = graph.compile()

    def verify(self, state: NewsVerificationState):
        user_msg = state["messages"][-1].content

        prompt = f"""You are a cyber threat intelligence (CTI) verification system.

Classify the claim as REAL or FAKE.
Use Google Search grounding. Base your answer ONLY on grounded web results.
If the claim is not clearly confirmed by reliable sources, classify it as FAKE.

Return STRICT JSON ONLY:
{{
  "verdict": "REAL | FAKE",
  "confidence": 0.0-1.0,
  "reason": "Short explanation based strictly on grounded evidence",
  "sources": ["list of source URLs used"]
}}

Claim:
{user_msg}
"""

        config = types.GenerateContentConfig(
            tools=[self.grounding_tool],
            temperature=0,
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )

        # Extract grounded URLs
        source_urls = []
        try:
            candidate = response.candidates[0]
            metadata = candidate.grounding_metadata
            used_indices = set()
            for support in metadata.grounding_supports:
                for idx in support.grounding_chunk_indices:
                    used_indices.add(idx)
            for idx in used_indices:
                chunk = metadata.grounding_chunks[idx]
                if chunk.web and chunk.web.uri:
                    source_urls.append(chunk.web.uri)
        except Exception:
            source_urls = []

        # Parse JSON response
        try:
            raw_text = response.candidates[0].content.parts[0].text.strip()
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```[a-zA-Z]*\n?", "", raw_text)
                raw_text = re.sub(r"\n?```$", "", raw_text)
            parsed = json.loads(raw_text)
            if not all(k in parsed for k in ["verdict", "confidence", "reason", "sources"]):
                raise ValueError("Invalid schema")
        except Exception:
            parsed = {
                "verdict": "FAKE",
                "confidence": 0.2,
                "reason": "Model output could not be parsed",
                "sources": source_urls,
            }

        # Merge grounded URLs into parsed sources
        all_sources = list(set(parsed.get("sources", []) + source_urls))
        parsed["sources"] = all_sources[:10]

        return {"messages": [AIMessage(content=json.dumps(parsed, separators=(",", ":")))]}

    async def stream(self, query: str) -> dict:
        state = {"messages": [HumanMessage(content=query)]}
        result = self.graph.invoke(state)
        final_msg = next(
            (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)), None
        )
        return {
            "agent_name": "NewsVerificationAgent",
            "agent_message": final_msg.content if final_msg else "{}",
        }
