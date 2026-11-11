"""
Hardware and Steam Launch Options Detection for CS2 Optimizer
Detects CPU architecture (including Ryzen X3D), GPU, MPO status, and Steam configuration.
"""

import os
import sys
import glob
import re
import winreg
import platform
import subprocess
import theme
from typing import Dict, Any, Optional, Tuple

def get_cpu_info() -> Dict[str, Any]:
    cpu_name = ""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as k:
            cpu_name = str(winreg.QueryValueEx(k, "ProcessorNameString")[0]).strip()
    except Exception:
        cpu_name = platform.processor() or "Unknown CPU"

    cores = os.cpu_count() or 0
    is_x3d = bool(re.search(r"x3d\b", cpu_name, re.IGNORECASE))
    is_laptop = bool(re.search(r"\b(mobile|[0-9]{4,5}[UHYHS])\b", cpu_name, re.IGNORECASE))
    is_intel = "intel" in cpu_name.lower()
    is_amd = "amd" in cpu_name.lower() or "ryzen" in cpu_name.lower()

    if is_x3d:
        rec_power = "Balanced"
        power_reason = "AMD 3D V-Cache detected. Windows Balanced allows AMD CPPC to properly schedule game threads on cache cores and prevents thermal throttling."
    elif is_laptop:
        rec_power = "Balanced"
        power_reason = "Laptop/Mobile CPU detected. Balanced power plan prevents thermal throttling and aggressive battery drain."
    elif is_intel:
        rec_power = "High Performance"
        power_reason = "Intel Core Desktop CPU detected. High Performance prevents CPU cores from downclocking during game rounds."
    else:
        rec_power = "High Performance"
        power_reason = "Standard AMD Desktop CPU detected. High Performance prevents CPU cores from downclocking during game pauses."

    return {
        "name": cpu_name,
        "cores": cores,
        "is_x3d": is_x3d,
        "is_laptop": is_laptop,
        "is_intel": is_intel,
        "is_amd": is_amd,
        "recommended_power_plan": rec_power,
        "power_reason": power_reason
    }

def get_gpu_info() -> Dict[str, Any]:
    gpu_name = ""
    base_class = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    for sub in ["0000", "0001", "0002"]:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{base_class}\\{sub}") as k:
                val = str(winreg.QueryValueEx(k, "DriverDesc")[0]).strip()
                if val:
                    gpu_name = val
                    break
        except Exception:
            pass

    if not gpu_name:
        try:
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_VideoController).Name"],
                text=True, creationflags=0x08000000
            )
            gpu_name = out.strip().split("\n")[0].strip()
        except Exception:
            gpu_name = "Standard Graphics Adapter"

    is_nvidia = "nvidia" in gpu_name.lower() or "geforce" in gpu_name.lower()
    is_amd = "amd" in gpu_name.lower() or "radeon" in gpu_name.lower()
    is_intel = "intel" in gpu_name.lower() or "arc" in gpu_name.lower()

    mpo_status = get_mpo_status()

    return {
        "name": gpu_name,
        "is_nvidia": is_nvidia,
        "is_amd": is_amd,
        "is_intel": is_intel,
        "mpo_status": mpo_status
    }

def get_mpo_status() -> str:
    """Read-only check of Windows Multi-Plane Overlay (MPO) registry setting across GraphicsDrivers and DWM."""
    # 1. Check GraphicsDrivers DisableOverlays (Primary WDDM kernel key)
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers") as k:
            val, _ = winreg.QueryValueEx(k, "DisableOverlays")
            if val == 1:
                return "Disabled"
    except Exception:
        pass

    # 2. Check DWM OverlayTestMode (HKLM)
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\Dwm") as k:
            val, _ = winreg.QueryValueEx(k, "OverlayTestMode")
            if val == 5:
                return "Disabled"
            elif val != 0:
                return f"Custom ({val})"
    except Exception:
        pass

    # 3. Check DWM OverlayTestMode (HKCU)
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Dwm") as k:
            val, _ = winreg.QueryValueEx(k, "OverlayTestMode")
            if val == 5:
                return "Disabled"
    except Exception:
        pass

    return "Enabled (Default)"

