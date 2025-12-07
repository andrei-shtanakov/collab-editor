"""
Session management API routes.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.models import (
    CreateSessionRequest,
    UpdateSessionRequest,
    SessionResponse,
    SessionListResponse,
    ErrorResponse,
)
from app.services import session_store, yjs_sync

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def get_urls():
    """Get base URLs from config (simplified)."""
    # In production, read from environment/config
    return {
        "base_url": "http://localhost:5173",
        "ws_base_url": "ws://localhost:8000",
    }


@router.post(
    "",
    response_model=SessionResponse,
    status_code=201,
    summary="Create a new session",
    responses={422: {"model": ErrorResponse}},
)
async def create_session(request: Optional[CreateSessionRequest] = None):
    """
    Create a new session for collaborative code editing.
    Returns the session ID and URLs for connecting.
    """
    urls = get_urls()
    session = session_store.create(
        request=request,
        base_url=urls["base_url"],
        ws_base_url=urls["ws_base_url"],
    )
    return session_store.to_response(
        session,
        base_url=urls["base_url"],
        ws_base_url=urls["ws_base_url"],
    )


@router.get(
    "",
    response_model=SessionListResponse,
    summary="List all sessions",
)
async def list_sessions(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Get a list of all active sessions.
    Useful for admin/debugging purposes.
    """
    urls = get_urls()
    sessions, total = session_store.list_all(limit=limit, offset=offset)
    
    return SessionListResponse(
        sessions=[
            session_store.to_response(s, urls["base_url"], urls["ws_base_url"])
            for s in sessions
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Get session info",
    responses={404: {"model": ErrorResponse}},
)
async def get_session(session_id: str):
    """Get information about a specific session."""
    session = session_store.get(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    urls = get_urls()
    return session_store.to_response(
        session,
        base_url=urls["base_url"],
        ws_base_url=urls["ws_base_url"],
    )


@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Update session",
    responses={404: {"model": ErrorResponse}},
)
async def update_session(session_id: str, request: UpdateSessionRequest):
    """Update session settings (language, title)."""
    session = session_store.update(session_id, request)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    urls = get_urls()
    return session_store.to_response(
        session,
        base_url=urls["base_url"],
        ws_base_url=urls["ws_base_url"],
    )


@router.delete(
    "/{session_id}",
    status_code=204,
    summary="Delete session",
    responses={404: {"model": ErrorResponse}},
)
async def delete_session(session_id: str):
    """Delete a session and disconnect all participants."""
    session = session_store.get(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Close all WebSocket connections
    await yjs_sync.delete_room(session_id)
    
    # Delete from store
    session_store.delete(session_id)
    
    return None
