"""Coursebook renderer: schema-2 lessons and the unit syllabus page.

Used by convert.py for any lesson with "schema": 2 and any level with a "unit"
block.  Levels without those keys render exactly as before.  Child-facing text is
escaped plainly; grown-up text keeps [@key] citations.
"""
from __future__ import annotations

import json
import re

LETTERS = "ABCD"
CITE = re.compile(r"(\[@[^\]]+\])")


def esc_cite(text: str, esc) -> str:
    """Escape prose but keep MyST citation groups like [@a; @b] intact."""
    return "".join(part if CITE.fullmatch(part) else esc(part) for part in CITE.split(text))


def lesson_link(lid: str) -> str:
    return f"[{lid}](#lesson-{lid.lower()})"


def lesson_v2(level: dict, L: dict, nxt: dict, *, esc, icon_md: str, stage: str, lab: tuple[str, str]) -> str:
    n = level["level"]
    title_by_id = {x["id"]: x["title"] for x in level["lessons"]}
    lab_file, lab_title = lab
    out = [
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
        f"**Big idea.** {esc(L['big_idea'])}  ",
        ("**Before this lesson.** " + ", ".join(lesson_link(p) for p in L["prerequisites"]) + "  ")
        if L["prerequisites"] else "**Before this lesson.** Nothing. Start here.  ",
        "**Grown-ups.** The guide for adults is at the end of this page.",
        ":::",
        "",
        "## What you will learn",
        "",
        *[f"- {esc(s)}" for s in L["i_can"]],
        "",
        ":::{note} Warm up",
        esc(L["warmup"]["prompt"]),
        *(["", f"Need a reminder? Look back at {lesson_link(L['warmup']['recall_of'])} · {esc(title_by_id.get(L['warmup']['recall_of'], ''))}."]
          if L["warmup"].get("recall_of") else []),
        ":::",
        "",
        f"## Story: {esc(L['story_title'])}",
        "",
    ]
    for p in L["story"]:
        out += [esc(p), ""]
    if L.get("picture"):
        pic = L["picture"]
        out += [f":::{{figure}} ../../_static/lessons/{pic['file']}", f":alt: {pic['alt']}", ":width: 100%", "",
                esc(pic["caption"]), ":::", ""]

    a = L["activity"]
    out += [f"## Hands-on: {esc(a['title'])}", "", f"*About {a['minutes']} minutes.*", "", "**You need:**", ""]
    out += [f"- {esc(m)}" for m in a["materials"]]
    out += ["", "**Steps:**", ""]
    out += [f"{i}. {esc(s)}" for i, s in enumerate(a["steps"], 1)]
    out += ["", ":::{tip} Record it", esc(a["record"]), ":::", "",
            ":::{warning} Stay safe", esc(a["safety"]), ":::", ""]

    g = L["guided"]
    out += ["## Practice together", "", esc(g["prompt"]), "", ":::{dropdown} Check your answer", esc(g["answer"]), ":::", "",
            "## Try it yourself", ""]
    for i, t in enumerate(L["try_it"], 1):
        out += [f"**{i}.** {esc(t['prompt'])}", "", ":::{dropdown} Check your answer", esc(t["answer"]), ":::", ""]

    out += ["## Talk about it", "", *[f"- {esc(t)}" for t in L["talk"]], "", "## Check yourself", ""]
    for i, q in enumerate(L["check"], 1):
        tag = f" *(Review of {q['review_of']})*" if q.get("review_of") else ""
        out += [f"**{i}. {esc(q['question'])}**{tag}", ""]
        out += [f"- **{LETTERS[k]}.** {esc(o)}" for k, o in enumerate(q["options"])]
        out += ["", ":::{dropdown} Show the answer",
                f"**{LETTERS[q['answer']]}. {esc(q['options'][q['answer']])}**", "", esc(q["explanation"]), ":::", ""]

    out += [":::{seealso} Where this leads", esc(L["connect"]), ":::", "", "## Words to know", ""]
    for w in L["words"]:
        out += [f"**{esc(w['word'])}**", f": {esc(w['meaning'])}", ""]

    gr = L["grownups"]
    out += [":::{dropdown} For grown-ups: about this lesson", ":open:", "",
            "**Why it matters.** " + esc_cite(gr["why"], esc), "",
            "**Watch for these mix-ups.**", ""]
    out += [f"- {esc(m)}" for m in gr["misconceptions"]]
    out += ["", "**To make it easier.** " + esc_cite(gr["simplify"], esc), "",
            "**To make it harder.** " + esc_cite(gr["extend"], esc), "",
            "**Limits.** " + esc(L["caution"]), "",
            f"**On the computer.** Grown-ups can see where this idea leads later in [Lab: {lab_title}](../../labs/{lab_file}.ipynb), "
            "written for older learners.", ""]
    if L.get("sources"):
        out += ["**Sources for this guide.** [" + "; ".join(f"@{s}" for s in L["sources"]) + "]", ""]
    out += [":::", ""]

    if nxt.get(L["id"]):
        nid, ntitle = nxt[L["id"]]
        out += [f"**Next:** [{nid} · {esc(ntitle)}](#lesson-{nid.lower()})", ""]
    return "\n".join(out)


