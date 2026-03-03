# Data Privacy — AG-UI + A2UI Complete Project

End-to-end data privacy pipeline with AG-UI streaming and A2UI card rendering.

## Project Structure

```
dp_privacy/
├── agent/                          # Python backend
│   ├── app.py                      # Starlette server
│   ├── agui_endpoint.py            # AG-UI SSE streaming endpoint
│   ├── views.py                    # A2UI card builders
│   ├── orchestrator/
│   │   └── dp_orchestrator.py      # Gemini 2.5 Pro orchestrator
│   ├── agents/
│   │   ├── news_verification.py    # Google Search grounded verification
│   │   ├── tavily_verification.py  # Tavily AI verification (2nd opinion)
│   │   ├── nlp_agent.py            # NLP extraction + Neo4j ingestion
│   │   ├── risk_agent.py           # GNN-based risk scoring
│   │   ├── similar_company.py      # Vector similarity search
│   │   ├── alert_agent.py          # RED/YELLOW alert generation
│   │   └── suggestion_agent.py     # Security recommendations
│   └── configs.py                  # Environment config
├── client/                         # React + Vite frontend
│   ├── src/
│   │   ├── App.tsx                 # Main app with AG-UI + A2UI
│   │   └── App.css                 # Styling
│   ├── package.json
│   └── index.html
├── pyproject.toml                  # Python dependencies
└── .env.example                    # Environment variables template
```

## Setup

### 1. Backend

```bash
cd dp_privacy
cp .env.example .env
# Fill in your API keys in .env

uv sync
uv run python -m agent
```

### 2. Frontend

```bash
cd dp_privacy/client
npm install
npm run dev
```

## Environment Variables

```
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
ORCHESTRATOR_PORT=8001
AGUI_PORT=8002
```

## How It Works

1. User pastes a news article about a data breach
2. AG-UI opens SSE stream → live progress updates to browser
3. NewsVerificationAgent + TavilyAgent verify if article is real/fake
4. If FAKE → A2UI renders warning card with "Proceed Anyway" / "Discard" buttons
5. If REAL (or override) → full pipeline: NLP → Risk → SimilarCompany → Alerts → Suggestions
6. ViewAgent converts response to A2UI card → rendered as structured report
