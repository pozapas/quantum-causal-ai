"""Check one advanced (schema 3) lesson draft, Levels 3-7.  Run from book/.

    python scripts/check_lesson_v3.py _data/level3_drafts/L3-01.json [more drafts...]

Structure, media mix, rendered animations (codec, length, size, on-screen facts present in
the text), figure functions (they run and return the right kind of figure), runnable code
blocks, citation keys, and house style (no em dashes or emoji).  Exit 0 only if every draft passes.
"""
from __future__ import annotations

import contextlib
import importlib
import importlib.util
import io
import json
import pathlib
import re
import sys

BOOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK))
sys.path.insert(0, str(BOOK / "scripts"))
from check import ALLOWED_IMPORTS, EMOJI_RE  # noqa: E402

KEYS = {s["id"] for s in json.loads((BOOK / "_data/sources.json").read_text(encoding="utf-8"))}
LABS = {"chance", "bayes", "causal", "interference", "qubit", "bell", "noise", "gradient", "switch", "shadows", "qcausal"}
REQUIRED = ["id", "schema", "title", "objective", "big_idea", "prerequisites", "time_minutes", "outcomes", "key_terms",
            "motivation", "sections", "worked_example", "exercises", "check", "misconceptions", "connect", "instructor",
            "caution", "sources", "lab"]
BLOCKS = {"text", "equation", "definition", "theorem", "proposition", "lemma", "corollary", "remark", "example",
          "algorithm", "axiom", "conjecture", "assumption", "proof", "callout", "animation", "diagram", "interactive",
          "figure", "code"}
MAX_BYTES = 3_500_000
MIN_ANIM = {3: 2, 4: 2, 5: 2, 6: 3, 7: 3}


def all_ids():
    out = []
    for n in range(8):
        f = BOOK.parent / "src" / "data" / f"level{n}.json"
        if not f.exists():
            f = BOOK / "_data" / "levels" / f"level{n}.json"
        out += [L["id"] for L in json.loads(f.read_text(encoding="utf-8"))["lessons"]]
    return out


def text_of(L) -> str:
    """All string values of the lesson, joined (raw text, not JSON-escaped)."""
    out = []

    def walk(x):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(L)
    return " | ".join(out)


def video_errors(path: pathlib.Path) -> list[str]:
    errs = []
    if path.stat().st_size > MAX_BYTES:
        errs.append(f"{path.name}: {path.stat().st_size // 1000} KB (max {MAX_BYTES // 1000})")
    import av
    c = av.open(str(path))
    v = c.streams.video[0]
    dur = float(c.duration / 1e6)
    if v.codec_context.name != "h264" or v.codec_context.pix_fmt != "yuv420p":
        errs.append(f"{path.name}: codec {v.codec_context.name}/{v.codec_context.pix_fmt} (need h264/yuv420p)")
    if not 12 <= dur <= 90:
        errs.append(f"{path.name}: {dur:.1f} s (need 12 to 90)")
    c.close()
    return errs


