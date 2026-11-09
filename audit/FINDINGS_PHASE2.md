# Phase 2 — the owner's 9 known bugs

Date: 2026-11-10 (+08:00). Branch: `final-audit`. Reviewer: Claude (Claude Code on the owner's PC).

Labels: **[TESTED]** = a test or measurement ran here, output in `audit/evidence_phase2_tests.txt`
(or the evidence file named). **[CODE REVIEW ONLY]** = read, not run. **[NOT TESTED]** = not checked.
**[NOT TESTED in game]** = a CS2 console command; CS2 was not launched (rule).

Test file: `desktop-app/test_phase2_bugs.py` — **36/36 pass** on the new code; the same file on the
original code: **35 fail** (14 failures + 21 errors), only the bug 8 check passes (that fix already existed).
The test redirects the app config to a temp folder, stubs the registry/Task Scheduler and all pop-ups,
and uses temp `cfg` folders: the owner's real settings and CS2 files are never touched
(config SHA-256 checked before/after: identical).

## Summary

| # | Bug | Root cause (plain words) | Status |
|---|---|---|---|
| 1 | Dashboard says "not edited by this app" after editing in the app | The Dashboard looked for `// --- CS2 COMMAND CENTER` and `GERONIMOHQ`, which the app **never writes** (it writes `[CS2 FPS OPTIMIZER …]` and `[CS2 COMMAND CENTER: ZE VISUAL…]`). The in-app text editor writes no marker at all. The label was built once and never refreshed. Also: the path was only set if autoexec.cfg existed at app start. | Fixed [TESTED] |
| 2 | "646 players in-game", "34 / 41 nodes online" look wrong | **Both numbers were fixed text** in the app (Dashboard and ZE Game Servers) and never computed. The website summed the A2S `players` field, which **includes bots**, and showed a 25-hour-old fallback file as if live. | Fixed [TESTED] |
| 3 | "SLOT SNIPER: IDLE" never changes | Fixed text, never updated. "GAMING DNS: ACTIVE" was **also fixed text** (never checked). | Fixed [TESTED] |
| 4 | Discord tab shows "Online / In Main Menu / 74.91.124.21" while CS2 is closed | The tab drew its preview from placeholder start values ("In Main Menu • Standby", a GFL IP) and decided "online" from that text, not from what was sent. | Fixed [TESTED] |
| 5 | App GEO "US 54% / CA 26% …" | The app's GEO line was **a fixed string per region**, never based on player data. | Fixed [TESTED] |
| 6 | "Check for updates when the app starts" not saved | `save_settings()` never wrote `check_updates_on_startup`. Also: "Saved" showed even when writing failed; "Reset" replaced the whole config and **deleted `presence_secret`, Discord client id and timestamps**. | Fixed [TESTED] |
| 7 | "100% VAC-SAFE" and similar claims | Claims nobody can prove. Two were also **false**: DNS FAQ said "zero … system modifications" (changing DNS *is* one); the website said the app does not "read process handles" (it opens CS2's process to set priority). | Fixed [TESTED: claim scan] |
| 8 | TRANSMISSION highlight on first click | Fix already present (click sets the active item before scrolling; bottom of page forces TRANSMISSION). | Already fixed — confirmed [TESTED: browser] |
| 9 | Autoexec generator | Null binds were already removed earlier (commit `527946b`), which is safer than renaming them: Valve blocks multi-action movement binds. Remaining problems found and fixed: app ZE block ran `host_writeconfig`; no undo lines; website file had contradicting duplicate cvars; **re-applying Engine Tweaks deleted everything after its block** (e.g. the ZE Studio block). | Fixed [TESTED] + commands [NOT TESTED in game] |

## Details

### #1 Autoexec status — [TESTED]
- One function `core_logic.get_autoexec_status()` reads the file **now** and knows every marker the app writes
  (`APP_AUTOEXEC_MARKERS`). In-app editor saves are remembered by SHA-256 (`autoexec_last_app_save` in the
  config) and reported only while the file still has exactly that content.
- Refresh: when the Dashboard is shown, after every autoexec write (all writers call
  `_refresh_autoexec_preview`), after an editor save, and when the main window gets focus.
- Wording: "not edited by this app" (a guess) → "no section written by this app" (a fact).
- Tests: `Bug1AutoexecStatus` 4/4 (ZE write, Engine Tweaks write, editor save, Notepad edit + focus, missing file).

### #2 Player / server totals — [TESTED]
Same-minute comparison (`audit/evidence_phase2_totals.md`, script `audit/tools/compare_totals.py`, 1 backend request):

| Source / rule | players | servers online |
|---|---|---|
| BEFORE app (fixed text) | 646 | 34 / 41 |
| BEFORE website (players incl. bots) | 228 | 28 / 41 |
| AFTER, direct A2S, humans only | **219** (8 bots removed) | 28 / 41 |
| AFTER, catalog + `rsscs2.kr` alias added | 219 (1 duplicate dropped) | 28 / 41 |

- Checked, not a problem today: the backend and app each have 41 servers; the 42nd "target" is the
  `rsscs2.kr` alias in the /connect allow-list (`catalog_targets`), not counted. Failed queries are not counted.
- **One rule, one function**: `compute_player_totals()` — humans only (players − bots), only servers that
  answered within 90 s, each ip:port once. Byte-identical copies in `desktop-app/server_browser.py`,
  `backend/api.py` and `scripts/fetch_live_servers.py` (a test compares their syntax trees), and a TypeScript
  twin `src/utils/playerTotals.ts` (a test runs it in Node and compares numbers).
- Backend `/api/servers` and the CI snapshot now include a `totals` field. The website and the app **display**
  that field; they only compute it themselves for an older backend.
- App: Dashboard card and ZE Game Servers pills use **one method** (`_refresh_ze_totals` →
  `server_browser.get_shared_totals`): backend (60 s cache) → offline fallback = direct A2S of the catalog.
  Network only while one of those pages is open and the window is visible.
- Website: a snapshot older than 90 s is labelled "as of N min ago"; the hard-coded `?? 33` is gone.
- Live check: app path returned `238 players in-game (bots unknown) · 29 / 41` from the live backend.
  "(bots unknown)" stays until the new backend is deployed (OWNER_STEPS A).

### #3 Status bar — [TESTED]
- Slot Sniper: Idle / Armed — server (join at ≤ N) / Triggered — connecting / Cooldown (Ns). Read from the
  shared sniper object every second via Tk timers, which also run when the window is in the tray, and
  whichever page armed it. Test arms a fake sniper with the window withdrawn.
- DNS: shows what `netsh` reports for the active adapter ("DNS: Cloudflare…", "automatic (router / ISP)",
  "custom (x.x.x.x)"); refreshed at start and after every DNS change.
- The third indicator ("100% VAC-SAFE") became "Hobby project · not affiliated with Valve".
- The hidden "CS2: GAME READY" label is never shown (not packed); left as is.

### #4 Discord tab — [TESTED]
- The preview is drawn **only** from `discord_rpc.broadcast_snapshot()` = the last activity really sent on an
  open pipe (cleared on close and on send failure). Placeholder start values removed.
- On open: neutral "Checking…", then an automatic check without pop-ups. Elapsed time uses the start time
  that was really sent.
- Contrast: small green status text `#23a55a` (4.9:1) → `#57d98a` (8.6:1) on `#232428`.
- Not tested: a real Discord client (rule: don't launch/close Discord). The pipe code is unchanged.

### #5 Geo radar — [TESTED] (method) / [CODE REVIEW ONLY] (website model)
**How the website's radar works (plain words):** for each server it starts from a **model**, not
measurements: a time-of-day curve per region spreads "unknown" players over countries, and player
**names** are scanned for scripts or clan tags (Hangul → KR, Cyrillic → RU, `[PH]` → PH …). Only for **GFL**
does it use real data: ZEGraph's live continent counts (players whose country ZEGraph knows). So:
continent split for GFL = measured (sample: 37 of 64 players at test time); every country % and every
non-GFL server = an estimate from assumptions.

**Why the app differed:** the app did not use any of that; it printed one fixed split per region.

**App now:** same real source as the website (ZEGraph continents for GFL), 5-min cache, offline fallback =
last value with its age; label `GEO (estimate, 37 of 64 players): Europe 43% · N. America 24% · Asia 19%`;
`server empty` at 0 players; `no measured data for this server` elsewhere (no invented numbers). Only
aggregate counts are used; the function cannot take player names. Uses humans only.
Not done: the website still shows the modelled country split → owner decision (OWNER_STEPS B, P2-D1).

### #6 Settings — [TESTED]
- One list `app_config.SETTINGS_DEFAULTS` (9 settings) drives Save, Reset and the test.
- Round trip for **every** setting: change all 9 → Save → check JSON on disk → fresh `load_config()`
  ("close and reopen") → reopen dialog shows all 9. Passed.
- Save shows "Settings saved." only after a successful write; otherwise an error with the file path and the
  dialog stays open. Windows startup (registry + scheduled task) is only touched when that option changed
  (before: every Save re-created the admin scheduled task).
- Reset now resets only those 9 keys in the dialog (kept until Save) — `presence_secret` etc. are kept.
- Frozen-exe path: `%APPDATA%\CS2CommandCenter\command_center_config.json` in both frozen and script mode
  (APPDATA is always set) [CODE REVIEW ONLY]. Atomic write from Phase 1 (D-06).
- Updater re-review per 1c: unchanged since Phase 1 D-T3 (HTTPS, host pinned, Ed25519, SHA-256 + size,
  user click). The startup check now really follows the saved tick.
- Found while testing (Phase 3 item P3-01): 5 of the 9 settings are saved but **nothing uses them**
  (start page, sniper sound on/off, sniper volume, refresh speed, Discord share). The Discord "share" tick
  is a privacy switch that does nothing.

### #7 Claims — [TESTED: scan of 12 user-facing files, 0 hits]
Replaced everywhere listed (app header chips, status bar, Discord banner, "100% clean", dashboard subtitle,
autoexec headers, website badge/box, Config Studio badge, sidebar "VAC Safety Protocol", module badges, FAQ,
/connect page "Verified"). New wording, all checked in code:
"Uses config files and standard Windows settings. Does not read or modify CS2 memory." plus what it *does*
touch (process priority, typing `connect` in the console) and "Hobby project, not affiliated with Valve.
Use at your own risk." Removed: "SUB-TICK VERIFIED" (no such check exists), "ZERO RUNTIME OVERHEAD"
(false: background queries, tray, GSI listener).
Checked, nothing to change: README, `<meta>` tags, exe metadata (`.spec` has no version/claims), test names.
Left on purpose: clearly labelled parody components ("PARODY MEME // NO REAL PRIZE"); technical uses
("signature verified" in the updater is a real Ed25519 check).

### #8 Navbar TRANSMISSION — [TESTED: browser]
Built to `scratch/dist`, served with `vite preview`, built-in browser. Both themes (theme is random per
load; pepe and banana both seen), desktop 1024 px and mobile 375 px menu: active = TRANSMISSION at 50 ms,
600 ms, 1.2 s, 2.5 s after the first click, at the click target and at the page bottom; mid-page shows the
right section. Note: the browser pane was hidden, so scrolling was also driven by setting the position and
firing `scroll` (background tabs throttle smooth scroll). Owner hand test in OWNER_STEPS D.

### #9 Autoexec generator — [TESTED] logic, [NOT TESTED in game] commands
- Null binds: none in app or website (removed in `527946b`). No `+left`/`+right` anywhere (test).
- App ZE block: `host_writeconfig` removed. **Side effect it had:** it saved *all* current settings and binds
  into CS2's own config on every launch, so binds stayed even after the block was deleted (undo failed).
- Undo lines in every header (app performance block, app ZE block, website file), including the console
  commands, because CS2 keeps many values after the file is gone. Defaults marked "check your own".
- **Data-loss bug fixed:** re-applying Engine Tweaks (or Restore without backup) deleted everything after
  the performance block. Now only the block is replaced/removed (new END marker; old files without it are
  recognised by their last line). Test: user line + Engine Tweaks + ZE Studio + user line + Engine Tweaks again
  → all kept, one performance block.
- Website file: each cvar once (last value kept, same effect in CS2), e.g. `rate 1000000` then `786432`,
  `snd_headphone_eq 0` then `1`, `fps_max` twice.
- Claims removed: "100% VAC-Safe" (comment/docstring and badges), "PRO". ("CS2 ENGINE VERIFIED",
  "MAXIMUM", "100% consistent" were already gone.) In-game checklist: OWNER_STEPS E.

## New findings for Phase 3 (found during Phase 2, not fixed yet)

| ID | Area | Finding | Severity |
|---|---|---|---|
| P3-01 | Desktop | 5 settings saved but unused, incl. the Discord "share" privacy tick (no effect). | Medium |
| P3-02 | Desktop | Map elapsed time for non-GFL servers is invented: `now - (hash(id) % 900 + 120)` s. | Medium |
| P3-03 | Website | Navbar "ping" is random 10-18 ms (simulated), shown like a live value. | Low |
| P3-04 | Website | Geo radar shows modelled country % (time-of-day curve + name regex; `geronimo` → PH) as live. | Medium (owner decision P2-D1) |
| P3-05 | Desktop | Servers query only the visible sub-tab; totals now come from the backend or a separate catalog query. | Info |
| P3-06 | Desktop | Engine Tweaks FAQ/tooltips still call `rate`/`cl_net_buffer_ticks` "sub-tick" settings (wording, Phase 5). | Low |
