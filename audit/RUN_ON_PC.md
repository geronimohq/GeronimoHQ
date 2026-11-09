# Commands to run on your PC

Why this file exists: in this session I could read and write files in `H:\GeronimoHQ`,
but I had **no command line on your PC**. So I could not run `git`, `npm`, `pip`,
Windows-only tests, or builds there. Run these in **PowerShell**, in order.
Nothing here deploys, merges, or pushes to `main`.

## 1. Check you are on the audit branch

```powershell
cd H:\GeronimoHQ
git switch final-audit
git status --short
```
You should see only the files listed in step 3 as changed (`M`) or new (`??`).

## 2. Run the new tests (Windows)

```powershell
python backend\test_api_security.py
python desktop-app\test_security_phase1c.py
python desktop-app\test_updater.py
python desktop-app\test_map_protection_dummy.py
Get-ChildItem desktop-app\test_*.py | ForEach-Object { Write-Host "== $($_.Name)"; python $_.FullName }
```
Expected: each file ends with `OK`. If one fails, copy the last 20 lines into the next chat.
(`backend\test_api_security.py` uses the real FastAPI if installed: `pip install -r backend\requirements.txt`.)

## 3. Commit (files added by name, never `git add .`)

```powershell
git add backend/api.py backend/.python-version backend/test_api_security.py src/components/GeronimoDiscordPresence.tsx src/utils/serverQuery.ts
git commit -m "audit(phase1b-recheck): use refresh lock, TLS on, 404 + cache for detail, block name impersonation, show Standby for unknown"

git add desktop-app/app.py desktop-app/app_config.py desktop-app/cs2_gsi.py desktop-app/custom_map_cleaner.py desktop-app/server_browser.py desktop-app/test_security_phase1c.py
git commit -m "audit(phase1c): owner-only heartbeat, host:port validation, safe URL opener, map cleaner path guard, GSI limits, atomic config save"

git add src/App.tsx src/components/ServerRadarPreview.tsx scripts/fetch_live_servers.py .github/workflows/deploy.yml
git commit -m "audit(phase1d): route ?ip= through /connect, rel noopener, TLS on in CI script, least-privilege workflow"

git add audit/AUDIT_PROGRESS.md audit/FINDINGS_PHASE1.md audit/RUN_ON_PC.md audit/OWNER_STEPS.md audit/evidence_phase1_tests.txt
git commit -m "audit: phase 1 findings, progress, owner steps"
```
Optional: `git push -u origin final-audit` (pushing this branch is OK; never push `main`).

## 4. Website checks (needs internet for npm)

```powershell
npm ci
npx tsc -b
npm run build
npm audit --omit=dev
npm audit
Get-ChildItem dist -Recurse -Filter *.map | Measure-Object   # expect Count 0 (no source maps)
```
Apply only safe fixes: `npm audit fix` (never `--force`). Note any "major" ones for the report.

## 5. Backend dependency check (needs internet)

```powershell
pip install pip-audit
pip-audit -r backend\requirements.txt
```

## 6. Optional: try the proposed CSP locally (do NOT commit unless it works)

See "CSP" in `audit/OWNER_STEPS.md`. Add the meta tag, run `npm run build` then `npm run preview`,
open http://localhost:4173 and check the browser console has no "Content Security Policy" errors.
