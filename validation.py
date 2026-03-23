import re
import sqlite3

from app_paths import resource_path


DB_PATH = resource_path("detective.db")
FORBIDDEN_KEYWORDS = ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE")


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def validate_select_query(query: str) -> tuple[bool, str]:
    trimmed = query.strip()
    if not trimmed:
        return False, "Enter a SQL query first."

    if not trimmed.upper().startswith("SELECT"):
        return False, "Only SELECT queries are allowed in training mode."

    if re.search(r";\s*\S+", trimmed):
        return False, "Please run a single SELECT statement only."

    upper_query = trimmed.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_query):
            return False, "Only safe SELECT queries are allowed in training mode."

    return True, ""


def execute_query(query: str) -> tuple[list[str], list[tuple], str | None]:
    try:
        with get_connection() as connection:
            cursor = connection.execute(query)
            columns = [description[0] for description in cursor.description or []]
            rows = [tuple(row) for row in cursor.fetchall()]
            return columns, rows, None
    except sqlite3.Error as error:
        return [], [], str(error)


def normalize_value(value):
    if value is None:
        return None
    if isinstance(value, float):
        return round(value, 6)
    return str(value).strip() if isinstance(value, str) else value


def normalize_rows(rows: list[tuple], order_matters: bool) -> list[tuple]:
    normalized = [tuple(normalize_value(value) for value in row) for row in rows]
    return normalized if order_matters else sorted(normalized)


def compare_results(
    learner_columns: list[str],
    learner_rows: list[tuple],
    expected_columns: list[str],
    expected_rows: list[tuple],
    order_matters: bool,
) -> tuple[bool, str]:
    normalized_learner_columns = [column.strip().lower() for column in learner_columns]
    normalized_expected_columns = [column.strip().lower() for column in expected_columns]

    if normalized_learner_columns != normalized_expected_columns:
        return False, "The query ran, but the returned columns do not match this case."

    if normalize_rows(learner_rows, order_matters) != normalize_rows(
        expected_rows, order_matters
    ):
        return False, "The query ran, but the returned rows do not match this case yet."

    return True, ""


def validate_query_result(
    learner_query: str, expected_query: str, order_matters: bool
) -> dict:
    is_valid, validation_message = validate_select_query(learner_query)
    if not is_valid:
        return {
            "accepted": False,
            "message": validation_message,
            "learner_columns": [],
            "learner_rows": [],
        }

    learner_columns, learner_rows, learner_error = execute_query(learner_query)
    if learner_error:
        return {
            "accepted": False,
            "message": f"SQLite could not run that query: {learner_error}",
            "learner_columns": [],
            "learner_rows": [],
        }

    expected_columns, expected_rows, expected_error = execute_query(expected_query)
    if expected_error:
        return {
            "accepted": False,
            "message": f"Challenge configuration error: {expected_error}",
            "learner_columns": learner_columns,
            "learner_rows": learner_rows,
        }

    matches, mismatch_message = compare_results(
        learner_columns,
        learner_rows,
        expected_columns,
        expected_rows,
        order_matters,
    )

    return {
        "accepted": matches,
        "message": mismatch_message,
        "learner_columns": learner_columns,
        "learner_rows": learner_rows,
    }
