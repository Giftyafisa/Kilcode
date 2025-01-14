import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'),
        'payment-admin': path.resolve(__dirname, 'payment-admin.html')
      }
    }
  },
  server: {
    port: 5174,
    strictPort: true,
    proxy: {
      '/api/v1/admin': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/v1\/admin/, '/api/v1/admin')
      }
    }
  }
}); 