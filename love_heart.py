"""Animated multilingual love heart built with Tkinter."""

from __future__ import annotations

import random
import tkinter as tk
from tkinter import font as tkfont
from collections.abc import Callable

# ----------------------------- Configuration ----------------------------- #

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 650
BACKGROUND = "#050505"
FONT_SIZE = 9
FONT_WEIGHT = "bold"
ANIMATION_DELAY_MS = 145
RESTART_DELAY_MS = 2500
HEART_SCALE = 175
TEXTS_PER_FRAME = 1

TEXT_COLORS = (
    "#ff5733",
    "#ff6347",
    "#ff453a",
    "#ff7043",
    "#ff8066",
)

LOVE_PHRASES = (
    "I love you", "Te amo", "Je t'aime", "Ich liebe dich", "Ti amo",
    "Eu te amo", "Seni seviyorum", "Я тебя люблю", "愛してる", "사랑해",
    "我爱你", "Mahal kita", "Kocham cię", "Te quiero", "Szeretlek",
    "Jeg elsker dig", "Aishiteru", "Te iubesc", "Ik hou van jou",
    "Anh yêu em", "Я тебе кохаю", "Aku cinta kamu", "ฉันรักคุณ", "أحبك",
    "আমি তোমাকে ভালোবাসি", "मैं तुमसे प्यार करता हूँ", "Σ' αγαπώ",
    "Nakupenda", "Volim te", "Minä rakastan sinua", "Jag älskar dig",
    "Jeg elsker deg", "Ik hâld fan dy", "Ljubim te", "Я люблю тебя",
    "Я кохаю тебе", "Miluji tě", "Mám ťa rád", "Saya cinta padamu",
    "Saya sayang kamu", "Ndinokuda", "Ngiyakuthanda", "Mo nifẹ rẹ",
    "Aloha wau iā ʻoe", "אני אוהב אותך", "Ես սիրում եմ քեզ", "მიყვარხარ",
    "我愛你", "사랑해요", "ฉันรักเธอ",
)


def heart_value(x: float, y: float) -> float:
    """Return the implicit heart equation value at a normalized point."""
    return (x * x + y * y - 1) ** 3 - x * x * y**3


def is_inside_heart(x: float, y: float) -> bool:
    """Return whether a normalized point is inside the heart."""
    return heart_value(x, y) <= 0


def make_heart_points() -> list[tuple[float, float]]:
    """Create spaced text positions, ordered from the edge toward the center."""
    points: list[tuple[float, float]] = []

    # A coarse grid avoids overlap and leaves the heart's outline readable.
    for row_index in range(23):
        y = 1.15 - row_index * 0.105
        valid_x = [
            -1.35 + column * 0.005
            for column in range(541)
            if is_inside_heart(-1.35 + column * 0.005, y)
        ]

        segments: list[list[float]] = []
        for x in valid_x:
            if not segments or x - segments[-1][-1] > 0.006:
                segments.append([x])
            else:
                segments[-1].append(x)

        for segment in segments:
            if len(segment) < 2:
                continue

            left, right = segment[0], segment[-1]
            phrase_count = max(1, int((right - left) * HEART_SCALE / 98))
            points.extend(
                (
                    left + (column + 0.5) * (right - left) / phrase_count,
                    y,
                )
                for column in range(phrase_count)
            )

    # Values near zero are on the boundary. Negative values are farther inside.
    points.sort(key=lambda point: heart_value(*point), reverse=True)
    return points


def choose_font(root: tk.Tk) -> tuple[str, int, str]:
    """Choose a common Windows font, falling back when Segoe UI is unavailable."""
    available_fonts = set(tkfont.families(root))
    family = "Segoe UI" if "Segoe UI" in available_fonts else "Arial"
    return family, FONT_SIZE, FONT_WEIGHT


def main() -> None:
    """Create the window and run the non-blocking heart animation."""
    root = tk.Tk()
    root.title("Love Heart")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.configure(bg=BACKGROUND)
    root.resizable(False, False)

    canvas = tk.Canvas(
        root,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        bg=BACKGROUND,
        highlightthickness=0,
    )
    canvas.pack()

    points = make_heart_points()
    phrase_index = random.randrange(len(LOVE_PHRASES))
    point_index = 0
    callback_id: str | None = None
    closed = False
    selected_font = choose_font(root)

    def schedule(callback: Callable[[], None], delay: int) -> None:
        nonlocal callback_id
        callback_id = root.after(delay, callback)

    def animate() -> None:
        nonlocal callback_id, phrase_index, point_index
        callback_id = None

        if closed:
            return
        if point_index >= len(points):
            schedule(restart, RESTART_DELAY_MS)
            return

        for _ in range(TEXTS_PER_FRAME):
            if point_index >= len(points):
                break
            x, y = points[point_index]
            canvas.create_text(
                WINDOW_WIDTH / 2 + x * HEART_SCALE,
                WINDOW_HEIGHT / 2 - y * HEART_SCALE,
                text=LOVE_PHRASES[phrase_index % len(LOVE_PHRASES)],
                fill=random.choice(TEXT_COLORS),
                font=selected_font,
                anchor="center",
                tags="heart-text",
            )
            phrase_index += 1
            point_index += 1

        schedule(animate, ANIMATION_DELAY_MS)

    def restart() -> None:
        nonlocal callback_id, phrase_index, point_index
        callback_id = None
        if closed:
            return
        canvas.delete("heart-text")
        phrase_index = random.randrange(len(LOVE_PHRASES))
        point_index = 0
        schedule(animate, ANIMATION_DELAY_MS)

    def close_window() -> None:
        nonlocal callback_id, closed
        closed = True
        if callback_id is not None:
            root.after_cancel(callback_id)
            callback_id = None
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_window)
    schedule(animate, 0)
    root.mainloop()


if __name__ == "__main__":
    main()
