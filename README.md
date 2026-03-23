# SQL Detective Academy

This directory contains the MVP for Task 4: a beginner-friendly SQL learning game built with Streamlit and backed by the real SQLite database in `detective.db`.

It also now includes a desktop `pygame` version with cartoon-style detective avatars and speech-bubble dialogue.

## Current App Scope

- Streamlit UI in `app.py`
- Challenge definitions in `challenges.json`
- Story seeds in `crime_stories.json`
- Query execution and result validation in `validation.py`
- Real SQL executed against `detective.db`
- `SELECT`-only safety rules
- Session-state progress tracking
- Five progressive levels:
  - Level 1: inspect data with `SELECT *` and `LIMIT`
  - Level 2: filter rows with `WHERE`
  - Level 3: sort and narrow results with `ORDER BY` and `LIMIT`
  - Level 4: summarize data with `GROUP BY` and `COUNT`
  - Level 5: combine tables with `JOIN`

## Run

From this directory:

```bash
streamlit run app.py
```

Desktop version:

```bash
pip install pygame
python3 desktop_app.py
```

## Files

- `app.py`: main UI and gameplay flow
- `desktop_app.py`: desktop `pygame` GUI with drawn detective avatars and speech-bubble storytelling
- `challenges.json`: case stories, prompts, expected queries, and hints
- `crime_stories.json`: persistent pool of 20 different investigation story seeds
- `validation.py`: SQLite execution, query safety checks, and result comparison
- `detective.db`: existing investigation database used by the game

## Design Notes

- Validation compares query results, not exact SQL text.
- Order is preserved only for challenges where `order_matters` is `true`.
- Table preview uses random two-row samples to help beginners inspect schema without revealing too much.
- Hints guide the learner conceptually and do not expose the full answer query.
- The case flow now follows one connected story: the Blackwood murder investigation.
- One of 20 persistent crime story variants is chosen when the player enters the app and stays fixed through all levels in that session.
