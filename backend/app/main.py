"""
Collaborative Code Editor - Backend API
"""

from datetime import datetime
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import HealthResponse
from app.routers import sessions_router, websocket_router
from app.services import session_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("🚀 Starting Collaborative Code Editor API")
    yield
    logger.info("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Collaborative Code Editor API",
    description="""
API для совместного редактирования кода в реальном времени.

## Возможности

- **Сессии**: Создание и управление сессиями для совместного кодинга
- **Real-time**: WebSocket синхронизация через Yjs protocol
- **Языки**: Поддержка множества языков программирования

## WebSocket Protocol

Подключение к `/ws/{session_id}` для real-time синхронизации.
Используется Yjs binary protocol для conflict-free editing.
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware - разрешаем frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions_router)
app.include_router(websocket_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        active_sessions=session_store.count_active(),
    )


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs."""
    return {
        "message": "Collaborative Code Editor API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
