# PHASES 3-7 + DELIVERABLES (copied word for word from the owner's superprompt, lines 61-82)
# Rules A-I from the superprompt (lines 11-20) and the owner's chat rules still apply.

PHASE 3 - FUNCTIONAL CHECK, front end and back end
App: every page, dialog, button, tray item and tooltip (none missing, none misleading). Extend test_comprehensive_audit.py. Screenshots at 100/125/150% scaling if you can capture them. Check text cut-off and leftover light-theme widgets. Error states: Steam closed, Discord closed, no internet, port 3000 in use, CS2 not installed, Steam library on another drive. Startup, exit and tray with no ghost processes.
Website: build locally and test the LIVE site in a real browser (Playwright or the browser tool). Every nav item, button and link (no 404, correct target), tooltips, presence card states (connecting / standby / offline / in-server), server radar, search and filters, web sniper (no auto-launch), autoexec generator, Mako game, /connect inputs (valid, host only, port 0, 99999, script tag, javascript:, empty, unknown host), 404 fallback, console errors, broken images, widths 390 / 768 / 1440.
Backend: every endpoint: status codes, schema, error cases, cold start (502/503 must show Connecting then Standby, never Offline).

PHASE 4 - PERFORMANCE
App: cold start, idle CPU and RAM (measure the real child process), memory and thread growth over 10 minutes with auto-refresh on. Website: Lighthouse mobile on the live site, bundle size, console errors.

PHASE 5 - WORDING, ACCESSIBILITY, UX
Claims sweep: grep all UI text, tooltips, docs, comments, generated files, meta tags and exe metadata for 100%, guarantee, verified, VAC, safe, zero, never, always, instant, millisecond, perfect, maximum, official, fix. Remove or soften whatever you cannot prove with a test. Check contrast, keyboard use (Tab/Enter/Esc), reduced motion, flashing under 3 per second.

PHASE 6 - SHARE-READINESS
README: what it does, what it changes on your PC, how to undo each tweak, what data leaves the PC, SmartScreen note with the SHA-256. Disclaimer: not affiliated with Valve or any server community, use at your own risk. Check every tweak has a working revert and "Restore Defaults" (test with mocks). Do NOT pick a license or decide on third-party logos or names; flag them for the owner. Recommend a download hosting approach (GitHub Releases vs a 31 MB exe in git); propose only.

PHASE 7 - BUILD AND HAND-OFF
Run all test suites. Run "npm ci" and "npm run build" in a clean clone. Rebuild the exe ONLY if tests pass. Smoke-test the new exe from a temp folder BEFORE replacing the working one. Record the new SHA-256, make sure public/ matches and the website badge matches. Keep the pre-audit backup. Never push to main.

DELIVERABLES (folder audit/)
- AUDIT_REPORT.md: summary at the top (counts of Critical/High/Medium/Low, Fixed, Not fixed, Not tested; Top 10 risks). Then one table: ID | Area | Finding | Severity | Status (Fixed / Owner action / Not fixed) | Evidence label | File and line.
- OWNER_STEPS.md: exact steps only the owner can do (Render env vars, deploy order, GitHub Settings > Pages, merge, plus a hand-test list: every autoexec command in the CS2 console, phone test, 5-minute hidden-tab sniper test, Windows Sandbox fresh-PC test with SmartScreen, real server connect, Discord share card, 125%/150% visual check).
- AUDIT_PROGRESS.md.
Final chat message: 15 lines maximum: counts, top 5 risks, what was fixed, what needs the owner, file locations, new exe SHA-256.
# RULES (lines 11-20)
RULES (follow without asking)
A. Before changing anything: record the git commit, branch and SHA-256 of dist/CS2_Command_Center.exe and public/CS2_Command_Center.exe. Copy the WHOLE project (all folders) to backups/final-audit-<date>/ (outside dist/, git-ignored). Put a one-line rollback in the report.
B. Git: new branch final-audit from main. Add files by name only (never "git add ."). Never push to main, never merge, never deploy. Pushing the branch is OK. Commit after each phase.
C. Do NOT run on this PC: SFC, DISM, TRIM, registry writes, power-plan or DWM changes, MPO changes, deleting real maps, launching or killing CS2/Steam/Discord, steam:// launches. Test those features only with mocks, dummy folders or dry-run. Read-only checks are fine.
D. Only test assets the owner owns: local files, geronimohq.com, geronimohq-telemetry.onrender.com. Low-impact tests only: at most 30 requests to the backend, no load tests, no brute force. Third parties (Discord, Spotify, YouTube, zegraph.xyz, maps.cybo.dev, Steam, game servers): normal use only, and at most 3 read-only A2S queries per game server.
E. Never print secret values (mask them). Never commit secrets.
F. Do not trust earlier reports or code comments. Verify against the code. If this prompt contradicts the code, trust the code and say so.
G. Irreversible or owner-only actions (deploying the backend, setting Render env vars, rotating secrets, merging, publishing a release, code signing): prepare everything, write exact steps in audit/OWNER_STEPS.md, and do NOT do them.
H. Budget: owner usage is limited. Use grep, AST and automated tools; do not paste whole files repeatedly. After each phase update audit/AUDIT_PROGRESS.md (done / next / findings so far). If running low, skip the lowest-priority phases, list what was skipped, and still write the final report. Never stop silently.
I. Label EVERY result: [TESTED: output shown], [CODE REVIEW ONLY] or [NOT TESTED]. Never write "works", "safe", "verified" or "100%" without a [TESTED] label and its output. Never write results in past tense before the work is done.
