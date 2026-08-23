# -*- mode: python ; coding: utf-8 -*-
"""Receita do PyInstaller para gerar o executavel unico do C0lorNote.

Construir com:  pyinstaller c0lornote.spec --noconfirm
"""

a = Analysis(
    ["src/main.py"],
    pathex=["."],
    binaries=[],
    datas=[("assets/c0lornote.png", "assets")],
    hiddenimports=["sqlalchemy.dialects.sqlite"],
    hookspath=[],
    runtime_hooks=[],
    # Modulos que o PyQt6 arrasta por padrao e que este app nao usa.
    excludes=[
        "tkinter",
        "matplotlib",
        "numpy",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtQml",
        "PyQt6.QtQuick",
        "PyQt6.QtMultimedia",
        "PyQt6.QtBluetooth",
        "PyQt6.QtNetworkAuth",
        "PyQt6.Qt3DCore",
        "PyQt6.QtCharts",
        "PyQt6.QtDataVisualization",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="C0lorNote",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,          # sem janela de terminal
    icon="assets/c0lornote.ico",
)
