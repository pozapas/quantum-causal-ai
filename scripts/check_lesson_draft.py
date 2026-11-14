"""Check one coursebook lesson draft before it is merged.  Run from book/.

    python scripts/check_lesson_draft.py _data/level0_drafts/L0-01.json

Applies the C10 content rules to a single draft (structure, reading level, long
words, sentence length, no child citations, safety line), plus: grown-up
citations must be verified source keys, no em dashes or emoji anywhere, and the
picture SVG must exist, be self-contained, and carry a <title> and <desc>.
Exit 0 only if the draft passes.
"""
import json
import pathlib
import re
import sys

BOOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / "scripts"))
import textstat  # noqa: E402
from check import (EMOJI_RE, animation_errors, child_fields, reading_errors, reading_limits)  # noqa: E402

ORDER = [f"L0-{i:02d}" for i in range(1, 11)]  # Level 0 order (kept for merge_level0.py)
KEYS = {s["id"] for s in json.loads((BOOK / "_data/sources.json").read_text(encoding="utf-8"))}
REQUIRED = ["id", "schema", "title", "objective", "prerequisites", "time_minutes", "big_idea", "i_can", "words", "warmup",
            "story_title", "story", "activity", "guided", "try_it", "talk", "check", "connect", "grownups",
            "caution", "sources", "lab"]


def check(path):
    L = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    errs = []
    missing = [k for k in REQUIRED if k not in L]
    if missing:
        return [f"missing keys: {missing}"]
    if not (L.get("picture") or L.get("animation")):
        return ["needs a picture or an animation"]
    lid = L["id"]
    n = int(lid[1])
    level_json = json.loads((BOOK.parent / "src" / "data" / f"level{n}.json").read_text(encoding="utf-8"))
    order = [f"L{n}-{k:02d}" for k in range(1, 11)]
    i = order.index(lid)
    a, gr = L["activity"], L["grownups"]
    rules = [
        (L["schema"] == 2, "schema must be 2"),
        (2 <= len(L["i_can"]) <= 3, "2-3 I-can statements"), (1 <= len(L["words"]) <= 3, "1-3 words"),
        ((i == 0 and not L["warmup"].get("recall_of")) or (L["warmup"].get("recall_of") in order[:i]),
         "warm-up recall_of must be an earlier lesson (null for L0-01)"),
        (len(L["story"]) >= 3, "story of 3+ paragraphs"), (len(a["steps"]) >= 4, "4+ activity steps"),
        (0 < a["minutes"] <= 20, "activity minutes 1-20"), (bool(a["record"]) and bool(a["safety"]), "record and safety line"),
        (bool(a["materials"]), "materials list"), (len(L["try_it"]) >= 2, "2+ tries"), (len(L["talk"]) >= 2, "2+ talk prompts"),
        (len(L["check"]) == 3, "exactly 3 checks"),
        (sum(1 for q in L["check"] if q.get("review_of")) == (0 if i == 0 else 1), "exactly one review check (none for L0-01)"),
        (all(q.get("review_of") in order[:i] for q in L["check"] if q.get("review_of")), "review_of must be an earlier lesson"),
        (all(0 <= q["answer"] < len(q["options"]) and len(set(q["options"])) == len(q["options"]) and 3 <= len(q["options"]) <= 4
             for q in L["check"]), "each check: 3-4 distinct options and a valid answer index"),
        (bool(L["connect"]), "where-this-leads text"),
        (bool(gr["why"]) and len(gr["misconceptions"]) >= 2 and bool(gr["simplify"]) and bool(gr["extend"]) and bool(L["caution"]),
         "full grown-up guide"),
        (all(p in order[:i] or int(p[1]) < n for p in L["prerequisites"]), "prerequisites must be earlier lessons"),
        (L["lab"] in {"chance", "bayes", "causal", "interference", "qubit", "bell", "noise", "gradient"}, "lab key"),
        (20 <= L["time_minutes"] <= (35 if n == 0 else 45), "time_minutes 20-35 (Level 0) or 20-45"),
    ]
    errs += [f"needs: {why}" for ok, why in rules if not ok]

    rerrs, fk = reading_errors(L, reading_limits(level_json))
    errs += rerrs + animation_errors(L)

    grown = " ".join([gr["why"], *gr["misconceptions"], gr["simplify"], gr["extend"], L["caution"]])
    cited = set(re.findall(r"@([A-Za-z][\w-]*)", grown)) | set(L["sources"])
    unknown = sorted(cited - KEYS)
    if unknown:
        errs.append(f"unknown source keys: {unknown}")
    if set(re.findall(r"@([A-Za-z][\w-]*)", grown)) - set(L["sources"]):
        errs.append("every key cited in the grown-up guide must also be listed in sources")

    blob = json.dumps(L, ensure_ascii=False)
    if "—" in blob:
        errs.append("em dash found")
    if EMOJI_RE.search(blob):
        errs.append("emoji found")

    svg = BOOK / "_static" / "lessons" / (L["picture"]["file"] if L.get("picture") else "__none__")
    if not L.get("picture"):
        pass
    elif not svg.exists():
        errs.append(f"picture missing: {svg.name}")
    else:
        t = svg.read_text(encoding="utf-8")
        if not t.lstrip().startswith("<svg") or "<title" not in t or "<desc" not in t:
            errs.append("SVG must start with <svg> and include <title> and <desc>")
        if re.search(r"<script|javascript:|href=\"http|@import|\son\w+=", t, re.I):
            errs.append("SVG must be self-contained (no scripts, events, or external links)")
        if "—" in t or EMOJI_RE.search(t):
            errs.append("SVG contains an em dash or emoji")
    return errs, round(fk, 2)


if __name__ == "__main__":
    ok = True
    for f in sys.argv[1:]:
        res = check(f)
        errs, fk = (res, None) if isinstance(res, list) else res
        print(f"{pathlib.Path(f).name}: {'PASS' if not errs else 'FAIL'} (reading level {fk})")
        for e in errs:
            print("   -", e)
        ok &= not errs
    sys.exit(0 if ok else 1)
