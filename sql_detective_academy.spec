# PyInstaller spec for the desktop pygame build.

from pathlib import Path


project_root = Path(SPECPATH)
data_files = [
    (str(project_root / "data" / "challenges.json"), "data"),
    (str(project_root / "data" / "crime_stories.json"), "data"),
    (str(project_root / "data" / "detective.db"), "data"),
    (str(project_root / "assets" / "images" / "animal_detective_1.png"), "assets/images"),
    (str(project_root / "assets" / "images" / "animal_detective_2.png"), "assets/images"),
    (str(project_root / "assets" / "images" / "animal_detective_3.png"), "assets/images"),
    (str(project_root / "assets" / "images" / "animal_detective_4.png"), "assets/images"),
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
