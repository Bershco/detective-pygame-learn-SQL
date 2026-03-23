import argparse
import json
import random
import time
from datetime import datetime
from pathlib import Path

try:
    import pygame
except ModuleNotFoundError as error:
    raise SystemExit(
        "pygame is required for desktop_app.py. Install it with: pip install pygame"
    ) from error

from validation import execute_query, validate_query_result


BASE_DIR = Path(__file__).parent
CHALLENGES_PATH = BASE_DIR / "challenges.json"
CRIME_STORIES_PATH = BASE_DIR / "crime_stories.json"
LEADERBOARD_PATH = BASE_DIR / "leaderboard.json"
CHARACTER_FILES = {
    "Lead Detective Mara Voss": BASE_DIR / "animal_detective_3.png",
    "Analyst Theo": BASE_DIR / "animal_detective_2.png",
    "Desk Sergeant Imani": BASE_DIR / "animal_detective_4.png",
    "Case Update": BASE_DIR / "animal_detective_1.png",
}
BADGE_MILESTONES = {3: "Bronze Streak", 5: "Silver Streak", 7: "Gold Streak"}
REVEAL_THRESHOLDS = {10: 0, 20: 1, 30: 2, 40: 3}
POST_ANSWER_EASTER_EGGS = {
    50: "I already gave the answer away. What more do you want?",
    55: "Seriously???",
    60: "These additional hints are not part of the test. They are part of your file.",
    65: "At this point, the enrichment center would like to remind you that excessive hint consumption is a sign of dependency.",
    70: "You are still here. The query is also still here. Nothing has changed.",
    75: "This was a triumph for persistence, if not for restraint.",
    80: "The hints will continue until morale improves.",
    85: "If you are waiting for a hidden shortcut, that was the shortcut.",
    90: "Look at us. Still pressing. Still not satisfied.",
    95: "The academy has concerns about your relationship with the hint button.",
    100: "The cake is a lie.",
}

WINDOW_WIDTH = 1450
WINDOW_HEIGHT = 930
FPS = 60

BG = (224, 205, 168)
PANEL = (246, 235, 214)
CARD = (255, 248, 236)
DARK = (48, 31, 19)
ACCENT = (121, 90, 49)
TITLE = (78, 53, 35)
GOLD = (205, 160, 84)
SUCCESS = (74, 126, 89)
WARNING = (166, 112, 63)
ERROR = (143, 71, 71)
WHITE = (255, 255, 255)
BLACK = (20, 14, 10)
MUTED = (113, 97, 83)
BRONZE = (167, 115, 72)
SILVER = (126, 135, 148)


def load_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, payload) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def draw_rounded_rect(surface, color, rect, radius=16, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, width=border, border_radius=radius)


