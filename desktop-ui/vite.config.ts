import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The built UI is written next to the Python code so web_main.py (and PyInstaller) can load it from ./web
export default defineConfig({
  plugins: [react()],
  base: './',
  build: { outDir: '../desktop-app/web', emptyOutDir: true, chunkSizeWarningLimit: 900 },
  server: { port: 5199, strictPort: true },
});
