"""AG-UI SSE endpoint for the Data Privacy application.

Streams events progressively to the browser:
1. RunStarted
2. For EACH agent in the pipeline:
   - StepStarted (with agent name)
   - TextMessageStart/Content/End (agent's response, labeled)
   - StepFinished
3. StateSnapshot (A2UI card for the final agent)
4. RunFinished

Toggle: USE_MOCK_DATA in configs.py (default: True)
"""
import uuid
import asyncio
import logging

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from sse_starlette.sse import EventSourceResponse

from ag_ui.core import (
    RunStartedEvent, RunFinishedEvent, RunErrorEvent,
    StepStartedEvent, StepFinishedEvent,
    TextMessageStartEvent, TextMessageContentEvent, TextMessageEndEvent,
    StateSnapshotEvent,
)
from agent.configs import USE_MOCK_DATA
from agent import views

logger = logging.getLogger(__name__)

# ─── Create orchestrator based on mode ───
if USE_MOCK_DATA:
    from agent.orchestrator.mock_orchestrator import MockOrchestrator
    _orchestrator = MockOrchestrator()
    _USE_LLM_STREAMING = False
    _genai_client = None
    _STREAMING_MODEL = None
    logger.info("🟡 MOCK MODE — using hardcoded mock data (no API keys needed)")
else:
    from agent.orchestrator.dp_orchestrator import DPOrchestrator
    _orchestrator = DPOrchestrator()
    import os
    try:
        from google import genai
        _genai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        _STREAMING_MODEL = os.getenv("VIEW_AGENT_MODEL", "gemini-2.5-flash")
        _USE_LLM_STREAMING = True
    except Exception:
        _genai_client = None
        _STREAMING_MODEL = None
        _USE_LLM_STREAMING = False
    logger.info("🟢 LIVE MODE — using real LLM agents")


async def agui_handler(request: Request) -> Response:
    body = await request.json()

    # ─── Handle button actions ───────────────────────────────────────
    override = False
    user_message = ""

    action = body.get("action")
    if action:
        action_name = action.get("name")

        if action_name == "force_proceed":
            override = True
            user_message = (
                body.get("previous_query")
                or body.get("previousQuery")
                or body.get("message", "")
            )
        elif action_name in ("cancel_workflow", "discard_article"):
            a2ui = views.render_cancel("Article discarded. Workflow cancelled.")
            return JSONResponse({"status": "cancelled", "a2ui": a2ui})
        else:
            from agent.action_results import get_action_result
            result_card = get_action_result(action_name)
            if result_card:
                return JSONResponse({"status": "action_complete", "a2ui": result_card})
            return JSONResponse({
                "status": "action_complete",
                "a2ui": views.render_success(f"Action '{action_name}' completed successfully."),
            })

    # ─── Extract user message ────────────────────────────────────────
    if not user_message:
        messages = body.get("messages", [])
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            user_message = part.get("text", "")
                            break
                elif isinstance(content, str):
                    user_message = content
                if user_message:
                    break
        if not user_message:
            user_message = body.get("message", "")

    thread_id = body.get("threadId", str(uuid.uuid4()))
    run_id = str(uuid.uuid4())
    session_id = thread_id
    mode = body.get("mode", "breach_analysis")
    metadata = {"override": override, "mode": mode}

    async def event_generator():
        try:
            # 1. Run Started
            yield {
                "event": "RunStarted",
                "data": RunStartedEvent(
                    type="RUN_STARTED",
                    threadId=thread_id,
                    runId=run_id,
                ).model_dump_json(),
            }

            # 2. Call orchestrator
            result = await _orchestrator.invoke(user_message, session_id, metadata)
            agent_results = result.get("agent_results", [])

            # Fallback for old-style single result
            if not agent_results and "agent_message" in result:
                agent_results = [{
                    "agent_name": result.get("agent_name", "Agent"),
                    "display_label": result.get("agent_name", "Agent"),
                    "agent_message": result["agent_message"],
                }]

            final_agent_message = ""
            final_agent_name = ""

            # 3. Stream EACH agent's response as a separate step + message
            for i, agent_result in enumerate(agent_results):
                agent_name = agent_result.get("agent_name", f"Agent-{i}")
                display_label = agent_result.get("display_label", agent_name)
                agent_message = agent_result.get("agent_message", "")

                # Track the final agent for A2UI card
                final_agent_message = agent_message
                final_agent_name = agent_name

                # ── Step Started ──
                yield {
                    "event": "StepStarted",
                    "data": StepStartedEvent(
                        type="STEP_STARTED",
                        step_name=display_label,
                    ).model_dump_json(),
                }

                await asyncio.sleep(0.2)

                # ── Text Message for this agent ──
                msg_id = str(uuid.uuid4())
                yield {
                    "event": "TextMessageStart",
                    "data": TextMessageStartEvent(
                        type="TEXT_MESSAGE_START",
                        messageId=msg_id,
                        role="assistant",
                    ).model_dump_json(),
                }

                # Send agent label header
                header = f"**🤖 {display_label}**\n\n"
                yield {
                    "event": "TextMessageContent",
                    "data": TextMessageContentEvent(
                        type="TEXT_MESSAGE_CONTENT",
                        messageId=msg_id,
                        delta=header,
                    ).model_dump_json(),
                }
                await asyncio.sleep(0.05)

                # Stream agent response in chunks (simulates token streaming)
                if agent_message:
                    words = agent_message.split(" ")
                    chunk_size = 6
                    for j in range(0, len(words), chunk_size):
                        chunk = " ".join(words[j:j + chunk_size])
                        if j > 0:
                            chunk = " " + chunk
                        yield {
                            "event": "TextMessageContent",
                            "data": TextMessageContentEvent(
                                type="TEXT_MESSAGE_CONTENT",
                                messageId=msg_id,
                                delta=chunk,
                            ).model_dump_json(),
                        }
                        await asyncio.sleep(0.02)

                yield {
                    "event": "TextMessageEnd",
                    "data": TextMessageEndEvent(
                        type="TEXT_MESSAGE_END",
                        messageId=msg_id,
                    ).model_dump_json(),
                }

                # ── Step Finished ──
                yield {
                    "event": "StepFinished",
                    "data": StepFinishedEvent(
                        type="STEP_FINISHED",
                        step_name=display_label,
                    ).model_dump_json(),
                }

                await asyncio.sleep(0.1)

            # 4. A2UI Card (for final agent result)
            a2ui = views.render_for_mode(mode, final_agent_message, user_message)

            yield {
                "event": "StateSnapshot",
                "data": StateSnapshotEvent(
                    type="STATE_SNAPSHOT",
                    snapshot={
                        "a2ui": a2ui,
                        "agentName": final_agent_name,
                        "previousQuery": user_message,
                    },
                ).model_dump_json(),
            }

            # 5. Run Finished
            yield {
                "event": "RunFinished",
                "data": RunFinishedEvent(
                    type="RUN_FINISHED",
                    threadId=thread_id,
                    runId=run_id,
                ).model_dump_json(),
            }

        except Exception as e:
            logger.error(f"AG-UI error: {e}", exc_info=True)
            yield {
                "event": "RunError",
                "data": RunErrorEvent(
                    type="RUN_ERROR",
                    message=str(e),
                ).model_dump_json(),
            }

    return EventSourceResponse(event_generator())
