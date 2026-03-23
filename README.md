# SQL Detective Academy

SQL Detective Academy is a desktop-only SQL learning game built with `pygame` and backed by a real SQLite database.

The active entry point is [desktop_app.py](/home/roee/week_1/task_4/desktop_app.py). The old Streamlit path and stale web-focused files were removed so the repository reflects only the current game.

## Run

```bash
pip install -r requirements.txt
python3 desktop_app.py
```

If you use the local alias discussed during verification:

```bash
agentenv
python3 desktop_app.py
```

## What The Game Includes

- A real SQLite database in [detective.db](/home/roee/week_1/task_4/detective.db)
- A desktop `pygame` app in [desktop_app.py](/home/roee/week_1/task_4/desktop_app.py)
- SQL safety and result validation in [validation.py](/home/roee/week_1/task_4/validation.py)
- A 10-level challenge bank with 2 variants per level in [challenges.json](/home/roee/week_1/task_4/challenges.json)
- Story variants in [crime_stories.json](/home/roee/week_1/task_4/crime_stories.json)
- Local leaderboard persistence through `leaderboard.json`

## Progression

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
- [PROGRESS.md](/home/roee/week_1/task_4/PROGRESS.md): current change log for the desktop-only version

## Git Notes

- `leaderboard.json` is ignored so local play history is not committed.
- The repo should now contain only the active desktop runtime, its assets, and current docs.
