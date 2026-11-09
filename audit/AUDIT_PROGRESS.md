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
| 1 Security | IN PROGRESS |
| 2 Known bugs | next |
| 3 Functional | pending |
| 4 Performance | pending |
| 5 Wording/a11y | pending |
| 6 Share-readiness | pending |
| 7 Build/hand-off | pending |

## Findings so far (details in AUDIT_REPORT.md when finished)
- CRITICAL: `/api/presence/heartbeat` accepts unauthenticated GET/POST; every app install sends a tokenless heartbeat every 8 s and on exit → any user can overwrite the owner's presence card. [CODE REVIEW ONLY]
- HIGH: backend CORS `allow_origins=["*"]` with `allow_credentials=True`. [CODE REVIEW ONLY]
- MEDIUM: backend disables TLS verification for zegraph calls (`SSL_CTX.verify_mode = CERT_NONE`). [CODE REVIEW ONLY]
- LOW: `scripts/__pycache__/*.pyc` committed; one third-party SteamID (a player name) in history commit `f3f2fa0` inside `public/data/live_servers.json`.
- INFO: `desktop-app/` is the source of truth for the exe [TESTED: audit/evidence_source_truth.txt — 177/178 sampled constants found].
- INFO: secret scan of history / tree / dist / exe — no tokens, webhooks or keys; exe hits are Python-stdlib false positives [TESTED: audit/evidence_secret_scan.txt].
