"""Unit `convert`: generate MyST lesson pages from the reviewed level JSON files.

Deterministic: the same JSON always produces the same pages.  Text fields are
copied verbatim (no rewriting), so the scientific review of the JSON carries
over.  Run from book/:  python scripts/convert.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

BOOK = pathlib.Path(__file__).resolve().parents[1]
SRC = BOOK.parent / "src" / "data"
if not SRC.exists():  # standalone repository: the vendored copy is the source
    SRC = BOOK / "_data" / "levels"
OUT = BOOK / "levels"

_tbp = BOOK / "_data" / "textbook_map.json"
TEXTBOOK = {e["lesson"]: e["chapters"] for e in json.loads(_tbp.read_text(encoding="utf-8"))["lessons"]} if _tbp.exists() else {}

LAB = {
    "chance": ("01-chance", "Chance and repeated trials"),
    "bayes": ("02-bayes", "Bayes' rule"),
    "causal": ("03-causal-inference", "Confounding and intervention"),
    "interference": ("04-interference", "Interference"),
    "qubit": ("05-qubit-bloch", "Qubits and the Bloch sphere"),
    "bell": ("06-entanglement-bell", "Entanglement and Bell tests"),
    "noise": ("07-noise-channels", "Noise and quantum channels"),
    "gradient": ("08-variational-gradients", "Variational circuits and gradients"),
}

STAGE = ["Grades 1–3", "Grades 4–6", "Grades 7–9", "High-school bridge",
         "Undergraduate", "Advanced undergraduate", "Graduate", "Doctoral & postdoctoral"]
def icon(name: str, up: str = "../../") -> str:
    """Inline SVG icon (decorative) from _static/icons; `up` climbs to the book root."""
    alt = name.replace("level-", "Level ").replace("-", " ").capitalize() + " icon"
    return f"![{alt}]({up}_static/icons/qicon-{name}.svg)"


ICON = [icon(f"level-{n}") for n in range(8)]


def esc(text: str) -> str:
    """Escape characters MyST would treat as markup inside plain prose."""
    text = text.replace("\\", "\\\\")
    text = re.sub(r"(?<!\w)\*", r"\\*", text)
    text = text.replace("_", "\\_").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("{", "\\{").replace("}", "\\}").replace("$", "\\$")
    text = text.replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")
    return text


def lesson_page(level: dict, L: dict, index: dict) -> str:
    lab_file, lab_title = LAB[L["lab"]]
    lines = [
        "---",
        f"title: {json.dumps(L['id'] + ' · ' + L['title'], ensure_ascii=False)}",
        f"short_title: {json.dumps(L['title'], ensure_ascii=False)}",
        f"subtitle: {json.dumps(L['objective'], ensure_ascii=False)}",
        f"description: {json.dumps(L['objective'], ensure_ascii=False)}",
        f"tags: [level-{level['level']}, {L['lab']}]",
        "---",
        "",
        f"(lesson-{L['id'].lower()})=",
        "",
        "",
        ":::{div}",
        f":class: qcai-meta",
        f"{ICON[level['level']]} **Level {level['level']} · {STAGE[level['level']]}**  ",
        f"**Objective.** {esc(L['objective'])}  ",
    ]
    if L["prerequisites"]:
        pre = ", ".join(f"[{p}](#lesson-{p.lower()})" for p in L["prerequisites"])
        lines.append(f"**Before this lesson.** {pre}  ")
    else:
        lines.append("**Before this lesson.** No prerequisites. Start here.  ")
    lines += [f"**Hands-on lab.** [{lab_title}](../../labs/{lab_file}.ipynb)", ":::", ""]

    lines += ["## Learn", ""]
    for p in L["paragraphs"]:
        lines += [esc(p), ""]

    if L.get("equation"):
        lines += [":::{important} Key relation", ":class: qcai-equation", esc(L["equation"]), ":::", ""]

    lines += [":::{tip} Worked example", esc(L["example"]), ":::", ""]

    lab = f"ex-{L['id'].lower()}"
    lines += ["## Practice", "", ":::{admonition} Exercise", ":class: tip", "", esc(L["exercise"]), ":::", "",
              ":::{dropdown} Solution", "", esc(L["solution"]), ":::", ""]

    q = L["quiz"]
    letters = "ABCD"
    lines += ["## Check your understanding", "", f"**{esc(q['question'])}**", ""]
    for i, opt in enumerate(q["options"]):
        lines.append(f"- **{letters[i]}.** {esc(opt)}")
    lines += ["", ":::{dropdown} Show the answer",
              f"**{letters[q['answer']]}. {esc(q['options'][q['answer']])}**", "",
              esc(q["explanation"]), ":::", ""]

    lines += [":::{caution} Scope and assumptions", esc(L["caution"]), ":::", ""]

    cites = "; ".join(f"@{s}" for s in L["sources"])
    lines += ["## Sources", "", f"This lesson draws on [{cites}].", ""]
    tb = TEXTBOOK.get(L["id"])
    if tb:
        lines += [":::{seealso} Read alongside the textbook",
                  f"Bareinboim, *Causal Artificial Intelligence* [@bareinboim], {tb}. "
                  "The draft is free at [causalai-book.net](https://causalai-book.net/).", ":::", ""]

    nxt = index.get(L["id"])
    if nxt:
        lines += [f"**Next:** [{nxt[0]} · {esc(nxt[1])}](#lesson-{nxt[0].lower()})", ""]
    return "\n".join(lines)


def level_page(level: dict) -> str:
    n = level["level"]
    rows = ["| Lesson | Objective | Lab |", "|---|---|---|"]
    for L in level["lessons"]:
        lab_file, lab_title = LAB[L["lab"]]
        rows.append(f"| [{L['id']} · {esc(L['title'])}](#lesson-{L['id'].lower()}) | {esc(L['objective'])} | "
                    f"[{lab_title}](../../labs/{lab_file}.ipynb) |")
    return "\n".join([
        "---",
        f"title: {json.dumps(f'Level {n} · ' + level['title'], ensure_ascii=False)}",
        f"short_title: {json.dumps(f'Level {n} · ' + level['title'], ensure_ascii=False)}",
        f"subtitle: {json.dumps(level['audience'], ensure_ascii=False)}",
        "---",
        "",
        f"(level-{n})=",
        "",
        f":::{{div}}",
        f":class: qcai-level-hero qcai-level-{n}",
        f"{ICON[n]} **{STAGE[n]}**: {esc(level['audience'])}",
        "",
        esc(level["intro"]),
        ":::",
        "",
        *([":::{tip} Core textbook for this level",
           "Elias Bareinboim's *Causal Artificial Intelligence: A Roadmap for Building Causally Intelligent Systems* "
           "[@bareinboim] is the main reference for causal AI in this course. The draft is free at "
           "[causalai-book.net](https://causalai-book.net/). Lessons marked *Read alongside the textbook* point to the matching chapter.",
           ":::", ""] if n in (2, 4, 7) else []),
        "## Lessons in this level",
        "",
        *rows,
        "",
        f"```{{include}} ../../media/_level-{n}.md",
        "```",
        "",
    ])


def main() -> int:
    (BOOK / "_data" / "levels").mkdir(parents=True, exist_ok=True)
    for n in range(8):  # vendored byte-for-byte so the published repo is self-contained
        dst = BOOK / "_data" / "levels" / f"level{n}.json"
        if dst.resolve() != (SRC / f"level{n}.json").resolve():
            dst.write_bytes((SRC / f"level{n}.json").read_bytes())
    levels = [json.loads((SRC / f"level{n}.json").read_text(encoding="utf-8")) for n in range(8)]
    order = [(L["id"], L["title"]) for lv in levels for L in lv["lessons"]]
    nxt = {order[i][0]: order[i + 1] for i in range(len(order) - 1)}
    toc = []
    for lv in levels:
        d = OUT / f"level-{lv['level']}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.md").write_text(level_page(lv), encoding="utf-8")
        children = []
        for L in lv["lessons"]:
            f = d / f"{L['id']}.md"
            f.write_text(lesson_page(lv, L, nxt), encoding="utf-8")
            children.append({"file": f"levels/level-{lv['level']}/{L['id']}.md"})
        toc.append({"file": f"levels/level-{lv['level']}/index.md", "children": children})
    (BOOK / "_data" / "toc-levels.json").write_text(json.dumps(toc, indent=1), encoding="utf-8")
    print(f"wrote {len(order)} lessons in {len(levels)} levels")
    return 0


if __name__ == "__main__":
    sys.exit(main())
