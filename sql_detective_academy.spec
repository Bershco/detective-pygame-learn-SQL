# PyInstaller spec for the desktop pygame build.

from pathlib import Path


project_root = Path(SPECPATH)
data_files = [
    (str(project_root / "challenges.json"), "."),
    (str(project_root / "crime_stories.json"), "."),
    (str(project_root / "detective.db"), "."),
    (str(project_root / "animal_detective_1.png"), "."),
    (str(project_root / "animal_detective_2.png"), "."),
    (str(project_root / "animal_detective_3.png"), "."),
    (str(project_root / "animal_detective_4.png"), "."),
]


a = Analysis(
    ["desktop_app.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=data_files,
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
    [],
    exclude_binaries=True,
    name="SQLDetectiveAcademy",
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SQLDetectiveAcademy",
)
