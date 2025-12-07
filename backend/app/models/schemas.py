"""
Pydantic models for the Collaborative Code Editor API.
Based on OpenAPI specification.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ProgrammingLanguage(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SQL = "sql"


class SessionStatus(str, Enum):
    """Session status."""
    ACTIVE = "active"
    IDLE = "idle"
    CLOSED = "closed"


# === Request Models ===

class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    language: ProgrammingLanguage = ProgrammingLanguage.PYTHON
    initial_code: str = Field(
        default="# Write your code here\n",
        max_length=100000,
        description="Initial code in the editor"
    )
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Session title (optional)"
    )


class UpdateSessionRequest(BaseModel):
    """Request to update session settings."""
    language: Optional[ProgrammingLanguage] = None
    title: Optional[str] = Field(default=None, max_length=200)


class ExecuteCodeRequest(BaseModel):
    """Request to execute code."""
    code: str = Field(..., max_length=100000, description="Code to execute")
    language: ProgrammingLanguage
    stdin: str = Field(default="", max_length=10000, description="Input data")
    timeout: int = Field(default=10, ge=1, le=30, description="Timeout in seconds")


# === Response Models ===

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    timestamp: datetime
    version: str = "1.0.0"
    active_sessions: int = 0


class SessionResponse(BaseModel):
    """Session information response."""
    id: str
    url: str
    websocket_url: str
    language: ProgrammingLanguage
    title: Optional[str] = None
    created_at: datetime
    status: SessionStatus
    participants_count: int = 0

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """List of sessions response."""
    sessions: list[SessionResponse]
    total: int
    limit: int
    offset: int


class ExecuteCodeResponse(BaseModel):
    """Code execution result."""
    success: bool
    output: str
    stderr: str = ""
    execution_time_ms: int
    exit_code: int = 0


class ExecutionErrorResponse(BaseModel):
    """Code execution error."""
    success: bool = False
    error: str
    error_type: str  # syntax_error, runtime_error, timeout, memory_limit
    line: Optional[int] = None
    column: Optional[int] = None


class ErrorResponse(BaseModel):
    """Generic error response."""
    detail: str
