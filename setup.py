"""
setup.py for py2app

Usage:
    python setup.py py2app

This will create a standalone .app in the dist/ folder.
"""

import sys
from pathlib import Path
from setuptools import setup, find_packages

src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

APP = ['main.py']
DATA_FILES = [
    ('templates', ['templates/base.html', 'templates/quotation.css']),
    ('examples', [
        'examples/config.yaml',
        'examples/3d_artist.md',
        'examples/photography.md',
        'examples/programming.md',
    ]),
    ('assets/images', ['assets/images/logo_code.svg']),
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,
    'plist': {
        'CFBundleName': 'MD2Angebot',
        'CFBundleDisplayName': 'MD2Angebot',
        'CFBundleIdentifier': 'com.yourcompany.md2angebot',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Markdown Document',
                'CFBundleTypeRole': 'Editor',
                'LSItemContentTypes': ['net.daringfireball.markdown'],
                'CFBundleTypeExtensions': ['md', 'markdown'],
            }
        ],
    },
    'packages': find_packages(where='src'),
    'includes': [
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
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtPrintSupport',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
        'mistune',
        'jinja2',
        'yaml',
        'watchdog',
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'PIL',
    ],
    'frameworks': [],
    'site_packages': True,
}

setup(
    name='MD2Angebot',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
)
