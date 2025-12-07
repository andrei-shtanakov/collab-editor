# Collaborative Code Editor

Web application for real-time collaborative code editing. Multiple users can write and edit code simultaneously, seeing each other's changes instantly.

## Features

- **Collaborative Editing** — Multiple users work on the same code simultaneously
- **Real-time Synchronization** — Changes are visible instantly thanks to CRDT (Conflict-free Replicated Data Types)
- **Syntax Highlighting** — Monaco Editor (editor from VS Code) with support for 50+ languages
- **In-browser Code Execution** — Python and JavaScript run securely via WebAssembly
- **Simple Sharing** — Create a session and share the link

## Requirements

- **Python 3.11+**
- **Node.js 18+**
- **uv** — Python package manager ([installation](https://docs.astral.sh/uv/getting-started/installation/))

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd collab-editor
```

### 2. Backend (Python/FastAPI)

```bash
cd backend
uv sync
```

### 3. Frontend (React/TypeScript)

```bash
cd frontend
npm install
```

## Running

### Option 1: Separate Run (for development)

**Terminal 1 — Backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

### Option 2: Production Build

```bash
# Build frontend
cd frontend
npm run build

# Run backend (will serve statics from frontend/dist)
cd ../backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Usage

### Create Session

1. Open http://localhost:5173
2. Write code in the editor
3. Click **"Create & Share"**
4. Copy the link and send it to colleagues

### Join Session

1. Open the received link (e.g., `http://localhost:5173/?session=abc123`)
2. You will automatically connect to the session
3. Start editing — all changes are synced

### Execute Code

1. Select language in the dropdown menu (Python or JavaScript for execution)
2. Write code
3. Click **"Run"**
4. The result will appear in the Output panel on the right

### Supported Languages

| Language | Highlighting | In-browser Execution |
|----------|--------------|----------------------|
| Python | ✅ | ✅ (Pyodide) |
| JavaScript | ✅ | ✅ |
| TypeScript | ✅ | ✅ (as JS) |
| Java | ✅ | ❌ |
| C++ | ✅ | ❌ |
| Go | ✅ | ❌ |
| Rust | ✅ | ❌ |
| Ruby | ✅ | ❌ |
| PHP | ✅ | ❌ |
| SQL | ✅ | ❌ |

## API

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions` | Create new session |
| GET | `/api/sessions/{id}` | Get session info |
| PATCH | `/api/sessions/{id}` | Update session (language, title) |
| DELETE | `/api/sessions/{id}` | Delete session |
| GET | `/health` | Server health check |

### WebSocket

```
ws://localhost:8000/ws/{session_id}
```

Uses Yjs binary protocol for document synchronization.

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Browser A     │         │   Browser B     │
│  ┌───────────┐  │         │  ┌───────────┐  │
│  │  Monaco   │  │         │  │  Monaco   │  │
│  │  Editor   │  │         │  │  Editor   │  │
│  └─────┬─────┘  │         │  └─────┬─────┘  │
│        │        │         │        │        │
│  ┌─────┴─────┐  │         │  ┌─────┴─────┐  │
│  │  Yjs Doc  │  │         │  │  Yjs Doc  │  │
│  └─────┬─────┘  │         │  └─────┬─────┘  │
└────────┼────────┘         └────────┼────────┘
         │      WebSocket            │
         └───────────┬───────────────┘
                     │
              ┌──────┴──────┐
              │   FastAPI   │
              │   Server    │
              │  ┌───────┐  │
              │  │pycrdt │  │
              │  │  Doc  │  │
              │  └───────┘  │
              └─────────────┘
```

- **Yjs** — CRDT library for automatic conflict resolution
- **pycrdt** — Python implementation of Yjs (Rust bindings)
- **Monaco** — Code editor from VS Code

## Project Structure

```
collab-editor/
├── frontend/           # React application
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── hooks/      # React hooks (useYjs)
│   │   └── lib/        # API client, executor
│   └── package.json
│
├── backend/            # FastAPI server
│   ├── app/
│   │   ├── routers/    # API endpoints
│   │   ├── models/     # Pydantic schemas
│   │   └── services/   # Business logic
│   └── pyproject.toml
│
└── openapi/            # OpenAPI specification
```

## License

MIT