def unit_page(level: dict, *, esc, icon_md: str, stage: str, media_include: str) -> str:
    n, u = level["level"], level["unit"]
    by_id = {L["id"]: L for L in level["lessons"]}
    t = u["time"]
    total = t["lessons"] + t["project_sessions"]

    def lessons_cell(ids):
        return ", ".join("project" if i == "PROJECT" else lesson_link(i) for i in ids)

    out = [
        "---",
        f"title: {json.dumps(f'Level {n} · ' + level['title'], ensure_ascii=False)}",
        f"short_title: {json.dumps(f'Level {n} · ' + level['title'], ensure_ascii=False)}",
        f"subtitle: {json.dumps(level['audience'], ensure_ascii=False)}",
        "---",
        "",
        f"(level-{n})=",
        "",
        ":::{div}",
        f":class: qcai-level-hero qcai-level-{n}",
        f"{icon_md} **{stage}**: {esc(level['audience'])}",
        "",
        f"**The big question:** {esc(u['big_question'])}",
        "",
        esc(u["summary"]),
        ":::",
        "",
        "## At a glance",
        "",
        "| | |",
        "|---|---|",
        f"| Who it is for | {esc(u['for_whom'])} |",
        f"| Lessons | {t['lessons']} lessons of about {t['minutes_per_lesson']} minutes, plus a {t['project_sessions']}-part final project |",
        f"| Pace | {esc(t['pace'])} |",
        f"| Total sittings | {total} |",
        "",
        "## How a lesson works",
        "",
        *[f"{i}. {esc(s)}" for i, s in enumerate(u["session_flow"], 1)],
        "",
        "## What you will be able to do",
        "",
        "| | I can... | Practised in |",
        "|---|---|---|",
        *[f"| {o['id']} | {esc(o['text'])} | {lessons_cell(o['lessons'])} |" for o in u["outcomes"]],
        "",
        "## Lessons",
        "",
        "| Lesson | Big idea | Hands-on |",
        "|---|---|---|",
    ]
    for L in level["lessons"]:
        idea = L.get("big_idea", L["objective"])
        act = L["activity"]["title"] if L.get("activity") else "Exercise and lab"
        out.append(f"| [{L['id']} · {esc(L['title'])}](#lesson-{L['id'].lower()}) | {esc(idea)} | {esc(act)} |")
    p = u["project"]
    out += ["", f"## Final project: {esc(p['title'])}", "", esc(p["summary"]), "", "**Pick one question, or make up your own:**", ""]
    out += [f"- {esc(q)}" for q in p["questions"]]
    out += ["", "**Steps:**", "", *[f"{i}. {esc(s)}" for i, s in enumerate(p["steps"], 1)], "",
            *([":::{warning} Project safety", esc(p["safety"]), ":::", ""] if p.get("safety") else []),
            "**How it is checked.** Each part has three steps up. Celebrate every step.", "",
            "| Part | Getting started | Got it | Can explain it |", "|---|---|---|---|"]
    out += [f"| {esc(r['part'])} | {esc(r['start'])} | {esc(r['got'])} | {esc(r['explain'])} |" for r in p["rubric"]]
    out += ["", "## Materials for the whole unit", "", *[f"- {esc(m)}" for m in u["materials"]], "",
            ":::{warning} Safety", esc(u["safety"]), ":::", "",
            "## How progress is checked", "", esc(u["evidence"]), "",
            ":::{dropdown} For grown-ups: how this unit is designed", ":open:", "",
            esc_cite(u["approach"], esc), "", "**Ways to adapt it.**", ""]
    out += [f"- {esc(x)}" for x in u["udl"]]
    out += ["", "**Connections to school standards.** These lessons connect to, but do not replace, the standards below.", "",
            "| Standard | What it asks | Source |", "|---|---|---|"]
    out += [f"| {esc(s['code'])} | {esc(s['text'])} | [@{s['key']}] |" for s in u["standards"]]
    out += [":::", "", f"```{{include}} {media_include}", "```", ""]
    return "\n".join(out)
