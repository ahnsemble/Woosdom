import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron/simple'

// Prevent Electron from running in Node.js mode
// (inherited from parent process when running inside Claude Code / VS Code)
delete process.env.ELECTRON_RUN_AS_NODE

export default defineConfig({
  plugins: [
    react(),
    electron({
      main: {
        entry: 'electron/main.ts',
      },
      preload: {
        input: 'electron/preload.ts',
      },
    }),
  ],
  build: {
    outDir: 'dist',
  },
})
