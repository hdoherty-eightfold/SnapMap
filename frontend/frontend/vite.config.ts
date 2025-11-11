import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    // Generate unique hashes for all assets to enable cache busting
    rollupOptions: {
      output: {
        // Add hash to all chunk filenames
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // Generate manifest for asset tracking
    manifest: true,
    // Ensure source maps are generated for debugging
    sourcemap: true
  },
  // CSS configuration for cache busting
  css: {
    devSourcemap: true
  }
})
