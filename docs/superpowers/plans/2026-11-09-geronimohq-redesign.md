# GeronimoHQ & CS2 Command Center Comprehensive Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Redesign both the GeronimoHQ web platform and the standalone CS2 Command Center desktop suite into a cohesive, military-grade "CyberDeck Command Console" with high-contrast tactical navigation, live server telemetry, and 100% theme/audio parity.

**Architecture:** The desktop application transitions from flat horizontal notebook tabs into a persistent Left Sidebar Rail (`190px`) + View Router + Bottom Status Bar architecture in `desktop-app/app.py`. The web platform (`CyberNavbar.tsx`, `ServerRadarPreview.tsx`, `BananaHeroStage.tsx`, `PepeHeroStage.tsx`) standardizes into a 2-tier container strictly aligned to `max-w-6xl mx-auto px-4` with active scroll spy, zero-overlap tactical server cards, and verified PyInstaller binary distribution.

**Tech Stack:** Python 3.14 / Tkinter / PyInstaller (Desktop), TypeScript / React 19 / Vite / Tailwind CSS (Web).

**Spec:** [`docs/superpowers/specs/2026-11-09-geronimohq-redesign-design.md`](file:///h:/GeronimoHQ/docs/superpowers/specs/2026-11-09-geronimohq-redesign-design.md)

## Global Constraints
- Preserve Pepe Theme (Cyan/Lime/Fuchsia neon) and Banana Phone Theme (Amber/Gold/Red neon) on the website.
- Preserve 3:16 symmetrical audio cycle and unified master volume slider.
- Zero competitor mentions in all copy and UI.
- Preserve 100% VAC safety across all CVARs and autoexec binds.
- Enforce the 5-tier typography scale across all desktop views.
- Ensure bit-for-bit SHA-256 match between `public/CS2_Command_Center.exe` and `dist/CS2_Command_Center.exe`.

## Review Focus
- **Sidebar view switching failure:** Switching between views must cleanly hide the prior view and show the active view without memory leaks or stale widget overlays.
- **Tkinter geometry layout glitch:** Main content container must smoothly resize with vertical scrollbar on lower resolution displays (1080p, 720p).
- **Map Cleaner safety invariants:** Inode and multi-pack protection rules for `730/csgo` and `730/content` must remain intact during UI restructuring.
- **Web responsive navbar overflow:** On screens from 360px to 2560px, navbar links must never truncate into `TRAN` or squish.
- **PyInstaller executable launch:** Compiled `.exe` must boot and run cleanly in `--test-mode` without missing runtime hooks or assets.

---

### Task 1: Desktop App Sidebar & View Router Architecture

**Files:**
- Create: `desktop-app/test_sidebar_architecture.py`
- Modify: `desktop-app/app.py`

**Interfaces:**
- Consumes: Existing module views in `desktop-app/app.py` (`create_autoexec_tab`, `create_tweaks_tab`, `create_server_tab`, `create_maintenance_tab`, `create_dns_tab`, etc.)
- Produces: `SidebarNav` component and `switch_view(view_id: str)` router in `CS2CommandCenterApp`.

- [x] **Step 1: Write test for sidebar navigation and view router**

Create `desktop-app/test_sidebar_architecture.py` checking that `CS2CommandCenterApp` initializes with a sidebar containing 8 tactical modules, a view router dictionary, and an active view property.

- [x] **Step 2: Run test to verify it fails**

Run: `cd desktop-app; python test_sidebar_architecture.py`  
Expected: FAIL (missing `sidebar_nav` / `switch_view`).

- [x] **Step 3: Implement SidebarNav & View Router in `desktop-app/app.py`**

Replace the top notebook tabs with:
1. Left Sidebar frame (`width=190`, background `#0A0D14`).
2. 8 Navigation buttons with cyber icons, bold Segoe UI typography, and active indicator bar.
3. Content viewport with dynamic view switching.
4. Persistent bottom status bar (`CS2 Process: DETECTED/RUNNING`, `Slot Sniper: IDLE/ACTIVE`, `Active DNS: 1.1.1.1`).

- [x] **Step 4: Run test to verify it passes**

Run: `cd desktop-app; python test_sidebar_architecture.py`  
Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add desktop-app/app.py desktop-app/test_sidebar_architecture.py
git commit -m "feat(desktop): implement tactical sidebar navigation rail and view router"
```

---

### Task 2: Desktop App Dashboard Overview View

**Files:**
- Modify: `desktop-app/app.py`
- Test: `desktop-app/test_sidebar_architecture.py`

**Interfaces:**
- Consumes: `hardware_info.py`, `core_logic.py`
- Produces: `create_dashboard_view()` returning the primary executive overview frame.

- [x] **Step 1: Write test for dashboard metrics and one-click optimization integration**

Add test in `desktop-app/test_sidebar_architecture.py` asserting `create_dashboard_view` renders hardware cards, CS2 status indicator, and quick optimization trigger.

- [x] **Step 2: Implement `create_dashboard_view()` in `desktop-app/app.py`**

Build the new `DASHBOARD` view containing:
- High-impact "SYSTEM READINESS & OPTIMIZATION" hero card.
- Live hardware telemetry panel (Balanced CPU & GPU specs).
- Quick launch & autoexec sync actions.
- Clean system activity log widget.

- [x] **Step 3: Run tests to verify all pass**

Run: `cd desktop-app; python test_sidebar_architecture.py`  
Expected: PASS.

- [x] **Step 4: Commit**

```bash
git add desktop-app/app.py desktop-app/test_sidebar_architecture.py
git commit -m "feat(desktop): add cyberdeck executive dashboard and telemetry view"
```

---

### Task 3: Desktop App Standalone Compilation & Hash Synchronization

**Files:**
- Modify: `public/CS2_Command_Center.exe`
- Modify: `dist/CS2_Command_Center.exe`
- Modify: `vite.config.ts`
- Modify: `src/components/CS2CommandCenterPreview.tsx`

**Interfaces:**
- Consumes: `desktop-app/CS2_Command_Center.spec`, `desktop-app/app.py`
- Produces: Freshly compiled Windows binary with verified SHA-256 hash.

- [x] **Step 1: Recompile `CS2_Command_Center.exe` using PyInstaller**

Run: `cd desktop-app; python -m PyInstaller CS2_Command_Center.spec --noconfirm`  
Expected: `desktop-app/dist/CS2_Command_Center.exe` generated.

- [x] **Step 2: Copy binary to `public/` and `dist/` and compute SHA-256**

Copy `desktop-app/dist/CS2_Command_Center.exe` to `public/CS2_Command_Center.exe` and `dist/CS2_Command_Center.exe`.  
Compute new SHA-256 hash.

- [x] **Step 3: Update hash in `vite.config.ts` and `CS2CommandCenterPreview.tsx`**

Ensure `vite.config.ts` build guard and web download badge reflect the new SHA-256.

- [x] **Step 4: Verify test mode execution**

Run: `& .\public\CS2_Command_Center.exe --test-mode`  
Expected: Clean exit code 0.

- [x] **Step 5: Commit**

```bash
git add public/CS2_Command_Center.exe dist/CS2_Command_Center.exe vite.config.ts src/components/CS2CommandCenterPreview.tsx
git commit -m "build(desktop): compile new cyberdeck command console standalone binary"
```

---

### Task 4: Web UI Polish & Zero-Overlap Tactical Server Radar

**Files:**
- Modify: `src/components/CyberNavbar.tsx`
- Modify: `src/components/ServerRadarPreview.tsx`
- Modify: `src/components/DeployHudFooter.tsx`

**Interfaces:**
- Consumes: Server telemetry API, Theme context
- Produces: Polished responsive web views aligned with the CyberDeck visual identity.

- [x] **Step 1: Verify CyberNavbar scroll spy and responsive layout**

Ensure 2-tier layout in `CyberNavbar.tsx` has active glowing accent, smooth anchor scroll, and zero truncation on mobile, tablet, and desktop.

- [x] **Step 2: Polish ServerRadarPreview tactical cards**

Ensure map thumbnail, timer, mapper pill (`👑 HoF`), and full-width `GEO RADAR` demographics bar render cleanly without collision.

- [x] **Step 3: Run web production build**

Run: `$env:PATH = 'C:\Program Files\nodejs;' + $env:PATH; & 'C:\Program Files\nodejs\npm.cmd' run build`  
Expected: Build passes in <1000ms with 0 errors.

- [x] **Step 4: Commit**

```bash
git add src/components/CyberNavbar.tsx src/components/ServerRadarPreview.tsx src/components/DeployHudFooter.tsx
git commit -m "feat(web): polish tactical cyberdeck UI and server radar responsiveness"
```

---

### Task 5: Full Regression Audit & GitHub Release

**Files:**
- Entire repository

**Interfaces:**
- Comprehensive test suite and verification commands.

- [x] **Step 1: Run all desktop app test suites**

Run: `cd desktop-app; python test_comprehensive_audit.py; python test_user_feedback_fixes.py; python test_website_feature_parity.py; python test_server_asset_protection.py`  
Expected: All tests PASS (`OK`).

- [x] **Step 2: Run website build guard**

Run: `npm run build`  
Expected: SHA-256 verified match, zero build errors.

- [x] **Step 3: Push to remote main**

Run: `git push origin main`  
Expected: Pushed cleanly.
