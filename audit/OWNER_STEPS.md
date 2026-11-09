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

## B. Decisions for you

| ID | Question | My suggestion |
|---|---|---|
| D-07 | "Start with Windows" makes a Scheduled Task that starts the app **as Administrator** at every logon (`/rl highest`). Keep it? | Use a normal (non-admin) start; ask for admin only when a feature needs it. |
| B-11 | `/api/servers` re-publishes every player name from the game servers. Keep it? | Only send counts, plus a yes/no "owner is here". |
| W-05 | Pin GitHub Actions to commit SHAs instead of `@v4`? | Yes (small extra safety). |
| P2-D1 | The website geo radar shows country % from a **model** (time-of-day curve + guesses from player names), not measurements. Only the GFL continent split is real (ZEGraph). Keep? | Show the measured continent split (GFL) labelled "estimate, N of M players", and for other servers "no measured data" — same as the app now. |

## C. CSP for the website (optional, test first)

GitHub Pages cannot send security headers, but a `<meta>` tag works for most of CSP.
I did not add it because I could not test it here. To try it, add this inside `<head>`
of `index.html`, then follow `RUN_ON_PC.md` step 6:

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://geronimohq-telemetry.onrender.com https://zegraph.xyz; media-src 'self' https: blob:; frame-src steam:; object-src 'none'; base-uri 'self'; form-action 'self'">
```
Note: `npm run dev` may break with this tag (the dev server uses inline scripts). Test with
`npm run build` + `npm run preview`.

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
