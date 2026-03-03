"""Mock orchestrator — returns hardcoded mock data without LLM calls.

Used when USE_MOCK_DATA=True. Returns ALL agent responses so the endpoint
can stream each one individually with proper attribution.
"""
import asyncio
from agent import mock_data


# Mode → list of (agent_name, display_label, mock_function, args_type)
MODE_PIPELINES = {
    "breach_analysis": [
        ("NewsVerificationAgent", "NewsVerify", mock_data.mock_news_verification, "message"),
        ("TavilyNewsVerificationAgent", "Tavily", mock_data.mock_tavily_verification, "message"),
        ("NLPAgent", "NLP", mock_data.mock_nlp_agent, "message"),
        ("RiskAgent", "Risk", mock_data.mock_risk_agent, "message"),
        ("SimilarCompanyAgent", "Similar", mock_data.mock_similar_company, "message"),
        ("AlertAgent", "Alert", mock_data.mock_alert_agent, "none"),
        ("SuggestionAgent", "Suggest", mock_data.mock_suggestion_agent, "message"),
    ],
    "knowledge_search": [
        ("NLPAgent", "NLP", mock_data.mock_nlp_agent, "message"),
    ],
    "compliance": [
        ("ComplianceAgent", "Compliance", mock_data.mock_compliance, "message"),
    ],
    "risk_assessment": [
        ("RiskAgent", "Risk", mock_data.mock_risk_agent, "message"),
        ("SimilarCompanyAgent", "SimilarCompany", mock_data.mock_similar_company, "message"),
    ],
    "safety": [],
    "incident_response": [
        ("IncidentResponseAgent", "IR", mock_data.mock_incident_response, "message"),
    ],
    "data_mapping": [
        ("DataMappingAgent", "DataMapping", mock_data.mock_data_mapping, "message"),
    ],
    "dsr": [
        ("DSRAgent", "DSR", mock_data.mock_dsr, "message"),
    ],
    "dark_web": [
        ("DarkWebMonitorAgent", "DarkWeb", mock_data.mock_dark_web, "message"),
    ],
    "reports": [
        ("ExecutiveReportAgent", "ExecutiveReport", mock_data.mock_executive_report, "message"),
    ],
    "threat_modeling": [
        ("ThreatModelAgent", "ThreatModel", mock_data.mock_threat_model, "message"),
    ],
    "vulnerability": [
        ("VulnScanAgent", "VulnScan", mock_data.mock_vuln_scan, "message"),
    ],
    "access_control": [
        ("AccessControlAgent", "AccessControl", mock_data.mock_access_control, "message"),
    ],
    "forensics": [
        ("ForensicsAgent", "Forensics", mock_data.mock_forensics, "message"),
    ],
    "security_arch": [
        ("SecurityArchAgent", "ZeroTrust", mock_data.mock_security_arch, "message"),
    ],
}


class MockOrchestrator:
    """Runs the mock pipeline for a given mode without any LLM calls.

    Returns all agent results so the endpoint can stream each one.
    """

    async def invoke(self, query: str, session_id: str, metadata: dict) -> dict:
        mode = metadata.get("mode", "breach_analysis")
        pipeline = MODE_PIPELINES.get(mode, [])

        if not pipeline:
            return {
                "agent_results": [{
                    "agent_name": "SafetyAgent",
                    "display_label": "Guardrails",
                    "agent_message": (
                        "✅ Safety check complete.\n\n"
                        "PII Scan: No PII detected\n"
                        "Toxicity: Clean\n"
                        "Hallucination: Grounded (no issues)\n"
                        "Content Filter: Passed"
                    ),
                }],
            }

        agent_results = []

        for agent_name, display_label, mock_fn, args_type in pipeline:
            await asyncio.sleep(0.3)

            if args_type == "message":
                result = mock_fn(query)
            elif args_type == "metadata":
                result = mock_fn(metadata)
            elif args_type == "none":
                result = mock_fn()
            else:
                result = mock_fn(query)

            agent_results.append({
                "agent_name": agent_name,
                "display_label": display_label,
                "agent_message": result.get("agent_message", ""),
            })

        return {"agent_results": agent_results}
