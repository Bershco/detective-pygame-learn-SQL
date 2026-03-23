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

- a real SQLite database in [data/detective.db](/home/roee/week_1/task_4/data/detective.db)
- 10 SQL levels with 2 variants per level in [data/challenges.json](/home/roee/week_1/task_4/data/challenges.json)
- story seeds in [data/crime_stories.json](/home/roee/week_1/task_4/data/crime_stories.json)
- score, streak, hint, badge, and leaderboard systems
- a desktop case-board UI with a SQL editor and live result previews

## Run From Source

```bash
pip install -r requirements.txt
python3 desktop_app.py
```

Administrator mode for browsing levels without progression gating:

```bash
python3 desktop_app.py --admin
```

## Download And Install

This project supports packaged desktop releases, but a GitHub Release may not always be published yet.

If a release artifact exists on GitHub:

1. Download the archive for your operating system from the Releases page.
2. Extract it.
3. Open the `SQLDetectiveAcademy` executable or app inside the extracted folder.

If no release artifact has been uploaded yet, build it locally:

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

## How It Works

Startup flow:

1. Load the challenge bank from [data/challenges.json](/home/roee/week_1/task_4/data/challenges.json).
2. Group challenges by level and pick one variant per level for the run.
3. Load one story seed from [data/crime_stories.json](/home/roee/week_1/task_4/data/crime_stories.json).
4. Resolve resource and save-data paths through [app_paths.py](/home/roee/week_1/task_4/app_paths.py).
5. Start the `pygame` case board and track score, streaks, hints, timing, and leaderboard state.

Challenge model:

- each level stores the story prompt, the expected query, hint data, and success text
- validation is result-based rather than string-matching SQL
- [validation.py](/home/roee/week_1/task_4/validation.py) allows only safe `SELECT` queries and compares learner output to the expected result set

Scoring model:

```text
max(25, 150 - elapsed_seconds - 15 * (attempts - 1))
```

Badge bonuses:

- streak 3: Bronze Streak, +30
- streak 5: Silver Streak, +50
- streak 7: Gold Streak, +70

Hint and completion rules:

- a level is perfect only if it is solved with no wrong attempt and no hint usage
- wrong attempts first consume the warm-up buffer before breaking a perfect run
- hints escalate at 10, 20, 30, 40, and 42 presses, with extra easter-egg lines beyond that
- if the player has a streak of 2 or more, the game asks for confirmation before a hint breaks it

## Platform Support

- Verified in this workspace: Linux source run and packaging flow
- Supported by packaging design: Windows and Linux
- Important: `PyInstaller` builds must be produced on each target operating system

## Packaging, Download, And Install

The supported release path is a packaged desktop build created with `PyInstaller`.

Build requirements:

- Python 3.12
- [requirements.txt](/home/roee/week_1/task_4/requirements.txt) for runtime dependencies
- [requirements-packaging.txt](/home/roee/week_1/task_4/requirements-packaging.txt) for packaging dependencies

Build commands:

```bash
pip install -r requirements-packaging.txt
python3 build_release.py
```

If you use the local alias:

```bash
agentenv
pip install -r requirements-packaging.txt
python3 build_release.py
```

The build is driven by [build_release.py](/home/roee/week_1/task_4/build_release.py) and [sql_detective_academy.spec](/home/roee/week_1/task_4/sql_detective_academy.spec). The packaged output is created in `dist/SQLDetectiveAcademy/`.

What gets bundled:

- the game code
- the SQLite database
- challenge and story JSON files
- the four portrait assets under `assets/images/`

Save data:

- Windows: `%APPDATA%/SQLDetectiveAcademy/leaderboard.json`
- Linux: `${XDG_DATA_HOME:-~/.local/share}/SQLDetectiveAcademy/leaderboard.json`

Recommended release flow:

1. Build on Linux for Linux and on Windows for Windows.
2. Smoke-test the packaged executable on that operating system.
3. Archive the `dist/SQLDetectiveAcademy/` output.
4. Upload the archives to a GitHub Release.

Automation:

- [`.github/workflows/build-release.yml`](/home/roee/week_1/task_4/.github/workflows/build-release.yml) builds release archives on Linux and Windows when a tag such as `V1` is pushed
- [release_v1_notes.txt](/home/roee/week_1/task_4/release_v1_notes.txt) contains a ready-to-paste title and body for the GitHub Release form

Player install flow:

1. If a GitHub Release exists, download the archive for the correct operating system.
2. If not, build the package locally with `python3 build_release.py`.
3. Extract the archive or open the generated build folder.
4. Open the `SQLDetectiveAcademy` executable or app inside it.

## Repository Notes

- packaged build output in `build/` and `dist/` is git-ignored
- local leaderboard progress is stored outside the repo in the user data directory for packaged builds
- extra markdown files were intentionally removed so `README.md` is the single maintained project document
