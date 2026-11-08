import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'

// Compute exact SHA-256 of the desktop app binary at build time to prevent hash drift
let calculatedExeHash = '739E821B12704ADC21464173D886E490B78390E3779856C2C6736AF932B92BB6'
try {
  const exePath = path.resolve('public', 'CS2_Command_Center.exe')
  const distExePath = path.resolve('dist', 'CS2_Command_Center.exe')
  if (fs.existsSync(exePath)) {
    const buf = fs.readFileSync(exePath)
    calculatedExeHash = crypto.createHash('sha256').update(buf).digest('hex').toUpperCase()

    // Safety check: ensure dist/ and public/ binaries have not diverged locally
    if (fs.existsSync(distExePath)) {
      const distBuf = fs.readFileSync(distExePath)
      const distHash = crypto.createHash('sha256').update(distBuf).digest('hex').toUpperCase()
      if (calculatedExeHash !== distHash) {
        throw new Error(
          `[EXE_DIVERGENCE_ERROR] Binary divergence detected! ` +
          `public/ (${calculatedExeHash.slice(0, 8)}...) != dist/ (${distHash.slice(0, 8)}...). ` +
          `Sync freshly built desktop executable to public/ before web build.`
        )
      }
    }
  }
} catch (err: any) {
  if (err.message?.includes('EXE_DIVERGENCE_ERROR')) {
    throw err
  }
}

function safeCopyPublicPlugin() {
  return {
    name: 'safe-copy-public',
    closeBundle() {
      const publicDir = path.resolve('public')
      const distDir = path.resolve('dist')
      if (!fs.existsSync(publicDir)) return

      function copyRecursive(src: string, dest: string) {
        if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true })
        for (const item of fs.readdirSync(src)) {
          const srcPath = path.join(src, item)
          const destPath = path.join(dest, item)
          const stat = fs.statSync(srcPath)
          if (stat.isDirectory()) {
            copyRecursive(srcPath, destPath)
          } else {
            try {
              fs.copyFileSync(srcPath, destPath)
            } catch {
              // If file is locked by a running test instance (EBUSY), skip without failing the build
            }
          }
        }
      }
      copyRecursive(publicDir, distDir)
    }
  }
}

export default defineConfig({
  define: {
    __APP_EXE_SHA256__: JSON.stringify(calculatedExeHash),
  },
  plugins: [
    react(),
    tailwindcss(),
    safeCopyPublicPlugin(),
  ],
  server: {
    host: true,
    port: 5173,
  },
  build: {
    emptyOutDir: false,
    copyPublicDir: false,
  },
})
