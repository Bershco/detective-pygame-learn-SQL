import json
import random
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
CHARACTER_FILES = {
    "Lead Detective Mara Voss": BASE_DIR / "animal_detective_3.png",
    "Analyst Theo": BASE_DIR / "animal_detective_2.png",
    "Desk Sergeant Imani": BASE_DIR / "animal_detective_4.png",
    "Case Update": BASE_DIR / "animal_detective_1.png",
}

WINDOW_WIDTH = 1450
WINDOW_HEIGHT = 900
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


def load_json(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


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


class Button:
    def __init__(self, rect, text, action, bg_color, fg_color=WHITE, disabled=False, icon=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.disabled = disabled
        self.icon = icon

    def draw(self, screen, font):
        color = (153, 141, 126) if self.disabled else self.bg_color
        draw_rounded_rect(screen, color, self.rect, radius=12, border=2, border_color=ACCENT)
        text_color = self.fg_color if not self.disabled else (90, 78, 70)
        label = font.render(self.text, True, text_color)
        text_x = self.rect.centerx
        if self.icon:
            self._draw_icon(screen, self.icon, self.rect.x + 14, self.rect.centery - 8, text_color)
            text_x += 8
        label_rect = label.get_rect(center=(text_x, self.rect.centery))
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
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def set_text(self, text: str):
        self.text = text

    def draw(self, screen, font):
        draw_rounded_rect(screen, CARD, self.rect, radius=14, border=2, border_color=ACCENT)
        inner = self.rect.inflate(-16, -16)
        lines = self.text.split("\n") or [""]
        y = inner.y
        line_height = font.get_height() + 4
        for line in lines[-12:]:
            rendered = font.render(line, True, DARK)
            screen.blit(rendered, (inner.x, y))
            y += line_height

        if self.active and self.cursor_visible:
            current_line = lines[-1] if lines else ""
            cursor_x = inner.x + font.size(current_line)[0] + 2
            cursor_y = inner.y + (len(lines[-12:]) - 1) * line_height
            pygame.draw.line(screen, DARK, (cursor_x, cursor_y), (cursor_x, cursor_y + font.get_height()), 2)

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
            self.text = self.text[:-1]
        elif event.key == pygame.K_RETURN:
            self.text += "\n"
        elif event.key == pygame.K_TAB:
            self.text += "    "
        elif event.unicode and event.unicode.isprintable():
            self.text += event.unicode


class DetectiveDesktopApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("SQL Detective Academy")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("georgia", 28, bold=True)
        self.header_font = pygame.font.SysFont("georgia", 20, bold=True)
        self.body_font = pygame.font.SysFont("arial", 19)
        self.small_font = pygame.font.SysFont("arial", 16)
        self.mono_font = pygame.font.SysFont("couriernew", 18)
        self.story_font = pygame.font.SysFont("arial", 17)

        self.challenges = load_json(CHALLENGES_PATH)
        self.story = random.choice(load_json(CRIME_STORIES_PATH))
        self.character_images = self._load_character_images()
        self.current_level = 1
        self.completed_levels: list[int] = []
        self.score = 0
        self.hint_index_by_challenge: dict[str, int] = {}
        self.hint_press_count: dict[str, int] = {}
        self.query_inputs = {challenge["id"]: "" for challenge in self.challenges}
        self.last_results: dict[str, dict] = {}
        self.feedback_messages: dict[str, tuple[str, str]] = {}
        self.overlay_message = ""

        self.editor = TextInput((920, 278, 480, 220))
        self.level_buttons: list[Button] = []
        self.preview_tabs: list[Button] = []
        self.active_preview_index = 0
        self.current_preview_rows: list[tuple] = []
        self.current_preview_columns: list[str] = []

        self._build_level_buttons()
        self._refresh_for_level_change()

    def _load_character_images(self):
        loaded = {}
        for role, path in CHARACTER_FILES.items():
            image = pygame.image.load(path.as_posix()).convert_alpha()
            loaded[role] = pygame.transform.smoothscale(image, (112, 150))
        return loaded

    def get_challenge(self, level=None):
        selected = level or self.current_level
        base = next(challenge for challenge in self.challenges if challenge["level"] == selected)
        challenge = dict(base)
        challenge["story"] = challenge["story_template"].format(**self.story)
        challenge["case_update"] = challenge["case_update_template"].format(**self.story)
        return challenge

    def unlocked_level(self):
        return min(len(self.challenges), max(1, len(self.completed_levels) + 1))

    def _build_level_buttons(self):
        self.level_buttons.clear()
        start_x = 920
        width = 88
        gap = 8
        for idx, challenge in enumerate(self.challenges):
            level = challenge["level"]
            rect = (start_x + idx * (width + gap), 190, width, 42)
            self.level_buttons.append(
                Button(rect, f"{level}", lambda selected=level: self.open_level(selected), GOLD)
            )

    def _refresh_for_level_change(self):
        challenge = self.get_challenge()
        self.editor.set_text(self.query_inputs.get(challenge["id"], ""))
        self._load_preview_tables(challenge)

    def _load_preview_tables(self, challenge):
        self.preview_tabs.clear()
        self.active_preview_index = 0
        start_x = 50
        for idx, table_name in enumerate(challenge["tables"]):
            rect = (start_x + idx * 144, 510, 134, 36)
            self.preview_tabs.append(
                Button(rect, table_name, lambda selected=idx: self._set_preview(selected), TITLE)
            )
        self._set_preview(0)

    def _set_preview(self, index):
        challenge = self.get_challenge()
        self.active_preview_index = index
        table_name = challenge["tables"][index]
        columns, rows, error = execute_query(f"SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT 2")
        if error:
            self.current_preview_columns = ["error"]
            self.current_preview_rows = [(error,)]
        else:
            self.current_preview_columns = columns
            self.current_preview_rows = rows

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

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            self.editor.update(dt)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                if self.overlay_message:
                    if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                        self.overlay_message = ""
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

    def _handle_action_buttons(self, pos):
        run_rect = pygame.Rect(920, 520, 228, 48)
        hint_rect = pygame.Rect(1172, 520, 228, 48)
        if run_rect.collidepoint(pos):
            self.run_query()
        elif hint_rect.collidepoint(pos):
            self.show_hint()

    def run_query(self):
        challenge = self.get_challenge()
        challenge_id = challenge["id"]
        learner_query = self.editor.text.strip()
        self.query_inputs[challenge_id] = learner_query
        result = validate_query_result(learner_query, challenge["expected_query"], challenge["order_matters"])
        self.last_results[challenge_id] = {
            "columns": result["learner_columns"],
            "rows": result["learner_rows"],
        }

        if result["accepted"]:
            if challenge["level"] not in self.completed_levels:
                self.completed_levels.append(challenge["level"])
                self.completed_levels.sort()
                self.score += 10
            self.feedback_messages[challenge_id] = ("success", challenge["success_explanation"])
            if challenge["level"] < len(self.challenges):
                self.current_level = challenge["level"] + 1
                self.overlay_message = (
                    f"Case Update\n\n{challenge['case_update']}\n\n"
                    f"Level {challenge['level'] + 1} is now open.\n\nPress any key to close."
                )
            else:
                self.overlay_message = (
                    f"Case Closed\n\n{challenge['case_update']}\n\n"
                    "Congratulations. You solved the case.\n\nPress any key to close."
                )
            self._refresh_for_level_change()
            return

        if result["message"]:
            self.feedback_messages[challenge_id] = ("warning", result["message"])
        else:
            self.show_hint(prefix="The query ran, but the result does not match this case yet.\n\n")

    def show_hint(self, prefix=""):
        challenge = self.get_challenge()
        challenge_id = challenge["id"]
        self.hint_press_count[challenge_id] = self.hint_press_count.get(challenge_id, 0) + 1
        if self.hint_press_count[challenge_id] >= 42:
            self.feedback_messages[challenge_id] = (
                "success",
                f"Answer unlocked after 42 hints:\n{challenge['expected_query']}",
            )
            return
        current = self.hint_index_by_challenge.get(challenge_id, -1) + 1
        self.hint_index_by_challenge[challenge_id] = min(current, len(challenge["hints"]) - 1)
        hint = challenge["hints"][self.hint_index_by_challenge[challenge_id]]
        self.feedback_messages[challenge_id] = ("warning", f"{prefix}Hint: {hint}")

    def draw(self):
        self.screen.fill(BG)
        self._draw_header()
        self._draw_left_panel()
        self._draw_right_panel()
        if self.overlay_message:
            self._draw_overlay()
        pygame.display.flip()

    def _draw_header(self):
        draw_rounded_rect(self.screen, TITLE, pygame.Rect(30, 24, 980, 104), radius=18)
        draw_rounded_rect(self.screen, (239, 227, 206), pygame.Rect(1035, 24, 385, 104), radius=18, border=2, border_color=ACCENT)
        title = self.title_font.render("SQL Detective Academy", True, WHITE)
        self.screen.blit(title, (52, 42))
        subtitle = self.small_font.render(
            f"Work the {self.story['case_name']}, write real SQL, and solve each lead against the live SQLite database.",
            True,
            WHITE,
        )
        self.screen.blit(subtitle, (52, 82))

        progress_lines = [
            f"Current Level: {self.current_level}",
            f"Score: {self.score}",
            f"Completed: {len(self.completed_levels)} / {len(self.challenges)}",
        ]
        y = 44
        for line in progress_lines:
            label = self.body_font.render(line, True, DARK)
            self.screen.blit(label, (1058, y))
            y += 24

    def _draw_left_panel(self):
        draw_rounded_rect(self.screen, PANEL, pygame.Rect(30, 150, 850, 720), radius=18)
        challenge = self.get_challenge()
        self._draw_avatar_bubble(
            pygame.Rect(50, 170, 810, 220),
            "Lead Detective Mara Voss",
            f"{challenge['title']}\n\n{challenge['story']}",
            bubble_color=CARD,
        )
        self._draw_avatar_bubble(
            pygame.Rect(50, 400, 810, 92),
            "Analyst Theo",
            challenge["description"],
            bubble_color=(254, 243, 217),
        )
        for tab in self.preview_tabs:
            tab.draw(self.screen, self.small_font)
        self._draw_table_box(pygame.Rect(50, 555, 810, 152), "Table Preview", self.current_preview_columns, self.current_preview_rows)
        result = self.last_results.get(challenge["id"], {"columns": [], "rows": []})
        self._draw_table_box(pygame.Rect(50, 723, 810, 127), "Query Result", result["columns"], result["rows"])

    def _draw_right_panel(self):
        draw_rounded_rect(self.screen, PANEL, pygame.Rect(900, 150, 520, 720), radius=18)
        header = self.header_font.render("Case Files", True, DARK)
        self.screen.blit(header, (920, 160))

        for button, challenge in zip(self.level_buttons, self.challenges):
            icon, disabled = self.level_button_state(challenge["level"])
            button.text = f"{challenge['level']}"
            button.disabled = disabled
            button.icon = icon
            button.draw(self.screen, self.small_font)

        editor_label = self.header_font.render("SQL Editor", True, DARK)
        self.screen.blit(editor_label, (920, 242))
        self.editor.draw(self.screen, self.mono_font)

        run_button = Button((920, 512, 228, 48), "Run Query", lambda: None, SUCCESS)
        hint_button = Button((1172, 512, 228, 48), "Show Hint", lambda: None, WARNING)
        run_button.draw(self.screen, self.body_font)
        hint_button.draw(self.screen, self.body_font)

        challenge = self.get_challenge()
        feedback_kind, feedback_text = self.feedback_messages.get(
            challenge["id"],
            ("info", "Run a query to test your lead, or ask for a hint if the case feels stuck."),
        )
        bubble_color = CARD if feedback_kind == "info" else ((233, 247, 229) if feedback_kind == "success" else (249, 237, 219))
        self._draw_avatar_bubble(
            pygame.Rect(920, 582, 480, 238),
            "Desk Sergeant Imani",
            feedback_text,
            bubble_color=bubble_color,
            allow_query_reveal=feedback_kind == "success" and feedback_text.startswith("Answer unlocked"),
        )

    def _draw_avatar_bubble(self, rect, speaker, text, bubble_color=CARD, allow_query_reveal=False):
        x, y, w, h = rect
        avatar = self.character_images[speaker]
        avatar_x = x + 8
        avatar_y = y + max(4, (h - avatar.get_height()) // 2)
        self.screen.blit(avatar, (avatar_x, avatar_y))
        bubble = pygame.Rect(x + 132, y, w - 132, h)
        draw_rounded_rect(self.screen, bubble_color, bubble, radius=18, border=2, border_color=ACCENT)
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
        self.screen.blit(speaker_surface, (bubble.x + 18, bubble.y + 16))
        self._draw_text_block_fit(
            text,
            DARK,
            bubble.x + 18,
            bubble.y + 42,
            bubble.width - 36,
            bubble.height - 58,
            preferred_size=17,
            min_size=13,
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
            col_rect = pygame.Rect(inner_x + idx * col_width, inner_y, col_width - 4, 28)
            draw_rounded_rect(self.screen, (228, 214, 191), col_rect, radius=8)
            label = self.small_font.render(str(column), True, DARK)
            self.screen.blit(label, (col_rect.x + 6, col_rect.y + 6))

        row_y = inner_y + 36
        max_rows = 4 if rect.height < 180 else 5
        for row in rows[:max_rows]:
            for idx, value in enumerate(row[:8]):
                value_text = str(value)
                value_rect = pygame.Rect(inner_x + idx * col_width, row_y, col_width - 4, 26)
                draw_rounded_rect(self.screen, (250, 245, 234), value_rect, radius=6, border=1, border_color=(208, 191, 165))
                rendered = self.small_font.render(value_text[:14], True, DARK)
                self.screen.blit(rendered, (value_rect.x + 6, value_rect.y + 5))
            row_y += 32

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

    def _draw_text_block_fit(self, text, color, x, y, width, height, preferred_size=17, min_size=13, monospace=False):
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

    def _draw_overlay(self):
        shade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        shade.fill((24, 18, 14, 180))
        self.screen.blit(shade, (0, 0))
        card = pygame.Rect(280, 210, 860, 320)
        draw_rounded_rect(self.screen, CARD, card, radius=20, border=3, border_color=ACCENT)
        overlay_avatar = self.character_images["Case Update"]
        self.screen.blit(overlay_avatar, (card.x + 24, card.y + 90))
        title, body = self.overlay_message.split("\n\n", 1)
        title_surface = self.header_font.render(title, True, DARK)
        self.screen.blit(title_surface, (card.x + 24, card.y + 24))
        self._draw_text_block(body, self.body_font, DARK, card.x + 160, card.y + 74, card.width - 190, max_lines=10)


def main():
    DetectiveDesktopApp().run()


if __name__ == "__main__":
    main()