def get_current_launch_options(steam_path: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not steam_path or not os.path.exists(steam_path):
        return None, None

    # The account that logged in last, and only CS2's own block (never another game's options).
    import steam_vdf
    vf = steam_vdf.localconfig_path(steam_path)
    if not vf:
        return "", None
    try:
        with open(vf, "r", encoding="utf-8", errors="ignore") as f:
            opts = steam_vdf.get_launch_options(f.read(), "730")
        return (opts if opts is not None else ""), vf
    except (OSError, steam_vdf.VdfError):
        return "", vf

def analyze_launch_options(current_opts: str) -> Dict[str, Any]:
    opts = current_opts.strip() if current_opts else ""
    tokens = [t.strip() for t in opts.split() if t.strip()]

    warnings = []
    suggestions = []

    if any("-threads" in t for t in tokens):
        warnings.append("'-threads' detected: Causes thread contention on Source 2's dynamic scheduler.")
    if any("-high" in t for t in tokens):
        warnings.append("'-high' detected: In Source 2, this can starve audio and helper threads.")
    if any("-nod3d9ex" in t or "-d3d9ex" in t for t in tokens):
        warnings.append("'-nod3d9ex' detected: Obsolete DirectX 9 flag, causes errors in CS2 (DirectX 11).")
    if "+exec autoexec.exe" in opts:
        warnings.append("'+exec autoexec.exe' detected: Typo detected (should be autoexec.cfg or omitted).")

    has_novid = any("-novid" in t for t in tokens)
    has_nojoy = any("-nojoy" in t for t in tokens)

    recommended_tokens = list(tokens)

    bad_prefixes = ["-threads", "-high", "-nod3d9ex", "-d3d9ex"]
    recommended_tokens = [t for t in recommended_tokens if not any(t.startswith(bp) for bp in bad_prefixes)]
    
    recommended_tokens = [t if t != "+exec autoexec.exe" else "+exec autoexec.cfg" for t in recommended_tokens]

    if not has_novid:
        recommended_tokens.append("-novid")
        suggestions.append("Added '-novid' to skip intro video and load faster.")
    if not has_nojoy:
        recommended_tokens.append("-nojoy")
        suggestions.append("Added '-nojoy' to save background gamepad polling interrupts.")

    return {
        "current": opts,
        "warnings": warnings,
        "suggestions": suggestions,
        "recommended": " ".join(recommended_tokens),
        "baseline_preset": "-novid -nojoy +fps_max 0"
    }

def get_game_dvr_status() -> Dict[str, Any]:
    """Checks whether Windows Game DVR background recording is enabled in HKCU."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore") as k:
            val, _ = winreg.QueryValueEx(k, "GameDVR_Enabled")
            return {"enabled": bool(val == 1), "status_label": "Enabled (Capturing)" if val == 1 else "Disabled (Clean)"}
    except Exception:
        return {"enabled": False, "status_label": "Disabled (Clean)"}

def set_game_dvr_status(enable: bool) -> Tuple[bool, str]:
    """Toggles Windows Game DVR background recording (used by 1-Click Optimizer / Restore Defaults)."""
    val = 1 if enable else 0
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore") as k:
            winreg.SetValueEx(k, "GameDVR_Enabled", 0, winreg.REG_DWORD, val)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR") as k:
            winreg.SetValueEx(k, "AppCaptureEnabled", 0, winreg.REG_DWORD, val)
        return True, f"Windows Game DVR {'Enabled' if enable else 'Disabled'} successfully."
    except Exception as e:
        return False, str(e)

# =========================================================================
# READ-ONLY SYSTEM DIAGNOSTICS & ADVISORY INSPECTORS
# NOTE: In accordance with the Critical Safety Rule, these functions ONLY inspect
# registry and system state. They NEVER write to the registry or execute system modifications.
# =========================================================================

def get_mpo_diagnostic(gpu_name: str) -> Dict[str, Any]:
    """Inspects Windows Multi-Plane Overlay (MPO) state across GraphicsDrivers and DWM keys."""
    disabled = False
    detail = ""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers") as k:
            val, _ = winreg.QueryValueEx(k, "DisableOverlays")
            if val == 1:
                disabled = True
                detail = r"DisableOverlays = 0x1 in HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    except Exception:
        pass

    if not disabled:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\Dwm") as k:
                val, _ = winreg.QueryValueEx(k, "OverlayTestMode")
                if val == 5:
                    disabled = True
                    detail = r"OverlayTestMode = 5 in HKLM\SOFTWARE\Microsoft\Windows\Dwm"
        except Exception:
            pass

    if not disabled:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Dwm") as k:
                val, _ = winreg.QueryValueEx(k, "OverlayTestMode")
                if val == 5:
                    disabled = True
                    detail = r"OverlayTestMode = 5 in HKCU\Software\Microsoft\Windows\Dwm"
        except Exception:
            pass

    g_upper = gpu_name.upper()
    if "AMD" in g_upper or "RADEON" in g_upper:
        brand = "AMD RADEON"
    elif "NVIDIA" in g_upper or "GEFORCE" in g_upper or "RTX" in g_upper or "GTX" in g_upper:
        brand = "NVIDIA GEFORCE"
    elif "INTEL" in g_upper or "ARC" in g_upper or "IRIS" in g_upper:
        brand = "INTEL GRAPHICS"
    else:
        brand = "WINDOWS MPO"

    badge = f"[{brand} • MPO DISABLED]" if disabled else f"[{brand} • MPO ENABLED]"
    badge_color = theme.CT_BLUE_TEXT if disabled else theme.GOOD_TEXT

    return {
        "disabled": disabled,
        "badge": badge,
        "badge_color": badge_color,
        "detail": detail or "Standard Windows Default (Multi-Plane Overlays Active)",
        "reg_path": r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    }

def get_hpet_diagnostic() -> Dict[str, Any]:
    """Read-only check of BCD boot variables for HPET and synthetic timer overrides."""
    try:
        res = subprocess.run(["bcdedit", "/enum"], capture_output=True, text=True, timeout=3, creationflags=0x08000000)
        out = (res.stdout or "") + " " + (res.stderr or "")
        if res.returncode != 0:
            if "access is denied" in out.lower() or "denied" in out.lower():
                return {
                    "admin_required": True,
                    "has_useplatformclock": False,
                    "has_dynamictick": False,
                    "has_platformtick": False,
                    "is_default": True,
                    "is_low_latency": False,
                    "badge": "[BOOT TIMERS • ADMIN REQUIRED TO QUERY]",
                    "badge_color": theme.TEXT_SECONDARY,
                    "detail": "Access denied to BCD store (Non-Elevated). Run app as Administrator to query live boot variables. Windows default utilizes your CPU native Invariant TSC.",
                    "cmd_text": "bcdedit /deletevalue useplatformclock\nbcdedit /set useplatformtick yes\nbcdedit /set disabledynamictick yes",
                    "cmd_restore": "bcdedit /deletevalue useplatformclock\nbcdedit /deletevalue disabledynamictick\nbcdedit /deletevalue useplatformtick"
                }
            return {
                "admin_required": False,
                "has_useplatformclock": False,
                "has_dynamictick": False,
                "has_platformtick": False,
                "is_default": False,
                "is_low_latency": False,
                "badge": "[BOOT TIMERS • UNKNOWN STATUS]",
                "badge_color": theme.TEXT_SECONDARY,
                "detail": f"BCD query returned status code {res.returncode}.",
                "cmd_text": "bcdedit /deletevalue useplatformclock\nbcdedit /set useplatformtick yes\nbcdedit /set disabledynamictick yes",
                "cmd_restore": "bcdedit /deletevalue useplatformclock\nbcdedit /deletevalue disabledynamictick\nbcdedit /deletevalue useplatformtick"
            }

        out_lower = out.lower()
        has_useplatformclock = "useplatformclock" in out_lower and ("yes" in out_lower or "true" in out_lower)
        has_dynamictick = "disabledynamictick" in out_lower and ("yes" in out_lower or "true" in out_lower)
        has_platformtick = "useplatformtick" in out_lower and ("yes" in out_lower or "true" in out_lower)

        if has_useplatformclock:
            badge = "[HPET: FORCED ON (NON-OPTIMAL)]"
            badge_color = theme.WARN_TEXT
            detail = "Forced HPET detected (useplatformclock = Yes). Windows is querying the motherboard chipset timer over PCIe instead of CPU Invariant TSC."
        elif has_dynamictick and has_platformtick:
            badge = "[TIMERS: LOW-LATENCY TSC (DYNAMIC TICK OFF)]"
            badge_color = theme.CT_BLUE_TEXT
            detail = "Low-latency configuration active: disabledynamictick = Yes and useplatformtick = Yes with Invariant TSC."
        elif has_dynamictick:
            badge = "[TIMERS: DYNAMIC TICK DISABLED]"
            badge_color = theme.CT_BLUE_TEXT
            detail = "disabledynamictick = Yes detected. Timer ticks deliver continuous polling at constant frequency."
        else:
            badge = "[TIMERS: INVARIANT TSC (WINDOWS DEFAULT)]"
            badge_color = theme.GOOD_TEXT
            detail = "Windows boot configuration is clean. Operating with native CPU Invariant TSC (Zero forced HPET overhead)."

        return {
            "admin_required": False,
            "has_useplatformclock": has_useplatformclock,
            "has_dynamictick": has_dynamictick,
            "has_platformtick": has_platformtick,
            "is_default": (not has_useplatformclock and not has_dynamictick and not has_platformtick),
            "is_low_latency": (has_dynamictick and has_platformtick),
            "badge": badge,
            "badge_color": badge_color,
            "detail": detail,
            "cmd_text": "bcdedit /deletevalue useplatformclock\nbcdedit /set useplatformtick yes\nbcdedit /set disabledynamictick yes",
            "cmd_restore": "bcdedit /deletevalue useplatformclock\nbcdedit /deletevalue disabledynamictick\nbcdedit /deletevalue useplatformtick"
        }
    except Exception as e:
        return {
            "admin_required": False,
            "has_useplatformclock": False,
            "has_dynamictick": False,
            "has_platformtick": False,
            "is_default": False,
            "is_low_latency": False,
            "badge": "[BOOT TIMERS • QUERY ERROR]",
            "badge_color": theme.TEXT_SECONDARY,
            "detail": str(e),
            "cmd_text": "bcdedit /deletevalue useplatformclock\nbcdedit /set useplatformtick yes\nbcdedit /set disabledynamictick yes",
            "cmd_restore": "bcdedit /deletevalue useplatformclock\nbcdedit /deletevalue disabledynamictick\nbcdedit /deletevalue useplatformtick"
        }

def get_vbs_diagnostic() -> Dict[str, Any]:
    """Read-only check of Virtualization-Based Security (VBS) and Hypervisor Enforced Code Integrity (HVCI)."""
    enabled = False
    detail = ""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity") as k:
            val, _ = winreg.QueryValueEx(k, "Enabled")
            if val == 1:
                enabled = True
                detail = r"HypervisorEnforcedCodeIntegrity Enabled = 1 in HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard"
            else:
                detail = r"HypervisorEnforcedCodeIntegrity Enabled = 0 in registry (Explicitly Disabled)"
    except Exception:
        detail = "HypervisorEnforcedCodeIntegrity registry key not present (Disabled by default / Clean)"

    badge = "[VBS / HVCI • ENABLED (SECURITY)]" if enabled else "[VBS / HVCI • DISABLED (MAX GAMING FPS)]"
    badge_color = theme.CT_BLUE_TEXT if enabled else theme.GOOD_TEXT

    return {
        "enabled": enabled,
        "badge": badge,
        "badge_color": badge_color,
        "detail": detail,
        "reg_path": r"HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity"
    }

def get_hags_diagnostic() -> Dict[str, Any]:
    """Read-only check of Hardware-Accelerated GPU Scheduling (HAGS)."""
    hags_val = None
    detail = ""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers") as k:
            val, _ = winreg.QueryValueEx(k, "HwSchMode")
            hags_val = val
    except Exception:
        pass

    if hags_val == 2:
        badge = "[HAGS • ENABLED (ON)]"
        badge_color = theme.CT_BLUE_TEXT
        detail = r"HwSchMode = 2 in HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers (Hardware GPU Scheduling Active)"
    elif hags_val == 1:
        badge = "[HAGS • DISABLED (OFF)]"
        badge_color = theme.TEXT_SECONDARY
        detail = r"HwSchMode = 1 in HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers (CPU Software Scheduling Active)"
    else:
        badge = "[HAGS • DISABLED (WINDOWS DEFAULT)]"
        badge_color = theme.TEXT_SECONDARY
        detail = r"HwSchMode key absent in GraphicsDrivers (Off by default for current display adapter)"

    return {
        "enabled": (hags_val == 2),
        "badge": badge,
        "badge_color": badge_color,
        "detail": detail,
        "reg_path": r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    }

def get_ulps_diagnostic(is_amd: bool) -> Dict[str, Any]:
    """Read-only check of Ultra Low Power State (ULPS) in the Windows Graphics Driver class keys."""
    if not is_amd:
        return {
            "applicable": False,
            "enabled": False,
            "badge": "[N/A • AMD RADEON ONLY]",
            "badge_color": theme.TEXT_SECONDARY,
            "detail": "Ultra Low Power State (ULPS) is an AMD Radeon-exclusive driver mechanism. Non-applicable for NVIDIA GeForce or Intel Arc GPUs.",
            "reg_path": r"HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000"
        }

    base_key = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    for sub in ["0000", "0001", "0002"]:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{base_key}\\{sub}") as k:
                val, _ = winreg.QueryValueEx(k, "EnableUlps")
                if val == 1:
                    return {
                        "applicable": True,
                        "enabled": True,
                        "badge": "[AMD ULPS • ENABLED (DEFAULT)]",
                        "badge_color": theme.WARN_TEXT,
                        "detail": f"EnableUlps = 1 in HKLM\\{base_key}\\{sub} (GPU enters deep sleep during idle/menus)",
                        "reg_path": f"HKLM\\{base_key}\\{sub}"
                    }
                else:
                    return {
                        "applicable": True,
                        "enabled": False,
                        "badge": "[AMD ULPS • DISABLED (OPTIMIZED)]",
                        "badge_color": theme.GOOD_TEXT,
                        "detail": f"EnableUlps = 0 in HKLM\\{base_key}\\{sub} (Clock domains stay active, preventing wake stutters)",
                        "reg_path": f"HKLM\\{base_key}\\{sub}"
                    }
        except Exception:
            pass

    return {
        "applicable": True,
        "enabled": False,
        "badge": "[AMD ULPS • NOT CONFIGURED]",
        "badge_color": theme.TEXT_SECONDARY,
        "detail": "EnableUlps registry entry not present in standard graphics class keys.",
        "reg_path": r"HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000"
    }

def get_mmcss_diagnostic() -> Dict[str, Any]:
    """Read-only check of MMCSS Network Throttling Index and System Responsiveness."""
    net_val = None
    sys_resp = None
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile") as k:
            net_val, _ = winreg.QueryValueEx(k, "NetworkThrottlingIndex")
            sys_resp, _ = winreg.QueryValueEx(k, "SystemResponsiveness")
    except Exception:
        pass

    is_unthrottled = (net_val == 0xffffffff or net_val == -1 or str(net_val).lower() == "0xffffffff")

    if is_unthrottled:
        badge = "[MMCSS • UNTHROTTLED (OPTIMAL)]"
        badge_color = theme.GOOD_TEXT
        detail = f"NetworkThrottlingIndex = 0xFFFFFFFF (Network packet limiter disabled). SystemResponsiveness = {sys_resp}%."
    else:
        badge = "[MMCSS • WINDOWS DEFAULT (THROTTLED)]"
        badge_color = theme.WARN_TEXT
        net_str = hex(net_val) if isinstance(net_val, int) else str(net_val)
        detail = f"NetworkThrottlingIndex = {net_str} (Default 10 pkts/ms limiter active). SystemResponsiveness = {sys_resp}% (Default 20% reserved)."

    return {
        "unthrottled": is_unthrottled,
        "badge": badge,
        "badge_color": badge_color,
        "detail": detail,
        "reg_path": r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
    }

def get_msi_mode_diagnostic() -> Dict[str, Any]:
    """Read-only check of GPU PCIe Message Signaled Interrupts (MSI Mode) via pure Win32 registry (<1ms, zero subprocesses)."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum\PCI") as pci_root:
            num_devs = winreg.QueryInfoKey(pci_root)[0]
            for i in range(num_devs):
                dev_name = winreg.EnumKey(pci_root, i)
                with winreg.OpenKey(pci_root, dev_name) as dev_key:
                    num_inst = winreg.QueryInfoKey(dev_key)[0]
                    for j in range(num_inst):
                        inst_name = winreg.EnumKey(dev_key, j)
                        inst_path = f"SYSTEM\\CurrentControlSet\\Enum\\PCI\\{dev_name}\\{inst_name}"
                        try:
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, inst_path) as k:
                                try:
                                    guid = str(winreg.QueryValueEx(k, "ClassGUID")[0]).lower()
                                except Exception:
                                    guid = ""
                                if "{4d36e968-e325-11ce-bfc1-08002be10318}" in guid:
                                    msi_path = f"{inst_path}\\Device Parameters\\Interrupt Management\\MessageSignaledInterruptProperties"
                                    try:
                                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, msi_path) as msi_k:
                                            msi_val = winreg.QueryValueEx(msi_k, "MSISupported")[0]
                                            if msi_val == 1:
                                                return {
                                                    "supported": True,
                                                    "badge": "[PCIe MSI • ENABLED (LOW DPC LATENCY)]",
                                                    "badge_color": theme.GOOD_TEXT,
                                                    "detail": r"MSISupported = 1. GPU delivers interrupts as direct memory writes over PCIe (Clean DPC latency).",
                                                    "reg_path": f"HKLM\\{msi_path}"
                                                }
                                            else:
                                                return {
                                                    "supported": False,
                                                    "badge": "[PCIe MSI • DISABLED (LINE IRQ)]",
                                                    "badge_color": theme.WARN_TEXT,
                                                    "detail": r"MSISupported = 0. GPU is falling back to legacy shared pin-based line interrupts.",
                                                    "reg_path": f"HKLM\\{msi_path}"
                                                }
                                    except Exception:
                                        pass
                        except Exception:
                            pass
    except Exception:
        pass

    return {
        "supported": True,
        "badge": "[PCIe MSI • DRIVER MANAGED]",
        "badge_color": theme.CT_BLUE_TEXT,
        "detail": "GPU MSI mode is negotiated automatically by the modern WDDM display driver stack.",
        "reg_path": r"HKLM\SYSTEM\CurrentControlSet\Enum\PCI\..."
    }
