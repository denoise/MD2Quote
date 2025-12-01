# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MD2Quote

Usage:
    pip install pyinstaller
    pyinstaller md2quote.spec

This will create MD2Quote.app in the dist/ folder.
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
        'md2quote',
        'md2quote.main',
        'md2quote.core',
        'md2quote.core.config',
        'md2quote.core.parser',
        'md2quote.core.pdf',
        'md2quote.core.renderer',
        'md2quote.ui',
        'md2quote.ui.main_window',
        'md2quote.ui.editor',
        'md2quote.ui.preview',
        'md2quote.ui.header',
        'md2quote.ui.config_dialog',
        'md2quote.ui.styles',
        'md2quote.ui.icons',
        'PyQt6.QtPrintSupport',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
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
    name='MD2Quote',
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
    name='MD2Quote',
)

# Create macOS .app bundle
app = BUNDLE(
    coll,
    name='MD2Quote.app',
    icon=None,  # Add path to .icns file if you have one
    bundle_identifier='com.denoise.md2quote',
    info_plist={
        'CFBundleName': 'MD2Quote',
        'CFBundleDisplayName': 'MD2Quote',
        'CFBundleVersion': '0.9.0 beta',
        'CFBundleShortVersionString': '0.9.0 beta',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',
    },
)

