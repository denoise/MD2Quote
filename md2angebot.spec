# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MD2Angebot

Usage:
    pip install pyinstaller
    pyinstaller md2angebot.spec

This will create MD2Angebot.app in the dist/ folder.
"""

import sys
from pathlib import Path

block_cipher = None

# Get the project root
project_root = Path(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[str(project_root / 'src')],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('examples', 'examples'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'md2angebot',
        'md2angebot.main',
        'md2angebot.core',
        'md2angebot.core.config',
        'md2angebot.core.parser',
        'md2angebot.core.pdf',
        'md2angebot.core.renderer',
        'md2angebot.ui',
        'md2angebot.ui.main_window',
        'md2angebot.ui.editor',
        'md2angebot.ui.preview',
        'md2angebot.ui.header',
        'md2angebot.ui.config_dialog',
        'md2angebot.ui.styles',
        'md2angebot.ui.icons',
        'PyQt6.QtPrintSupport',
        'weasyprint',
        'mistune',
        'jinja2',
        'yaml',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'PIL',
        'PIL.Image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MD2Angebot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MD2Angebot',
)

# Create macOS .app bundle
app = BUNDLE(
    coll,
    name='MD2Angebot.app',
    icon=None,  # Add path to .icns file if you have one
    bundle_identifier='com.yourcompany.md2angebot',
    info_plist={
        'CFBundleName': 'MD2Angebot',
        'CFBundleDisplayName': 'MD2Angebot',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',
    },
)

