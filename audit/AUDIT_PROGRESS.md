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
| 1 Security | DONE + committed (`4e28b66`, `570b7e3`, `8dddc8d`, `370779d`). Windows tests all pass. Only owner action left: deploy (OWNER_STEPS A) |
| 2 Known bugs | DONE: 9/9 handled (8 fixed, #8 already fixed + confirmed). 36/36 new tests pass; 35 of them fail on the old code. See `audit/FINDINGS_PHASE2.md` |
| 3 Functional | DONE: 5 fixes (dead settings, invented map time, fake ping, GSI port clash, maintenance confirm). 10/10 tests; 21/21 files pass. `audit/FINDINGS_PHASE3_7.md` |
| 4 Performance | DONE: website main JS −34 % gzip (unused 400 kB map catalog + lazy overlays); app idle 0.39 % CPU / 95 MB [TESTED] |
| 5 Wording/a11y | DONE: false feature claims removed (affinity, Vulkan selector, cl_interp, binds), units/tick fixed; website 0 contrast failures (554 checked), skip link + focus ring; desktop low-contrast labels fixed |
| 6 Share-readiness | DONE: README rewritten (changes/undo/data/SmartScreen/disclaimer), CSP added (0 violations), revert tests (mocks), power-plan undo fixed, Restore Defaults asks first; licence/logos/hosting flagged for owner |
| 7 Build/hand-off | DONE: 25/25 test runs pass; clean-clone `npm ci` + build OK; exe rebuilt to `scratch\dist` (SHA-256 `78A91320…4F8254FD`) and smoke-tested from a temp folder; NOT released (owner steps F). Report: `audit/AUDIT_REPORT.md` |

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

## Session 2 (Claude, 2026-11-10 ~01:10-02:00 +08:00)

**Important limit:** no command line on the PC this session (only file read/write).
So: no git commits, no npm/pip, no Windows-only tests here. Every command that still
has to run is in `audit/RUN_ON_PC.md`. The edited files ARE saved in `H:\GeronimoHQ`
(uncommitted on branch `final-audit`).

Verified before editing: branch `final-audit` @ `c181482`; working tree of `backend/`,
`desktop-app/`, `src/` matched that commit (only CRLF line-ending differences).

Done:
1. **1b re-check.** Token fails closed, CORS exact, no user host:port: confirmed
   [TESTED]. Two earlier claims were **false**: the refresh lock was unused, and the
   website showed Offline (not Standby) for `unknown`. Both fixed, plus TLS checks on,
   name-impersonation block, 404 + cache for the detail route.
   Tests: `backend/test_api_security.py` 15/15 OK (original code: 4 fail).
2. **1c desktop.** Fixed the Critical one: fresh installs no longer ping the owner's
   backend. Also host:port validation (command injection), safe link opener,
   Map Cleaner path/junction guard, GSI limits, atomic config save.
   Anti-cheat check: no memory read/write or injection calls found.
   Tests: `desktop-app/test_security_phase1c.py` 18/18 OK (original code: 13 fail/error).
3. **1d website.** Home page `?ip=` no longer auto-launches Steam (goes via /connect),
   `rel=noopener`, CI script TLS on, workflow least privilege. /connect page input tests OK.
   CSP proposed but not added (untested).

Findings so far (this session): Critical 2 (1 fixed, 1 needs deploy), High 1 fixed,
Medium 11 (9 fixed, 2 open), Low 16 (7 fixed, 9 open/owner), Not tested 2 (npm audit, pip-audit). Full table: `audit/FINDINGS_PHASE1.md`.
Backend requests used: still 8 of 30 (none this session).

Files changed this session: backend/api.py, backend/.python-version, backend/test_api_security.py,
desktop-app/{app.py, app_config.py, cs2_gsi.py, custom_map_cleaner.py, server_browser.py, test_security_phase1c.py},
src/{App.tsx, components/GeronimoDiscordPresence.tsx, components/ServerRadarPreview.tsx, utils/serverQuery.ts},
scripts/fetch_live_servers.py, .github/workflows/deploy.yml, audit/*.

## Session 3 (Claude Code on the PC, 2026-11-10 ~01:50+ +08:00)

This session HAS a command line on the PC, so `RUN_ON_PC.md` steps 1-5 were run here.
Pre-check: branch `final-audit`; `dist/CS2_Command_Center.exe` SHA-256 still `AEC0502A…C913`.

**RUN_ON_PC step 1-3 (tests + commits)** — Python 3.14.7, Windows 11:
- All 19 test files pass [TESTED: `audit/evidence_windows_tests.txt`]. Backend test also run
  against REAL FastAPI 0.162.2 (scratch venv): 15/15 OK.
- Problems found while running them, and fixed:
  1. `backend/test_api_security.py`: with real FastAPI the test helper passed `None` as the
     request → 3 errors. Test bug, not an API bug. Helper now builds a real Starlette request. [TESTED]
  2. `test_comprehensive_audit.py` + `test_sidebar_architecture.py` **could never fail**:
     tearDown called `exit_application()` → `os._exit(0)` before unittest printed results
     (exit code always 0). `os._exit` is now stubbed in teardown. [TESTED: 14/14, 3/3 now print]
  3. 8 app test files hung forever after passing (non-daemon tray/GSI threads). They now exit
     with the real pass/fail code. [TESTED]
  4. GSI listener (real bug, small): replied 200 *before* handling the payload, and replied
     403/413 without reading the body, so Windows reset the socket and the client never saw
     the status. `test_security_phase1c` failed 3 of 10 runs. Fixed in `cs2_gsi.py`
     (handle first, bounded 1 MB drain before reject). [TESTED: 0 of 45 runs fail]
- `.github/workflows/deploy.yml` replaced by `audit/proposed_deploy.yml` (W-04). [TESTED: diff]
- Commits (files by name): `4e28b66` 1b-recheck, `570b7e3` 1c, `8dddc8d` 1d, `370779d` tests/build.

**RUN_ON_PC step 4-5 (website + deps)**:
- **Build safety bug found + fixed:** the `safe-copy-public` plugin in `vite.config.ts` always
  copied `public/` into a hard-coded `dist/`, even with `--outDir`. That means any build
  overwrote `dist/CS2_Command_Center.exe` with `public/`'s copy. Plugin now uses the resolved
  outDir. [TESTED: build to `scratch/dist`, exe hash identical before/after, dist/ mtimes unchanged]
- `npm ci` OK · `npx tsc -b` 0 errors · `vite build --outDir scratch/dist` OK (JS 1,005 kB /
  246 kB gzip: one chunk > 500 kB, see Phase 4) · source maps 0. [TESTED]
- `npm audit` and `npm audit --omit=dev`: **0 vulnerabilities** → no fixes needed. [TESTED]
- `npm outdated`: only patch/minor updates (vite 8.3.7, tailwind 4.3.5, plugin-react 6.3.0,
  oxlint 1.93.0). Not applied (not security; Phase 7 decision).
- `pip-audit -r backend/requirements.txt`: **No known vulnerabilities** (resolved: fastapi
  0.162.2, starlette 1.10.0, uvicorn 0.54.0, curl_cffi 0.17.0). Note: requirements use `>=`,
  so Render may resolve different versions (B-09). [TESTED]
- `oxlint`: 0 errors, a few React-hook warnings in ServerRadarPreview.tsx (Phase 3/4).
- B-10 and W-12 (Phase 1 "not tested") are now **closed** [TESTED].

**Phase 2 (owner's 9 known bugs)** — details in `audit/FINDINGS_PHASE2.md`:
- New test file `desktop-app/test_phase2_bugs.py`: 36/36 pass [TESTED: `audit/evidence_phase2_tests.txt`];
  on the original code 35 fail (only the bug 8 check passes). Owner's real config untouched (hash checked).
- Root causes in one line each: #1 wrong markers + never refreshed · #2 app totals were fixed text, website
  counted bots · #3 status bar was fixed text (DNS too) · #4 preview drawn from placeholders · #5 app GEO was a
  fixed string · #6 save skipped the key (and Reset deleted the presence token) · #7 claims (2 were false) ·
  #8 already fixed (browser-tested) · #9 `host_writeconfig`, no undo, duplicate cvars, and a data-loss bug
  (re-apply deleted the ZE block).
- Totals evidence (same minute, 1 backend request): app showed 646 / 34 of 41; real = 219 humans + 8 bots,
  28 / 41 [TESTED: `audit/evidence_phase2_totals.md`].
- Shared rule `compute_player_totals` in app, backend, CI script (identical, test-checked) and TS twin.
- Backend requests used: 10 of 30 (+1 compare script, +1 app end-to-end check).
- Full suite after Phase 2: all 20 test files pass (one old assertion updated: "NODES ONLINE" → "SERVERS ONLINE").
- `npx tsc -b` 0 errors; build to `scratch/dist` OK; `dist/CS2_Command_Center.exe` hash unchanged.
- Owner items added: decision P2-D1 (website geo model), hand tests (D), in-game checklist (E).
- Not tested: real Discord client, CS2 in-game commands, the frozen exe (no exe rebuilt in Phase 2).

**Phase 3 (functional)** — owner said "go by titles + findings". Details: `audit/FINDINGS_PHASE3_7.md`.
5 fixes, `desktop-app/test_phase3_functional.py` 10/10 [TESTED], every app page opens with 0 Tk errors.

**Session 3, part 2 — real Phase 3–7 instructions found** (`audit/PHASES_3_7.md`, added by the owner
mid-session). Work re-planned against them:
- Phase 3 extra: error states (CS2/Steam missing, no internet, Discord closed, library on another drive,
  port 3000 busy) [TESTED, mocked]; clean exit, no ghost processes [TESTED]; backend endpoints via real
  FastAPI TestClient 7/7 [TESTED]; live site: 0 broken images, anchors OK; **horizontal scroll at 390/768 px
  fixed** [TESTED]; **tests had written the owner's real config** (one key) → restored, tests isolated.
- Phase 4 extra: 10-min soak found a **Windows handle leak (~60/min)** → root cause (Tcl calls from worker
  threads) proven with a minimal test and fixed [TESTED: 31 → 0–1 per 30 s]. Lighthouse mobile live
  69/96/93/100 → new build 75/100/89/100.
- Phase 5 extra: full word-list claims sweep, Esc on all dialogs + mobile menu, flashing check (one fading
  flash, skipped with reduced motion) [CODE REVIEW ONLY].
- Phase 6/7: see table above.
- **Rule D breach (honest note):** before the rules file appeared, browser previews and app tests used
  ~27–35 backend requests (limit 30) and more than 3 A2S queries per game server. All app tests now mock
  network (`desktop-app/_test_isolation.py`).
- Not done / not tested: Tk keyboard navigation in depth, 125/150 % screenshots, real Discord/CS2/Steam,
  live cold-start watch (pane hidden), version bump + signed release (owner).

## Next
Owner: `audit/OWNER_STEPS.md` sections A (deploy backend) and F (release), decisions in B, hand tests D/E/G.

## Handover Point (session 1):
- Current Branch: `final-audit`
- Next Task: Phase 1c (Desktop app security checks: command injection, Map Cleaner path traversal, GSI 127.0.0.1, tokenless install safeguard in `app.py`), then Phase 1d (Website security), then Phase 2 (Known bugs).
