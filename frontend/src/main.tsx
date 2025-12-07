import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Note: StrictMode disabled because it causes double WebSocket connections
// which interferes with Yjs collaboration. Re-enable for non-WebSocket debugging.
createRoot(document.getElementById('root')!).render(<App />)
