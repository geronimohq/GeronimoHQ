import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'

// Compute exact SHA-256 of the desktop app binary at build time to prevent hash drift
let calculatedExeHash = '66B78485C7C1F5622C12B702D07C83B7CEC781E344DC7AFE35B0272B494E7A01'
let calculatedExeSizeMb = 26
try {
  const exePath = path.resolve('public', 'CS2_Command_Center.exe')
  const distExePath = path.resolve('dist', 'CS2_Command_Center.exe')
  if (fs.existsSync(exePath)) {
    const buf = fs.readFileSync(exePath)
    calculatedExeHash = crypto.createHash('sha256').update(buf).digest('hex').toUpperCase()
    calculatedExeSizeMb = Math.round(buf.length / (1024 * 1024))

    // Safety check: ensure dist/ and public/ binaries have not diverged locally
    // In CI or fresh checkouts where dist/ does not exist, this check is safely skipped.
    if (fs.existsSync(distExePath)) {
      const distBuf = fs.readFileSync(distExePath)
      const distHash = crypto.createHash('sha256').update(distBuf).digest('hex').toUpperCase()
      if (calculatedExeHash !== distHash) {
        throw new Error(
          `\n[EXE_DIVERGENCE_ERROR] Binary divergence detected!\n` +
          `  public/CS2_Command_Center.exe: ${calculatedExeHash}\n` +
          `  dist/CS2_Command_Center.exe:   ${distHash}\n\n` +
          `To resolve this mismatch, sync the binary:\n` +
          `  Windows: copy /Y dist\\CS2_Command_Center.exe public\\CS2_Command_Center.exe\n` +
          `  Unix:    cp dist/CS2_Command_Center.exe public/CS2_Command_Center.exe\n`
        )
      } else {
        console.log(`[BUILD_GUARD] Binary SHA-256 verified match between public/ and dist/ (${calculatedExeHash.slice(0, 8)}...).`)
      }
    } else {
      console.log('[BUILD_GUARD] No dist/ binary found (fresh clone / CI build). Skipping binary divergence check.')
    }
  }
} catch (err: any) {
  if (err.message?.includes('EXE_DIVERGENCE_ERROR')) {
    throw err
  }
}

function safeCopyPublicPlugin() {
  // AUDIT P7: copy into the configured outDir (was hard-coded 'dist'), so a build
  // with --outDir scratch/dist can never overwrite dist/CS2_Command_Center.exe.
  let outDir = path.resolve('dist')
  return {
    name: 'safe-copy-public',
    configResolved(config: { root: string; build: { outDir: string } }) {
      outDir = path.resolve(config.root, config.build.outDir)
    },
    closeBundle() {
      const publicDir = path.resolve('public')
      const distDir = outDir
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

// AUDIT P6 (W-06): Content-Security-Policy as a <meta> tag (GitHub Pages cannot send headers).
// Build only: the dev server needs inline scripts that this policy blocks.
// Tested on a production build: 0 violations on load, 40 Chaos effects and a full scroll.
// worker-src blob: is needed by canvas-confetti's worker.
const CSP = [
  "default-src 'self'",
  "script-src 'self'",
  "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
  "font-src 'self' https://fonts.gstatic.com",
  "img-src 'self' data: https:",
  "connect-src 'self' https://geronimohq-telemetry.onrender.com https://zegraph.xyz",
  "media-src 'self' https: blob:",
  "worker-src 'self' blob:",
  "frame-src steam:",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
].join('; ')

function cspMetaPlugin() {
  return {
    name: 'csp-meta',
    apply: 'build' as const,
    transformIndexHtml(html: string) {
      const tag = `<meta http-equiv="Content-Security-Policy" content="${CSP}" />`
      return html.includes('<meta charset="UTF-8" />')
        ? html.replace('<meta charset="UTF-8" />', `<meta charset="UTF-8" />\n    ${tag}`)
        : html.replace('<head>', `<head>\n    ${tag}`)
    },
  }
}

export default defineConfig({
  define: {
    __APP_EXE_SHA256__: JSON.stringify(calculatedExeHash),
    __APP_EXE_SIZE_MB__: JSON.stringify(calculatedExeSizeMb),
  },
  plugins: [
    react(),
    tailwindcss(),
    safeCopyPublicPlugin(),
    cspMetaPlugin(),
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
