"""DP Orchestrator — Gemini 2.5 Pro router that delegates to specialized agents across 15 modes."""
import json
import uuid
import asyncio
from typing import Optional

from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from agent.configs import GOOGLE_API_KEY, ORCHESTRATOR_MODEL

# ─── Core DP agents (Mode 1: Breach Analysis) ───
from agent.agents.news_verification import NewsVerificationAgent
from agent.agents.tavily_verification import TavilyNewsVerificationAgent
from agent.agents.nlp_agent import NLPAgent
from agent.agents.risk_agent import RiskAgent
from agent.agents.similar_company import SimilarCompanyAgent
from agent.agents.alert_agent import AlertAgent
from agent.agents.suggestion_agent import SuggestionAgent

# ─── New agents for modes 3-15 ───
from agent.agents.compliance_agent import ComplianceAgent
from agent.agents.incident_response_agent import IncidentResponseAgent
from agent.agents.data_mapping_agent import DataMappingAgent
from agent.agents.dsr_agent import DSRAgent
from agent.agents.dark_web_agent import DarkWebMonitorAgent
from agent.agents.threat_model_agent import ThreatModelAgent
from agent.agents.vuln_scan_agent import VulnScanAgent
from agent.agents.access_control_agent import AccessControlAgent
from agent.agents.forensics_agent import ForensicsAgent
from agent.agents.security_arch_agent import SecurityArchAgent
from agent.agents.executive_report_agent import ExecutiveReportAgent

import logging
logger = logging.getLogger(__name__)


# ─── Mode → Agent mapping ───
MODE_AGENTS = {
    "breach_analysis": [
        "NewsVerificationAgent", "TavilyNewsVerificationAgent",
        "NLPAgent", "RiskAgent", "SimilarCompanyAgent",
        "AlertAgent", "SuggestionAgent",
    ],
    "knowledge_search": ["NLPAgent"],  # Uses NLPCypher via Neo4j
    "compliance": ["ComplianceAgent"],
    "risk_assessment": ["RiskAgent", "SimilarCompanyAgent"],
    "safety": [],  # Handled by existing guardrails
    "incident_response": ["IncidentResponseAgent"],
    "data_mapping": ["DataMappingAgent"],
    "dsr": ["DSRAgent"],
    "dark_web": ["DarkWebMonitorAgent"],
    "reports": ["ExecutiveReportAgent"],
    "threat_modeling": ["ThreatModelAgent"],
    "vulnerability": ["VulnScanAgent"],
    "access_control": ["AccessControlAgent"],
    "forensics": ["ForensicsAgent"],
    "security_arch": ["SecurityArchAgent"],
}