def check(path) -> list[str]:
    L = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if k not in L]
    if missing:
        return [f"missing keys: {missing}"]
    errs: list[str] = []
    lid = L["id"]
    n = int(lid[1])
    ids = all_ids()
    earlier = ids[:ids.index(lid)]
    w, ins = L["worked_example"], L["instructor"]
    levels = [e["level"] for e in L["exercises"]]
    rules = [
        (L["schema"] == 3, "schema must be 3"),
        (2 <= len(L["outcomes"]) <= 4, "2-4 outcomes"),
        (3 <= len(L["key_terms"]) <= 7 and all(k.get("term") and k.get("meaning") for k in L["key_terms"]), "3-7 key terms"),
        (len(L["motivation"]) >= 2, "2+ motivation paragraphs"),
        (3 <= len(L["sections"]) <= 7, "3-7 sections"),
        (all(s.get("heading") and len(s.get("blocks", [])) >= 2 for s in L["sections"]), "each section: heading and 2+ blocks"),
        (bool(w.get("problem")) and len(w.get("steps", [])) >= 3 and bool(w.get("result")), "worked example with 3+ steps"),
        (4 <= len(L["exercises"]) <= 7 and {"core", "stretch", "challenge"} <= set(levels)
         and all(e.get("prompt") and e.get("solution") for e in L["exercises"]), "4-7 exercises incl. core, stretch, challenge"),
        (3 <= len(L["check"]) <= 4, "3-4 checks"),
        (sum(1 for q in L["check"] if q.get("review_of")) == 1, "exactly one review check"),
        (all(q["review_of"] in earlier for q in L["check"] if q.get("review_of")), "review_of must be an earlier lesson"),
        (all(0 <= q["answer"] < len(q["options"]) and len(set(q["options"])) == len(q["options"]) and 3 <= len(q["options"]) <= 4
             and q.get("explanation") for q in L["check"]), "each check: 3-4 distinct options, valid answer, explanation"),
        (len(L["misconceptions"]) >= 2 and all(m.get("claim") and m.get("correction") for m in L["misconceptions"]), "2+ misconceptions"),
        (bool(L["connect"]) and bool(L["caution"]), "connect and caution text"),
        (bool(ins.get("why")) and len(ins.get("teaching_notes", [])) >= 2 and bool(ins.get("assessment")) and bool(ins.get("extend")),
         "full instructor notes"),
        (all(p in earlier for p in L["prerequisites"]), "prerequisites must be earlier lessons"),
        (L["lab"] in LABS, f"lab key one of {sorted(LABS)}"),
        (45 <= L["time_minutes"] <= 150, "time_minutes 45-150"),
        (len(L["sources"]) >= 3, "3+ sources"),
    ]
    errs += [f"needs: {why}" for ok, why in rules if not ok]

    bl = [b for s in L["sections"] for b in s["blocks"]]
    bad = sorted({b.get("type") for b in bl} - BLOCKS)
    if bad:
        errs.append(f"unknown block types {bad}")
    kinds = [b.get("type") for b in bl]
    if kinds.count("animation") < MIN_ANIM[n]:
        errs.append(f"needs {MIN_ANIM[n]}+ animations (has {kinds.count('animation')})")
    if "interactive" not in kinds:
        errs.append("needs 1+ interactive figure")
    if "code" not in kinds:
        errs.append("needs 1+ runnable code block")
    if not ({"figure", "diagram"} & set(kinds)):
        errs.append("needs 1+ static figure or diagram")
    if len(set(kinds) - {"text"}) < 5:
        errs.append("needs 5+ different non-text block types (media and mathematics mix)")

    # animations
    anims = [b for b in bl if b["type"] == "animation"]
    files = [a.get("file") for a in anims]
    if len(set(files)) != len(files):
        errs.append("animation files must be unique")
    scene_file = BOOK / "scripts" / "manim" / f"{lid.lower().replace('-', '_')}.py"
    for a in anims:
        for k in ("file", "scene", "alt", "caption", "describe"):
            if not a.get(k):
                errs.append(f"animation needs '{k}'")
        if not a.get("file", "").startswith(lid.lower().replace("-", "_") + "_"):
            errs.append(f"animation file {a.get('file')} must start with {lid.lower().replace('-', '_')}_")
        sf, _, cls = a.get("scene", "").partition(":")
        if BOOK / sf != scene_file:
            errs.append(f"animation scene must live in scripts/manim/{scene_file.name}")
        elif not scene_file.exists() or f"class {cls}(" not in scene_file.read_text(encoding="utf-8"):
            errs.append(f"scene {a.get('scene')} not found")
        mp4 = BOOK / "_static" / "animations" / a.get("file", "__none__")
        if not mp4.exists():
            errs.append(f"animation not rendered: {a.get('file')} (run scripts/render_lesson_media.py)")
        else:
            errs += video_errors(mp4)
    if scene_file.exists():
        spec = importlib.util.spec_from_file_location(f"scene_{lid.replace('-', '_')}", scene_file)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            if not hasattr(mod, "facts"):
                errs.append(f"{scene_file.name} must define facts(L): strings shown on screen that also appear in the text")
            else:
                fs = mod.facts(L)
                blob = text_of(L)
                if len(fs) < 3:
                    errs.append("facts(L) must return 3+ strings")
                miss = [f for f in fs if f not in blob]
                if miss:
                    errs.append(f"on-screen facts missing from the lesson text: {miss[:4]}")
        except Exception as e:  # noqa: BLE001
            errs.append(f"{scene_file.name} failed to import: {type(e).__name__}: {e}")

    # figure functions
    mname = lid.lower().replace("-", "_")
    figfuncs = [b for b in bl if b["type"] in ("interactive", "figure")]
    if figfuncs:
        try:
            mod = importlib.import_module(f"qcai.lessonfigs.{mname}")
            importlib.reload(mod)
            for b in figfuncs:
                fn = getattr(mod, b.get("func", ""), None)
                if fn is None:
                    errs.append(f"qcai/lessonfigs/{mname}.py has no function {b.get('func')}")
                    continue
                fig = fn()
                if b["type"] == "interactive":
                    import plotly.graph_objects as go
                    if not isinstance(fig, go.Figure):
                        errs.append(f"{b['func']} must return a plotly Figure")
                    elif not (fig.layout.meta and "qcai" in fig.layout.meta):
                        errs.append(f"{b['func']}: lay the figure out with qcai.viz.frame(...)")
                    for k in ("caption", "describe"):
                        if not b.get(k):
                            errs.append(f"interactive {b['func']} needs '{k}'")
                else:
                    import matplotlib.figure
                    import matplotlib.pyplot as plt
                    if not isinstance(fig, matplotlib.figure.Figure):
                        errs.append(f"{b['func']} must return a matplotlib Figure")
                    else:
                        plt.close(fig)
                    if not b.get("caption"):
                        errs.append(f"figure {b['func']} needs a caption")
        except Exception as e:  # noqa: BLE001
            errs.append(f"qcai/lessonfigs/{mname}.py: {type(e).__name__}: {e}")
        src = (BOOK / "qcai" / "lessonfigs" / f"{mname}.py")
        if src.exists():
            for m in re.findall(r"^\s*(?:from|import)\s+([A-Za-z_]\w*)", src.read_text(encoding="utf-8"), flags=re.M):
                if m not in ALLOWED_IMPORTS:
                    errs.append(f"lessonfigs/{mname}.py imports {m} (not allowed)")

    # code blocks run, in order, in one namespace (like the notebook)
    ns: dict = {}
    for b in bl:
        if b["type"] != "code":
            continue
        for m in re.findall(r"^\s*(?:from|import)\s+([A-Za-z_]\w*)", b["source"], flags=re.M):
            if m not in ALLOWED_IMPORTS:
                errs.append(f"code block imports {m} (not allowed)")
        if "fig.show(" in b["source"] or "plt.show" in b["source"]:
            errs.append("code blocks must not call fig.show or plt.show (print results; figures go in figure blocks)")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(b["source"], f"{lid}-code", "exec"), ns)  # noqa: S102
        except Exception as e:  # noqa: BLE001
            errs.append(f"code block failed: {type(e).__name__}: {e}")
    for b in bl:
        if b["type"] == "diagram" and not (b.get("mermaid") and b.get("caption")):
            errs.append("diagram needs mermaid source and caption")

    # citations, style
    blob = text_of(L)
    cited = set(re.findall(r"\[@([A-Za-z][\w-]*)", blob)) | set(re.findall(r";\s*@([A-Za-z][\w-]*)", blob)) | set(L["sources"])
    cited |= {f["key"] for f in L.get("further", [])}
    unknown = sorted(cited - KEYS)
    if unknown:
        errs.append(f"unknown source keys: {unknown}")
    if "—" in blob:
        errs.append("em dash found")
    if EMOJI_RE.search(blob):
        errs.append("emoji found")
    if re.search(r"\bTODO\b|lorem ipsum|\bTBD\b", blob, re.I):
        errs.append("placeholder text found")
    for q in L["check"]:
        if re.search(r"(option|answer) [ABCD]\b", q["explanation"], re.I):
            errs.append("check explanations must not refer to letters (options are shuffled)")
    return errs


if __name__ == "__main__":
    ok = True
    for f in sys.argv[1:]:
        errs = check(f)
        print(f"{pathlib.Path(f).name}: {'PASS' if not errs else 'FAIL'}")
        for e in errs:
            print("   -", e)
        ok &= not errs
    sys.exit(0 if ok else 1)
