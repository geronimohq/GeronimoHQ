# Phases 3–7 — findings

Date: 2026-11-10 (+08:00). Branch: `final-audit`. Reviewer: Claude (Claude Code on the owner's PC).
The owner chose: "go by the phase titles + findings so far" (the superprompt text for Phases 3–7 was not
available). Labels as before: [TESTED] / [CODE REVIEW ONLY] / [NOT TESTED].

## Phase 3 — Functional

Tests: `desktop-app/test_phase3_functional.py` 10/10 [TESTED]. Full suite after Phase 3: 21/21 files pass.

| ID | Finding | Fix | Status |
|---|---|---|---|
| P3-01 | 5 Settings options were saved but used by nothing. | **Start page**: Dashboard or "Last used page" (remembered at exit). **Query speed**: sets the ZE Game Servers refresh (was always 1 s; default "Normal" = 5 s). **Sound when a slot opens**: plays a short Windows sound (none existed). **Share with Discord**: now the same switch as the Discord tab (`discord_rpc_enabled`); turning it off clears your Discord activity. **Volume slider removed**: Windows' simple sound API cannot set a volume, so it could never work. | Fixed [TESTED] |
| P3-02 | Non-GFL "time on map" was invented (`now − hash(id) % 900 − 120` s). | First sighting shows "≥ mm:ss on map" (a lower bound); exact only after the app saw the map change. | Fixed [TESTED: source check] / display [CODE REVIEW ONLY] |
| P3-03 | Website navbar "ping" was a random 10–18 ms. | Removed; the pill shows the local clock + "LOCAL". Other `Math.random` uses are decorative (particles, jokes). | Fixed [TESTED: tsc + scan] |
| D-13 | GSI listener failed silently if port 3000 was busy. Also, Python's HTTPServer sets SO_REUSEADDR, which on Windows lets two programs bind the same port with **no** error. | Exclusive bind (`SO_EXCLUSIVEADDRUSE`); the app log says live game state is off and why. | Fixed [TESTED: clash on a free test port] |
| D-12 | "Run Maintenance" deleted temp/cache files with no question. | Asks first, listing exactly what is ticked ("permanently deletes …", Recycle Bin "cannot be undone"); nothing ticked → says so. | Fixed [TESTED: cancel = nothing deleted, cleaners mocked] |
| P3-S | Smoke: all 10 app pages open with 0 Tk callback errors. | — | [TESTED] |
| P3-04 | Website geo country % is modelled. | Owner decision P2-D1. | Open (owner) |
| P3-05 | App queries only the visible server sub-tab. | Totals no longer depend on it (Phase 2). | Info |
| P3-06 | "sub-tick" wording for `rate` / `cl_net_buffer_ticks`. | Phase 5. | → Phase 5 |

## Phase 4 — Performance

| ID | Finding | Fix / result | Status |
|---|---|---|---|
| P4-01 | Website main JS was 1,006.7 kB (247.3 kB gzip). A source-map analysis showed **~400 kB came from `src/data/zeMapCatalog.json`** (1,608 maps with image URLs and addon ids) — only the mapper names are ever used. | Import a generated slim index `src/data/zeMapMappers.json` (61.7 kB, same keys/order; `scripts/build_map_mappers.py`). The full catalog stays as source data. | Fixed [TESTED: build] |
| P4-02 | Three floating overlays (Chaos button, roaming gremlin, Discord card) were in the main bundle. | Lazy-loaded (`React.lazy`), each its own chunk. They hold no navbar anchors, so scroll/TRANSMISSION behaviour is unaffected. | Fixed [TESTED: build + browser load] |
| — | **Result**: main JS **582.6 kB (162.2 kB gzip), −34 % gzip**; first page load in the browser = **240 kB transferred**, 46 requests, no media downloaded up front (audio/video load on demand). | | [TESTED] |
| P4-03 | Map thumbnails try up to 4 places (self-hosted → zegraph ×3); every miss logs a 404 in the console. No image ends up broken. | Not changed (cosmetic console noise; changing the cascade risks missing thumbnails). | Low, open |
| P4-04 | `FakeRetroScamAds.tsx` and `SecretGeronimoVault.tsx` (74 kB source) are not imported anywhere. Not in the bundle (tree-shaken). | Phase 6 decision (dead code). | Info |
| P4-05 | Desktop app idle, in the tray, from source with a temp `APPDATA`: **0.39 % of one core over 60 s, 95 MB working set, 10 threads**; ~0.9 s CPU to start. | No change needed. Default server refresh on the ZE page is now 5 s (was 1 s), per the setting. | [TESTED] |
| P4-06 | Backend: one full 41-server sweep ~3 s; cached 3.5 s; one sweep at a time (Phase 1 B-01). | No change. | [TESTED: evidence_phase2_totals.md] |

## Phase 5 — Wording and accessibility

Tests: `desktop-app/test_phase5_wording_a11y.py` 5/5 [TESTED]; browser scans on the built site [TESTED].

| ID | Finding | Fix | Status |
|---|---|---|---|
| P5-01 | **False feature claims.** App FAQ said Engine Tweaks set `cl_interp 0.015625` and add jumpthrow / C4-drop / ragdoll-clear binds; the website's Live Booster card said it sets **CPU core affinity** (`0x0000FFFF`), has a **D3D11/Vulkan selector** and tunes `cl_interp`. None of this exists in the code (grep: 0 hits). | Rewritten to what the code does (one marked block; process priority only, reverts when CS2 closes). | Fixed [TESTED: scan] |
| P5-02 | Wrong units: `rate 1000000` was described as "1 Mbps". It is bytes/s (≈ 8 Mbps). | "max bytes/s (about 8 Mbps; CS2 may cap it lower)" in the app block, website file and labels. | Fixed |
| P5-03 | "128 TICK" labels (servers, footer, HUD). CS2 servers run 64 tick + sub-tick. | "64 TICK (+ SUB-TICK)". | Fixed |
| P5-04 | "Sub-tick" used as a marketing word for ordinary network cvars (P3-06). | Plain names ("network rate settings", "Engine Tweaks"). The educational FAQ about CS2's sub-tick model is kept. Parody sections untouched. | Fixed |
| P5-05 | Website contrast: 3 text styles under 4.5:1 (`text-slate-500/600` on near-black, e.g. "IDLE (0 PLAYERS)" 2.6:1). | → `text-slate-400`. Re-scan of 554 visible text elements: **0 below WCAG AA**. (Tailwind v4 uses oklch colours; the scan converts them via canvas.) | Fixed [TESTED: browser] |
| P5-06 | Website keyboard: no skip link, no explicit focus style. | "Skip to content" link (first Tab stop) + orange `:focus-visible` outline. Built CSS contains both rules [TESTED]; the visual slide-in could not be seen because the browser pane was hidden (`:focus` does not match in an unfocused page) → owner hand test. | Fixed / visual [NOT TESTED] |
| P5-07 | Website basics already fine: `lang="en"`, 1 `<h1>`, `<main>`, all 7 images have `alt`, every visible button/link/input has a name, a `prefers-reduced-motion` rule exists. | — | [TESTED] |
| P5-08 | Desktop contrast: theme colours are fine (muted text 7.8–9:1, orange 6.2–7.2:1), but 7 labels hard-coded `#64748b` / `#4b5563` (2.5–4.1:1), e.g. sidebar "NAVIGATION", "SYSTEM ACTIVITY LOGS". | → theme muted colour (≥ 7.8:1). Disabled-state grey kept (WCAG exempts disabled controls). | Fixed [TESTED: computed ratios] |
| P5-09 | Desktop app keyboard navigation (Tk) not audited in depth. | — | [NOT TESTED] |
