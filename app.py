import json
import random
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from validation import execute_query, validate_query_result


BASE_DIR = Path(__file__).parent
CHALLENGES_PATH = BASE_DIR / "challenges.json"
CRIME_STORIES_PATH = BASE_DIR / "crime_stories.json"


def load_challenges() -> list[dict]:
    with CHALLENGES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_crime_stories() -> list[dict]:
    with CRIME_STORIES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def initialize_state(challenges: list[dict]) -> None:
    if "current_level" not in st.session_state:
        st.session_state.current_level = 1
    if "completed_levels" not in st.session_state:
        st.session_state.completed_levels = []
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "attempts_by_challenge" not in st.session_state:
        st.session_state.attempts_by_challenge = {}
    if "hint_index_by_challenge" not in st.session_state:
        st.session_state.hint_index_by_challenge = {}
    if "query_inputs" not in st.session_state:
        st.session_state.query_inputs = {
            challenge["id"]: "" for challenge in challenges
        }
    if "last_result" not in st.session_state:
        st.session_state.last_result = {}
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    if "solved_message" not in st.session_state:
        st.session_state.solved_message = {}
    if "overlay_message" not in st.session_state:
        st.session_state.overlay_message = ""
    if "selected_story" not in st.session_state:
        st.session_state.selected_story = random.choice(load_crime_stories())


def challenge_for_level(challenges: list[dict], level: int) -> dict:
    return next(challenge for challenge in challenges if challenge["level"] == level)


def challenge_with_story(challenge: dict, story: dict) -> dict:
    challenge_copy = dict(challenge)
    challenge_copy["story"] = challenge_copy["story_template"].format(**story)
    challenge_copy["case_update"] = challenge_copy["case_update_template"].format(**story)
    return challenge_copy


