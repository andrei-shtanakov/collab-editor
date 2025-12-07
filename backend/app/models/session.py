"""
Internal session model for storage.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Set

from .schemas import ProgrammingLanguage, SessionStatus


@dataclass
class Session:
    """Internal session representation."""
    id: str
    language: ProgrammingLanguage
    created_at: datetime
    title: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE
    initial_code: str = ""
    
    # Connected WebSocket clients (connection IDs)
    _participants: Set[str] = field(default_factory=set)
    
    @property
    def participants_count(self) -> int:
        return len(self._participants)
    
    def add_participant(self, conn_id: str) -> None:
        self._participants.add(conn_id)
    
    def remove_participant(self, conn_id: str) -> None:
        self._participants.discard(conn_id)
    
    def has_participants(self) -> bool:
        return len(self._participants) > 0