def wrap_text(text: str, font, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def format_duration(seconds: int) -> str:
    minutes, remaining = divmod(max(0, int(seconds)), 60)
    return f"{minutes}:{remaining:02d}"


def preview_table(table_name: str) -> tuple[list[str], list[tuple]]:
    columns, rows, error = execute_query(
        f"SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT 2"
    )
    if error:
        return ["error"], [(error,)]
    return columns, rows


def calculate_level_score(elapsed_seconds: int, attempts: int) -> int:
    return max(25, 150 - elapsed_seconds - 15 * max(0, attempts - 1))


def badge_bonus_for_streak(streak: int) -> int:
    if streak == 3:
        return 30
    if streak == 5:
        return 50
    if streak == 7:
        return 70
    return 0


def group_challenges_by_level(challenge_bank: list[dict]) -> dict[int, list[dict]]:
    grouped: dict[int, list[dict]] = {}
    for challenge in challenge_bank:
        grouped.setdefault(challenge["level"], []).append(challenge)
    return grouped


class Button:
    def __init__(
        self,
        rect,
        text,
        action,
        bg_color,
        fg_color=WHITE,
        disabled=False,
        icon=None,
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.disabled = disabled
        self.icon = icon

    def draw(self, screen, font):
        color = (153, 141, 126) if self.disabled else self.bg_color
        draw_rounded_rect(
            screen, color, self.rect, radius=12, border=2, border_color=ACCENT
        )
        text_color = self.fg_color if not self.disabled else (90, 78, 70)
        label = font.render(self.text, True, text_color)
        if self.icon:
            self._draw_icon(
                screen, self.icon, self.rect.x + 6, self.rect.centery - 8, text_color
            )
            label_rect = label.get_rect(center=(self.rect.x + 30, self.rect.centery))
        else:
            label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def handle_click(self, pos):
        if not self.disabled and self.rect.collidepoint(pos):
            self.action()

    def _draw_icon(self, screen, icon, x, y, color):
        if icon == "lock":
            pygame.draw.rect(screen, color, (x, y + 6, 14, 10), width=2, border_radius=2)
            pygame.draw.arc(screen, color, (x + 2, y, 10, 12), 0, 3.14, 2)
        elif icon == "briefcase":
            pygame.draw.rect(screen, color, (x, y + 4, 16, 11), width=2, border_radius=2)
            pygame.draw.rect(screen, color, (x + 5, y, 6, 5), width=2, border_radius=2)
        elif icon == "folder":
            pygame.draw.rect(screen, color, (x, y + 5, 16, 10), width=2, border_radius=2)
            pygame.draw.rect(screen, color, (x + 2, y + 1, 7, 5), width=2, border_radius=2)


class TextInput:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.cursor_position = 0
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def set_text(self, text: str):
        self.text = text
        self.cursor_position = len(text)

    def _insert_text(self, inserted_text: str):
        self.text = (
            f"{self.text[:self.cursor_position]}{inserted_text}{self.text[self.cursor_position:]}"
        )
        self.cursor_position += len(inserted_text)

    def _line_starts(self) -> list[int]:
        starts = [0]
        for index, character in enumerate(self.text):
            if character == "\n":
                starts.append(index + 1)
        return starts

    def _cursor_line_and_column(self) -> tuple[int, int, list[int]]:
        line_starts = self._line_starts()
        line_index = 0
        for idx, start in enumerate(line_starts):
            if start <= self.cursor_position:
                line_index = idx
            else:
                break
        column = self.cursor_position - line_starts[line_index]
        return line_index, column, line_starts

    def _move_vertical(self, direction: int):
        line_index, column, line_starts = self._cursor_line_and_column()
        target_line = line_index + direction
        if target_line < 0 or target_line >= len(line_starts):
            return
        current_line_end = (
            line_starts[target_line + 1] - 1
            if target_line + 1 < len(line_starts)
            else len(self.text)
        )
        target_column = min(column, current_line_end - line_starts[target_line])
        self.cursor_position = line_starts[target_line] + max(0, target_column)

    def draw(self, screen, font):
        draw_rounded_rect(screen, CARD, self.rect, radius=14, border=2, border_color=ACCENT)
        inner = self.rect.inflate(-16, -16)
        lines = self.text.split("\n") or [""]
        cursor_line_index, _, line_starts = self._cursor_line_and_column()
        visible_start = max(0, len(lines) - 12)
        if cursor_line_index < visible_start:
            visible_start = cursor_line_index
        visible_lines = lines[visible_start:visible_start + 12]
        y = inner.y
        line_height = font.get_height() + 4
        for line in visible_lines:
            rendered = font.render(line, True, DARK)
            screen.blit(rendered, (inner.x, y))
            y += line_height

        if self.active and self.cursor_visible:
            current_line = lines[cursor_line_index] if lines else ""
            visible_cursor_line = cursor_line_index - visible_start
            cursor_x = inner.x + font.size(current_line)[0] + 2
            current_line_start = line_starts[cursor_line_index]
            current_column = self.cursor_position - current_line_start
            cursor_x = inner.x + font.size(current_line[:current_column])[0] + 2
            cursor_y = inner.y + visible_cursor_line * line_height
            pygame.draw.line(
                screen,
                DARK,
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + font.get_height()),
                2,
            )

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return

        if event.type != pygame.KEYDOWN or not self.active:
            return

        if event.key == pygame.K_BACKSPACE:
            if self.cursor_position > 0:
                self.text = (
                    f"{self.text[:self.cursor_position - 1]}{self.text[self.cursor_position:]}"
                )
                self.cursor_position -= 1
        elif event.key == pygame.K_RETURN:
            self._insert_text("\n")
        elif event.key == pygame.K_TAB:
            self._insert_text("    ")
        elif event.key == pygame.K_LEFT:
            self.cursor_position = max(0, self.cursor_position - 1)
        elif event.key == pygame.K_RIGHT:
            self.cursor_position = min(len(self.text), self.cursor_position + 1)
        elif event.key == pygame.K_UP:
            self._move_vertical(-1)
        elif event.key == pygame.K_DOWN:
            self._move_vertical(1)
        elif event.unicode and event.unicode.isprintable():
            self._insert_text(event.unicode)


class DetectiveDesktopApp:
    def __init__(self, admin_mode: bool = False):
        pygame.init()
        pygame.display.set_caption("SQL Detective Academy")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.admin_mode = admin_mode

        self.title_font = pygame.font.SysFont("georgia", 28, bold=True)
        self.header_font = pygame.font.SysFont("georgia", 20, bold=True)
        self.body_font = pygame.font.SysFont("arial", 18)
        self.small_font = pygame.font.SysFont("arial", 15)
        self.tiny_font = pygame.font.SysFont("arial", 13)
        self.mono_font = pygame.font.SysFont("couriernew", 17)

        self.challenge_bank = load_json(CHALLENGES_PATH, [])
        self.story_pool = load_json(CRIME_STORIES_PATH, [])
        self.leaderboard_entries = load_json(LEADERBOARD_PATH, [])
        self.character_images = self._load_character_images()

        self.editor = TextInput((920, 280, 485, 190))
        self.level_buttons: list[Button] = []
        self.preview_tabs: list[Button] = []
        self.current_preview_columns: list[str] = []
        self.current_preview_rows: list[tuple] = []
        self.active_preview_index = 0
        self.modal = None
        self.modal_buttons: list[tuple[pygame.Rect, callable]] = []

        self._start_new_game()

    def _load_character_images(self):
        loaded = {}
        for role, path in CHARACTER_FILES.items():
            image = pygame.image.load(path.as_posix()).convert_alpha()
            loaded[role] = pygame.transform.smoothscale(image, (112, 150))
        return loaded

    def _start_new_game(self):
        grouped = group_challenges_by_level(self.challenge_bank)
        expected_levels = list(range(1, 11))
        missing = [level for level in expected_levels if level not in grouped]
        if missing:
            raise SystemExit(f"Missing challenge definitions for levels: {missing}")

        self.story = random.choice(self.story_pool)
        self.selected_challenges = {
            level: random.choice(grouped[level]) for level in expected_levels
        }
        self.current_level = 1
        self.completed_levels: list[int] = []
        self.score = 0
        self.current_streak = 0
        self.max_streak = 0
        self.perfect_levels = 0
        self.earned_badges: list[str] = []
        self.game_started_at = time.monotonic()
        self.game_recorded = False
        self.feedback_messages: dict[str, dict] = {}
        self.last_results: dict[str, dict] = {}
        self.query_inputs = {
            challenge["id"]: "" for challenge in self.selected_challenges.values()
        }
        self.level_states = {
            challenge["id"]: {
                "attempts": 0,
                "hint_count": 0,
                "hint_index": -1,
                "hint_history": [],
                "hint_history_index": -1,
                "hint_used": False,
                "is_perfect_candidate": True,
                "started_at": None,
                "completed_in": None,
            }
            for challenge in self.selected_challenges.values()
        }
        self.modal = None
        self._build_level_buttons()
        self._refresh_for_level_change()

    def get_challenge(self, level=None):
        selected_level = level or self.current_level
        base = self.selected_challenges[selected_level]
        challenge = dict(base)
        challenge["story"] = challenge["story_template"].format(**self.story)
        challenge["case_update"] = challenge["case_update_template"].format(**self.story)
        return challenge

    def unlocked_level(self):
        if self.admin_mode:
            return len(self.selected_challenges)
        return min(len(self.selected_challenges), max(1, len(self.completed_levels) + 1))

    def current_state(self):
        challenge = self.get_challenge()
        return self.level_states[challenge["id"]]

    def _ensure_level_timer(self, challenge_id: str):
        state = self.level_states[challenge_id]
        if state["started_at"] is None:
            state["started_at"] = time.monotonic()

    def _build_level_buttons(self):
        self.level_buttons.clear()
        start_x = 920
        width = 46
        gap = 4
        for level in range(1, 11):
            rect = (start_x + (level - 1) * (width + gap), 192, width, 38)
            self.level_buttons.append(
                Button(rect, str(level), lambda selected=level: self.open_level(selected), GOLD)
            )

    def _refresh_for_level_change(self):
        challenge = self.get_challenge()
        self._ensure_level_timer(challenge["id"])
        self.editor.set_text(self.query_inputs.get(challenge["id"], ""))
        self._load_preview_tables(challenge)

    def _load_preview_tables(self, challenge):
        self.preview_tabs.clear()
        self.active_preview_index = 0
        if len(challenge["tables"]) > 1:
            self.preview_tabs.append(
                Button((50, 540, 40, 34), "<", lambda: self._cycle_preview(-1), TITLE)
            )
            self.preview_tabs.append(
                Button((96, 540, 40, 34), ">", lambda: self._cycle_preview(1), TITLE)
            )
        self._set_preview(0)

    def _set_preview(self, index):
        challenge = self.get_challenge()
        table_name = challenge["tables"][index]
        self.active_preview_index = index
        self.current_preview_columns, self.current_preview_rows = preview_table(table_name)

    def _cycle_preview(self, direction):
        challenge = self.get_challenge()
        total_tables = len(challenge["tables"])
        next_index = (self.active_preview_index + direction) % total_tables
        self._set_preview(next_index)

    def open_level(self, level):
        if level > self.unlocked_level():
            return
        self.query_inputs[self.get_challenge()["id"]] = self.editor.text
        self.current_level = level
        self._refresh_for_level_change()

    def level_button_state(self, level):
        if level in self.completed_levels:
            return "folder", False
        if level > self.unlocked_level():
            return "lock", True
        return "briefcase", False

    def _set_feedback(self, challenge_id: str, kind: str, text: str, reveal_query=False):
        self.feedback_messages[challenge_id] = {
            "kind": kind,
            "text": text,
            "reveal_query": reveal_query,
        }

    def _break_streak(self):
        self.current_streak = 0

    def _record_game_if_needed(self):
        if self.game_recorded:
            return
        duration_seconds = int(time.monotonic() - self.game_started_at)
        entry = {
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "case_name": self.story["case_name"],
            "score": self.score,
            "perfect_levels": self.perfect_levels,
            "max_streak": self.max_streak,
            "duration_seconds": duration_seconds,
        }
        self.leaderboard_entries.append(entry)
        save_json(LEADERBOARD_PATH, self.leaderboard_entries)
        self.game_recorded = True

    def _show_message_modal(self, title: str, body: str):
        self.modal = {
            "title": title,
            "body": body,
            "buttons": [],
            "dismiss_any": True,
        }

    def _show_confirm_modal(self, title: str, body: str, buttons: list[dict]):
        self.modal = {
            "title": title,
            "body": body,
            "buttons": buttons,
            "dismiss_any": False,
        }

    def _close_modal(self):
        self.modal = None
        self.modal_buttons = []

    def _record_and_start_new_game(self):
        self._record_game_if_needed()
        self._start_new_game()

    def _request_new_game(self):
        self._show_confirm_modal(
            "New Game",
            "Start a fresh case file and log the current run to the leaderboard with its current score?",
            [
                {"label": "Cancel", "action": self._close_modal, "color": MUTED},
                {"label": "Start New", "action": self._record_and_start_new_game, "color": GOLD},
            ],
        )

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            self.editor.update(dt)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                if self.modal:
                    if self._handle_modal_event(event):
                        continue

                self.editor.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.level_buttons:
                        button.handle_click(event.pos)
                    for button in self.preview_tabs:
                        button.handle_click(event.pos)
                    self._handle_action_buttons(event.pos)

            self.draw()

        pygame.quit()

    def _handle_modal_event(self, event):
        if not self.modal:
            return False
        if self.modal["buttons"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, action in self.modal_buttons:
                    if rect.collidepoint(event.pos):
                        self._close_modal()
                        action()
                        return True
            return True
        if self.modal["dismiss_any"] and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self._close_modal()
            return True
        return False

    def _handle_action_buttons(self, pos):
        run_rect = pygame.Rect(920, 480, 154, 42)
        hint_rect = pygame.Rect(1085, 480, 154, 42)
        new_game_rect = pygame.Rect(1250, 480, 154, 42)
        hint_prev_rect = pygame.Rect(1326, 543, 28, 24)
        hint_next_rect = pygame.Rect(1360, 543, 28, 24)
        if run_rect.collidepoint(pos):
            self.run_query()
        elif hint_rect.collidepoint(pos):
            self.request_hint()
        elif new_game_rect.collidepoint(pos):
            self._request_new_game()
        elif hint_prev_rect.collidepoint(pos):
            self._scroll_hint_history(-1)
        elif hint_next_rect.collidepoint(pos):
            self._scroll_hint_history(1)

    def run_query(self):
        challenge = self.get_challenge()
        challenge_id = challenge["id"]
        if challenge["level"] in self.completed_levels:
            self._set_feedback(
                challenge_id,
                "info",
                "This level is already solved. Progress, streaks, and score stay locked once a case is cleared.",
            )
            return
        state = self.level_states[challenge_id]
        learner_query = self.editor.text.strip()
        self.query_inputs[challenge_id] = learner_query
        state["attempts"] += 1

        result = validate_query_result(
            learner_query, challenge["expected_query"], challenge["order_matters"]
        )
        self.last_results[challenge_id] = {
            "columns": result["learner_columns"],
            "rows": result["learner_rows"],
        }

        if result["accepted"]:
            self._handle_success(challenge, state)
            return

        if state["is_perfect_candidate"]:
            self._break_streak()
        state["is_perfect_candidate"] = False
        self._set_feedback(challenge_id, "warning", result["message"])

    def _handle_success(self, challenge: dict, state: dict):
        challenge_id = challenge["id"]
        elapsed_seconds = int(time.monotonic() - state["started_at"])
        state["completed_in"] = elapsed_seconds
        level_score = calculate_level_score(elapsed_seconds, state["attempts"])
        badge_bonus = 0
        summary_parts = [
            challenge["success_explanation"],
            f"Level score: +{level_score} (time {elapsed_seconds}s, attempts {state['attempts']}).",
        ]

        if challenge["level"] not in self.completed_levels:
            self.completed_levels.append(challenge["level"])
            self.completed_levels.sort()

        if state["is_perfect_candidate"] and not state["hint_used"]:
            self.perfect_levels += 1
            self.current_streak += 1
            self.max_streak = max(self.max_streak, self.current_streak)
            summary_parts.append(f"Perfect clear. Streak is now {self.current_streak}.")
            badge_name = BADGE_MILESTONES.get(self.current_streak)
            if badge_name and badge_name not in self.earned_badges:
                self.earned_badges.append(badge_name)
                badge_bonus = badge_bonus_for_streak(self.current_streak)
                summary_parts.append(f"Badge earned: {badge_name} (+{badge_bonus}).")
        else:
            self.current_streak = 0
            summary_parts.append("Case solved, but the streak does not continue on this level.")

        self.score += level_score + badge_bonus
        self._set_feedback(challenge_id, "success", "\n\n".join(summary_parts))

        if challenge["level"] < len(self.selected_challenges):
            self.current_level = challenge["level"] + 1
            self._refresh_for_level_change()
            self._show_message_modal(
                "Case Update",
                f"{challenge['case_update']}\n\nLevel {challenge['level'] + 1} is now open.",
            )
            return

        self._record_game_if_needed()
        total_time = int(time.monotonic() - self.game_started_at)
        self._show_confirm_modal(
            "Case Closed",
            (
                f"{challenge['case_update']}\n\n"
                f"Final score: {self.score}\n"
                f"Perfect clears: {self.perfect_levels}/10\n"
                f"Best streak: {self.max_streak}\n"
                f"Run time: {format_duration(total_time)}"
            ),
            [
                {"label": "Close", "action": self._close_modal, "color": MUTED},
                {"label": "New Game", "action": self._record_and_start_new_game, "color": GOLD},
            ],
        )

    def request_hint(self):
        challenge = self.get_challenge()
        state = self.level_states[challenge["id"]]
        if self.current_streak >= 2 and state["is_perfect_candidate"]:
            self._show_confirm_modal(
                "Use Hint?",
                (
                    f"You are on a streak of {self.current_streak}. "
                    "Taking a hint will break it for this run. Continue?"
                ),
                [
                    {"label": "Keep Streak", "action": self._close_modal, "color": MUTED},
                    {"label": "Use Hint", "action": self._grant_hint, "color": WARNING},
                ],
            )
            return
        self._grant_hint()

    def _grant_hint(self):
        challenge = self.get_challenge()
        challenge_id = challenge["id"]
        state = self.level_states[challenge_id]
        state["hint_count"] += 1

        if state["is_perfect_candidate"]:
            self._break_streak()
        state["hint_used"] = True
        state["is_perfect_candidate"] = False

        if state["hint_count"] >= 42:
            if state["hint_count"] == 42:
                unlocked_text = f"Answer unlocked after 42 hints:\n{challenge['expected_query']}"
                self._store_hint(state, unlocked_text)
                self._set_feedback(
                    challenge_id,
                    "success",
                    unlocked_text,
                    reveal_query=True,
                )
                return

            post_answer_line = POST_ANSWER_EASTER_EGGS.get(state["hint_count"])
            if post_answer_line:
                self._store_hint(state, post_answer_line)
                self._set_feedback(
                    challenge_id,
                    "warning",
                    post_answer_line,
                )
            return

        if state["hint_count"] in REVEAL_THRESHOLDS:
            reveal_index = REVEAL_THRESHOLDS[state["hint_count"]]
            reveal_hint = challenge["reveal_hints"][reveal_index]
            stored_hint = f"Deeper clue {state['hint_count']}: {reveal_hint}"
            self._store_hint(state, stored_hint)
            self._set_feedback(
                challenge_id,
                "warning",
                stored_hint,
            )
            return

        state["hint_index"] = min(state["hint_index"] + 1, len(challenge["hints"]) - 1)
        hint = challenge["hints"][state["hint_index"]]
        stored_hint = f"Hint: {hint}"
        self._store_hint(state, stored_hint)
        self._set_feedback(challenge_id, "warning", stored_hint)

    def _store_hint(self, state: dict, hint_text: str):
        if hint_text in state["hint_history"]:
            state["hint_history_index"] = state["hint_history"].index(hint_text)
            return
        state["hint_history"].append(hint_text)
        state["hint_history_index"] = len(state["hint_history"]) - 1

    def _scroll_hint_history(self, direction: int):
        challenge = self.get_challenge()
        state = self.current_state()
        if not state["hint_history"]:
            return
        state["hint_history_index"] = (
            state["hint_history_index"] + direction
        ) % len(state["hint_history"])
        hint_text, _, _ = self._current_hint_history_entry()
        if hint_text is None:
            return
        is_answer_unlock = hint_text.startswith("Answer unlocked after 42 hints:")
        self._set_feedback(
            challenge["id"],
            "success" if is_answer_unlock else "warning",
            hint_text,
            reveal_query=is_answer_unlock,
        )

    def _current_hint_history_entry(self):
        state = self.current_state()
        if not state["hint_history"]:
            return None, 0, 0
        index = state["hint_history_index"]
        if index < 0:
            index = len(state["hint_history"]) - 1
            state["hint_history_index"] = index
        return state["hint_history"][index], index + 1, len(state["hint_history"])

    def leaderboard_rows(self) -> list[dict]:
        ordered = sorted(
            self.leaderboard_entries,
            key=lambda row: (-row["score"], row["duration_seconds"], -row["max_streak"]),
        )
        return ordered[:5]

    def draw(self):
        self.screen.fill(BG)
        self._draw_header()
        self._draw_left_panel()
        self._draw_right_panel()
        if self.modal:
            self._draw_modal()
        pygame.display.flip()

    def _draw_header(self):
        draw_rounded_rect(self.screen, TITLE, pygame.Rect(30, 24, 980, 108), radius=18)
        draw_rounded_rect(
            self.screen,
            (239, 227, 206),
            pygame.Rect(1035, 24, 385, 108),
            radius=18,
            border=2,
            border_color=ACCENT,
        )
        title = self.title_font.render("SQL Detective Academy", True, WHITE)
        self.screen.blit(title, (52, 42))
        subtitle = self.small_font.render(
            f"Work the {self.story['case_name']} with the desktop case board and a live SQLite database.",
            True,
            WHITE,
        )
        self.screen.blit(subtitle, (52, 84))

        challenge = self.get_challenge()
        state = self.level_states[challenge["id"]]
        elapsed = (
            int(time.monotonic() - state["started_at"]) if state["started_at"] is not None else 0
        )
        progress_lines = [
            f"Level: {self.current_level}/10",
            f"Score: {self.score}",
            f"Streak: {self.current_streak}",
            f"Attempts: {state['attempts']}",
            f"Time: {format_duration(elapsed)}",
        ]
        y = 38
        for index, line in enumerate(progress_lines):
            column_x = 1056 if index < 3 else 1228
            row_y = y + (index % 3) * 22
            label = self.small_font.render(line, True, DARK)
            self.screen.blit(label, (column_x, row_y))
        if self.admin_mode:
            admin_label = self.small_font.render("Administrator Mode", True, ERROR)
            self.screen.blit(admin_label, (1056, 103))

    def _draw_left_panel(self):
        draw_rounded_rect(self.screen, PANEL, pygame.Rect(30, 150, 850, 750), radius=18)
        challenge = self.get_challenge()
        case_title = challenge["title"].split(": ", 1)[-1]
        self._draw_avatar_bubble(
            pygame.Rect(50, 170, 810, 215),
            "Lead Detective Mara Voss",
            f"{case_title}\n{challenge['story']}",
            bubble_color=CARD,
        )
        self._draw_avatar_bubble(
            pygame.Rect(50, 392, 810, 105),
            "Analyst Theo",
            f"{challenge['description']}\n\nFocus: {challenge['concept']}",
            bubble_color=(254, 243, 217),
        )
        for tab in self.preview_tabs:
            tab.draw(self.screen, self.small_font)
        preview_title = f"{challenge['tables'][self.active_preview_index]} preview"
        self._draw_table_box(
            pygame.Rect(50, 580, 810, 145),
            preview_title,
            self.current_preview_columns,
            self.current_preview_rows,
        )
        result = self.last_results.get(challenge["id"], {"columns": [], "rows": []})
        self._draw_table_box(
            pygame.Rect(50, 740, 810, 140),
            "Query Result",
            result["columns"],
            result["rows"],
        )

    def _draw_right_panel(self):
        draw_rounded_rect(self.screen, PANEL, pygame.Rect(900, 150, 520, 750), radius=18)
        header = self.header_font.render("Case Files", True, DARK)
        self.screen.blit(header, (920, 160))

        for button, level in zip(self.level_buttons, range(1, 11)):
            icon, disabled = self.level_button_state(level)
            button.text = str(level)
            button.disabled = disabled
            button.icon = icon
            button.draw(self.screen, self.small_font)

        editor_label = self.header_font.render("SQL Editor", True, DARK)
        self.screen.blit(editor_label, (920, 248))
        self.editor.draw(self.screen, self.mono_font)

        Button((920, 480, 154, 42), "Run Query", lambda: None, SUCCESS).draw(
            self.screen, self.body_font
        )
        Button((1085, 480, 154, 42), "Show Hint", lambda: None, WARNING).draw(
            self.screen, self.body_font
        )
        Button((1250, 480, 154, 42), "New Game", lambda: None, TITLE).draw(
            self.screen, self.body_font
        )

        challenge = self.get_challenge()
        feedback = self.feedback_messages.get(
            challenge["id"],
            {
                "kind": "info",
                "text": (
                    "Run a query to test your lead. Perfect clears keep the streak alive. "
                    "Hints break the streak."
                ),
                "reveal_query": False,
            },
        )
        bubble_color = CARD
        if feedback["kind"] == "success":
            bubble_color = (233, 247, 229)
        elif feedback["kind"] == "warning":
            bubble_color = (249, 237, 219)
        elif feedback["kind"] == "error":
            bubble_color = (245, 227, 227)

        self._draw_avatar_bubble(
            pygame.Rect(920, 535, 480, 132),
            "Desk Sergeant Imani",
            feedback["text"],
            bubble_color=bubble_color,
            allow_query_reveal=feedback["reveal_query"],
        )
        self._draw_feedback_hint_controls()
        self._draw_badges_box(pygame.Rect(920, 678, 480, 74))
        self._draw_leaderboard_box(pygame.Rect(920, 760, 480, 124))

    def _draw_feedback_hint_controls(self):
        hint_text, current_index, total = self._current_hint_history_entry()
        if not hint_text:
            return
        Button((1326, 543, 28, 24), "<", lambda: None, TITLE).draw(
            self.screen, self.small_font
        )
        Button((1360, 543, 28, 24), ">", lambda: None, TITLE).draw(
            self.screen, self.small_font
        )
        counter = self.tiny_font.render(f"{current_index}/{total}", True, MUTED)
        self.screen.blit(counter, (1292, 548))

    def _draw_badges_box(self, rect):
        draw_rounded_rect(self.screen, CARD, rect, radius=16, border=2, border_color=ACCENT)
        header = self.header_font.render("Badges", True, DARK)
        self.screen.blit(header, (rect.x + 14, rect.y + 10))
        colors = {
            "Bronze Streak": BRONZE,
            "Silver Streak": SILVER,
            "Gold Streak": GOLD,
        }
        if not self.earned_badges:
            return
        x = rect.x + 18
        for badge in self.earned_badges:
            width = max(110, self.small_font.size(badge)[0] + 26)
            pill = pygame.Rect(x, rect.y + 36, width, 24)
            draw_rounded_rect(
                self.screen,
                colors.get(badge, GOLD),
                pill,
                radius=12,
                border=1,
                border_color=ACCENT,
            )
            label = self.small_font.render(badge, True, WHITE)
            self.screen.blit(label, (pill.x + 12, pill.y + 4))
            x += width + 10

    def _draw_leaderboard_box(self, rect):
        draw_rounded_rect(self.screen, CARD, rect, radius=16, border=2, border_color=ACCENT)
        header = self.header_font.render("Leaderboard", True, DARK)
        games_label = self.small_font.render(
            f"Games played: {len(self.leaderboard_entries)}", True, DARK
        )
        self.screen.blit(header, (rect.x + 14, rect.y + 8))
        games_x = rect.right - games_label.get_width() - 14
        self.screen.blit(games_label, (games_x, rect.y + 12))

        columns = [("Rank", 18), ("Score", 78), ("Perfect", 150), ("Streak", 242), ("Time", 330)]
        for label, x_offset in columns:
            text = self.tiny_font.render(label, True, MUTED)
            self.screen.blit(text, (rect.x + x_offset, rect.y + 34))

        for index, row in enumerate(self.leaderboard_rows(), start=1):
            y = rect.y + 52 + (index - 1) * 16
            values = [
                str(index),
                str(row["score"]),
                str(row["perfect_levels"]),
                str(row["max_streak"]),
                format_duration(row["duration_seconds"]),
            ]
            positions = [18, 78, 150, 242, 330]
            for value, x_offset in zip(values, positions):
                text = self.tiny_font.render(value, True, DARK)
                self.screen.blit(text, (rect.x + x_offset, y))

    def _draw_avatar_bubble(
        self,
        rect,
        speaker,
        text,
        bubble_color=CARD,
        allow_query_reveal=False,
    ):
        x, y, w, h = rect
        avatar = self.character_images[speaker]
        avatar_x = x + 8
        avatar_y = y + max(4, (h - avatar.get_height()) // 2)
        self.screen.blit(avatar, (avatar_x, avatar_y))
        bubble = pygame.Rect(x + 132, y, w - 132, h)
        draw_rounded_rect(
            self.screen, bubble_color, bubble, radius=18, border=2, border_color=ACCENT
        )
        tail_mid = y + min(max(h // 2, 42), h - 42)
        pygame.draw.polygon(
            self.screen,
            bubble_color,
            [(x + 132, tail_mid - 18), (x + 108, tail_mid), (x + 132, tail_mid + 18)],
        )
        pygame.draw.lines(
            self.screen,
            ACCENT,
            False,
            [(x + 132, tail_mid - 18), (x + 108, tail_mid), (x + 132, tail_mid + 18)],
            2,
        )
        speaker_surface = self.small_font.render(speaker, True, ACCENT)
        self.screen.blit(speaker_surface, (bubble.x + 18, bubble.y + 14))
        self._draw_text_block_fit(
            text,
            DARK,
            bubble.x + 18,
            bubble.y + 38,
            bubble.width - 34,
            bubble.height - 52,
            preferred_size=16,
            min_size=12,
            monospace=allow_query_reveal,
        )

    def _draw_table_box(self, rect, title, columns, rows):
        draw_rounded_rect(self.screen, CARD, rect, radius=16, border=2, border_color=ACCENT)
        header = self.header_font.render(title, True, DARK)
        self.screen.blit(header, (rect.x + 14, rect.y + 10))
        if not columns:
            empty = self.small_font.render("No rows yet.", True, DARK)
            self.screen.blit(empty, (rect.x + 16, rect.y + 48))
            return

        inner_x = rect.x + 14
        inner_y = rect.y + 48
        available_width = rect.width - 28
        col_width = max(90, available_width // max(1, len(columns)))
        for idx, column in enumerate(columns[:8]):
            col_rect = pygame.Rect(inner_x + idx * col_width, inner_y, col_width - 4, 24)
            draw_rounded_rect(self.screen, (228, 214, 191), col_rect, radius=8)
            label = self.tiny_font.render(str(column), True, DARK)
            self.screen.blit(label, (col_rect.x + 6, col_rect.y + 5))

        row_y = inner_y + 30
        max_rows = 3 if rect.height < 150 else 4
        for row in rows[:max_rows]:
            for idx, value in enumerate(row[:8]):
                value_text = str(value)
                value_rect = pygame.Rect(
                    inner_x + idx * col_width, row_y, col_width - 4, 24
                )
                draw_rounded_rect(
                    self.screen,
                    (250, 245, 234),
                    value_rect,
                    radius=6,
                    border=1,
                    border_color=(208, 191, 165),
                )
                rendered = self.tiny_font.render(value_text[:14], True, DARK)
                self.screen.blit(rendered, (value_rect.x + 6, value_rect.y + 5))
            row_y += 28

    def _draw_text_block(self, text, font, color, x, y, width, max_lines=None):
        lines: list[str] = []
        for paragraph in text.split("\n"):
            lines.extend(wrap_text(paragraph, font, width))
            lines.append("")
        if lines and lines[-1] == "":
            lines.pop()
        if max_lines and len(lines) > max_lines:
            lines = lines[:max_lines]
            last_line = lines[-1]
            while last_line and font.size(f"{last_line}...")[0] > width:
                last_line = last_line[:-1]
            lines[-1] = f"{last_line}..."
        for line in lines:
            rendered = font.render(line, True, color)
            self.screen.blit(rendered, (x, y))
            y += font.get_height() + 5

    def _draw_text_block_fit(
        self,
        text,
        color,
        x,
        y,
        width,
        height,
        preferred_size=17,
        min_size=13,
        monospace=False,
    ):
        chosen_font = None
        chosen_lines = None
        for size in range(preferred_size, min_size - 1, -1):
            font_name = "couriernew" if monospace else "arial"
            font = pygame.font.SysFont(font_name, size)
            lines: list[str] = []
            for paragraph in text.split("\n"):
                lines.extend(wrap_text(paragraph, font, width))
                lines.append("")
            if lines and lines[-1] == "":
                lines.pop()
            required_height = len(lines) * (font.get_height() + 5)
            if required_height <= height:
                chosen_font = font
                chosen_lines = lines
                break
        if chosen_font is None:
            font_name = "couriernew" if monospace else "arial"
            chosen_font = pygame.font.SysFont(font_name, min_size)
            chosen_lines = []
            for paragraph in text.split("\n"):
                chosen_lines.extend(wrap_text(paragraph, chosen_font, width))
                chosen_lines.append("")
            if chosen_lines and chosen_lines[-1] == "":
                chosen_lines.pop()
            max_lines = max(1, height // (chosen_font.get_height() + 5))
            chosen_lines = chosen_lines[:max_lines]
            if chosen_lines:
                last_line = chosen_lines[-1]
                while last_line and chosen_font.size(f"{last_line}...")[0] > width:
                    last_line = last_line[:-1]
                chosen_lines[-1] = f"{last_line}..."

        current_y = y
        for line in chosen_lines:
            rendered = chosen_font.render(line, True, color)
            self.screen.blit(rendered, (x, current_y))
            current_y += chosen_font.get_height() + 5

    def _draw_modal(self):
        shade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        shade.fill((24, 18, 14, 190))
        self.screen.blit(shade, (0, 0))
        card = pygame.Rect(260, 210, 930, 360)
        draw_rounded_rect(self.screen, CARD, card, radius=20, border=3, border_color=ACCENT)
        overlay_avatar = self.character_images["Case Update"]
        self.screen.blit(overlay_avatar, (card.x + 24, card.y + 108))
        title_surface = self.header_font.render(self.modal["title"], True, DARK)
        self.screen.blit(title_surface, (card.x + 24, card.y + 24))
        self._draw_text_block(
            self.modal["body"],
            self.body_font,
            DARK,
            card.x + 160,
            card.y + 76,
            card.width - 190,
            max_lines=11,
        )

        self.modal_buttons = []
        buttons = self.modal["buttons"]
        if not buttons:
            note = self.small_font.render("Press any key or click to continue.", True, MUTED)
            self.screen.blit(note, (card.x + 160, card.y + 314))
            return

        total_width = len(buttons) * 150 + (len(buttons) - 1) * 16
        start_x = card.centerx - total_width // 2
        for index, button in enumerate(buttons):
            rect = pygame.Rect(start_x + index * 166, card.y + 300, 150, 40)
            draw_rounded_rect(
                self.screen,
                button["color"],
                rect,
                radius=12,
                border=2,
                border_color=ACCENT,
            )
            label = self.body_font.render(button["label"], True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            self.screen.blit(label, label_rect)
            self.modal_buttons.append((rect, button["action"]))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--administator",
        action="store_true",
        help="Unlock all levels for inspection without normal progression gating.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    DetectiveDesktopApp(admin_mode=args.administator).run()


if __name__ == "__main__":
    main()
