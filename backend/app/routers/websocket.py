"""
WebSocket endpoint for Yjs synchronization.
"""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services import session_store, yjs_sync

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time code synchronization.
    
    Uses Yjs binary protocol:
    - Sync messages (type 0): Document state synchronization
    - Awareness messages (type 1): Cursor positions, user info
    
    Connection flow:
    1. Client connects
    2. Server sends current document state
    3. Bidirectional incremental updates
    """
    # Check if session exists
    session = session_store.get(session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    # Accept the connection
    await websocket.accept()
    logger.info(f"WebSocket connected: session={session_id}")
    
    # Track participant
    conn_id = str(id(websocket))
    session.add_participant(conn_id)
    
    try:
        # Join the Yjs room
        await yjs_sync.join_room(session_id, websocket)
        
        # Handle messages
        while True:
            # Receive binary message (Yjs protocol)
            message = await websocket.receive_bytes()
            
            # Process and broadcast
            await yjs_sync.handle_message(session_id, websocket, message)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session={session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up
        session.remove_participant(conn_id)
        await yjs_sync.leave_room(session_id, websocket)
