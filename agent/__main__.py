"""Run the Data Privacy AG-UI server."""
import os
import uvicorn
from agent.configs import AGUI_PORT

if __name__ == "__main__":
    # Railway sets PORT env var — use it in production, fallback to AGUI_PORT
    port = int(os.getenv("PORT", AGUI_PORT))
    is_production = os.getenv("RAILWAY_ENVIRONMENT") is not None

    uvicorn.run(
        "agent.app:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production,
        reload_excludes=[".venv", "__pycache__", "*.pyc"],
    )
