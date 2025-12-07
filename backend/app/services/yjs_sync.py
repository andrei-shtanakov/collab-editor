"""
Yjs document synchronization service.
Handles WebSocket connections and Yjs protocol messages.

This implementation uses a relay approach - messages are broadcast
to all clients without server-side CRDT parsing. Document state is
preserved by storing raw updates for new clients.
"""

import asyncio
from typing import Dict, Set, Optional
from dataclasses import dataclass, field
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


# Yjs sync protocol message types
MSG_SYNC = 0
MSG_AWARENESS = 1

# Yjs sync subtypes (second byte in sync messages)
SYNC_STEP1 = 0  # State vector request - don't store
SYNC_STEP2 = 1  # State update response - store
SYNC_UPDATE = 2  # Incremental update - store


@dataclass
class YjsRoom:
    """
    A room for Yjs document synchronization.

    Stores raw Yjs updates to replay for new clients.
    """
    session_id: str
    connections: Set[WebSocket] = field(default_factory=set)
    # Store raw updates for replay to new clients
    updates: list[bytes] = field(default_factory=list)

    async def broadcast(self, message: bytes, exclude: Optional[WebSocket] = None):
        """Broadcast message to all connections except sender."""
        disconnected = []

        for ws in self.connections:
            if ws != exclude:
                try:
                    await ws.send_bytes(message)
                except Exception as e:
                    logger.warning(f"Failed to send to client: {e}")
                    disconnected.append(ws)

        # Clean up disconnected clients
        for ws in disconnected:
            self.connections.discard(ws)


class YjsSyncService:
    """
    Manages Yjs document synchronization across WebSocket connections.

    Uses relay approach:
    - Sync messages are broadcast to all other clients
    - Updates are stored for replay to new clients
    - No server-side CRDT parsing (compatible with any Yjs version)
    """

    def __init__(self):
        self._rooms: Dict[str, YjsRoom] = {}
        self._lock = asyncio.Lock()

    async def get_or_create_room(self, session_id: str) -> YjsRoom:
        """Get or create a room for a session."""
        async with self._lock:
            if session_id not in self._rooms:
                self._rooms[session_id] = YjsRoom(session_id=session_id)
            return self._rooms[session_id]

    async def join_room(
        self,
        session_id: str,
        websocket: WebSocket,
    ) -> YjsRoom:
        """Add a WebSocket connection to a room."""
        room = await self.get_or_create_room(session_id)
        room.connections.add(websocket)

        # Send stored updates to new client
        for update in room.updates:
            try:
                await websocket.send_bytes(update)
            except Exception as e:
                logger.error(f"Failed to send stored update: {e}")

        logger.info(f"Client joined room {session_id}. Total: {len(room.connections)}")
        return room

    async def leave_room(self, session_id: str, websocket: WebSocket):
        """Remove a WebSocket connection from a room."""
        if session_id in self._rooms:
            room = self._rooms[session_id]
            room.connections.discard(websocket)

            logger.info(f"Client left room {session_id}. Remaining: {len(room.connections)}")

    async def handle_message(
        self,
        session_id: str,
        websocket: WebSocket,
        message: bytes
    ):
        """
        Handle incoming Yjs protocol message.

        Simply relay sync messages to other clients and store updates.
        """
        if session_id not in self._rooms:
            return

        room = self._rooms[session_id]

        if len(message) < 1:
            return

        msg_type = message[0]

        if msg_type == MSG_SYNC:
            # Check sync subtype (second byte)
            if len(message) >= 2:
                sync_type = message[1]

                # Only store actual updates (step2 and update messages)
                # Don't store sync step1 (state vector requests)
                if sync_type in (SYNC_STEP2, SYNC_UPDATE):
                    room.updates.append(message)

                    # Limit stored updates to prevent memory issues
                    if len(room.updates) > 100:
                        room.updates = room.updates[-50:]

            # Broadcast to other clients
            await room.broadcast(message, exclude=websocket)

        elif msg_type == MSG_AWARENESS:
            # Awareness messages are just broadcast (not stored)
            await room.broadcast(message, exclude=websocket)

        else:
            logger.warning(f"Unknown message type: {msg_type}")

    def get_room_info(self, session_id: str) -> dict:
        """Get room statistics."""
        if session_id not in self._rooms:
            return {"exists": False, "connections": 0, "updates": 0}

        room = self._rooms[session_id]
        return {
            "exists": True,
            "connections": len(room.connections),
            "updates": len(room.updates),
        }

    async def delete_room(self, session_id: str):
        """Delete a room and disconnect all clients."""
        if session_id in self._rooms:
            room = self._rooms[session_id]

            # Close all connections
            for ws in list(room.connections):
                try:
                    await ws.close(code=4000, reason="Session deleted")
                except Exception:
                    pass

            del self._rooms[session_id]
            logger.info(f"Room {session_id} deleted")


# Singleton instance
yjs_sync = YjsSyncService()
