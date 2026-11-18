"""Advanced coursebook (schema 3) for Levels 3-7: lesson notebooks and the unit syllabus page.

A schema-3 lesson is written as JSON (see scripts/check_lesson_v3.py for the rules) and rendered
into a Jupyter notebook page, so one lesson can mix prose, display mathematics, definition and
theorem blocks, several Manim animations, interactive Plotly explorers, vector figures, Mermaid
diagrams and runnable code.  Text fields are MyST Markdown and are copied verbatim.

    python scripts/lesson_v3.py L3-01        # build (and execute) one lesson notebook
    python scripts/lesson_v3.py --level 3    # every schema-3 lesson of a level

convert.py calls `write_lesson` for every schema-3 lesson; a notebook is rebuilt and
re-executed only when its inputs (lesson JSON, figure module, qcai.viz) change.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import nbformat as nbf

BOOK = pathlib.Path(__file__).resolve().parents[1]
LETTERS = "ABCD"
PRF = {"definition", "theorem", "proposition", "lemma", "corollary", "remark", "example", "algorithm", "axiom",
       "conjecture", "assumption"}
BOOT = '''import sys, pathlib, subprocess
here = pathlib.Path.cwd()
root = next((p for p in [here, *here.parents] if (p / "qcai").is_dir()), None)
if root is None:  # for example on Google Colab: fetch the course's small teaching package
    root = pathlib.Path("quantum-causal-ai")
    if not root.exists():
        subprocess.run(["git", "clone", "--depth", "1", "https://github.com/pozapas/quantum-causal-ai.git", str(root)], check=True)
    root = root.resolve()
sys.path.insert(0, str(root))'''


def lesson_link(lid: str) -> str:
    return f"[{lid}](#lesson-{lid.lower()})"


def figmod(L: dict) -> str:
    return L["id"].lower().replace("-", "_")


def blocks(L: dict):
    for s in L["sections"]:
        yield from s["blocks"]


def lesson_cells(level: dict, L: dict, nxt: dict, *, icon_md: str, stage: str, lab: tuple[str, str]) -> list:
    n = level["level"]
    lab_file, lab_title = lab
    title_by_id = {x["id"]: x["title"] for lv in [level] for x in lv["lessons"]}
    cells: list = []
    md: list[str] = []

    def flush():
        if md and any(x.strip() for x in md):
            cells.append(nbf.v4.new_markdown_cell("\n".join(md).strip() + "\n"))
        md.clear()

    def code(src: str, hide: str | None):
        flush()
        meta = {"tags": [hide]} if hide else {}
        cells.append(nbf.v4.new_code_cell(src, metadata=meta))

    pre = (", ".join(lesson_link(p) for p in L["prerequisites"])) if L["prerequisites"] else "Nothing beyond the level introduction."
    md += [
        "---",
        f"title: {json.dumps(L['id'] + ' · ' + L['title'], ensure_ascii=False)}",
        f"short_title: {json.dumps(L['title'], ensure_ascii=False)}",
        f"subtitle: {json.dumps(L['big_idea'], ensure_ascii=False)}",
        f"description: {json.dumps(L['objective'], ensure_ascii=False)}",
        f"tags: [level-{n}, coursebook]",
        "---",
        "",
        f"(lesson-{L['id'].lower()})=",
        "",
        ":::{div}",
        ":class: qcai-meta",
        f"{icon_md} **Level {n} · {stage}** · about {L['time_minutes']} minutes  ",
        f"**Big idea.** {L['big_idea']}  ",
        f"**Before this lesson.** {pre}  ",
        f"**Lab.** [{lab_title}](../../labs/{lab_file}.ipynb)",
        ":::",
        "",
        "## What you will be able to do",
        "",
        *[f"- {o}" for o in L["outcomes"]],
        "",
        "## Why this matters",
        "",
    ]
    for p in L["motivation"]:
        md += [p, ""]
    md += [":::{dropdown} Key terms", ""]
    for k in L["key_terms"]:
        md += [f"**{k['term']}**", f": {k['meaning']}", ""]
    md += [":::", ""]
    flush()
    code(BOOT + f"\nfrom qcai.viz import show as _show, show_mpl as _show_mpl\nfrom qcai.lessonfigs import {figmod(L)} as _lessonfigs", "remove-cell")

    fig_no = 0
    for s in L["sections"]:
        md += [f"## {s['heading']}", ""]
        for b in s["blocks"]:
            t = b["type"]
            if t == "text":
                md += [b["md"], ""]
            elif t == "equation":
                md += ["$$", b["latex"], "$$" + (f" ({b['label']})" if b.get("label") else ""), ""]
            elif t in PRF:
                md += [f":::{{prf:{t}}} {b.get('title', '')}".rstrip()]
                if b.get("label"):
                    md += [f":label: {b['label']}"]
                md += [b["md"], ":::", ""]
            elif t == "proof":
                md += [":::{prf:proof}", b["md"], ":::", ""]
            elif t == "callout":
                md += [f":::{{{b.get('kind', 'note')}}} {b.get('title', '')}".rstrip(), b["md"], ":::", ""]
            elif t == "animation":
                fig_no += 1
                md += [f":::{{figure}} ../../_static/animations/{b['file']}", f":alt: {b['alt']}", ":width: 100%", "",
                       b["caption"], ":::", "", ":::{dropdown} What the animation shows", b["describe"], ":::", ""]
            elif t == "diagram":
                md += ["```{mermaid}", b["mermaid"].strip(), "```", "", f"*{b['caption']}*", ""]
            elif t == "interactive":
                code(f"_show(_lessonfigs.{b['func']}())", "remove-input")
                md += [f"**Explore.** {b['caption']}", "", ":::{dropdown} What the figure shows", b["describe"], ":::", ""]
            elif t == "figure":
                code(f"_show_mpl(_lessonfigs.{b['func']}())", "remove-input")
                md += [f"*{b['caption']}*", ""]
            elif t == "code":
                if b.get("explain"):
                    md += [b["explain"], ""]
                code(b["source"].rstrip(), None)
            else:
                raise ValueError(f"{L['id']}: unknown block type {t}")

    w = L["worked_example"]
    md += ["## Worked example", "", f":::{{admonition}} {w.get('title', 'Worked example')}", ":class: tip", "", w["problem"], ""]
    md += [f"{i}. {s}" for i, s in enumerate(w["steps"], 1)]
    md += ["", f"**Result.** {w['result']}", ":::", "", "## Exercises", ""]
    for i, e in enumerate(L["exercises"], 1):
        md += [f"**{i}. ({e['level'].capitalize()})** {e['prompt']}", "", ":::{dropdown} Solution", e["solution"], ":::", ""]

    md += ["## Check your understanding", ""]
    for i, q in enumerate(L["check"], 1):
        tag = f" *(Review of {lesson_link(q['review_of'])})*" if q.get("review_of") else ""
        md += [f"**{i}. {q['question']}**{tag}", ""]
        md += [f"- **{LETTERS[k]}.** {o}" for k, o in enumerate(q["options"])]
        md += ["", ":::{dropdown} Show the answer", f"**{LETTERS[q['answer']]}. {q['options'][q['answer']]}**", "",
               q["explanation"], ":::", ""]

    md += ["## Common misconceptions", ""]
    md += [f"- **{m['claim']}** {m['correction']}" for m in L["misconceptions"]]
    md += ["", ":::{caution} Scope and limits", L["caution"], ":::", "", ":::{seealso} Where this leads", L["connect"], ":::", ""]
    ins = L["instructor"]
    md += [":::{dropdown} For instructors", "", f"**Why this lesson.** {ins['why']}", "", "**Teaching notes.**", ""]
    md += [f"- {x}" for x in ins["teaching_notes"]]
    md += ["", f"**Assessment.** {ins['assessment']}", "", f"**Going further.** {ins['extend']}", "", ":::", ""]
    md += ["## References", "", "This lesson draws on [" + "; ".join(f"@{s}" for s in L["sources"]) + "].", ""]
    if L.get("further"):
        md += ["**Further reading.**", ""] + [f"- [@{f['key']}]: {f['note']}" for f in L["further"]] + [""]
    if nxt.get(L["id"]):
        nid, ntitle = nxt[L["id"]]
        md += [f"**Next:** [{nid} · {ntitle}](#lesson-{nid.lower()})", ""]
    flush()
    _ = title_by_id
    return cells


def inputs_hash(L: dict) -> str:
    h = hashlib.sha256(json.dumps(L, sort_keys=True, ensure_ascii=False).encode())
    for f in [BOOK / "qcai" / "lessonfigs" / f"{figmod(L)}.py", BOOK / "qcai" / "viz.py", pathlib.Path(__file__)]:
        if f.exists():
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


def write_lesson(level: dict, L: dict, nxt: dict, out: pathlib.Path, *, icon_md: str, stage: str, lab: tuple[str, str],
                 execute: bool = True, force: bool = False) -> bool:
    """Write (and execute) the lesson notebook; returns True if it was rebuilt."""
    key = inputs_hash(L)
    if out.exists() and not force:
        old = nbf.read(str(out), 4)
        if old.metadata.get("qcai", {}).get("inputs") == key:
            return False
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {"display_name": "Python 3 (qcai)", "language": "python", "name": "qcai"}
    nb.metadata["language_info"] = {"name": "python"}
    nb.metadata["qcai"] = {"inputs": key, "lesson": L["id"]}
    nb.cells = lesson_cells(level, L, nxt, icon_md=icon_md, stage=stage, lab=lab)
    if execute:
        from nbclient import NotebookClient
        NotebookClient(nb, timeout=600, kernel_name="qcai", resources={"metadata": {"path": str(out.parent)}}).execute()
        bad = [o for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.get("output_type") == "error"]
        if bad:
            raise RuntimeError(f"{L['id']}: {bad[0].get('ename')}: {bad[0].get('evalue')}")
    out.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, str(out))
    return True


def unit_page_adv(level: dict, *, esc, icon_md: str, stage: str, media_include: str) -> str:
    """Syllabus page for an advanced level (unit with "tier": "advanced")."""
    n, u = level["level"], level["unit"]
    t = u["time"]

    def cell(ids):
        return ", ".join("capstone" if i == "PROJECT" else lesson_link(i) for i in ids)

    out = [
        "---",
        f"title: {json.dumps(f'Level {n} · ' + level['title'], ensure_ascii=False)}",
        f"short_title: {json.dumps(f'Level {n} · ' + level['title'], ensure_ascii=False)}",
        f"subtitle: {json.dumps(level['audience'], ensure_ascii=False)}",
        "---", "", f"(level-{n})=", "",
        ":::{div}", f":class: qcai-level-hero qcai-level-{n}", f"{icon_md} **{stage}**: {esc(level['audience'])}", "",
        f"**The central question:** {u['big_question']}", "", u["summary"], ":::", "",
        "## At a glance", "", "| | |", "|---|---|",
        f"| Who it is for | {u['for_whom']} |",
        f"| Prerequisites | {u['prerequisites']} |",
        f"| Lessons | {t['lessons']} lessons of about {t['minutes_per_lesson']} minutes, plus a {t['project_sessions']}-session capstone |",
        f"| Pace | {t['pace']} |",
        "", "## How each lesson is built", "",
        *[f"{i}. {s}" for i, s in enumerate(u["session_flow"], 1)], "",
        "## Learning outcomes", "", "| | By the end you can... | Practised in |", "|---|---|---|",
        *[f"| {o['id']} | {o['text']} | {cell(o['lessons'])} |" for o in u["outcomes"]], "",
        "## Lessons", "", "| Lesson | Big idea | Worked example |", "|---|---|---|",
    ]
    for L in level["lessons"]:
        ex = L.get("worked_example", {}).get("title", "") if L.get("schema") == 3 else ""
        out.append(f"| [{L['id']} · {L['title']}](#lesson-{L['id'].lower()}) | {L.get('big_idea', L['objective'])} | {ex} |")
    p = u["project"]
    out += ["", f"## Capstone: {p['title']}", "", p["summary"], "", "**Choose a question, or propose your own:**", ""]
    out += [f"- {q}" for q in p["questions"]]
    out += ["", "**Milestones:**", "", *[f"{i}. {s}" for i, s in enumerate(p["steps"], 1)], "",
            "**Assessment rubric.**", "", "| Criterion | Developing | Proficient | Advanced |", "|---|---|---|---|"]
    out += [f"| {r['part']} | {r['start']} | {r['got']} | {r['explain']} |" for r in p["rubric"]]
    out += ["", "## Tools", "", *[f"- {m}" for m in u["materials"]], "",
            "## How progress is assessed", "", u["evidence"], "",
            "## Core readings", "", *[f"- [@{r['key']}]: {r['note']}" for r in u["readings"]], "",
            ":::{dropdown} For instructors: how this level is designed", "", u["approach"], "", "**Ways to adapt it.**", ""]
    out += [f"- {x}" for x in u["udl"]]
    out += [":::", "", f"```{{include}} {media_include}", "```", ""]
    return "\n".join(out)


if __name__ == "__main__":
    sys.path.insert(0, str(BOOK / "scripts"))
    import convert  # noqa: E402
    args = sys.argv[1:]
    force = "--force" in args
    args = [a for a in args if a != "--force"]
    if args and args[0] == "--level":
        ids = None
        levels_wanted = {int(args[1])}
    else:
        ids = set(args)
        levels_wanted = {int(a[1]) for a in args}
    sys.exit(convert.build_v3(levels_wanted, ids, force=force))
