"""Configuration — loads environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Mock Mode Toggle ───
# Set to True to use hardcoded mock responses (no API keys needed)
# Set to False to use real LLM calls (requires GOOGLE_API_KEY)
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

# Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Tavily
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Server
ORCHESTRATOR_PORT = int(os.getenv("ORCHESTRATOR_PORT", "8001"))
AGUI_PORT = int(os.getenv("AGUI_PORT", "8002"))

# Agent Ports
AGENT_PORTS = {
    "NewsVerificationAgent":  int(os.getenv("NEWS_VERIFICATION_PORT", "8010")),
    "TavilyNewsVerificationAgent": int(os.getenv("TAVILY_VERIFICATION_PORT", "8011")),
    "NLPAgent":              int(os.getenv("NLP_AGENT_PORT", "8012")),
    "RiskAgent":             int(os.getenv("RISK_AGENT_PORT", "8013")),
    "SimilarCompanyAgent":   int(os.getenv("SIMILAR_COMPANY_PORT", "8014")),
    "AlertAgent":            int(os.getenv("ALERT_AGENT_PORT", "8015")),
    "SuggestionAgent":       int(os.getenv("SUGGESTION_AGENT_PORT", "8016")),
}

# Model names
ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "gemini-2.5-pro")
NLP_MODEL = os.getenv("NLP_MODEL", "gemini-2.0-flash")
RISK_MODEL = os.getenv("RISK_MODEL", "gemini-2.5-flash")
ALERT_MODEL = os.getenv("ALERT_MODEL", "gemini-2.0-flash")
SUGGESTION_MODEL = os.getenv("SUGGESTION_MODEL", "gemini-2.0-flash")
VIEW_AGENT_MODEL = os.getenv("VIEW_AGENT_MODEL", "gemini-2.5-flash")
