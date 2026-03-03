"""Starlette web application for the Data Privacy AG-UI server."""
import logging
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse

from agent.agui_endpoint import agui_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "dp-privacy-agui"})


app = Starlette(
    routes=[
        Route("/health", health, methods=["GET"]),
        Route("/ag-ui", agui_handler, methods=["POST"]),
    ],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ],
)


@app.on_event("startup")
async def startup():
    logger.info("Data Privacy AG-UI server started")
    logger.info("Endpoint: POST /ag-ui")
    logger.info("Health:   GET  /health")
