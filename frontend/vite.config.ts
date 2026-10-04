import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
        secure: false,
        configure: (proxy) => {
          proxy.on('error', (err, _req, res) => {
            console.warn('[vite proxy notice] Backend connection issue:', err.message);
            if (res && 'writeHead' in res && !(res as any).headersSent) {
              (res as any).writeHead(503, { 'Content-Type': 'application/json' });
              (res as any).end(
                JSON.stringify({
                  success: false,
                  error: {
                    code: 'BACKEND_NOT_RUNNING',
                    message:
                      'Cannot connect to Flask backend at http://127.0.0.1:5001. Please ensure the backend is running in Terminal 1 (python -m backend.app).',
                  },
                })
              );
            }
          });
        },
      },
    },
  },
})