# Mode-specific instructions for the LLM
MODE_INSTRUCTIONS = {
    "breach_analysis": (
        "You are handling BREACH ANALYSIS mode.\n"
        "MANDATORY PRE-CHECK: Verify using NewsVerificationAgent AND TavilyNewsVerificationAgent.\n"
        "If FAKE → STOP and return 'FAKE_NEWS_DETECTED: <reason> SOURCES: <urls>'\n"
        "If REAL → run: NLPAgent → RiskAgent → SimilarCompanyAgent → AlertAgent → SuggestionAgent\n"
        "Return structured report with EXECUTIVE SUMMARY, INCIDENT PROFILE, RED ALERTS, YELLOW ALERTS, SUGGESTIONS."
    ),
    "knowledge_search": (
        "You are handling KNOWLEDGE SEARCH mode.\n"
        "Use NLPAgent to query the Neo4j graph database in natural language.\n"
        "Convert the user's question into a graph search and return results."
    ),
    "compliance": (
        "You are handling COMPLIANCE CHECK mode.\n"
        "Use ComplianceAgent to assess regulatory obligations.\n"
        "Pass the user's query directly to the ComplianceAgent."
    ),
    "risk_assessment": (
        "You are handling RISK ASSESSMENT mode.\n"
        "Use RiskAgent for risk scoring and SimilarCompanyAgent for finding similar risk profiles."
    ),
    "safety": (
        "You are handling SAFETY CHECK mode.\n"
        "Analyze the text for PII, toxicity, and factual accuracy."
    ),
    "incident_response": (
        "You are handling INCIDENT RESPONSE mode.\n"
        "Use IncidentResponseAgent to generate IR playbooks.\n"
        "Pass the incident description directly."
    ),
    "data_mapping": (
        "You are handling DATA MAPPING mode.\n"
        "Use DataMappingAgent for data flow analysis and classification.\n"
        "Pass the user's query directly."
    ),
    "dsr": (
        "You are handling DATA SUBJECT RIGHTS mode.\n"
        "Use DSRAgent to process data subject requests.\n"
        "Pass the request details directly."
    ),
    "dark_web": (
        "You are handling DARK WEB MONITORING mode.\n"
        "Use DarkWebMonitorAgent to scan for leaked credentials.\n"
        "Pass the domains/emails to monitor."
    ),
    "reports": (
        "You are handling EXECUTIVE REPORTING mode.\n"
        "Use ExecutiveReportAgent to generate board reports and metrics.\n"
        "Pass the report request directly."
    ),
    "threat_modeling": (
        "You are handling THREAT MODELING mode.\n"
        "Use ThreatModelAgent for STRIDE/DREAD analysis.\n"
        "Pass the system description directly."
    ),
    "vulnerability": (
        "You are handling VULNERABILITY ASSESSMENT mode.\n"
        "Use VulnScanAgent for CVE scanning and patch prioritization.\n"
        "Pass the software/system details directly."
    ),
    "access_control": (
        "You are handling ACCESS CONTROL mode.\n"
        "Use AccessControlAgent for IAM review and privilege analysis.\n"
        "Pass the request directly."
    ),
    "forensics": (
        "You are handling DIGITAL FORENSICS mode.\n"
        "Use ForensicsAgent for log analysis and timeline reconstruction.\n"
        "Pass the evidence/logs directly."
    ),
    "security_arch": (
        "You are handling SECURITY ARCHITECTURE mode.\n"
        "Use SecurityArchAgent for Zero Trust assessment and security posture.\n"
        "Pass the request directly."
    ),
}


