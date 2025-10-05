import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig({
  plugins: [react()],
    resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@pages': path.resolve(__dirname, 'src/pages'),
      '@state': path.resolve(__dirname, 'src/state'),
      '@utils': path.resolve(__dirname, 'src/utils')
    }
  },
  server: {
    open: false, // Automatically opens the browser
    port: 5173,
    host: '0.0.0.0', // Enable this for dev container access
    strictPort: true,
  },
  build: {
    outDir: 'dist', // Output directory for production build
  },
  esbuild: {
    loader: 'tsx',
    include: /src\/.*\.(js|jsx|ts|tsx)$/, // Apply to .js, .jsx, .ts, and .tsx files in the src directory
  },
});