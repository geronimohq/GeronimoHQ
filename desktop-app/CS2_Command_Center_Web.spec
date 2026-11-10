# -*- mode: python ; coding: utf-8 -*-
# Build:  cd desktop-ui && npm run build        (writes desktop-app/web)
#         cd desktop-app && python -m PyInstaller --noconfirm --clean --distpath ..\scratch\dist_web --workpath ..\scratch\build_web CS2_Command_Center_Web.spec
from PyInstaller.utils.hooks import collect_all

webview_datas, webview_binaries, webview_hidden = collect_all('webview')

a = Analysis(
    ['web_main.py'],
    pathex=[],
    binaries=webview_binaries,
    datas=[('app.ico', '.'), ('app.png', '.'), ('s2ze_maps_cache.json', '.'), ('web', 'web')] + webview_datas,
    hiddenimports=['pystray._win32', 'clr_loader', 'pythonnet'] + webview_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CS2_Command_Center',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app.ico'],
)
