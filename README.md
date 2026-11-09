# GeronimoHQ

Source for **geronimohq.com** (React + Vite website) and **CS2 Command Center** (a Windows desktop
app for Counter-Strike 2 Zombie Escape players), plus a small backend that relays server status.

> **Hobby project. Not affiliated with Valve, Steam, Discord, or any server community (GFL,
> Mapeadores, EXG, …). Use at your own risk.** The app uses config files and standard Windows
> settings. It does not read or modify CS2 memory, inject DLLs, or patch game files.

## Folders

| Folder | What it is |
|---|---|
| `src/`, `public/`, `index.html` | The website (React + TypeScript + Vite) |
| `desktop-app/` | CS2 Command Center (Python, Tkinter); `python app.py` to run from source |
| `backend/` | FastAPI relay on Render: `/api/servers` (server status + shared player totals) and the owner's presence card |
| `scripts/` | CI and maintenance scripts (e.g. `fetch_live_servers.py`, `build_map_mappers.py`) |
| `audit/` | Audit reports, evidence and owner steps |

## What CS2 Command Center changes on your PC, and how to undo it

Nothing below happens on its own: each item is a button or a tick you choose (except the GSI file,
see the last row of the first table).

| Change | Where | How to undo |
|---|---|---|
| Performance block in `autoexec.cfg` (fps_max, rate, audio buffer, HUD graphs) | `…\game\csgo\cfg\autoexec.cfg`, marked block; your first file is kept as `autoexec_backup.cfg` | **Restore Defaults** (puts back `autoexec_backup.cfg`), or delete the block. CS2 remembers some values: the block header lists the console commands to type. |
| ZE Studio block (viewmodel, HUD colour, F7/F8 audio toggles) | same file, marked block | Delete the block; its header lists `unbind …` and the values to type in the console. |
| Manual edits in the in-app editor | same file; a copy is saved as `autoexec.cfg.manual_bak` | Rename the `.manual_bak` file back. |
| Game DVR / background capture off | `HKCU\System\GameConfigStore`, `HKCU\…\GameDVR` | **Restore Defaults** sets the Windows default values (not necessarily the values you had before). |
| "Fullscreen optimizations" flag for `cs2.exe` | `HKCU\…\AppCompatFlags\Layers` | **Restore Defaults** deletes the value. Note: if you had other compatibility flags on `cs2.exe`, applying this replaces them. |
| Power plan (High performance) | Windows power settings | **Restore Defaults** switches back to the plan you had before the app changed it (Balanced if none was recorded). |
| DNS servers of your network adapter (needs Administrator) | Windows network settings (`netsh`) | **Restore ISP Default (DHCP)** button. If you used a custom DNS before, write it down first; the button restores *automatic* DNS. |
| Steam launch options for CS2 | Steam `localconfig.vdf` (Steam must be closed); original kept as `localconfig.vdf.backup` | Edit the launch options in Steam, or copy the `.backup` file back while Steam is closed. |
| CS2 process priority (High) while it runs | Windows process priority | Resets when CS2 closes. |
| "Start with Windows" | `HKCU\…\Run` (starts as a normal user; an elevated task `CS2CommandCenter_AutoStart` from older versions is removed) | Untick it in Settings. |
| Game State Integration file (written automatically when CS2 is found) | `…\game\csgo\cfg\gamestate_integration_cs2commandcenter.cfg` | Delete the file. CS2 then stops sending game state to `127.0.0.1:3000`. |

**Cannot be undone (the app asks first):** PC Maintenance clean-up (temp files, Windows Update
download cache, Discord/Steam web caches, thumbnail cache, Recycle Bin) and the Custom Map cleaner.
Windows and the apps rebuild their caches; deleted downloaded maps are downloaded again by CS2.

App files: `%APPDATA%\CS2CommandCenter\` (settings `command_center_config.json`, your custom
servers, map thumbnails). Delete the folder to reset the app.

## What data leaves your PC

| When | To | What |
|---|---|---|
| App start (Settings → "Check for updates", on by default) | `geronimohq.com/update/latest.json` | A normal HTTPS request; the app version is in the User-Agent. Updates install only after you click. |
| ZE Game Servers page | each game server (UDP, Steam query protocol) | A standard server query; the server sees your IP, as with the in-game browser. |
| Dashboard / ZE Game Servers totals | `geronimohq-telemetry.onrender.com/api/servers` | A plain GET (no user data); cached 60 s. |
| GFL details, geo estimate, map pictures | `zegraph.xyz` | Plain GETs (no user data). |
| DNS benchmark (button) | the listed DNS providers | DNS look-ups of a fixed name. |
| Discord Rich Presence (on by default, can be turned off) | the **Discord app on your PC** (local pipe) | Server name, map and player count while CS2 runs; Discord shows it to your friends. |
| Owner's presence card | the backend | **Only** on the owner's PC (needs a secret token in the config). Other installs send nothing. |

The website itself loads data from the same backend and zegraph.xyz, and fonts from Google Fonts.
It uses no analytics and no cookies; `localStorage` keeps only volume/mute.

## Windows SmartScreen

The exe is not code-signed, so Windows may show "Windows protected your PC" on first launch.
Check the file before running it: in PowerShell, `Get-FileHash .\CS2_Command_Center.exe -Algorithm SHA256`
must match the SHA-256 shown on geronimohq.com (the app's Settings → About → "Copy SHA-256"
gives the same value). Then choose "More info" → "Run anyway".

## Building

Website: `npm ci`, `npm run build` (output in `dist/`; a Content-Security-Policy tag is added to
production builds). Tests: see `audit/RUN_ON_PC.md`.

Desktop app: `pip install -r desktop-app/requirements.txt` (Pillow, cryptography, pystray,
PyInstaller), then PyInstaller with `desktop-app/CS2_Command_Center.spec`. Every Python test file is `python desktop-app/test_*.py`;
the tests use a temporary settings file and never write the registry.

Backend: `pip install -r backend/requirements.txt`; set `GERONIMO_PRESENCE_TOKEN` on the server.
