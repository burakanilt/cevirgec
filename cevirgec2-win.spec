from PyInstaller.utils.hooks import collect_data_files

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/models/*.onnx', 'assets/models'),
        ('assets/models/*.txt', 'assets/models'),
        ('assets/icons/*', 'assets/icons'),
        ('core/convert/templates/*.json', 'core/convert/templates'),
        ('LICENSE.txt', '.'),
        ('CREDITS.txt', '.')
    ] + collect_data_files('rapidocr_onnxruntime') + collect_data_files('reportlab'),
    hiddenimports=['49480697f7d29e053205__mypyc'],
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
    [],
    exclude_binaries=True,
    name='cevirgec-pdf',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='cevirgec-pdf',
)

# Post-build copy step: Copy LICENSE.txt and CREDITS.txt next to the exe
import shutil
import os

dist_dir = os.path.join('dist', 'cevirgec-pdf')
if os.path.exists(dist_dir):
    shutil.copy('LICENSE.txt', dist_dir)
    shutil.copy('CREDITS.txt', dist_dir)
    print("Post-build: Copied LICENSE.txt and CREDITS.txt to", dist_dir)
else:
    print("Post-build: Distribution directory not found at", dist_dir)
