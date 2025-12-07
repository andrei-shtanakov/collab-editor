# Collaborative Code Editor

Real-time collaborative code editor similar to CoderPad/HackerRank. Multiple users can edit code simultaneously with automatic conflict resolution.

## Project Structure

```
collab-editor/
├── frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── CodeEditor.tsx      # Monaco editor with Yjs binding
│   │   │   ├── LanguageSelector.tsx
│   │   │   ├── OutputPanel.tsx     # Code execution results
│   │   │   └── ShareButton.tsx
│   │   ├── hooks/
│   │   │   └── useYjs.ts           # Yjs WebSocket connection hook
│   │   ├── lib/
│   │   │   ├── api.ts              # Backend API client
│   │   │   └── executor.ts         # Browser-side code execution (Pyodide/JS)
│   │   ├── App.tsx
│   │   └── types.ts
│   └── package.json
│
├── backend/           # FastAPI Python backend
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── routers/
│   │   │   ├── sessions.py         # REST API for session management
│   │   │   └── websocket.py        # WebSocket endpoint for Yjs sync
│   │   ├── models/
│   │   │   ├── schemas.py          # Pydantic request/response models
│   │   │   └── session.py          # Internal session model
│   │   └── services/
│   │       ├── session_store.py    # In-memory session storage
│   │       └── yjs_sync.py         # Yjs CRDT sync using pycrdt
│   └── pyproject.toml
│
└── openapi/           # OpenAPI specification
```

## Tech Stack

### Frontend
- **React 18** + **TypeScript** - UI framework
- **Monaco Editor** - VS Code's editor component
- **Yjs** + **y-websocket** - CRDT for real-time collaboration
- **y-monaco** - Monaco/Yjs binding
- **Tailwind CSS** - Styling
- **Pyodide** - Python execution in browser via WebAssembly
- **Vite** - Build tool

### Backend
- **FastAPI** - Async Python web framework
- **pycrdt** - Python CRDT library (Yrs bindings), replaces deprecated y-py
- **WebSockets** - Real-time communication
- **Pydantic** - Data validation
- **nanoid** - Session ID generation
- **uvicorn** - ASGI server

## Key Concepts

### Real-time Sync (CRDT)
Uses Yjs CRDT protocol for conflict-free collaborative editing:
1. Each client maintains a local Yjs Doc
2. Changes are encoded as binary updates
3. Server (pycrdt) maintains authoritative document state
4. Updates are broadcast to all connected clients
5. CRDT algorithm ensures eventual consistency

### Session Flow
1. `POST /api/sessions` - Create new session, get session ID
2. Client opens `/?session={id}` URL
3. WebSocket connects to `/ws/{session_id}`
4. Yjs sync protocol exchanges document state
5. All edits sync automatically

### Code Execution
Browser-side execution for security (no server load):
- **Python**: Pyodide (CPython compiled to WebAssembly)
- **JavaScript**: Sandboxed eval with custom console

## Development

### Backend
```bash
cd backend
uv sync                           # Install dependencies
uv run uvicorn app.main:app --reload  # Start dev server on :8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                       # Start Vite dev server on :5173
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions` | Create new session |
| GET | `/api/sessions/{id}` | Get session info |
| PATCH | `/api/sessions/{id}` | Update session (language, title) |
| DELETE | `/api/sessions/{id}` | Delete session |
| WS | `/ws/{session_id}` | WebSocket for Yjs sync |
| GET | `/health` | Health check |

## Supported Languages
Python, JavaScript, TypeScript, Java, C++, Go, Rust, Ruby, PHP, SQL

Browser execution available for: Python, JavaScript, TypeScript
