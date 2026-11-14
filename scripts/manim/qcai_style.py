"""Shared style for the course's Manim animations (Manim Community Edition).

Every lesson scene imports this module: white background, the course palette,
readable type, and `lesson()` to read the lesson's own JSON so the animation and
the text always use the same numbers.
"""
from __future__ import annotations

import json
import pathlib
import sys

from manim import BLACK, Text, config

BOOK = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BOOK))  # so scenes can `from qcai import science`

INK = "#1e1b4b"
MUTED = "#475569"
VIOLET = "#7c3aed"
VIOLET_LIGHT = "#a78bfa"
CYAN = "#06b6d4"
CYAN_LIGHT = "#cffafe"
BLUE = "#3b82f6"
BLUE_LIGHT = "#93c5fd"
AMBER = "#f59e0b"
RED = "#ef4444"
GRID = "#e2e8f0"
BG = "#ffffff"

config.background_color = BG
FONT = "Segoe UI"


def label(text: str, size: int = 30, color: str = INK, weight: str = "NORMAL") -> Text:
    """Plain text in the course font (no LaTeX needed)."""
    return Text(text, font=FONT, font_size=size, color=color, weight=weight)


def lesson(lesson_id: str) -> dict:
    """The lesson's JSON: the draft if one exists, else the merged level file."""
    n = lesson_id[1]
    draft = BOOK / "_data" / f"level{n}_drafts" / f"{lesson_id}.json"
    if draft.exists():
        return json.loads(draft.read_text(encoding="utf-8"))
    for f in (BOOK.parent / "src" / "data" / f"level{n}.json", BOOK / "_data" / "levels" / f"level{n}.json"):
        if f.exists():
            for L in json.loads(f.read_text(encoding="utf-8"))["lessons"]:
                if L["id"] == lesson_id:
                    return L
    raise FileNotFoundError(lesson_id)


def params(lesson_id: str) -> dict:
    return lesson(lesson_id)["animation"].get("params", {})


_ = BLACK  # keep the import used; scenes may rely on manim's palette names