class DPOrchestrator:
    """
    Gemini 2.5 Pro orchestrator supporting 15 modes with 18 specialized agents.
    """

    def __init__(self):
        # Instantiate all agents
        self._agents = {
            # Core DP
            "NewsVerificationAgent": NewsVerificationAgent(),
            "TavilyNewsVerificationAgent": TavilyNewsVerificationAgent(),
            "NLPAgent": NLPAgent(),
            "RiskAgent": RiskAgent(),
            "SimilarCompanyAgent": SimilarCompanyAgent(),
            "AlertAgent": AlertAgent(),
            "SuggestionAgent": SuggestionAgent(),
            # New agents
            "ComplianceAgent": ComplianceAgent(),
            "IncidentResponseAgent": IncidentResponseAgent(),
            "DataMappingAgent": DataMappingAgent(),
            "DSRAgent": DSRAgent(),
            "DarkWebMonitorAgent": DarkWebMonitorAgent(),
            "ThreatModelAgent": ThreatModelAgent(),
            "VulnScanAgent": VulnScanAgent(),
            "AccessControlAgent": AccessControlAgent(),
            "ForensicsAgent": ForensicsAgent(),
            "SecurityArchAgent": SecurityArchAgent(),
            "ExecutiveReportAgent": ExecutiveReportAgent(),
        }

        # Gemini 2.5 Pro LLM agent for routing
        self._llm_agent = LlmAgent(
            model=ORCHESTRATOR_MODEL,
            name="DPOrchestratorAgent",
            description="Routes data privacy queries to specialized agents across 15 modes.",
            instruction=self._root_instruction,
            tools=[self._list_agents, self._delegate_task],
        )

        self._user_id = "dp_orchestrator_user"
        self._runner = Runner(
            app_name=self._llm_agent.name,
            agent=self._llm_agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

        self._metadata: dict = {}

    def _root_instruction(self, context: ReadonlyContext) -> str:
        metadata = context.state.get("metadata", {})
        override = metadata.get("override", False)
        mode = metadata.get("mode", "breach_analysis")

        agent_list = "\n".join(f"- {name}" for name in MODE_AGENTS.get(mode, []))
        mode_instruction = MODE_INSTRUCTIONS.get(mode, "Process the user's security query.")

        base = (
            f"You are a DPOrchestrator managing specialist agents.\n"
            f"Current MODE: {mode}\n\n"
            f"Available agents for this mode:\n{agent_list}\n\n"
            f"{mode_instruction}\n\n"
        )

        if mode == "breach_analysis" and override:
            base += (
                "OVERRIDE ACTIVE: Skip NewsVerificationAgent and TavilyNewsVerificationAgent.\n"
                "Immediately proceed: NLPAgent → RiskAgent → SimilarCompanyAgent → AlertAgent → SuggestionAgent\n\n"
            )

        base += (
            "IMPORTANT: Call the appropriate agent(s) using delegate_task.\n"
            "For single-agent modes, just call that agent and return its response.\n"
            "Always provide the full user query to the agent."
        )

        return base

    def _list_agents(self) -> list[str]:
        return list(self._agents.keys())

    async def _delegate_task(self, agent_name: str, message: str, tool_context: ToolContext) -> str:
        if agent_name not in self._agents:
            return f"Agent '{agent_name}' not available."

        state = tool_context.state
        if "session_id" not in state:
            state["session_id"] = str(uuid.uuid4())
        metadata = state.get("metadata", {})

        agent = self._agents[agent_name]

        try:
            # Core breach pipeline agents (original behavior)
            if agent_name == "NewsVerificationAgent":
                result = await agent.stream(message)
            elif agent_name == "TavilyNewsVerificationAgent":
                result = await agent.stream(message)
            elif agent_name == "NLPAgent":
                result = await agent.stream(message)
                if "agent_metadata" in result:
                    metadata["NLPAgent"] = result["agent_metadata"]
                    state["metadata"] = metadata
            elif agent_name == "RiskAgent":
                result = await agent.stream(message, metadata)
                if "predictions" in result:
                    metadata["RiskAgent"] = result["predictions"]
                    state["metadata"] = metadata
            elif agent_name == "SimilarCompanyAgent":
                result = await agent.stream(message, metadata)
                if "similar_companies" in result:
                    metadata["SimilarCompanyAgent"] = result["similar_companies"]
                    state["metadata"] = metadata
            elif agent_name == "AlertAgent":
                result = await agent.stream(metadata)
                if "alerts" in result:
                    metadata["AlertAgent"] = result["alerts"]
                    state["metadata"] = metadata
            elif agent_name == "SuggestionAgent":
                nlp_data = metadata.get("NLPAgent", {})
                incident_id = nlp_data.get("Incident", {}).get("id", message)
                result = await agent.stream(incident_id)
            else:
                # All new agents follow the same pattern
                result = await agent.stream(message, metadata)

            return result.get("agent_message", "No response")

        except Exception as e:
            logger.error(f"Error in {agent_name}: {e}", exc_info=True)
            return f"Error calling {agent_name}: {str(e)}"

    async def invoke(self, query: str, session_id: str, metadata: dict) -> dict:
        """Main entry point: run the orchestrator with Gemini 2.5 Pro routing."""
        session = await self._runner.session_service.get_session(
            app_name=self._llm_agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._llm_agent.name,
                user_id=self._user_id,
                session_id=session_id,
                state={"metadata": metadata},
            )
        else:
            session.state["metadata"] = metadata

        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)],
        )

        events = []
        async for event in self._runner.run_async(
            user_id=self._user_id,
            session_id=session.id,
            new_message=content,
        ):
            events.append(event)

        if not events or not events[-1].content or not events[-1].content.parts:
            return {"agent_name": "DPOrchestratorAgent", "agent_message": ""}

        reply = "\n".join(p.text for p in events[-1].content.parts if p.text)
        return {"agent_name": "DPOrchestratorAgent", "agent_message": reply}
