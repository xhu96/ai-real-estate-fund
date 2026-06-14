import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Backend the dev server proxies API calls to. Override with VITE_PROXY_TARGET or
// BACKEND_URL if your backend runs elsewhere; otherwise it just works on :8000.
const backend = process.env.VITE_PROXY_TARGET || process.env.BACKEND_URL || 'http://localhost:8000';

// The backend's routers live at the root path space. Proxy exactly those prefixes
// to the backend; everything else (/, /src, /assets, /@vite) stays with Vite.
// The SPA uses HashRouter, so these are only ever XHR/fetch paths, never page loads.
const apiPrefixes = [
  'analyses', 'institutional', 'committee', 'comps', 'llm', 'validation',
  'portfolio', 'exports', 'scenarios', 'watchlist', 'ops', 'health',
  'research', 'storage', 'properties',
];

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      [`^/(${apiPrefixes.join('|')})(/|$|\\?)`]: { target: backend, changeOrigin: true },
    },
  },
});
