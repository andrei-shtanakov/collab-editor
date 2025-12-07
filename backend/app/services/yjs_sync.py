"""
Yjs document synchronization service using pycrdt.
Handles WebSocket connections and Yjs protocol messages.

Uses pycrdt (Python CRDT library based on Yrs) for proper
CRDT document handling and conflict-free synchronization.
"""

import asyncio
from typing import Dict, Set, Optional
from dataclasses import dataclass, field
import logging

from fastapi import WebSocket
from pycrdt import Doc, Text

logger = logging.getLogger(__name__)


# Yjs sync protocol message types
MSG_SYNC = 0
MSG_AWARENESS = 1

# Yjs sync protocol subtypes
MSG_SYNC_STEP1 = 0  # Client sends state vector
MSG_SYNC_STEP2 = 1  # Server sends missing updates
MSG_SYNC_UPDATE = 2  # Incremental update


@dataclass
class YjsRoom:
    """
    A room for Yjs document synchronization.

    Uses pycrdt Doc for proper CRDT handling, ensuring all
    concurrent edits are merged correctly without conflicts.
    """
    session_id: str
    connections: Set[WebSocket] = field(default_factory=set)
    doc: Doc = field(default_factory=Doc)
    _initialized: bool = False

    def __post_init__(self):
        """Initialize the shared text type in the document."""
        if not self._initialized:
            # Create shared text type that matches frontend's 'monaco' key
            self.doc["monaco"] = Text()
            self._initialized = True

    def get_text(self) -> Text:
        """Get the shared text from the document."""
        return self.doc["monaco"]

    def set_initial_code(self, code: str):
        """Set initial code if document is empty."""
        text = self.get_text()
        if len(text) == 0 and code:
            text += code

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

    Implements the Yjs sync protocol:
    - Sync Step 1: Client sends state vector, server responds with missing updates
    - Sync Step 2: Server sends updates to bring client up to date
    - Sync Update: Incremental updates broadcast to all clients

    Uses pycrdt for proper CRDT document handling, ensuring:
    - Conflict-free merging of concurrent edits
    - Consistent document state across all clients
    - Proper state vector and update encoding
    """

    def __init__(self):
        self._rooms: Dict[str, YjsRoom] = {}
        self._lock = asyncio.Lock()

    async def get_or_create_room(
        self,
        session_id: str,
        initial_code: str = ""
    ) -> YjsRoom:
        """Get or create a room for a session."""
        async with self._lock:
            if session_id not in self._rooms:
                room = YjsRoom(session_id=session_id)
                if initial_code:
                    room.set_initial_code(initial_code)
                self._rooms[session_id] = room
            return self._rooms[session_id]

    async def join_room(
        self,
        session_id: str,
        websocket: WebSocket,
        initial_code: str = ""
    ) -> YjsRoom:
        """Add a WebSocket connection to a room."""
        room = await self.get_or_create_room(session_id, initial_code)
        room.connections.add(websocket)

        # Send current document state to new connection
        # This is Sync Step 2 - sending the full document state
        try:
            state = room.doc.get_state()
            if state:
                # Create sync step 2 message with full state
                sync_message = self._create_sync_step2_message(
                    room.doc.get_update()
                )
                await websocket.send_bytes(sync_message)
        except Exception as e:
            logger.error(f"Failed to send initial state: {e}")

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

        Message format:
        - Byte 0: Message type (0=sync, 1=awareness)
        - For sync messages:
          - Byte 1: Sync type (0=step1, 1=step2, 2=update)
          - Rest: Payload (state vector or update)
        """
        if session_id not in self._rooms:
            return

        room = self._rooms[session_id]

        if len(message) < 1:
            return

        msg_type = message[0]

        if msg_type == MSG_SYNC:
            await self._handle_sync_message(room, websocket, message)
        elif msg_type == MSG_AWARENESS:
            # Awareness messages are just broadcast to other clients
            await room.broadcast(message, exclude=websocket)
        else:
            logger.warning(f"Unknown message type: {msg_type}")

    async def _handle_sync_message(
        self,
        room: YjsRoom,
        websocket: WebSocket,
        message: bytes
    ):
        """Handle Yjs sync protocol messages."""
        if len(message) < 2:
            return

        sync_type = message[1]
        payload = message[2:] if len(message) > 2 else b""

        if sync_type == MSG_SYNC_STEP1:
            # Client sent state vector, respond with missing updates
            try:
                # Get update diff based on client's state vector
                update = room.doc.get_update(payload) if payload else room.doc.get_update()

                if update:
                    response = self._create_sync_step2_message(update)
                    await websocket.send_bytes(response)
            except Exception as e:
                logger.error(f"Error handling sync step 1: {e}")
                # Fallback: send full state
                update = room.doc.get_update()
                if update:
                    response = self._create_sync_step2_message(update)
                    await websocket.send_bytes(response)

        elif sync_type == MSG_SYNC_STEP2:
            # Server received updates from client (during initial sync)
            try:
                if payload:
                    room.doc.apply_update(payload)
            except Exception as e:
                logger.error(f"Error applying sync step 2 update: {e}")

        elif sync_type == MSG_SYNC_UPDATE:
            # Incremental update from client
            try:
                if payload:
                    # Apply update to server's document
                    room.doc.apply_update(payload)

                    # Broadcast to other clients
                    await room.broadcast(message, exclude=websocket)
            except Exception as e:
                logger.error(f"Error handling sync update: {e}")

        else:
            logger.warning(f"Unknown sync type: {sync_type}")

    def _create_sync_step2_message(self, update: bytes) -> bytes:
        """Create a sync step 2 message containing an update."""
        return bytes([MSG_SYNC, MSG_SYNC_STEP2]) + update

    def get_room_info(self, session_id: str) -> dict:
        """Get room statistics."""
        if session_id not in self._rooms:
            return {"exists": False, "connections": 0, "doc_size": 0}

        room = self._rooms[session_id]
        doc_state = room.doc.get_state()

        return {
            "exists": True,
            "connections": len(room.connections),
            "doc_size": len(doc_state) if doc_state else 0,
            "text_length": len(room.get_text()),
        }

    def get_document_content(self, session_id: str) -> Optional[str]:
        """Get the current text content of a document."""
        if session_id not in self._rooms:
            return None

        room = self._rooms[session_id]
        return str(room.get_text())

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
