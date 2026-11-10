# Retro (CS 1.6 / VGUI) skin for CS2 Command Center — report

Branch `ui-retro-skin` (from `main` @ `60dfbec`). Desktop app only; the website keeps its own look.
Owner decisions applied: **app-only palette, accent stays the approved CS2 orange `#E48716`**,
one primary button per screen, no new features. Labels: [TESTED] = automated test, output in
`audit/evidence_retro_skin.txt`; [NOT TESTED] = needs eyes on the screen (OWNER_STEPS section H).

## 1. Stack and files

Tkinter (+ ttk `clam`), one 8,000-line `app.py`. Before: 764 hard-coded color literals (117 distinct) in
`app.py`, 21 in `hardware_info.py`, a `theme.py` with the old navy/orange palette, Segoe UI everywhere.

## 2. Theme

`desktop-app/theme.py` is the single source: surfaces (base / panel / raised / inset), bevels, text,
accent, status (+ `*_TEXT` variants), team colors, fonts (Verdana, Consolas), type scale
(8 / 9 / 10 / 11 / 14 pt = 11 / 12 / 13 / 15 / 18 px, in points so Windows DPI scaling still applies),
`lighten()` for hover, `apply_retro_ttk()` for every ttk widget and the combobox drop-downs.

Where I changed the brief's numbers (needed to meet its own 4.5:1 rule):
- **Accent** kept `#E48716` (approved) instead of `#D9772B`.
- **Darker, retro-futuristic pass (owner request):** surfaces are dark phosphor olive (base `#1C2119`, panel `#262D22`, raised `#2F3829`, inset `#12160F`); text is fitted to ≥ 4.5:1 on all four (text-primary `#D5DACF` 11.5 / 10.0 / 8.6 / 12.9:1); accent headings and the log use monospace (Consolas).
- Status hues are clearly distinct: good green `#6FCB57`, ct-blue `#66ACE9`, warn rust `#EB8E6D`, bad `#F18882`, secondary grey. Map Cleaner rows and filter tabs use the same four (subscribed = green, server asset = blue, temp = grey, duplicate = rust); the active tab is sunken.
- Tuned for 100 % Windows scaling (owner's setting); 125 % / 150 % not checked.
- A 4th surface "raised" `#4A5242` for rows; warn fill `#AC5733` (74 % saturation → 70 %); text on red/rust
  fills is white (`#D5DACF` gave 3.4–3.8:1).

## 3. Changes per file

| File | Change |
|---|---|
| `theme.py` | rewritten (above); old `COLOR_*` names kept as aliases of the new tokens |
| `app.py` | 764 literals → tokens; fonts → `theme.FONT_UI/FONT_MONO` + type scale; new retro classes `Button` (bevel, kinds primary / secondary / danger / good), `Frame` (1-px bevel panels), `Entry` (inset), `Checkbutton`, `Label` (accent only for bold ≥ 15 px headings; uppercase bold headings become accent); `add_accent_bar()` (3-px left bars); header badges, check chips, status panels with left borders, ZE humans (ct-blue) / zombies (t-gold), country chips, red/green dots, colored activity log, status bar, DNS selected-row bar, map-cleaner status colors, FAQ Q: markers, Settings text, one primary button per screen |
| `hardware_info.py` | badge colors → tokens (included one amber `#F59E0B`) |
| tests | `test_theme_contrast.py` (new), `test_retro_skin.py` (new), `retro_audit.py` (widget-tree audit); `test_banned_hues.py`, `test_token_parity.py`, `test_user_feedback_fixes.py`, `test_phase2_bugs.py` updated for the new palette/wording |

## 4. Verification

| Check | Result | Evidence |
|---|---|---|
| No color literals outside theme | **Pass** [TESTED] | 0 in app.py and every shipped module; exception: `make_cs2_badge.py` (stand-alone icon generator, not in the exe) |
| No yellow / neon / gradients / glows / shadows / rounded corners | **Pass** [TESTED] for colors on all 1,152 widgets (hue 48–70° banned; saturation cap on tokens). Tk has no gradients, glows, shadows or rounded corners. The app icon and map thumbnails are images and were not changed | test_no_yellow_or_neon_on_any_widget |
| Accent never small body text or status | **Pass** [TESTED] | 0 violations; accent only on bold ≥ 15 px headings (≥ 3:1: 6.07 base / 5.25 panel / 6.78 inset), the primary button, nav bar/icon, bars |
| OK / Enabled / Online green, none orange | **Pass** [CODE REVIEW + TEST] | `ACCENT_GREEN` is now good-text; offline dots red |
| ≤ 1 primary button per screen | **Pass** [TESTED] | Header (global): ONE-CLICK OPTIMIZE · Autoexec: Apply Engine Autoexec Tweaks · Launch Options: Copy Options · Live Booster: Apply CPU Priority Boost · ZE Servers: featured Connect · PC Maintenance: Run Selected PC Cleanup · dialogs: Save Server, Connect To Server, Save Settings. Dashboard, Engine, GPU MPO, Discord, FAQ: none. Delete Selected Maps is the only red fill |
| Contrast table, body text ≥ 4.5:1 | **Pass** [TESTED] | text-primary 11.52 / 9.97 / 8.59 / 12.86 (base / panel / raised / inset); every other text token ≥ 5.0; also on hovered panel/raised; labels on fills 4.90–6.96. Widget tree: 1,152 widgets, 0 under 4.5:1. Exceptions: disabled text (exempt) |
| Both popups match the main chrome | **Pass** [TESTED] | the 5 dialogs (Settings, Add Server, Players, Soundtrack, Map Cleaner) are in the same audit and use the same classes |
| Settings text / minimize checkbox no longer clipped | **Wording, smaller font and left alignment [TESTED in code]**; visual [NOT TESTED] | OWNER_STEPS H |
| App launches, every page renders, no Tk errors | **Pass** [TESTED] | all 10 pages + 5 dialogs; 25/25 desktop test files pass |

## 5. Not done, or only approximated — with proposed fix

| Item | Why | Proposed fix |
|---|---|---|
| Exact bevel colors (`bevel-light/dark`) | Tk shades the 3-D edges itself from the fill color | custom canvas-drawn buttons (large change); current look is the Windows-classic bevel in olive |
| Dotted 1-px keyboard focus outline | Tk only draws a solid focus ring | solid 1-px text-primary ring is used |
| Monochrome icons | icons are color emoji (Segoe UI Emoji) | replace by drawn monochrome glyphs with Pillow (needs an icon set) |
| Letter-spacing on headings | Tk has none | skip |
| Check mark in `good` color on checkboxes | `tk.Checkbutton` draws the tick in the label color | switch the 22 checkboxes to custom `ttk` indicators |
| Selected-row accent bar in tables / tabs (Map Cleaner) | `Treeview` and `ttk` tabs cannot draw a side bar | selection uses the lighter raised surface; a custom list widget would allow the bar |
| Map Cleaner status color per **column** | `Treeview` colors whole rows | rows are colored by status instead |
| Disabled controls "no bevel" | Tk keeps the relief when disabled | recolor only (text-disabled) |
| "Active flags" list, disk > 85 % warning | new features; brief forbids them | skipped as agreed |
| Dead space on Launch Options / Discord | layout-only, needs eyes on the screen | after your visual check |
| MPO page warn blocks, "What this does" ct-blue border, Engine "Enabled" icon | not individually restyled | after your visual check, list what looks off |
| Header "Standard Permissions" etc. | done as inset badges with a status dot | — |
