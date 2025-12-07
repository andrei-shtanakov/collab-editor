"""
Pytest configuration and fixtures for backend tests.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.session_store import session_store


@pytest.fixture
def client():
    """Synchronous test client for simple API tests."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client for async tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def clean_session_store():
    """Clean session store before each test."""
    session_store._sessions.clear()
    yield
    session_store._sessions.clear()
