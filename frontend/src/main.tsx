import { createRoot } from 'react-dom/client'
import { loader } from '@monaco-editor/react'
import * as monaco from 'monaco-editor'
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker'
import tsWorker from 'monaco-editor/esm/vs/language/typescript/ts.worker?worker'
import './index.css'
import App from './App.tsx'

// Configure Monaco workers for Vite
self.MonacoEnvironment = {
  getWorker(_, label) {
    if (label === 'json') {
      return new jsonWorker()
    }
    if (label === 'typescript' || label === 'javascript') {
      return new tsWorker()
    }
    return new editorWorker()
  },
}

// Configure Monaco to use bundled version instead of CDN
loader.config({ monaco })

// Note: StrictMode disabled because it causes double WebSocket connections
// which interferes with Yjs collaboration. Re-enable for non-WebSocket debugging.
createRoot(document.getElementById('root')!).render(<App />)