def preview_table(table_name: str) -> pd.DataFrame:
    columns, rows, error = execute_query(f"SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT 2")
    if error:
        return pd.DataFrame({"error": [error]})
    return pd.DataFrame(rows, columns=columns)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #f5ecd9 0%, #e5d1ab 100%);
            color: #23180d;
        }
        .academy-shell {
            background: rgba(72, 49, 33, 0.92);
            border: 2px solid #a67843;
            border-radius: 16px;
            color: #f6efe1;
            padding: 12px 18px;
            box-shadow: 0 10px 24px rgba(40, 25, 12, 0.18);
        }
        .academy-progress {
            background: #f7f0e3;
            border: 2px solid #7a5a31;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 6px 16px rgba(60, 40, 20, 0.12);
        }
        .academy-story {
            background: rgba(255, 248, 235, 0.9);
            border-left: 5px solid #7a5a31;
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 16px;
        }
        .academy-label {
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #7a5a31;
        }
        .academy-level-button button {
            padding: 0.35rem 0.2rem;
            min-height: 2.2rem;
            font-size: 0.9rem;
        }
        .academy-overlay {
            position: fixed;
            inset: 0;
            background: rgba(22, 14, 8, 0.72);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            padding: 1.25rem;
        }
        .academy-overlay-card {
            background: #f7f0e3;
            border: 2px solid #7a5a31;
            border-radius: 16px;
            max-width: 680px;
            width: 100%;
            padding: 1.2rem 1.3rem;
            box-shadow: 0 14px 30px rgba(0, 0, 0, 0.25);
            color: #23180d;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def run_current_query(challenge: dict, total_levels: int) -> None:
    challenge_id = challenge["id"]
    learner_query = st.session_state.query_inputs[challenge_id]
    result = validate_query_result(
        learner_query, challenge["expected_query"], challenge["order_matters"]
    )
    st.session_state.last_result[challenge_id] = {
        "columns": result["learner_columns"],
        "rows": result["learner_rows"],
    }

    if result["message"] and not result["accepted"]:
        st.session_state.feedback[challenge_id] = {
            "type": "warning",
            "text": result["message"],
        }
        attempts = st.session_state.attempts_by_challenge.get(challenge_id, 0) + 1
        st.session_state.attempts_by_challenge[challenge_id] = attempts
        current_hint = st.session_state.hint_index_by_challenge.get(challenge_id, 0)
        max_hint_index = len(challenge["hints"]) - 1
        st.session_state.hint_index_by_challenge[challenge_id] = min(
            current_hint + 1, max_hint_index
        )
        return

    if result["accepted"]:
        if challenge["level"] not in st.session_state.completed_levels:
            st.session_state.completed_levels.append(challenge["level"])
            st.session_state.completed_levels.sort()
            st.session_state.score += 10
        st.session_state.feedback[challenge_id] = {
            "type": "success",
            "text": "Correct result. Case solved.",
        }
        st.session_state.solved_message[challenge_id] = challenge["success_explanation"]
        if challenge["level"] < total_levels:
            st.session_state.overlay_message = (
                f"<strong>Case Update:</strong> {challenge['case_update']} "
                f"<br><br><strong>Next:</strong> Level {challenge['level'] + 1} is now open. "
                "Press any key to close this message."
            )
        else:
            st.session_state.overlay_message = (
                "<strong>Case Closed:</strong> "
                f"{challenge['case_update']} "
                "<br><br>Congratulations. You solved the Blackwood investigation. "
                "Press any key to close this message."
            )
        if challenge["level"] < total_levels:
            st.session_state.current_level = challenge["level"] + 1
            st.rerun()
        st.rerun()


def level_button_label(level: int, current_level: int, completed_levels: list[int], unlocked_levels: int) -> str:
    if level in completed_levels:
        return f"📂 Level {level}"
    if level == current_level:
        return f"💼 Level {level}"
    if level > unlocked_levels:
        return f"🔒 Level {level}"
    return f"💼 Level {level}"


def render_overlay() -> None:
    if not st.session_state.overlay_message:
        return

    st.markdown(
        f"""
        <div class="academy-overlay">
            <div class="academy-overlay-card">
                {st.session_state.overlay_message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <style>
        .overlay-dismiss-anchor {
            position: fixed;
            left: -9999px;
            top: -9999px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="overlay-dismiss-anchor">', unsafe_allow_html=True)
    if st.button("Dismiss update", key="dismiss_overlay_button"):
        st.session_state.overlay_message = ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    components.html(
        """
        <script>
        const parentDoc = window.parent.document;
        const dismiss = () => {
          const buttons = Array.from(parentDoc.querySelectorAll("button"));
          const target = buttons.find(
            (button) => button.innerText && button.innerText.trim() === "Dismiss update"
          );
          if (target) {
            target.click();
          }
        };
        const keyHandler = () => dismiss();
        const clickHandler = () => dismiss();
        window.parent.focus();
        parentDoc.addEventListener("keydown", keyHandler, { once: true });
        parentDoc.addEventListener("click", clickHandler, { once: true });
        </script>
        """,
        height=0,
    )


st.set_page_config(page_title="SQL Detective Academy", page_icon="🕵️", layout="wide")
apply_theme()

challenges = load_challenges()
initialize_state(challenges)
selected_story = st.session_state.selected_story
current_level = st.session_state.current_level
current_challenge = challenge_with_story(
    challenge_for_level(challenges, current_level),
    selected_story,
)
challenge_id = current_challenge["id"]

header_left, header_right = st.columns([3, 1])

with header_left:
    st.markdown(
        f"""
        <div class="academy-shell">
            <div class="academy-label">Training Division</div>
            <h1 style="margin: 0 0 0.4rem 0;">SQL Detective Academy</h1>
            <p style="margin: 0;">Work the {selected_story['case_name']}, write real SQL, and solve each lead against the live SQLite database.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        f"""
        <div class="academy-progress">
            <div class="academy-label">Progress</div>
            <p style="margin: 0.4rem 0;"><strong>Current Level:</strong> {current_level}</p>
            <p style="margin: 0.4rem 0;"><strong>Score:</strong> {st.session_state.score}</p>
            <p style="margin: 0.4rem 0;"><strong>Completed:</strong> {len(st.session_state.completed_levels)} / {len(challenges)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

render_overlay()

left_column, right_column = st.columns([2, 1])

with right_column:
    unlocked_levels = max(
        1, len(st.session_state.completed_levels) + 1
    )
    st.subheader("Case Files")
    level_columns = st.columns(len(challenges))
    for column, challenge in zip(level_columns, challenges):
        button_label = level_button_label(
            challenge["level"],
            current_level,
            st.session_state.completed_levels,
            unlocked_levels,
        )
        with column:
            st.markdown('<div class="academy-level-button">', unsafe_allow_html=True)
            if st.button(
                button_label,
                key=f"level_button_{challenge['level']}",
                disabled=challenge["level"] > unlocked_levels,
                use_container_width=True,
            ):
                st.session_state.current_level = challenge["level"]
                current_level = challenge["level"]
                current_challenge = challenge_with_story(
                    challenge_for_level(challenges, current_level),
                    selected_story,
                )
                challenge_id = current_challenge["id"]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("SQL Editor")
    st.text_area(
        "Write a SELECT query",
        key=f"editor_{challenge_id}",
        value=st.session_state.query_inputs.get(challenge_id, ""),
        height=220,
        on_change=lambda cid=challenge_id: st.session_state.query_inputs.__setitem__(
            cid, st.session_state[f"editor_{cid}"]
        ),
    )

    if st.button("Run Query", type="primary", use_container_width=True):
        st.session_state.query_inputs[challenge_id] = st.session_state[f"editor_{challenge_id}"]
        run_current_query(current_challenge, len(challenges))

with left_column:
    st.subheader(current_challenge["title"])
    st.markdown(
        f"""
        <div class="academy-story">
            <strong>Case Brief:</strong> {current_challenge['story']}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write(current_challenge["description"])

    st.subheader("Table Preview")
    for table_name in current_challenge["tables"]:
        st.write(f"**{table_name}**")
        st.dataframe(preview_table(table_name), use_container_width=True)

    feedback = st.session_state.feedback.get(challenge_id)
    if feedback:
        if feedback["type"] == "success":
            st.success(feedback["text"])
        elif feedback["type"] == "warning":
            st.warning(feedback["text"])
        else:
            st.error(feedback["text"])

    result = st.session_state.last_result.get(challenge_id)
    if result and result["columns"]:
        st.subheader("Query Result")
        st.dataframe(
            pd.DataFrame(result["rows"], columns=result["columns"]),
            use_container_width=True,
        )

    hint_index = st.session_state.hint_index_by_challenge.get(challenge_id)
    if hint_index is not None:
        st.subheader("Hint")
        st.info(current_challenge["hints"][hint_index])

    solved_message = st.session_state.solved_message.get(challenge_id)
    if solved_message:
        st.subheader("Why It Works")
        st.success(solved_message)
