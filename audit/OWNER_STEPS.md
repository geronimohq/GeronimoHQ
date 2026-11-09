# Owner steps (only you can do these)

I prepared everything but did **not** do any of these. This file will grow in later phases.

## A. Lock down your presence card (do this first — fixes L-01, the Critical one)

Today the live backend lets anyone change your presence card. The fix is in the code,
but it only works after you add a secret token and deploy.

1. **Make a token** (PowerShell; it goes straight to your clipboard and is not shown):
   ```powershell
   $b = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b)
   ($b | ForEach-Object { $_.ToString("x2") }) -join "" | Set-Clipboard
   ```
2. **Put it in YOUR app only.** Close CS2 Command Center (also from the tray). Open
   `%APPDATA%\CS2CommandCenter\command_center_config.json` in Notepad and add one line
   inside the `{ }`:  `"presence_secret": "<paste>",`  Save. Never share this file.
3. **Render → your service → Environment**: add
   - `GERONIMO_PRESENCE_TOKEN` = the same token (paste)
   - `PYTHON_VERSION` = `3.11.9`
   Do not add `ENABLE_API_DOCS` (keeps /docs hidden).
4. **Deploy the backend** from the `final-audit` code (after you are happy with the review;
   usually that means merging to `main` first — your call).
5. **Check** (3 requests):
   - `https://geronimohq-telemetry.onrender.com/docs` → should be 404.
   - `https://geronimohq-telemetry.onrender.com/api/presence/heartbeat` → should be 401.
   - Open your app, wait 10 s, open geronimohq.com → your card should update.

Other people's copies of the app send nothing to your backend after the next exe release
(D-05). Old copies already out there get "401" from the new backend, so they can no longer
change your card.

## Status (2026-11-10, owner)

- **A** done by the owner (backend deployed with the token).
- **B** decided: D-07 normal-user startup (done), W-05 pinned Actions (done), B-11 keep player lists,
  P2-D1 app geo radar uses the website's method (done), P6-10 GitHub Releases recommended (owner's
  call during F), P9-01 / P6-08 licence and third-party content: still the owner's call.
- **C** nothing to do.
- **D, E, G** skipped by the owner: problems will be reported by the owner and friends.
- **Next: F** (release). The exe must be rebuilt first: code changed after the last build.

## B. Decisions for you

| ID | Question | My suggestion |
|---|---|---|
| D-07 | "Start with Windows" makes a Scheduled Task that starts the app **as Administrator** at every logon (`/rl highest`). Keep it? | Use a normal (non-admin) start; ask for admin only when a feature needs it. |
| B-11 | `/api/servers` re-publishes every player name from the game servers. Keep it? | Only send counts, plus a yes/no "owner is here". |
| W-05 | Pin GitHub Actions to commit SHAs instead of `@v4`? | Yes (small extra safety). |
| P9-01 | Third-party content: Pepe artwork, the "Banana Phone" song/video in `public/media`, Valve/CS2/Steam and Discord names, community server names/logos (GFL, Mapeadores, EXG, FyS, ...). I did not check rights. | Decide what to keep before sharing widely; for the song, use a licensed or original track. |
| P6-08 | Licence: the repo has none (all rights reserved by default). I do not pick one. | Choose one (or "all rights reserved") and add `LICENSE`. |
| P6-10 | Download hosting: the 37 MB exe is committed in git (`public/`), so every release grows the repo by about 37 MB for good. | **Recommend GitHub Releases** for the exe (the website links to the release asset; `latest.json` points to it). Proposal only. |
| P6-03 | The fullscreen-optimizations tweak replaces any other compatibility flags you had on cs2.exe. | Fine for most users (documented in README); or change it to append the flag. |
| P2-D1 | The website geo radar shows country % from a **model** (time-of-day curve + guesses from player names), not measurements. Only the GFL continent split is real (ZEGraph). Keep? | Show the measured continent split (GFL) labelled "estimate, N of M players", and for other servers "no measured data" — same as the app now. |

## C. CSP for the website — done

No action needed. The Content-Security-Policy is now added to production builds by `vite.config.ts`
(`cspMetaPlugin`). Tested on a production build: 0 violations on load, 40 Chaos effects and a full
scroll. If you add a new external site (fonts, APIs, embeds), add it to the `CSP` list there.

## D. Hand tests (added so far)

Phase 2 (normal app use, CS2 can stay closed unless noted):
- Settings: tick/untick "Check for updates when the app starts" → Save → you see "Settings saved." →
  close the app (also from the tray) → reopen → Settings shows the same tick.
- Autoexec & Binds → Edit Config → change a line → Save → Dashboard says "last saved in this app at …"
  without restarting. Then edit autoexec.cfg in Notepad, click back into the app → "no section written by this app".
- Dashboard ZE card and ZE Game Servers pills show the **same** numbers. After the backend deploy (A),
  "(bots unknown)" disappears.
