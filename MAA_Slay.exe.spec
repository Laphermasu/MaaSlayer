# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_ui.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Windows 10\\.conda\\envs\\RL\\lib\\site-packages\\maa/bin', 'maa/bin'), ('C:\\Users\\Windows 10\\.conda\\envs\\RL\\lib\\site-packages\\MaaAgentBinary', 'MaaAgentBinary'), ('C:\\Users\\Windows 10\\.conda\\envs\\RL\\lib\\site-packages\\sb3_contrib', 'sb3_contrib'), ('C:\\Users\\Windows 10\\.conda\\envs\\RL\\lib\\site-packages\\stable_baselines3', 'stable_baselines3')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='MAA_Slay.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
