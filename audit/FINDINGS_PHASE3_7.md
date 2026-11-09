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