- Discord tab, CS2 closed: first open shows "Checking…" then "Standby"; never "Online | In Main Menu".
- Arm Slot Sniper on any server, minimize to tray, reopen: status bar says "ARMED — <server>".
- Website: click TRANSMISSION once (wait for the page theme to be Pepe, then Banana): it lights up at once.

- After step A: close the app → the website card should go to Offline/Standby within ~25 s.
- On a second PC or Windows Sandbox **without** your config: run the app for 1 minute →
  your card must not change.

## E. In-game checklist (Phase 2 bug #9) — I could not run CS2

Every command below is **[NOT TESTED in game]**. Do this once, on a normal (not Premier) session:
1. In the app: Autoexec & Binds → apply Engine Tweaks, then the ZE Studio block. Open autoexec.cfg:
   each block starts with "UNDO:" lines and ends with an END line; `host_writeconfig` is gone.
2. Start CS2, open the console: `exec autoexec` → no "Unknown command" lines for our cvars.
3. Press F7 twice → console shows "[ZE-FOCUS] … ON (22%)" then "… Restored (100%)". Press F8 → voice toggles.
4. Check `viewmodel_fov`, `cl_hud_color`, `fps_max` with the console (type the name, Enter).
5. Undo test: delete both blocks, restart CS2, type the UNDO commands from the header, restart again →
   F7/F8 do nothing, values are back. Note any default that was wrong (the headers say "check your own").
6. Website Config Studio: download a file, check the "HOW TO UNDO" part is at the top and each setting
   appears once.
Tell me the results; I will mark them [TESTED in game].

## F. Release the audited app (order matters)

The new exe is **not** released. It is in `scratch\dist\CS2_Command_Center.exe`
(SHA-256 `78A91320400E43D17583952BFAA2C620E9744A0BB6197EDF8EF3744D4F8254FD`, 37,047,960 bytes,
built from a clean clone of `final-audit` at `85a0bbf`, smoke-tested from a temp folder).
Per your rule I did not touch `dist\CS2_Command_Center.exe` or `public\`.

1. **Bump the version first** (the updater only offers a *newer* version; this build still says 1.5.0):
   set `APP_VERSION = "1.5.1"` and `BUILD_DATE` in `desktop-app/version.py`, update the website
   references, then run `python desktop-app\test_version_consistency.py` until it passes.
2. Run all tests (the command list is in `audit/evidence_final_tests.txt`; every line must end in OK).
3. Rebuild into scratch, never over the working exe:
   `cd desktop-app` then
   `python -m PyInstaller --noconfirm --clean --distpath ..\scratch\dist --workpath ..\scratch\build_exe CS2_Command_Center.spec`
4. Smoke test: copy the exe to an empty temp folder, run it, open each page, exit from the tray,
   check Task Manager shows no `CS2_Command_Center.exe` left.
5. Only then copy it to `dist\` and `public\` (the old one stays in `backups\final-audit-2026-11-10\dist\`).
6. Sign the manifest with your key (kept outside the repo): `python tools\make_update_manifest.py`
   writes `public\update\latest.json`. Then `python desktop-app\test_updater.py` must pass.
7. `npm ci` and `npm run build`: the website's SHA-256 badge is computed from
   `public\CS2_Command_Center.exe` at build time; check it shows the new hash.
8. Merge `final-audit` into `main` (your decision), push, and let GitHub Actions deploy Pages.
9. Deploy the backend (section A) before or together with the site, so the presence card and the new
   `totals` field work. Render, Environment: `GERONIMO_PRESENCE_TOKEN`, `PYTHON_VERSION=3.11.9`.
10. GitHub, Settings, Pages: Source = GitHub Actions; custom domain `geronimohq.com`; Enforce HTTPS on.

## G. More hand tests (from the audit brief)

- **Every autoexec command in the CS2 console**: section E.
- **Phone test**: open geronimohq.com on your phone (portrait): no sideways scrolling, the menu opens
  and closes, TRANSMISSION lights up on the first tap.
- **5-minute hidden-tab sniper test**: on the website arm "Auto Join" on a full server, switch to another
  tab for 5 minutes: it must **not** launch Steam by itself; when you come back it shows the state.
- **Windows Sandbox fresh-PC test**: copy the new exe into Windows Sandbox and run it: SmartScreen appears
  ("More info", "Run anyway"); compare `Get-FileHash` with the SHA-256 above; your website card must
  **not** change while it runs (no token in that install).
- **Real server connect**: connect to GFL from the app and from the website `/connect` page.
- **Discord share card**: with CS2 running and Discord open, the Discord tab preview must match what your
  friends see; untick "Share ... with Discord" in Settings and the activity disappears.
- **125 % / 150 % scaling**: set Windows Display scale to 125 % and 150 %: no cut-off text in Settings,
  the Dashboard cards and the ZE Game Servers table.
- **Keyboard on the website**: press Tab once on a fresh page: "Skip to content" appears top-left.
- **Cold start**: when Render is asleep, the presence card shows "Connecting..." then "Standby", never "Offline".
- **Leave the app running for a day**: Task Manager, Details, add the "Handles" column; it should stay
  roughly flat (a leak of about 60 per minute was fixed).
