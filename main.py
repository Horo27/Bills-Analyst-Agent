"""
Main entry point for the Smart Home Expense & Maintenance Analyst Agent
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from smart_home_agent.core.config import settings
from smart_home_agent.core.database import init_db
from smart_home_agent.api.routes import api_router
from smart_home_agent.api.middleware import setup_middleware
from smart_home_agent.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    setup_logging()
    await init_db()
    yield
    # Shutdown
    pass


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Smart Home Expense & Maintenance Analyst",
        description="An intelligent agent for managing household expenses and maintenance",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware
    setup_middleware(app)

    # Include routers
    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
