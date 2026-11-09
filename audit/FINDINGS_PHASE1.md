# Phase 1 findings (security) — session 2 (1b re-check, 1c, 1d)

Date: 2026-11-10 (+08:00). Branch: `final-audit`. Reviewer: Claude.

How to read the labels:
- **[TESTED: …]** = a test ran and its output is in `audit/evidence_phase1_tests.txt` (or quoted here).
- **[CODE REVIEW ONLY]** = I read the code; nothing was run.
- **[NOT TESTED]** = not checked yet.

Tests ran in a Linux sandbox with small stand-ins for FastAPI and Windows-only modules.
They still need one run on the Windows PC (see `audit/RUN_ON_PC.md`).

## Earlier report vs code (Rule F)

| Earlier claim (AUDIT_PROGRESS, Phase 1b) | What the code really does |
|---|---|
| "ThreadPoolExecutor … with a concurrency lock" | `REFRESH_LOCK` was created but **never used**. Now used (B-01). |
| "Frontend shows Standby for unknown" | The website showed **Offline** for `unknown`. The frontend was not changed in the 1b commit. Now fixed (B-06). |
| Token check fails closed, CORS exact origins, no user host:port | **Confirmed in code** and by tests (see B-T1..B-T3). |

## Table

| ID | Area | Finding (plain words) | Severity | Status | Evidence | File:line (after fix) |
|---|---|---|---|---|---|---|
| L-01 | Backend (LIVE) | The backend running on Render today is the OLD code: it accepted a heartbeat with no token (HTTP 200), reflects any website origin with credentials, and shows /docs. Anyone's app (or anyone) can change the owner's presence card until the new code is deployed. | Critical | Owner action (deploy) | [TESTED: earlier session, `audit/evidence_backend_probe_before.txt` #3-#7] | backend/api.py |
| D-05 | Desktop | Every copy of the app (no config at all) pinged the owner's backend every 8 s with its CS2/Steam status, and on exit sent an "offline" ping with no token. On the live backend this can flip the owner's card. Now only an install with `presence_secret` set sends anything, and it always sends the token. | Critical | Fixed | [TESTED: `test_fresh_install_sends_nothing`, `test_owner_install_sends_token`, `test_exit_ping_is_owner_only`] | desktop-app/app.py:942, 5062 |
| D-01 | Desktop | "Add Server" accepted any text as host. That text went into `cmd.exe start steam://connect/…` and was typed into the CS2 console as `connect …`. A host like `1.2.3.4;quit` or `x&calc` could run extra commands. One shared check now allows only IPv4/hostname + port 1-65535 (dialog, saved file, and every connect function). | High | Fixed | [TESTED: `ServerAddressTests` 4/4] | desktop-app/server_browser.py:158, app.py:6517 |
| D-03 | Desktop | Map Cleaner deleted whatever path it was given. Now it only deletes `…/steamapps/workshop/content/730/<number>` folders or `…/game/csgo/maps/*.vpk` files, and never through a symlink/junction. Note: if a Steam folder itself sits behind a junction, deletes are now refused (safe side). | Medium | Fixed | [TESTED: `MapCleanerTests` 3/3, dummy folders only] | desktop-app/custom_map_cleaner.py:460 |
| D-04 | Desktop | GSI listener (127.0.0.1:3000) had no size limit and any web page in a browser could post fake game state to it. Now: max 64 KB, JSON object only, requests with a browser `Origin` header are refused. | Medium | Fixed | [TESTED: `GsiTests` 4/4] | desktop-app/cs2_gsi.py:60 |
| D-02 | Desktop | The link opener accepted any scheme and characters that `cmd.exe` treats as commands. Now only `http(s)` links without `& | < > ^ " \``; the `cmd start` fallback is skipped when a link has `%`. | Medium | Fixed | [TESTED: `UrlOpenerTests`] | desktop-app/app.py:58 |
| B-05 | Backend | Anyone can name themselves "Geronimo" on a monitored server and the card said the owner was "in server". Now the name match only counts when the owner's token heartbeat or the owner's public Steam profile says CS2 is running. | Medium | Fixed | [TESTED: `test_name_impersonation_ignored`, `test_name_match_trusted_when_owner_signal_says_cs2`] | backend/api.py:534 |
| B-06 | Website | Presence card showed **Offline** when the backend said `unknown`. Now it shows **Standby**. | Medium | Fixed | [CODE REVIEW ONLY] + syntax [TESTED] | src/components/GeronimoDiscordPresence.tsx:191 |
| B-07 | Website | The card also switched to "in server" for ANY GFL player whose name merely contains "geronimo". Removed; the backend decides. | Medium | Fixed | [CODE REVIEW ONLY] | src/components/GeronimoDiscordPresence.tsx:186 |
| B-01 | Backend | Refresh lock was never used, so many visitors at once could each start a full 42-server UDP sweep. Now one sweep at a time; others reuse the cache. | Medium | Fixed | [CODE REVIEW ONLY] | backend/api.py:779 |
| B-02 | Backend | TLS certificate checks were turned OFF for the zegraph fallback request. Turned back on. | Medium | Fixed | [TESTED: `test_tls_verification_on`] | backend/api.py:654 |
| W-01 | Website | Home page `/?ip=…` or `/?connect=…` launched `steam://connect` to ANY host with no click, skipping the checks on `/connect/`. Because 404.html forwards the query to `/`, any link on the domain could do this. Now it hands off to `/connect/`, which checks the address and only auto-connects to catalog servers. | Medium | Fixed | [CODE REVIEW ONLY] | src/App.tsx:25 |
| W-06 | Website | No Content-Security-Policy. GitHub Pages cannot send headers; a `<meta>` CSP is possible but untested here, so it was NOT added (it could break the site). Proposed value is in OWNER_STEPS.md. | Medium | Not fixed | [NOT TESTED] | index.html |
| D-07 | Desktop | "Start with Windows" creates a Scheduled Task with `/rl highest`, so the app starts as Administrator at every logon. Admin should only be used when a feature needs it. Owner decision. | Medium | Not fixed | [CODE REVIEW ONLY] | desktop-app/app_config.py:177 |
| B-03 | Backend | Map name from a game server reply went into a zegraph URL unchecked. Now allow-listed and URL-encoded. | Low | Fixed | [TESTED: `test_map_name_cannot_inject_url`] | backend/api.py:705 |
| B-04 | Backend | `/api/servers/<unknown>` returned 200, and every call ran a fresh UDP query. Now 404 + 5 s cache. | Low | Fixed | [TESTED: `test_detail_unknown_id_404_and_catalog_only`] | backend/api.py:798 |
| B-08 | Website | Card showed made-up values (`ze_eizures_b1_1`, `62/64`) when data was missing. Now shows `-`. | Low | Fixed | [CODE REVIEW ONLY] | GeronimoDiscordPresence.tsx:210-215 |
| W-03 | CI script | `scripts/fetch_live_servers.py` also turned TLS checks off and put the map name in a URL unchecked. Fixed like B-02/B-03. | Low | Fixed | py_compile [TESTED] | scripts/fetch_live_servers.py |
| W-04 | GitHub Actions | Build job had `pages: write` + `id-token: write`. Moved to the deploy job only. | Low | Fixed | YAML parse [TESTED] | .github/workflows/deploy.yml |
| W-02 | Website | 6 `target=_blank` links had `rel="noreferrer"` only. Now `noopener noreferrer`. | Low | Fixed | [TESTED: tag scan, 0 left] | ServerRadarPreview.tsx, GeronimoDiscordPresence.tsx |
| D-06 | Desktop | Settings file was written in place (a crash = half-written file = all settings reset). Now temp file + replace. (Phase 2 bug #6 still needs its own check.) | Low | Fixed | [TESTED: `test_atomic_round_trip`] | desktop-app/app_config.py:59 |
| B-09 | Backend | Python version not pinned; packages use `>=`. Added `backend/.python-version` (3.11.9). Render may also need `PYTHON_VERSION`. | Low | Owner action | [CODE REVIEW ONLY] | backend/.python-version |
| B-11 | Backend | `/api/servers` returns full player-name lists (public A2S data, but it re-publishes names). Owner decision. | Low | Not fixed | [CODE REVIEW ONLY] | backend/api.py (fetch_single_server) |
| W-05 | GitHub Actions | Actions pinned to tags (`@v4`), not commit SHAs. | Low | Not fixed | [CODE REVIEW ONLY] | deploy.yml |
| W-11 | Website | `vite` dev server uses `host: true` (visible on your home network while `npm run dev` runs). | Low | Not fixed | [CODE REVIEW ONLY] | vite.config.ts:84 |
| W-13 | Website | `emptyOutDir: false` means old files in `dist/` can be published. | Low | Not fixed | [CODE REVIEW ONLY] | vite.config.ts:88 |
| D-10 | Desktop | Update helper `.bat` is written as UTF-8; a non-English install path may break the update swap. | Low | Not fixed | [CODE REVIEW ONLY] | desktop-app/updater.py:300 |
| D-11 | Desktop | `presence_secret` is stored as plain text in `%APPDATA%\CS2CommandCenter\command_center_config.json` (owner PC only). | Low | Not fixed | [CODE REVIEW ONLY] | desktop-app/app_config.py |
| D-12 | Desktop | Dashboard "Run Maintenance" deletes temp/Steam/Discord cache files with no confirm (Recycle Bin is off by default). | Low | Not fixed | [CODE REVIEW ONLY] | desktop-app/app.py:5618 |
| D-13 | Desktop | If port 3000 is busy, the GSI listener fails silently. | Low | Not tested (Phase 3) | [NOT TESTED] | desktop-app/cs2_gsi.py:122 |
| B-10 | Backend | `pip-audit` not run (no internet in sandbox). | — | Not tested | [NOT TESTED] → RUN_ON_PC | backend/requirements.txt |
| W-12 | Website | `npm audit`, `tsc -b`, `npm run build` not run (no node_modules / internet in sandbox). | — | Not tested | [NOT TESTED] → RUN_ON_PC | package.json |

## Checks with no problem found

| ID | Check | Result | Evidence |
|---|---|---|---|
| B-T1 | Presence token | No secret set → 503 (fails closed). Missing/wrong token → 401 and presence unchanged. Uses `hmac.compare_digest`. | [TESTED: TokenTests 4/4] |
| B-T2 | CORS | Exact origins only (geronimohq.com, www, localhost 5173/4173), no `*`, no credentials. | [TESTED: `test_cors_exact_origins_only`] |
| B-T3 | No user host:port | No route takes host/port/url/ip; detail route uses the fixed catalog. | [TESTED: AST test + 404 test] |
| B-T4 | Real client IP | Right-most X-Forwarded-For entry (added by Render) is used; spoofed left entry ignored. | [TESTED: `test_spoofed_xff_ignored`] |
| B-T5 | Steam check fails | Returns `unknown`, not `offline`. | [TESTED: `test_steam_unknown_gives_unknown_not_offline`] |
| D-T1 | Anti-cheat claim | Only Windows calls on cs2.exe: process list (`CreateToolhelp32Snapshot`), `OpenProcess(PROCESS_SET_INFORMATION \| PROCESS_QUERY_LIMITED_INFORMATION)` + `SetPriorityClass(HIGH)`, window focus calls, and `keybd_event` to paste `connect …` into the CS2 console. No ReadProcessMemory / WriteProcessMemory / CreateRemoteThread / VirtualAllocEx / hooks found. `PROCESS_ALL_ACCESS` is defined but never used. | [TESTED: `test_no_process_memory_or_injection_apis`] + [CODE REVIEW ONLY] for the call list |
| D-T2 | Unsafe deserialization | No eval/exec/pickle/marshal/yaml.load in app code. | [TESTED: `test_no_unsafe_deserialization`] |
| D-T3 | Updater | HTTPS only, host must be geronimohq.com, max 2 redirects, Ed25519-signed manifest, SHA-256 + size check, installs only after the user clicks. Signing key is kept outside the repo (`Documents\GeronimoHQ-keys`). | [TESTED: live `public/update/latest.json` signature valid = True; tampered URL = False; SHA matches pre-audit exe] |
| D-T4 | GSI bind | Binds 127.0.0.1 only. | [TESTED: `test_binds_localhost_only`] |
| D-T5 | Discord IPC | Tries `discord-ipc-0..9` named pipes with a 0.8 s read timeout; sends only the client id + activity. | [CODE REVIEW ONLY] |
| D-T6 | Admin elevation | `runas` relaunch is asked with a Yes/No dialog each time. | [CODE REVIEW ONLY] |
| D-T7 | Personal paths / Steam IDs in desktop source | None found. | [TESTED: grep, 0 hits] |
| W-T1 | /connect page | `74.91.124.21:27015` valid; `rsscs2.kr` → :27015; port 0, 99999, `<script>`, `javascript:`, empty, `1.2.3.4:27015&calc` blocked. Non-catalog hosts need a click. Text is set with `textContent`. | [TESTED: node run of the page's `validateTarget`] |
| W-T2 | XSS | `dangerouslySetInnerHTML` only holds fixed CSS text in ChaosAnomalyEngine.tsx; no user data. No `innerHTML`, `eval`, `document.write`. | [CODE REVIEW ONLY] |
| W-T3 | Third-party embeds | No iframes, no CDN scripts in src or index.html, so SRI is not needed. Google Fonts CSS is the only third-party style. | [CODE REVIEW ONLY] |
| W-T4 | Visitor data | No analytics/cookies. `localStorage` keeps volume/mute only. Visitors' browsers call the Render backend, zegraph.xyz and Google Fonts directly (those sites see the visitor's IP). | [CODE REVIEW ONLY] |
| W-T5 | Source maps | Not enabled (Vite default off). | [CODE REVIEW ONLY]; confirm after build |
| W-T6 | Workflow secrets | Workflow uses no secrets. | [CODE REVIEW ONLY] |
