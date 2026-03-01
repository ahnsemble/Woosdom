import os
from setuptools import setup

ENTRY_POINT = ['desktop.py']

OPTIONS = {
    'argv_emulation': False,
    'strip': True,
    'iconfile': 'icon.icns',
    'includes': ['WebKit', 'Foundation', 'webview'],
    'packages': ['webview'],
    'plist': {
        'CFBundleName': 'Woosdom',
        'CFBundleDisplayName': 'Woosdom',
        'CFBundleIdentifier': 'com.woosdom.app',
        'CFBundleVersion': '0.3.0',
        'CFBundleShortVersionString': '0.3',
        'NSHighResolutionCapable': True,
    },
}

setup(
    app=ENTRY_POINT,
    name='Woosdom',
    options={'py2app': OPTIONS},
)
