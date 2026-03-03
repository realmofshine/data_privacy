"""Run the Data Privacy AG-UI server."""
import uvicorn
from agent.configs import AGUI_PORT

if __name__ == "__main__":
    uvicorn.run(
        "agent.app:app",
        host="0.0.0.0",
        port=AGUI_PORT,
        reload=True,
        reload_excludes=[".venv", "__pycache__", "*.pyc"],
    )
