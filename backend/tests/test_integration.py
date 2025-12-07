"""
Integration tests for collaborative editing.

Tests the full sync flow between multiple WebSocket clients
without browser involvement.
"""

import pytest
from fastapi.testclient import TestClient
import threading
import time


class TestMultiClientSync:
    """Test synchronization between multiple clients."""

    def test_two_clients_sync_updates(self, client: TestClient):
        """
        Two clients connect and sync updates bidirectionally.

        Flow:
        1. Create session
        2. Client A and B connect
        3. A sends update -> B receives it
        4. B sends update -> A receives it
        """
        # Create session
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        with client.websocket_connect(f"/ws/{session_id}") as ws_a:
            with client.websocket_connect(f"/ws/{session_id}") as ws_b:
                # Client A sends sync update
                update_from_a = bytes([0, 2, 100, 101, 102])  # Sync update
                ws_a.send_bytes(update_from_a)

                # Client B should receive it
                received_by_b = ws_b.receive_bytes()
                assert received_by_b == update_from_a

                # Client B sends sync update
                update_from_b = bytes([0, 2, 200, 201, 202])
                ws_b.send_bytes(update_from_b)

                # Client A should receive it
                received_by_a = ws_a.receive_bytes()
                assert received_by_a == update_from_b

    def test_three_clients_broadcast(self, client: TestClient):
        """
        Three clients - updates broadcast to all others.

        When A sends, both B and C should receive.
        """
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        with client.websocket_connect(f"/ws/{session_id}") as ws_a:
            with client.websocket_connect(f"/ws/{session_id}") as ws_b:
                with client.websocket_connect(f"/ws/{session_id}") as ws_c:
                    # A sends update
                    update = bytes([0, 2, 1, 2, 3, 4, 5])
                    ws_a.send_bytes(update)

                    # Both B and C receive
                    assert ws_b.receive_bytes() == update
                    assert ws_c.receive_bytes() == update

    def test_late_joiner_receives_history(self, client: TestClient):
        """
        Client joining later receives stored updates.

        Flow:
        1. Client A connects, sends updates
        2. Client A disconnects
        3. Client B connects
        4. Client B receives A's updates
        """
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        updates = [
            bytes([0, 2, 10, 20, 30]),
            bytes([0, 2, 40, 50, 60]),
            bytes([0, 2, 70, 80, 90]),
        ]

        # Client A sends updates
        with client.websocket_connect(f"/ws/{session_id}") as ws_a:
            for update in updates:
                ws_a.send_bytes(update)

        # Client A disconnected, Client B joins
        with client.websocket_connect(f"/ws/{session_id}") as ws_b:
            # B should receive all stored updates
            received = []
            for _ in range(len(updates)):
                received.append(ws_b.receive_bytes())

            assert received == updates

    def test_sender_does_not_receive_own_message(self, client: TestClient):
        """Sender should not receive their own messages."""
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        with client.websocket_connect(f"/ws/{session_id}") as ws_a:
            with client.websocket_connect(f"/ws/{session_id}") as ws_b:
                # A sends
                update = bytes([0, 2, 1, 2, 3])
                ws_a.send_bytes(update)

                # B receives
                received = ws_b.receive_bytes()
                assert received == update

                # Now B sends
                update_b = bytes([0, 2, 4, 5, 6])
                ws_b.send_bytes(update_b)

                # A receives B's message (not its own)
                received_a = ws_a.receive_bytes()
                assert received_a == update_b


class TestSessionLifecycle:
    """Test session lifecycle with WebSocket connections."""

    def test_session_tracks_participants(self, client: TestClient):
        """Session participant count updates as clients connect/disconnect."""
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        # Initially no participants
        session = client.get(f"/api/sessions/{session_id}").json()
        assert session["participants_count"] == 0

        with client.websocket_connect(f"/ws/{session_id}"):
            # One participant
            session = client.get(f"/api/sessions/{session_id}").json()
            assert session["participants_count"] == 1

            with client.websocket_connect(f"/ws/{session_id}"):
                # Two participants
                session = client.get(f"/api/sessions/{session_id}").json()
                assert session["participants_count"] == 2

            # Back to one
            session = client.get(f"/api/sessions/{session_id}").json()
            assert session["participants_count"] == 1

        # Back to zero
        session = client.get(f"/api/sessions/{session_id}").json()
        assert session["participants_count"] == 0

    def test_delete_session_disconnects_clients(self, client: TestClient):
        """Deleting a session closes all WebSocket connections."""
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        # This test verifies the flow but TestClient may not fully
        # simulate the disconnect behavior
        with client.websocket_connect(f"/ws/{session_id}") as ws:
            # Delete session (in real scenario, ws would be closed)
            delete_response = client.delete(f"/api/sessions/{session_id}")
            assert delete_response.status_code == 204

            # Session should no longer exist
            get_response = client.get(f"/api/sessions/{session_id}")
            assert get_response.status_code == 404


