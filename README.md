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

### Option 1: Quick Start (Recommended)

```bash
npm install    # Install dependencies (only first time)
npm run dev    # Start backend and frontend together
```

Open http://localhost:5173 in your browser.

### Option 2: Separate Run

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

### Option 3: Production Build

```bash
# Build frontend
cd frontend
npm run build

# Run backend (will serve statics from frontend/dist)
cd ../backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testing

```bash
npm test              # Run all tests (backend + frontend)
npm run test:e2e      # Run E2E tests with Playwright
```

Or separately:

```bash
cd backend && uv run pytest          # Backend tests (35 tests)
cd frontend && npm test              # Frontend unit tests (15 tests)
cd frontend && npx playwright test   # E2E tests (13 tests)
```

## Deployment (Railway)

### 1. Create Project on Railway

1. Go to [railway.app](https://railway.app) and create new project
2. Select "Deploy from GitHub repo"
3. Connect your repository

### 2. Add Backend Service

1. Click "New Service" → "GitHub Repo"
2. Set Root Directory: `backend`
3. Add environment variables (Settings → Variables):
   - Railway auto-detects the Dockerfile

### 3. Add Frontend Service

1. Click "New Service" → "GitHub Repo"
2. Set Root Directory: `frontend`
3. Add environment variables:
   ```
   VITE_API_URL=https://your-backend.railway.app/api
   VITE_WS_URL=wss://your-backend.railway.app/ws
   ```

### 4. Generate Domains

1. Backend: Settings → Networking → Generate Domain
2. Frontend: Settings → Networking → Generate Domain
3. Update frontend env vars with actual backend URL

## Docker / Podman

### Development

```bash
podman-compose up              # Start with hot reload
podman-compose up --build      # Rebuild images
podman-compose down            # Stop containers
```

Open http://localhost:5173

### Production

```bash
podman-compose -f docker-compose.prod.yml up -d --build
```

Open http://localhost (port 80)

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
