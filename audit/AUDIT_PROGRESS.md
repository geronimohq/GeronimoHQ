# Audit Progress — GeronimoHQ final audit

Started: 2026-11-10 00:38 (+08:00) · Branch: `final-audit` (from `main` @ `9cd8f07`)

## Pre-audit state (Rule A)
| Item | Value |
|---|---|
| Git commit / branch | `9cd8f0719cd620d1d673b998f1376a6fd62793d5` / `main` |
| `dist/CS2_Command_Center.exe` SHA-256 | `AEC0502A34299F19CEC6723E2D981A3D70E8278873F3345D8EF9B4EE1BF5C913` (36,908,530 bytes) |
| `public/CS2_Command_Center.exe` SHA-256 | `AEC0502A34299F19CEC6723E2D981A3D70E8278873F3345D8EF9B4EE1BF5C913` (same file) |
| Backup | `backups/final-audit-2026-11-10/` (347 MB, all folders except `node_modules` and `backups`; full git history as `repo-full-history.bundle`) |

**Rollback (one line):** `git checkout main && git branch -D final-audit` (code) — exe: `Copy-Item backups\final-audit-2026-11-10\dist\CS2_Command_Center.exe dist\ -Force`

Assumption logged: `node_modules/` was not copied (it is re-created exactly by `npm ci` from `package-lock.json`, which *is* backed up).

## Phase status
| Phase | Status |
|---|---|
| 0 Recon | DONE |
| 1 Security | IN PROGRESS (1a done, 1b done in backend/api.py; 1c desktop & 1d website next) |
| 2 Known bugs | next |
| 3 Functional | pending |
| 4 Performance | pending |
| 5 Wording/a11y | pending |
| 6 Share-readiness | pending |
| 7 Build/hand-off | pending |

## Work Completed in this Session:
1. **Rule A (Safety & Snapshot):**
   - Full backup created at `backups/final-audit-2026-11-10/` (347 MB).
   - Full git history bundled in `backups/final-audit-2026-11-10/repo-full-history.bundle`.
   - Branch created: `final-audit`.
2. **Phase 0 (Recon & Source Truth):**
   - Verified that `desktop-app/` is the true source of truth for the built exe (`audit/evidence_source_truth.txt` — 177/178 sampled constants match).
   - Removed accidentally committed `.pyc` from git cache.
3. **Phase 1a (Secret & Hygiene Scan):**
   - Scanned all commits, working tree, built `dist/`, and exe decompressed zlib strings for secrets.
   - Zero leaked credentials/tokens found (`audit/evidence_secret_scan.txt`).
4. **Phase 1b (Backend Security Hardening in `backend/api.py`):**
   - Replaced wildcard CORS with strict `ALLOWED_ORIGINS` (`https://geronimohq.com`, `https://www.geronimohq.com`, `localhost`).
   - Implemented real client IP extraction behind trusted proxy hops (`get_client_ip`).
   - Added in-memory sliding window rate-limiting on all routes.
   - Enforced request payload size limits (`MAX_REQUEST_BYTES = 2048`).
   - Disabled Swagger/OpenAPI docs by default unless `ENABLE_API_DOCS=1`.
   - Added security response headers: `nosniff`, `DENY` frames, `no-referrer`, `no-store`, `HSTS`.
   - Fixed presence heartbeat: requires `X-Geronimo-Token` with `hmac.compare_digest`, fails closed (503) if `GERONIMO_PRESENCE_TOKEN` is unset.
   - Fixed Steam profile failure handling: returns `state: "unknown"` instead of fake `offline`.
   - Tuned ThreadPoolExecutor from 24 to 16 workers with a concurrency lock to prevent thundering herd.
   - Added bot count tracking to A2S parser so human player count is isolated.

## Handover Point for Next Agent (e.g. Claude):
- Current Branch: `final-audit`
- Next Task: Phase 1c (Desktop app security checks: command injection, Map Cleaner path traversal, GSI 127.0.0.1, tokenless install safeguard in `app.py`), then Phase 1d (Website security), then Phase 2 (Known bugs).