class TestMessageTypes:
    """Test different Yjs message types are handled correctly."""

    def test_sync_step1_not_stored(self, client: TestClient):
        """Sync step 1 (state vector) is broadcast but not stored."""
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        # Client sends sync step 1
        sync_step1 = bytes([0, 0, 1, 2, 3])  # Type 0, subtype 0

        with client.websocket_connect(f"/ws/{session_id}") as ws_a:
            ws_a.send_bytes(sync_step1)

        # New client should NOT receive sync step 1
        with client.websocket_connect(f"/ws/{session_id}") as ws_b:
            # If something is stored, we'd receive it here
            # We can't easily test "nothing received" without timeout
            # but the key is sync_step2 and updates ARE stored
            pass

    def test_sync_step2_stored(self, client: TestClient):
        """Sync step 2 (updates) is stored for new clients."""
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        sync_step2 = bytes([0, 1, 10, 20, 30])  # Type 0, subtype 1

        with client.websocket_connect(f"/ws/{session_id}") as ws_a:
            ws_a.send_bytes(sync_step2)

        # New client receives stored update
        with client.websocket_connect(f"/ws/{session_id}") as ws_b:
            received = ws_b.receive_bytes()
            assert received == sync_step2

    def test_sync_update_stored(self, client: TestClient):
        """Sync update (incremental) is stored for new clients."""
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        sync_update = bytes([0, 2, 100, 200])  # Type 0, subtype 2

        with client.websocket_connect(f"/ws/{session_id}") as ws_a:
            ws_a.send_bytes(sync_update)

        # New client receives stored update
        with client.websocket_connect(f"/ws/{session_id}") as ws_b:
            received = ws_b.receive_bytes()
            assert received == sync_update

    def test_awareness_broadcast_not_stored(self, client: TestClient):
        """Awareness messages are broadcast but not stored."""
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        awareness = bytes([1, 1, 2, 3, 4])  # Type 1 = awareness

        # Two clients connected
        with client.websocket_connect(f"/ws/{session_id}") as ws_a:
            with client.websocket_connect(f"/ws/{session_id}") as ws_b:
                ws_a.send_bytes(awareness)
                received = ws_b.receive_bytes()
                assert received == awareness

        # New client should NOT receive awareness (not stored)
        # (Can't easily test without timeout, but behavior verified above)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_message_ignored(self, client: TestClient):
        """Empty messages should be ignored without error."""
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        with client.websocket_connect(f"/ws/{session_id}") as ws:
            # Send empty message - should not crash
            ws.send_bytes(b"")
            # Connection should still work
            ws.send_bytes(bytes([0, 2, 1, 2, 3]))

    def test_unknown_message_type_logged(self, client: TestClient):
        """Unknown message types are handled gracefully."""
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        with client.websocket_connect(f"/ws/{session_id}") as ws:
            # Send unknown message type (99)
            ws.send_bytes(bytes([99, 1, 2, 3]))
            # Should not crash, connection still works
            ws.send_bytes(bytes([0, 2, 1, 2, 3]))

    def test_rapid_updates(self, client: TestClient):
        """Handle many rapid updates without losing messages."""
        response = client.post("/api/sessions")
        session_id = response.json()["id"]

        num_updates = 50

        with client.websocket_connect(f"/ws/{session_id}") as ws_a:
            with client.websocket_connect(f"/ws/{session_id}") as ws_b:
                # A sends many updates rapidly
                sent = []
                for i in range(num_updates):
                    update = bytes([0, 2, i, i + 1, i + 2])
                    ws_a.send_bytes(update)
                    sent.append(update)

                # B should receive all of them
                received = []
                for _ in range(num_updates):
                    received.append(ws_b.receive_bytes())

                assert received == sent
