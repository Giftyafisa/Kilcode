import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  base: '/code-analyzer',
  server: {
    port: 5176,  // Code analyzers portal port
    proxy: {
      '/api/v1/code-analyzer': {
        target: 'http://localhost:8003',  // Code analyzer backend
        changeOrigin: true,
        secure: false
      }
    },
    // Add middleware to handle SPA routing
    middlewares: [
      (req, res, next) => {
        // If the request is for a static file, let it through
        if (req.url.includes('.')) {
          return next();
        }

        // If the request starts with /code-analyzer, serve the HTML file
        if (req.url.startsWith('/code-analyzer')) {
          req.url = '/codeanalyzer.html';
        }
        next();
      }
    ]
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    }
  },
  css: {
    postcss: './postcss.config.cjs'
  },
  build: {
    rollupOptions: {
      input: {
        'code-analyzer': path.resolve(__dirname, 'codeanalyzer.html')
      },
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui': ['framer-motion', 'react-hot-toast', 'react-icons']
        }
      }
    },
    outDir: 'dist/code-analyzer',
    assetsDir: 'assets'
  }
}); 