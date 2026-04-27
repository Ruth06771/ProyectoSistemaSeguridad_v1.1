import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  root: process.cwd(),
  server: {
    port: 3000,
    host: true,
    proxy: {
      // Proxy API requests to the Flask backend. Use 127.0.0.1 to avoid
      // potential hostname resolution issues on Windows and set changeOrigin
      // so the proxy rewrites Host header correctly.
      '/api': {
        // Use the machine network IP to avoid localhost/loopback resolution
        // differences on Windows that sometimes cause ECONNREFUSED from Node.
        target: 'http://172.168.7.196:5000',
        changeOrigin: true,
        secure: false,
        // preserve path
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
})
