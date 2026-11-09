# Design Document: GeronimoHQ Web & CS2 Command Center Comprehensive Redesign

**Date:** 2026-11-09  
**Author:** Antigravity Engineering Suite & Geronimo  
**Status:** PROPOSED (Pending Review & Plan)  
**Target:** [`geronimohq.com`](https://geronimohq.com) & Standalone Desktop Suite (`CS2_Command_Center.exe`)

---

## 1. Intent & The "Why"
GeronimoHQ is the premier personal cyber-hub for Counter-Strike 2 Zombie Escape enthusiasts, retro-futuristic meme culture, and high-performance gaming utilities.

The goal of this redesign is to elevate both the **Web Platform** and the **Desktop Application** into a unified, visually breathtaking **"CyberDeck Command OS"**:
- **Website:** Preserve the beloved **Pepe Holo-Chamber** and **Banana Phone Hotline** themes, 3:16 symmetrical audio cycle, and authentic retro cyberpunk flavor, while refining the UI into an immaculate, zero-friction experience with glowing scroll spy navigation, zero-overlap tactical server radar cards, and razor-sharp responsive layouts.
- **Desktop Application:** Complete freedom redesign. Transform the desktop companion from a traditional multi-tab window into an elite **Tactical Left-Sidebar CyberDeck Console** featuring a unified dashboard, live telemetry rail, automated slot sniper status, VAC-safe autoexec studio, gaming DNS benchmark, and multi-server safe custom map cleaner.

---

## 2. Goals, Non-Goals & Anti-Goals

### Goals
- **Website:**
  - Maintain 100% theme fidelity: Pepe Theme (Cyan/Lime/Fuchsia neon) and Banana Phone Theme (Amber/Gold/Red neon).
  - Perfect responsive visual balance from mobile (`360px`) to ultra-wide desktop (`2560px`).
  - Active scroll spy on the CyberNavbar with live illuminated section indicators.
  - Zero-overlap tactical server cards with enlarged thumbnails, real-time ticking map elapsed timers, and clear mapper attributions.
  - Smooth 3:16 audio/theme switching with persistent master volume and mute controls.
- **Desktop Application:**
  - Modernize layout from flat horizontal tabs to a **Left Icon Rail / Sidebar Navigation** with smooth view switching.
  - Enforce the 5-tier typography scale across all screens and modals.
  - Uniform button heights (32–34px) with crisp tactile cyber hover states.
  - Real-time persistent bottom status bar (CS2 Process detection, Slot Sniper status, Active DNS, Hardware profile).
  - Standalone single-file PyInstaller distribution with identical bit-for-bit SHA-256 hash across `public/` and `dist/`.

### Non-Goals
- Do not remove or alter the satirical core: "Download More RAM" and the 120-anomaly Chaos Engine remain intact.
- Do not introduce server-side database requirements for user accounts; keep the site and desktop app 100% client-side, portable, and zero-install.

### Anti-Goals
- **No generic flat templates:** Never look like a generic corporate SaaS dashboard; it must maintain genuine cyberpunk grit, CRT glow, and high-energy gamer identity.
- **No competitor mentions:** Strict policy against referencing competing tools or third-party launchers.
- **No breaking changes:** Never break existing Steam Game Server connect protocols, CS2 console binds, or map cleaner file safety guarantees.

---

## 3. Approaches Considered

### Approach A: "CyberDeck Command Console" (SELECTED & RECOMMENDED)
- **Concept:** Tactical military-grade cyber terminal inspired by Source 2 developer HUDs and cyberpunk deck operating systems.
- **Desktop UI:** Left-hand vertical navigation rail with high-tech glowing icons; content area displays modular cards with neon borders; bottom telemetry bar tracks CS2 process and sniper loop.
- **Web UI:** Floating dual-tier CyberNavbar with active scroll spy, multi-layered holo-pedestals for Pepe/Banana, and satellite radar server cards.
- **Trade-off:** Requires reorganizing the desktop application container into a sidebar + content frame architecture, but delivers unmatched visual hierarchy, thumb/mouse ergonomics, and futuristic aesthetics.

### Approach B: "Modern Sleek Esports Suite"
- **Concept:** Clean minimalist dark-mode software similar to modern peripheral suites (SteelSeries GG, NZXT CAM).
- **Trade-off:** High readability and simple cards, but loses the gritty retro cyberpunk soul that makes GeronimoHQ unique.

### Approach C: "Retro 90s Cyber Arcade Station"
- **Concept:** Heavy 90s SGI / Amiga terminal with intense CRT scanlines and pixelated fonts.
- **Trade-off:** Fun retro novelty, but hurts long-term readability when inspecting detailed autoexec configs or dense server player rosters.

---

## 4. Detailed Specification: Web Platform

### 4.1 Navigation Architecture (`CyberNavbar.tsx`)
- **Container:** Strictly aligned to `max-w-6xl mx-auto px-4`.
- **Top Row:** Brand insignia (`GERONIMOHQ // ONLINE`) on left; 7 Nav links on right (`HOLO-DECK`, `DOWNLOAD RAM`, `ZE SERVERS`, `ZE TOOLKIT`, `CFG STUDIO`, `CS2 APP`, `TRANSMISSION`).
- **Sub-HUD Row:** Current Theme badge (Read-only status), Interactive Roamer Toggle button, Real-time Clock, and Simulated low-latency Ping badge.
- **Scroll Spy:** Live listener detects active section offset and highlights current nav link with glowing accent backdrop (`drop-shadow-[0_0_10px_rgba(0,240,255,0.3)]`).

### 4.2 Hero Stage (`PepeHeroStage.tsx` & `BananaHeroStage.tsx`)
- **Pepe Stage:** 3D perspective pedestal with dual spinning dashed neon rings, specimen display tabs (`ALL`, `CRY`, `LAUGH`, `DANCE`), and synthesized chiptune audio.
- **Banana Stage:** Golden potassium chamber with dual pom-pom cheerleader animations, Commander Peel lore card, bundled HTML5 video player, and safe confetti cannon on clicks.
- **Symmetrical 3:16 Lifecycle:** Seamless cross-fade transition every 196 seconds or on manual toggle.

### 4.3 Tactical ZE Server Radar (`ServerRadarPreview.tsx`)
- **Card Hierarchy:**
  - Row 1: Country badge, Server Name, Tickrate (128T), Cluster name, Discord/Portal links.
  - Row 2: Enlarged map thumbnail (`w-32 sm:w-40`), Map name with Tier badge (`T1` Warmup to `T6` Hell), Live Map Elapsed Timer (`⏱️ 14:10 on map`), 3D Cybo map link, Dedicated Mapper attribution pill with `👑 HoF` badge, Live Player Count, Regional Ping estimate.
  - Row 3: **`GEO RADAR`** Demographics bar spanning 100% width on its own dedicated row (zero collision).
  - Row 4: 1-Click Steam Connect CTA, Auto Join slot watcher toggle, Live Player Roster modal button, Copy Console Command button.

---

## 5. Detailed Specification: Desktop Application (`desktop-app/app.py`)

### 5.1 Main Layout Frame Structure
```
+---------------------------------------------------------------------------------------------------+
|  [G] GERONIMOHQ CS2 COMMAND CENTER   [v1.4.0]               [ _ ]  [ X ]  (Custom Cyber Title Bar) |
+---------------------------------------------------------------------------------------------------+
|  PROCESSOR: AMD Ryzen 7 5700X3D (8C/16T)  |  GRAPHICS: AMD Radeon RX 6600 (8GB)  | [ONE-CLICK OPT] |
+-----------+---------------------------------------------------------------------------------------+
|  SIDEBAR  |  MAIN CONTENT VIEWPORT                                                                |
|  [⚡ DASH] |                                                                                       |
|  [🎯 SRV]  |  Active Section Content (e.g. ZE Server Browser, Autoexec Studio, DNS Optimizer)     |
|  [⚙️ ENG]  |  - High-contrast 5-tier typography                                                   |
|  [📝 CFG]  |  - Standardized 32-34px rounded action buttons                                        |
|  [🚀 LNK]  |  - Smooth vertical scrolling with dark scrollbars                                     |
|  [🌐 DNS]  |                                                                                       |
|  [🧹 MAP]  |                                                                                       |
|  [💬 RPC]  |                                                                                       |
+-----------+---------------------------------------------------------------------------------------+
|  STATUS: CS2 Process: ACTIVE (pid 14220) | Slot Sniper: IDLE | DNS: 1.1.1.1 (9ms) | Safe Mode: ON  |
+---------------------------------------------------------------------------------------------------+
```

### 5.2 Tactical Sidebar Components
- **Width:** `190px` fixed, styled with `#0A0D14`, subtle right border `#1E293B`.
- **Navigation Buttons:**
  - 8 Dedicated Tactical Modules:
    1. `DASHBOARD` — Quick overview, 1-click optimization, hardware benchmark.
    2. `ZE SERVERS` — Live game server browser, slot sniper, map elapsed timers.
    3. `ENGINE TWEAKS` — Source 2 engine performance, thread affinity, FPS stabilizer.
    4. `AUTOEXEC & BINDS` — ZE laser binds, low viewmodel, manual CFG editor.
    5. `LAUNCH OPTIONS` — Steam launch option helper with auto-apply.
    6. `DNS OPTIMIZER` — Real-time latency benchmark & 1-click adapter switcher.
    7. `MAP CLEANER` — Multi-server pack safe disk recovery tool.
    8. `DISCORD RPC` — Rich presence controls & server auto-broadcasting.
  - Active button highlights with cyan/lime neon border and glowing indicator bar.

### 5.3 Standardization & Visual Polish
- **Color Palette:**
  - Background: `#070A10` (Dark Void)
  - Card Surfaces: `#0F172A` (Slate Dark) / `#0A0F1D` (Deep Navy)
  - Primary Accent: `#00F0FF` (Cyber Ice Cyan)
  - Secondary Accent: `#39FF14` (Toxic Lime)
  - Warning Accent: `#F59E0B` (Amber Gold)
  - Danger Accent: `#EF4444` (Laser Red)
  - Text Primary: `#FFFFFF`
  - Text Secondary: `#94A3B8`
- **Typography Scale:**
  - Tier 1 (Titles): `16px Bold Uppercase #FFFFFF`
  - Tier 2 (Headers): `13px Bold Uppercase Light Slate/Cyan`
  - Tier 3 (Row Labels / Server Names): `14px Semi-Bold #FFFFFF`
  - Tier 4 (Body / Descriptions): `12px Regular #94A3B8`
  - Tier 5 (Badges / Tags): `11px Semi-Bold Uppercase`
- **Buttons:**
  - Standard Action Buttons: `font=("Segoe UI", -12, "bold")`, height `32px–34px`.
  - Global CTA ("One-Click Optimize"): `14px Bold`.

---

## 6. Execution Plan & Validation Steps
1. **Desktop App Architecture Transition:**
   - Implement the `SidebarNav` and modular `ViewContainer` in `desktop-app/app.py`.
   - Preserve 100% of the underlying business logic (`server_browser.py`, `core_logic.py`, `custom_map_cleaner.py`, `discord_rpc.py`, `cs2_gsi.py`).
2. **Web UI Visual Elevation:**
   - Enhance CyberNavbar, Hero Stages, and Server Radar styles.
   - Verify zero console errors, zero build warnings, and flawless mobile responsiveness.
3. **Automated Verification:**
   - Run desktop test suites (`test_comprehensive_audit.py`, `test_user_feedback_fixes.py`, etc.).
   - Recompile `CS2_Command_Center.exe` with PyInstaller.
   - Verify SHA-256 parity in `vite.config.ts`.
   - Run production web build (`npm run build`).
4. **Git Commit & Release:**
   - Stage, commit, and push clean release to GitHub `main`.
