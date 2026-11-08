"""The placement quiz must have correct answer keys; the widgets must embed valid data."""
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qcai import widgets as w  # noqa: E402
from qcai import science as s  # noqa: E402


def key(i):
    r, p, o, a = w.QUESTIONS[i]
    return o[a]


def test_quiz_answers_are_correct():
    # two heads with a fair coin
    assert key(0) == str(Fraction(1, 2) * Fraction(1, 2))
    # 3x + 2 = 11
    assert key(1) == f"x = {(11 - 2) // 3}" and 3 * 3 + 2 == 11
    # common cause explanation
    assert key(2) == "Hot weather drives both"
    # X matrix times (1, 0)
    v = np.array([[0, 1], [1, 0]]) @ np.array([1, 0])
    assert key(3) == f"({v[0]}, {v[1]})"
    # back-door adjustment for a single measured confounder
    assert key(4) == "Adjust for Z"
    # P(0) for |+>
    p0 = abs((s.H @ s.KET0)[0]) ** 2
    assert math.isclose(p0, 0.5) and key(5) == "1/2"
    # quantum switch: superposition of orders
    assert "order" in key(6)


def test_quiz_rungs_cover_levels_in_order():
    rungs = [q[0] for q in w.QUESTIONS]
    assert rungs == list(range(7))
    for r, p, o, a in w.QUESTIONS:
        assert 0 <= a < len(o) and len(set(o)) == len(o)


def test_widgets_embed_all_lessons_and_no_em_dash():
    m = w.learning_map().data
    p = w.placement().data
    data = json.loads(re.search(r"const D=(\{.*?\}), svgNS", m, re.S).group(1))
    assert len(data["nodes"]) == 80
    ids = {n["id"] for n in data["nodes"]}
    assert all(pre in ids for n in data["nodes"] for pre in n["pre"])
    for html in (m, p):
        assert "—" not in html
