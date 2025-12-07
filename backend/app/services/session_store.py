"""
Session management service.
In-memory storage for MVP. Can be replaced with Redis/PostgreSQL later.
"""

from datetime import datetime
from typing import Dict, Optional, List
from nanoid import generate

from app.models import (
    Session,
    SessionStatus,
    ProgrammingLanguage,
    CreateSessionRequest,
    UpdateSessionRequest,
    SessionResponse,
)


class SessionStore:
    """In-memory session storage."""
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
    
    def _generate_id(self) -> str:
        """Generate a unique session ID."""
        # URL-safe characters, 10 chars long
        return generate(size=10)
    
    def create(
        self,
        request: Optional[CreateSessionRequest] = None,
        base_url: str = "http://localhost:5173",
        ws_base_url: str = "ws://localhost:8000"
    ) -> Session:
        """Create a new session."""
        session_id = self._generate_id()
        
        # Ensure unique ID
        while session_id in self._sessions:
            session_id = self._generate_id()
        
        language = ProgrammingLanguage.PYTHON
        initial_code = "# Write your code here\n"
        title = None
        
        if request:
            language = request.language
            initial_code = request.initial_code
            title = request.title
        
        session = Session(
            id=session_id,
            language=language,
            created_at=datetime.utcnow(),
            title=title,
            initial_code=initial_code,
        )
        
        self._sessions[session_id] = session
        return session
    
    def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        return self._sessions.get(session_id)
    
    def update(self, session_id: str, request: UpdateSessionRequest) -> Optional[Session]:
        """Update session settings."""
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        if request.language is not None:
            session.language = request.language
        if request.title is not None:
            session.title = request.title
        
        return session
    
    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def list_all(self, limit: int = 50, offset: int = 0) -> tuple[List[Session], int]:
        """List all sessions with pagination."""
        all_sessions = list(self._sessions.values())
        total = len(all_sessions)
        
        # Sort by created_at descending (newest first)
        all_sessions.sort(key=lambda s: s.created_at, reverse=True)
        
        # Apply pagination
        paginated = all_sessions[offset:offset + limit]
        
        return paginated, total
    
    def count_active(self) -> int:
        """Count active sessions."""
        return sum(
            1 for s in self._sessions.values()
            if s.status == SessionStatus.ACTIVE
        )
    
    def to_response(
        self,
        session: Session,
        base_url: str = "http://localhost:5173",
        ws_base_url: str = "ws://localhost:8000"
    ) -> SessionResponse:
        """Convert Session to SessionResponse."""
        return SessionResponse(
            id=session.id,
            url=f"{base_url}/?session={session.id}",
            websocket_url=f"{ws_base_url}/ws/{session.id}",
            language=session.language,
            title=session.title,
            created_at=session.created_at,
            status=session.status,
            participants_count=session.participants_count,
        )


# Singleton instance
session_store = SessionStore()
