import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Backend URL: use 'backend' service name in Docker, 'localhost' otherwise
const backendUrl = process.env.VITE_BACKEND_URL || 'http://localhost:8000'
const backendWsUrl = backendUrl.replace('http', 'ws')

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Monaco workers need to be built as separate chunks
  optimizeDeps: {
    include: ['monaco-editor'],
  },
  server: {
    port: 5173,
    host: true, // Listen on all interfaces (needed for Docker)
    proxy: {
      '/api': {
        target: backendUrl,
        changeOrigin: true,
      },
      '/ws': {
        target: backendWsUrl,
        ws: true,
      },
    },
  },
})
