# Phases 3–7: checklist against `audit/PHASES_3_7.md`

Each requirement from the brief, what covers it, and its state. "Owner (screen)" = needs eyes on
the screen; listed in `OWNER_STEPS.md` section H instead of being run (owner instruction, session 3).
CS2, Steam and Discord are never launched or closed.

## Phase 3 — Functional

| Requirement (brief) | Covered by | State |
|---|---|---|
| App: every page | P3_Smoke_EveryPage, ErrorStatesAudit | [TESTED] |
| App: every dialog | gap → G3-1 dialog test | see below |
| App: every button / tooltip (none missing, none misleading) | gap → G3-2 widget audit; wording sweeps P2-7/P5 | see below |
| App: every tray item | gap → G3-3 tray audit | see below |
| Extend test_comprehensive_audit.py | ErrorStatesAudit added | [TESTED] |
| Screenshots 100/125/150 % | Owner (screen) | OWNER_STEPS H |
| Text cut-off | Owner (screen); DPI tests exist | OWNER_STEPS H |
| Leftover light-theme widgets | gap → G3-2 colour scan | see below |
| Error: Steam closed | gap → G3-4 (code review; launching Steam is forbidden) | see below |
| Error: Discord closed, no internet, port 3000, CS2 missing, library on other drive | ErrorStatesAudit, P3_D13 | [TESTED] |
| Startup / exit / tray, no ghost processes | exit test (source + exe) | [TESTED]; tray click = Owner (screen) |
| Website: LIVE site in a browser | live load: images, anchors, widths | [TESTED] partial |
| Every nav item, button, link (no 404, right target) | gap → G3-5 link audit | see below |
| Tooltips | gap → G3-5 | see below |
| Presence card states connecting/standby/offline/in-server | gap → G3-6 fixture test | see below |
| Server radar, search and filters | gap → G3-6 | see below |
| Web sniper: no auto-launch | code review + gap G3-6 (no navigation recorded) | see below |
| Autoexec generator | gap → G3-6 (generated text) | see below |
| Mako game | gap → G3-6 | see below |
| /connect inputs | Phase 1 node test; gap → re-run on current file G3-7 | see below |
| 404 fallback | gap → G3-7 | see below |
| Console errors, broken images, widths 390/768/1440 | Phase 3b | [TESTED] |
| Backend: every endpoint, codes, schema, errors | test_api_endpoints 7/7 | [TESTED] |
| Cold start 502/503: Connecting then Standby, never Offline | gap → G3-6 | see below |

## Phase 4 — Performance

| Requirement | Covered by | State |
|---|---|---|
| App cold start | gap → G4-2 exe time-to-ready | see below |
| Idle CPU and RAM of the real child process | perf run | [TESTED] |
| Memory and thread growth over 10 min, auto-refresh on | 10-min soak found the leak; after the fix only 3 min | gap → G4-1 10-min after fix |
| Lighthouse mobile on the live site | Lighthouse | [TESTED] |
| Bundle size, console errors | build, browser | [TESTED] |

## Phase 5 — Wording, accessibility, UX

| Requirement | Covered by | State |
|---|---|---|
| Claims sweep: 100%, guarantee, verified, VAC, safe | P2-7, P5 sweeps | [TESTED] |
| … zero, never, always, instant, millisecond, perfect, maximum, official, fix; comments, generated files, meta tags, exe metadata | gap → G5-1 | see below |
| Contrast | browser scan + desktop ratios | [TESTED] |
| Keyboard Tab / Enter / Esc | Esc done; gap → G5-2 Tab/Enter reachability | see below |
| Reduced motion | gap → G5-3 check every animation path | see below |
| Flashing under 3/s | code review | [CODE REVIEW ONLY] |

## Phase 6 — Share-readiness

| Requirement | Covered by | State |
|---|---|---|
| README: what it does, changes, undo, data leaving the PC | README | [CODE REVIEW ONLY] |
| SmartScreen note **with the SHA-256** | gap → G6-2 put the hashes in README | see below |
| Disclaimer | README, app status bar | done |
| Every tweak has a working revert; Restore Defaults (mocks) | test_phase6_revert; gap → G6-1 DNS + launch options | see below |
| No licence / logo decisions, flag them | OWNER_STEPS B | done |
| Hosting recommendation | OWNER_STEPS B | done |

## Phase 7 — Build and hand-off

| Requirement | Covered by | State |
|---|---|---|
| All test suites | evidence_final_tests.txt | re-run after gap fixes (G7-1) |
| npm ci + npm run build in a clean clone | evidence_exe_smoke.txt | [TESTED] |
| Rebuild exe only if tests pass; smoke from a temp folder | evidence_exe_smoke.txt | re-do after gap fixes (G7-1) |
| New SHA-256; public/ and website badge match | owner rule: dist\ and public\ untouched | gap → G7-2 verify badge mechanism |
| Keep the pre-audit backup | gap → G7-3 verify it still exists | see below |
| Never push to main | nothing pushed | done |

## Gap results
(filled in below as each gap is closed)
