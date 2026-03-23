# SQL Detective Academy

SQL Detective Academy is a desktop-only SQL learning game built with `pygame` and backed by a real SQLite database. The player works through a detective story, solves 10 SQL cases, and learns query skills against a live database instead of mock text answers.

The active entry point is [desktop_app.py](/home/roee/week_1/task_4/desktop_app.py). The repository now reflects only the current desktop game and the files needed to run or package it.

## Project Flow

The project has two practical tracks:

- source development: run the Python game directly from the repo
- desktop release packaging: build a downloadable desktop package with `PyInstaller`

Core files:

- [desktop_app.py](/home/roee/week_1/task_4/desktop_app.py): main `pygame` game
- [validation.py](/home/roee/week_1/task_4/validation.py): SQL safety and result validation
- [app_paths.py](/home/roee/week_1/task_4/app_paths.py): resource and user-data paths for source runs and packaged builds
- [sql_detective_academy.spec](/home/roee/week_1/task_4/sql_detective_academy.spec): `PyInstaller` spec
- [build_release.py](/home/roee/week_1/task_4/build_release.py): repeatable packaging entry point

## Game Summary

The game includes:

- a real SQLite database in [detective.db](/home/roee/week_1/task_4/detective.db)
- 10 SQL levels with 2 variants per level in [challenges.json](/home/roee/week_1/task_4/challenges.json)
- story seeds in [crime_stories.json](/home/roee/week_1/task_4/crime_stories.json)
- score, streak, hint, badge, and leaderboard systems
- a desktop case-board UI with a SQL editor and live result previews

## Run From Source

```bash
pip install -r requirements.txt
python3 desktop_app.py
```

If you use the local alias discussed during verification:

```bash
agentenv
python3 desktop_app.py
```

Administrator mode for browsing levels without progression gating:

```bash
python3 desktop_app.py --administator
```

## Download And Install

For players, the intended release flow is a packaged desktop build:

1. Download the archive for your operating system from the GitHub Release page.
2. Extract the archive.
3. Open the `SQLDetectiveAcademy` executable or app inside the extracted folder.

If you are building the release yourself:

```bash
pip install -r requirements-packaging.txt
python3 build_release.py
```

The packaged output is created in `dist/SQLDetectiveAcademy/`.

## SQL Learning Progression

The game now teaches SQL in 10 steps:

1. `SELECT *` and `LIMIT`
2. selecting specific columns
3. `WHERE`
4. multiple `WHERE` conditions
5. `ORDER BY` and `LIMIT`
6. basic aggregation
7. `GROUP BY`
8. `JOIN`
9. `JOIN` with filtering
10. final evidence joins

Each run selects one challenge variant per level, which reduces repetition while keeping the story structure intact.

## Scoring And Streaks

- Score is based on time and attempts.
- Perfect clears require no wrong attempt and no hint usage.
- Perfect clears extend the streak.
- Any mistake or hint resets the streak.
- Streak badges are awarded at 3, 5, and 7.
- If the player has a streak of 2 or more, the game asks for confirmation before spending it on a hint.

## Docs

- [GAMEPLAY.md](/home/roee/week_1/task_4/GAMEPLAY.md): gameplay rules and architecture notes
- [RELEASE.md](/home/roee/week_1/task_4/RELEASE.md): packaging, release, and install instructions
- [PROGRESS.md](/home/roee/week_1/task_4/PROGRESS.md): current desktop and packaging milestone log

## Platform Support

- Verified in this workspace: Linux source run and packaging flow
- Supported by packaging design: Windows, Linux, and macOS
- Important: `PyInstaller` builds must be produced on each target operating system

## Git Notes

- packaged build output in `build/` and `dist/` is git-ignored
- local leaderboard progress is stored outside the repo in the user data directory for packaged builds
