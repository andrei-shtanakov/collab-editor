"""
Tests for session management API.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client: TestClient):
        """Health endpoint returns 200 and correct status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
        assert data["active_sessions"] == 0


class TestSessionCreation:
    """Tests for session creation endpoint."""

    def test_create_session_default(self, client: TestClient):
        """Create session with default parameters."""
        response = client.post("/api/sessions")
        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert len(data["id"]) == 10  # nanoid length
        assert data["language"] == "python"
        assert data["status"] == "active"
        assert data["participants_count"] == 0
        assert "url" in data
        assert "websocket_url" in data
        assert data["id"] in data["url"]
        assert data["id"] in data["websocket_url"]

    def test_create_session_with_language(self, client: TestClient):
        """Create session with specific language."""
        response = client.post(
            "/api/sessions",
            json={"language": "javascript"}
        )
        assert response.status_code == 201
        assert response.json()["language"] == "javascript"

    def test_create_session_with_initial_code(self, client: TestClient):
        """Create session with initial code."""
        code = "console.log('hello');"
        response = client.post(
            "/api/sessions",
            json={
                "language": "javascript",
                "initial_code": code,
            }
        )
        assert response.status_code == 201
        # Initial code is stored but not returned in response

    def test_create_session_with_title(self, client: TestClient):
        """Create session with title."""
        response = client.post(
            "/api/sessions",
            json={"title": "My Coding Session"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == "My Coding Session"

    def test_create_multiple_sessions(self, client: TestClient):
        """Each session gets unique ID."""
        response1 = client.post("/api/sessions")
        response2 = client.post("/api/sessions")

        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["id"] != response2.json()["id"]


class TestSessionRetrieval:
    """Tests for session retrieval endpoint."""

    def test_get_session(self, client: TestClient):
        """Get existing session by ID."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["id"]

        # Get session
        response = client.get(f"/api/sessions/{session_id}")
        assert response.status_code == 200
        assert response.json()["id"] == session_id

    def test_get_nonexistent_session(self, client: TestClient):
        """Get non-existent session returns 404."""
        response = client.get("/api/sessions/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestSessionUpdate:
    """Tests for session update endpoint."""

    def test_update_session_language(self, client: TestClient):
        """Update session language."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["id"]

        # Update language
        response = client.patch(
            f"/api/sessions/{session_id}",
            json={"language": "typescript"}
        )
        assert response.status_code == 200
        assert response.json()["language"] == "typescript"

    def test_update_session_title(self, client: TestClient):
        """Update session title."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["id"]

        # Update title
        response = client.patch(
            f"/api/sessions/{session_id}",
            json={"title": "Updated Title"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_update_nonexistent_session(self, client: TestClient):
        """Update non-existent session returns 404."""
        response = client.patch(
            "/api/sessions/nonexistent",
            json={"language": "python"}
        )
        assert response.status_code == 404


class TestSessionDeletion:
    """Tests for session deletion endpoint."""

    def test_delete_session(self, client: TestClient):
        """Delete existing session."""
        # Create session
        create_response = client.post("/api/sessions")
        session_id = create_response.json()["id"]

        # Delete session
        response = client.delete(f"/api/sessions/{session_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_session(self, client: TestClient):
        """Delete non-existent session returns 404."""
        response = client.delete("/api/sessions/nonexistent")
        assert response.status_code == 404


class TestSessionList:
    """Tests for session list endpoint."""

    def test_list_sessions_empty(self, client: TestClient):
        """List sessions when none exist."""
        response = client.get("/api/sessions")
        assert response.status_code == 200
        data = response.json()
        assert data["sessions"] == []
        assert data["total"] == 0

    def test_list_sessions_with_data(self, client: TestClient):
        """List sessions with existing sessions."""
        # Create sessions
        client.post("/api/sessions")
        client.post("/api/sessions")
        client.post("/api/sessions")

        response = client.get("/api/sessions")
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 3
        assert data["total"] == 3

    def test_list_sessions_pagination(self, client: TestClient):
        """List sessions with pagination."""
        # Create 5 sessions
        for _ in range(5):
            client.post("/api/sessions")

        # Get first 2
        response = client.get("/api/sessions?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 0

        # Get next 2
        response = client.get("/api/sessions?limit=2&offset=2")
        data = response.json()
        assert len(data["sessions"]) == 2
        assert data["offset"] == 2
