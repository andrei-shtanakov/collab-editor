"""
Tests for WebSocket synchronization.
"""

import pytest
from fastapi.testclient import TestClient


class TestWebSocketConnection:
    """Tests for WebSocket connection handling."""

    def test_websocket_connect_valid_session(self, client: TestClient):
        """WebSocket connects successfully to valid session."""
        # Create session first
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        # Connect via WebSocket
        with client.websocket_connect(f"/ws/{session_id}") as websocket:
            # Connection should be established
            # Send a simple ping to verify connection works
            pass  # Just connecting and disconnecting is the test

    def test_websocket_connect_invalid_session(self, client: TestClient):
        """WebSocket connection to non-existent session fails."""
        # Try to connect to non-existent session
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/nonexistent"):
                pass

    def test_websocket_multiple_clients(self, client: TestClient):
        """Multiple clients can connect to same session."""
        # Create session
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        # Connect first client
        with client.websocket_connect(f"/ws/{session_id}") as ws1:
            # Connect second client
            with client.websocket_connect(f"/ws/{session_id}") as ws2:
                # Both should be connected
                pass

    def test_websocket_message_relay(self, client: TestClient):
        """Messages are relayed between clients."""
        # Create session
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        with client.websocket_connect(f"/ws/{session_id}") as ws1:
            with client.websocket_connect(f"/ws/{session_id}") as ws2:
                # Send a sync message from ws1 (type 0 = sync, subtype 2 = update)
                # Format: [msg_type, sync_type, ...data]
                test_message = bytes([0, 2, 1, 2, 3, 4])  # Sync update message
                ws1.send_bytes(test_message)

                # ws2 should receive it
                received = ws2.receive_bytes()
                assert received == test_message


class TestWebSocketSync:
    """Tests for Yjs sync protocol handling."""

    def test_sync_message_stored(self, client: TestClient):
        """Sync update messages are stored for new clients."""
        # Create session
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        # First client sends update
        update_msg = bytes([0, 2, 10, 20, 30])  # Sync update
        with client.websocket_connect(f"/ws/{session_id}") as ws1:
            ws1.send_bytes(update_msg)

        # New client should receive stored updates on connect
        with client.websocket_connect(f"/ws/{session_id}") as ws2:
            received = ws2.receive_bytes()
            assert received == update_msg

    def test_awareness_broadcast(self, client: TestClient):
        """Awareness messages are broadcast to connected clients."""
        # Create session
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        # Two clients connected simultaneously
        awareness_msg = bytes([1, 1, 2, 3])  # Awareness message (type 1)
        with client.websocket_connect(f"/ws/{session_id}") as ws1:
            with client.websocket_connect(f"/ws/{session_id}") as ws2:
                # ws1 sends awareness
                ws1.send_bytes(awareness_msg)
                # ws2 should receive it
                received = ws2.receive_bytes()
                assert received == awareness_msg
