"""Build a packaged desktop release with PyInstaller."""

from pathlib import Path

import PyInstaller.__main__


PROJECT_ROOT = Path(__file__).resolve().parent
SPEC_PATH = PROJECT_ROOT / "sql_detective_academy.spec"


def main() -> None:
    PyInstaller.__main__.run(
        [
            str(SPEC_PATH),
            "--noconfirm",
            "--clean",
        ]
    )


if __name__ == "__main__":
    main()
