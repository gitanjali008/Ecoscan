import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // In development the app calls /api on its own origin and Vite forwards it
    // to the FastAPI backend, so no CORS setup is needed.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
