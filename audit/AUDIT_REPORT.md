# GeronimoHQ final audit — report

Branch `final-audit` (from `main` @ `9cd8f07`). Auditor: Claude (Claude Code on the owner's PC), 2026-11-10.
Pre-audit backup: `backups/final-audit-2026-11-10/` (full copy + `repo-full-history.bundle`).
**Rollback (one line):** `git checkout main && git branch -D final-audit` — the working exe `dist\CS2_Command_Center.exe` was never changed (SHA-256 `AEC0502A…C913` before and after).

<!-- SUMMARY:START -->
**Findings: 79** — Critical 2, High 2, Medium 32, Low 38, Info 5.  
**Status:** Fixed 60, Not fixed 11, Owner action 6, Not tested 2.  
**Evidence:** [TESTED] 58, [CODE REVIEW ONLY] 20, [NOT TESTED] 1.
<!-- SUMMARY:END -->

## Top 10 risks (what matters most, in order)

1. **L-01 Live backend** — owner reports the token deploy is done (OWNER_STEPS A); quick check: `/docs` = 404, heartbeat without token = 401.
2. **D-05 Old app copies** in the wild still send presence pings; they stop affecting the card only after the backend deploy (fixed in the new exe, which is not released yet).
3. **P7-01 New exe not released** — `scratch\dist\CS2_Command_Center.exe` (SHA-256 `F48472BB…E9D6BE16 (v1.5.1)`) holds every fix (incl. the handle leak); the site still serves the pre-audit exe. Release = owner steps (copy, sign manifest, deploy).
4. **Fixes since the PR need a fresh exe** — the exe in scratch\dist predates the owner-feedback round; rebuild in step F.
5. **P9-01 Third-party content** (Pepe artwork, "Banana Phone" song/video, Valve/CS2 and community names/logos) — rights not checked; owner decision before sharing widely.
6. **B-11 `/api/servers` republishes player names** (owner kept it for the Players lists).
7. **Geo radar is a model** (time-of-day + name guesses), now labelled "estimate" in both app and site (owner choice).
8. **Not tested in game**: every autoexec/console command (CS2 not launched by rule) — OWNER_STEPS E.
9. **P6-03/P6-04 Partial undo**: the fullscreen flag replaces other compatibility flags on cs2.exe; Game DVR "revert" writes Windows defaults, not your earlier values (documented in README).
10. **P0-01 Audit request budget exceeded** (rule D): ~27–35 backend requests (limit 30) and >3 A2S queries per game server during sessions 3 tests; tests now mock all network.

## Findings

Severity: Critical / High / Medium / Low / Info. Status: Fixed / Owner action / Not fixed / Not tested.
Evidence: [TESTED] (output in the named `audit/evidence_*` file or test), [CODE REVIEW ONLY], [NOT TESTED].

| ID | Area | Finding | Severity | Status | Evidence | File and line |
|---|---|---|---|---|---|---|
| L-01 | Backend (live) | Live Render backend is pre-audit: presence heartbeat accepted without token, any origin reflected, /docs public. | Critical | Owner action | [TESTED] before; owner reports deployed 2026-11-10 (not re-checked: request budget) | backend/api.py (deploy) |
| D-05 | Desktop | Every install pinged the owner's backend (presence) incl. an unauthenticated exit ping. Now owner-only + token. | Critical | Fixed | [TESTED] test_security_phase1c | desktop-app/app.py `_start_presence_heartbeat` |
| D-01 | Desktop | "Add Server" host went into `cmd start steam://…` and the console: command injection. Strict host:port check everywhere. | High | Fixed | [TESTED] ServerAddressTests | desktop-app/server_browser.py `validate_server_address` |
| P4-07 | Desktop | **Windows handle leak ~60/min** (342→939 in 10 min): worker threads called Tcl (`after`, `winfo_exists`, `log`). Now queued to the Tk thread. | High | Fixed | [TESTED] handle probe 31→0–1 per 30 s; P4_NoTclCallsFromWorkerThreads | desktop-app/app.py `CS2TruePanoramaApp.after`, `safe_after`, `log` |
| D-03 | Desktop | Map Cleaner deleted any given path; now only Workshop/maps folders, no junctions. | Medium | Fixed | [TESTED] MapCleanerTests | desktop-app/custom_map_cleaner.py |
| D-04 | Desktop | GSI listener: no size limit, browser pages could post fake state. | Medium | Fixed | [TESTED] GsiTests | desktop-app/cs2_gsi.py |
| D-02 | Desktop | Link opener accepted any scheme / cmd metacharacters. | Medium | Fixed | [TESTED] UrlOpenerTests | desktop-app/app.py `open_url_safely` |
| B-05 | Backend | Anyone named "Geronimo" flipped the card to "in server". | Medium | Fixed | [TESTED] | backend/api.py `get_geronimo_steam_status` |
| B-06 | Website | Card showed Offline for backend `unknown`. | Medium | Fixed | [CODE REVIEW ONLY] | src/components/GeronimoDiscordPresence.tsx |
| B-07 | Website | Any GFL player containing "geronimo" set "in server". | Medium | Fixed | [CODE REVIEW ONLY] | GeronimoDiscordPresence.tsx |
| B-01 | Backend | Refresh lock unused → parallel 42-server sweeps. | Medium | Fixed | [CODE REVIEW ONLY] | backend/api.py `get_servers` |
| B-02 | Backend | TLS verification off for zegraph fallback. | Medium | Fixed | [TESTED] | backend/api.py |
| W-01 | Website | `/?ip=` auto-launched steam:// to any host. Now via /connect checks. | Medium | Fixed | [CODE REVIEW ONLY] | src/App.tsx |
| W-06 | Website | No Content-Security-Policy. Added as build-time meta tag. | Medium | Fixed | [TESTED] 0 violations (load, 40 effects, scroll) | vite.config.ts `cspMetaPlugin` |
| D-07 | Desktop | Start with Windows created an elevated (/rl highest) logon task as well as the Run key. Owner chose normal user: task no longer created; old one removed. | Medium | Fixed | [TESTED] StartupNotElevated | desktop-app/app_config.py `set_windows_startup` |
| P2-1 | Desktop | Dashboard autoexec status used markers the app never writes; never refreshed. | Medium | Fixed | [TESTED] Bug1AutoexecStatus | desktop-app/core_logic.py `get_autoexec_status` |
| P2-2 | App+Web | Totals were fixed text in the app (646 / 34 of 41); website counted bots; stale snapshot shown as live. One shared rule now. | Medium | Fixed | [TESTED] evidence_phase2_totals.md | server_browser.py / api.py / playerTotals.ts `compute_player_totals` |
| P2-3 | Desktop | Status bar Slot Sniper and DNS were fixed text. | Medium | Fixed | [TESTED] Bug3StatusBar | desktop-app/app.py `_status_bar_tick` |
| P2-4 | Desktop | Discord preview drawn from placeholders ("Online", GFL IP) with CS2 closed. | Medium | Fixed | [TESTED] Bug4DiscordPreview | desktop-app/discord_rpc.py `broadcast_snapshot` |
| P2-5 | Desktop | App GEO line was a fixed string per region. Now measured ZEGraph continents, labelled estimate + sample. | Medium | Fixed | [TESTED] Bug5Geo | desktop-app/server_browser.py `get_server_demographics_text` |
| P2-6 | Desktop | "Check for updates" not saved; Reset deleted presence token; "Saved" shown on failure. | Medium | Fixed | [TESTED] Bug6SettingsPersist | desktop-app/app_config.py `SETTINGS_DEFAULTS` |
| P2-7 | App+Web | "100% VAC-SAFE", "SUB-TICK VERIFIED", "ZERO RUNTIME OVERHEAD"; two false statements (DNS "no system modification", "no process handles"). | Medium | Fixed | [TESTED] Bug7Claims | many (see FINDINGS_PHASE2) |
| P2-9 | Desktop | Re-applying Engine Tweaks deleted everything after its block (e.g. the ZE block); `host_writeconfig` defeated undo. | Medium | Fixed | [TESTED] Bug9Autoexec | desktop-app/core_logic.py `split_perf_block` |
| P3-01 | Desktop | 5 Settings saved but unused (incl. Discord share privacy tick). | Medium | Fixed | [TESTED] P3_01 | desktop-app/app_config.py |
| P3-02 | Desktop | Invented "time on map" (hash of id). | Medium | Fixed | [TESTED] source check | desktop-app/app.py `server_map_start_exact` |
| D-12 | Desktop | Maintenance deleted files with no confirmation. | Medium | Fixed | [TESTED] P3_D12 | desktop-app/app.py `run_pc_maintenance` |
| P3-07 | Tests | Older tests wrote the owner's real config (`last_page_key`); restored from backup; tests isolated. | Medium | Fixed | [TESTED] config hash c3838aa1 before/after | desktop-app/_test_isolation.py |
| P3-08 | Website | Horizontal scroll at 390 px (442) and 768 px (885): non-wrapping rows; custom CSS beat `hidden sm:` so a phone badge never hid. | Medium | Fixed | [TESTED] 390/768/1440 = no overflow | src/index.css, CyberNavbar.tsx, ServerRadarPreview.tsx |
| P5-01 | App+Web | False feature claims: core affinity, D3D11/Vulkan selector, cl_interp, jumpthrow/C4 binds. | Medium | Fixed | [TESTED] test_phase5 | CS2CommandCenterPreview.tsx, app.py FAQ |
| P5-11 | App+Web | Claims sweep ("100% safe/healthy/read-only…", "never be banned"). | Medium | Fixed | [TESTED] ClaimsSweep | app.py, core_logic.py, website |
| P6-01 | Desktop | Restore Defaults always set Balanced (not your earlier plan). | Medium | Fixed | [TESTED] test_phase6_revert | desktop-app/core_logic.py `restore_previous_power_plan` |
| P6-02 | Desktop | Restore Defaults: no confirmation (overwrites autoexec with first backup) and claimed "All settings restored" (DNS/launch options untouched). | Medium | Fixed | [TESTED] RestoreDefaults | desktop-app/app.py `run_revert_all` |
| P2-D1 | Website | Geo radar: owner chose the website method for both. App now uses a line-by-line port (geo_estimate.py), same numbers as the site, labelled estimate. | Medium | Fixed | [TESTED] parity test vs website | src/utils/serverDemographics.ts |
| P9-01 | Share | Third-party content: Pepe artwork, "Banana Phone" audio/video, Valve/CS2, Discord, server community names and logos. Rights not reviewed. | Medium | Owner action | [CODE REVIEW ONLY] | public/media, src/components |
| B-03 | Backend | Map name in zegraph URL unchecked. | Low | Fixed | [TESTED] | backend/api.py |
| B-04 | Backend | Unknown server id 200 + uncached UDP per call. | Low | Fixed | [TESTED] | backend/api.py `get_server_detail` |
| B-08 | Website | Card showed made-up map/players when data missing. | Low | Fixed | [CODE REVIEW ONLY] | GeronimoDiscordPresence.tsx |
| W-03 | CI | fetch script: TLS off, unchecked map name. | Low | Fixed | [TESTED] py_compile | scripts/fetch_live_servers.py |
| W-04 | CI | Build job had Pages write + OIDC token. | Low | Fixed | [TESTED] YAML | .github/workflows/deploy.yml |
| W-02 | Website | `target=_blank` without noopener. | Low | Fixed | [TESTED] scan | src/components |
| D-06 | Desktop | Config written in place (crash = reset). Atomic now. | Low | Fixed | [TESTED] | desktop-app/app_config.py `save_config` |
| P1-GSI | Desktop | GSI replied before handling and without draining → flaky on Windows. | Low | Fixed | [TESTED] 0/45 flaky | desktop-app/cs2_gsi.py |
| D-13 | Desktop | GSI port busy failed silently; SO_REUSEADDR hid clashes. | Low | Fixed | [TESTED] P3_D13 | desktop-app/cs2_gsi.py `_ExclusiveHTTPServer` |
| P3-03 | Website | Random "ping" shown like a live value. | Low | Fixed | [TESTED] scan | src/components/CyberNavbar.tsx |
| P3-09 | Desktop | No internet showed "0 players / 0 of 41 online". | Low | Fixed | [TESTED] ErrorStatesAudit | desktop-app/server_browser.py `format_totals` |
| P4-01 | Website | Unused 400 kB map catalog in main JS; overlays not lazy. Main JS −34 % gzip. | Low | Fixed | [TESTED] build + Lighthouse | src/data/s2zeMappersCatalog.ts, src/App.tsx |
| P5-02 | App+Web | "1 Mbps" for `rate 1000000` (bytes/s ≈ 8 Mbps); "128 TICK" labels (CS2 = 64 + sub-tick). | Low | Fixed | [TESTED] test_phase5 | core_logic.py, website |
| P5-05 | Website | 3 text styles below WCAG AA contrast. | Low | Fixed | [TESTED] 0/554 below AA | src/components |
| P5-06 | Website | No skip link / focus style. | Low | Fixed | [TESTED] rules in build; visual [NOT TESTED] | src/index.css, src/App.tsx |
| P5-08 | Desktop | 7 labels hard-coded low-contrast grey. | Low | Fixed | [TESTED] ratios | desktop-app/app.py |
| P5-10 | App+Web | Esc did not close 5 app dialogs or the mobile menu. | Low | Fixed | [TESTED] | app.py `bind_escape_to_close`, CyberNavbar.tsx |
| P6-07 | Share | README was the Vite template. Now: changes, undo, data, SmartScreen, disclaimer. | Low | Fixed | [CODE REVIEW ONLY] | README.md |
| P6-11 | Share | Desktop dependencies not listed. Pinned; pip-audit clean. | Low | Fixed | [TESTED] pip-audit | desktop-app/requirements.txt |
| B-09 | Backend | Python version not pinned on Render. | Low | Owner action | [CODE REVIEW ONLY] | backend/.python-version |
| B-11 | Backend | `/api/servers` republishes player names. Owner decision: keep (needed for the Players lists). | Low | Not fixed | [CODE REVIEW ONLY] | backend/api.py `fetch_single_server` |
| W-05 | CI | Actions pinned to tags, not SHAs. | Low | Fixed | [TESTED] YAML parse; SHAs from git ls-remote | .github/workflows/deploy.yml |
| P6-08 | Share | No LICENSE (owner chooses; not picked by audit). | Low | Owner action | [CODE REVIEW ONLY] | (repo root) |
| P6-10 | Share | 37 MB exe committed in git (`public/`). Recommend GitHub Releases. | Low | Owner action | [CODE REVIEW ONLY] | public/CS2_Command_Center.exe |
| P6-03 | Desktop | Fullscreen flag replaces other compat flags on cs2.exe; revert deletes the value. | Low | Not fixed | [TESTED] test_phase6_revert (behaviour) | desktop-app/core_logic.py `disable_fullscreen_optimizations` |
| P6-04 | Desktop | Game DVR revert writes Windows defaults, not earlier values. | Low | Not fixed | [TESTED] test_phase6_revert | desktop-app/core_logic.py `revert_windows_game_dvr` |
| P6-05 | Desktop | Launch options: backup kept, no restore button. | Low | Not fixed | [CODE REVIEW ONLY] | desktop-app/core_logic.py `save_launch_options` |
| P6-06 | Desktop | DNS restore = automatic (DHCP), not an earlier custom DNS. | Low | Not fixed | [CODE REVIEW ONLY] | desktop-app/core_logic.py `restore_dns_to_dhcp` |
| W-11 | Website | Dev server `host: true` (LAN-visible while `npm run dev`). | Low | Not fixed | [CODE REVIEW ONLY] | vite.config.ts |
| W-13 | Website | `emptyOutDir: false` can publish stale files. | Low | Not fixed | [CODE REVIEW ONLY] | vite.config.ts |
| D-10 | Desktop | Update helper .bat written as UTF-8 (non-ASCII install path). | Low | Not fixed | [CODE REVIEW ONLY] | desktop-app/updater.py |
| D-11 | Desktop | presence_secret stored in plain text (owner PC only). | Low | Not fixed | [CODE REVIEW ONLY] | desktop-app/app_config.py |
| P4-03 | Website | Thumbnail fallback cascade logs 404s (no broken images). | Low | Not fixed | [TESTED] browser | src/utils/serverQuery.ts |
| P0-01 | Process | Audit exceeded rule D budgets (backend ~27–35 of 30; >3 A2S per server) in session 3. Tests now mock network. | Low | Fixed | [TESTED] _test_isolation | desktop-app/_test_isolation.py |
| P8-01 | Desktop | Discord/presence noticed "left the server" only after ~35-40 s (roster fallback: 30 s grace + 3 misses) and "CS2 closed" after up to ~27 s (25 s GSI window). Now the live GSI feed decides (5 s freshness); roster check only when GSI is silent. | Medium | Fixed | [CODE REVIEW ONLY] (needs CS2 to test) | desktop-app/app.py `_gsi_is_fresh` |
| P4-08 | Desktop | Dialogs (players, soundtrack, ...) still called Tk from worker threads (`dlg.after`, `winfo_exists`) = more handle leaks. Guard now covers every widget. | Medium | Fixed | [TESTED] 0 thread Tcl calls (test_phase3_gaps) | desktop-app/app.py `_install_thread_guards` |
| P3-11 | Desktop | 57 clickable controls had no tooltip. | Low | Fixed | [TESTED] test_phase3_gaps: 0 missing | desktop-app/app.py `FALLBACK_TOOLTIPS` |
| P8-02 | Desktop | GFL / Sniper Target dropdowns: empty gap before the arrow (sized for the longest option). Now sized to the current choice. | Low | Fixed | [TESTED] gap 31-36 px for every option (was ~60) | desktop-app/app.py `fit_combobox_width` |
| P8-03 | Website | Navbar "SERVERS: 6 CLUSTERS · ONLINE" was fixed text. Now the real count from the radar's data (no extra requests). | Low | Fixed | [TESTED] browser: 29 / 41 SNAPSHOT = radar pill | src/components/CyberNavbar.tsx |
| P8-04 | Website+App | Geo model treated Chinese clusters ("Hong Kong / BGP Multi-Line") as non-Asian (estimated mostly RU/PL/DE). | Low | Fixed | [TESTED] parity + test | src/utils/serverDemographics.ts, desktop-app/geo_estimate.py |
| P7-01 | Release | New exe built + smoke-tested in scratch\dist, not released (chat rule: never touch dist\ exe). | Info | Owner action | [TESTED] smoke | scratch\dist\CS2_Command_Center.exe |
| P4-04 | Website | 2 unused components (74 kB source, not bundled). | Info | Not fixed | [CODE REVIEW ONLY] | FakeRetroScamAds.tsx, SecretGeronimoVault.tsx |
| P6-12 | Share | "C:\Users\Gala…" in the exe is a library doc example ("Galahad"), not a user path. No personal path in either exe. | Info | Fixed | [TESTED] exe scan | — |
| P5-09 | Desktop | Tk keyboard navigation and 125/150 % visual check not done (DPI tests exist). | Info | Not tested | [NOT TESTED] | — |
| P3-10 | Website | Presence card cold start (Connecting → Standby, never Offline) by code; not watched live (hidden pane). | Info | Not tested | [CODE REVIEW ONLY] | GeronimoDiscordPresence.tsx |

## Measurements (selected)

| What | Before | After | Evidence |
|---|---|---|---|
| Website main JS (gzip) | 247.3 kB | 162.1 kB | build output |
| Lighthouse mobile (perf / a11y / BP / SEO) | 69 / 96 / 93 / 100 (live) | 75 / 100 / 89* / 100 (local) | *BP drop = console errors from blocked backend in the test copy |
| App idle in tray | — | 0.39 % of one core, 95 MB | [TESTED] |
| App 10 min, refresh 1 s: handles | +597 (leak) | flat (see evidence_soak.txt) | [TESTED] |
| Test suites | 19 files (2 could never fail, 8 hung) | 25/25 runs pass | evidence_final_tests.txt |
