"""Fixed acceptance check for the Jupyter Book (see ACCEPTANCE.json).

Run from book/:   python scripts/check.py [--skip-build] [--only C1,C2]
Exit 0 only if every selected check passes.  Writes evidence/check-report.json.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import unicodedata

BOOK = pathlib.Path(__file__).resolve().parents[1]
ROOT = BOOK.parent
SRC = ROOT / "src" / "data"
if not SRC.exists():  # standalone repository: the vendored copy is the source
    SRC = BOOK / "_data" / "levels"
PY = sys.executable
VENV_SCRIPTS = pathlib.Path(PY).parent
BASE_URL = "/quantum-causal-ai"
REPORT = BOOK / "evidence" / "check-report.json"


def tokens(s: str) -> set[str]:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\\[a-zA-Z]+|[{}$]", " ", s.lower())
    return set(re.findall(r"[a-z0-9]+", s))


def jaccard(a: str, b: str) -> float:
    A, B = tokens(a), tokens(b)
    return len(A & B) / max(1, len(A | B))


def toc_files() -> list[pathlib.Path]:
    text = (BOOK / "myst.yml").read_text(encoding="utf-8")
    return [BOOK / f for f in re.findall(r"file:\s*([^\s#]+)", text)]


def book_sources() -> list[pathlib.Path]:
    files = []
    for f in toc_files():
        files.append(f)
    for f in BOOK.glob("media/_level-*.md"):
        files.append(f)
    return [f for f in files if f.exists()]


def text_of(f: pathlib.Path) -> str:
    if f.suffix == ".ipynb":
        nb = json.loads(f.read_text(encoding="utf-8"))
        return "\n".join("".join(c["source"]) for c in nb["cells"])
    return f.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
def c1_content():
    errs = []
    import convert  # noqa: E402  (scripts dir is on sys.path)

    ids, prereq = set(), {}
    n_lessons = 0
    for n in range(8):
        if (BOOK / "_data" / "levels" / f"level{n}.json").read_bytes() != (SRC / f"level{n}.json").read_bytes():
            errs.append(f"_data/levels/level{n}.json differs from reviewed src/data/level{n}.json")
        lv = json.loads((SRC / f"level{n}.json").read_text(encoding="utf-8"))
        if lv["level"] != n:
            errs.append(f"level{n}.json has level {lv['level']}")
        for L in lv["lessons"]:
            n_lessons += 1
            ids.add(L["id"])
            prereq[L["id"]] = L["prerequisites"]
            if L.get("schema") in (2, 3):
                continue  # coursebook lessons are checked by C10
            page = BOOK / "levels" / f"level-{n}" / f"{L['id']}.md"
            if not page.exists():
                errs.append(f"missing page {page.name}")
                continue
            t = page.read_text(encoding="utf-8")
            need = [L["objective"], *L["paragraphs"], L["example"], L["exercise"], L["solution"],
                    L["quiz"]["question"], *L["quiz"]["options"], L["quiz"]["explanation"], L["caution"]]
            if L.get("equation"):
                need.append(L["equation"])
            for field in need:
                if convert.esc(field) not in t:
                    errs.append(f"{L['id']}: field text dropped: {field[:40]}")
            if len(L["paragraphs"]) < 3:
                errs.append(f"{L['id']}: <3 paragraphs")
            for k in (":::{admonition} Exercise", ":::{dropdown} Solution", ":::{dropdown} Show the answer", ":::{caution}"):
                if k not in t:
                    errs.append(f"{L['id']}: missing {k}")
            for s in L["sources"]:
                if f"@{s}" not in t:
                    errs.append(f"{L['id']}: source {s} not cited")
            if not (0 <= L["quiz"]["answer"] < len(L["quiz"]["options"])):
                errs.append(f"{L['id']}: bad answer index")
    if n_lessons != 80:
        errs.append(f"expected 80 lessons, found {n_lessons}")
    for k, ps in prereq.items():
        for p in ps:
            if p not in ids:
                errs.append(f"{k}: unknown prerequisite {p}")
    # acyclic (DFS)
    state = {}

    def dfs(u):
        state[u] = 1
        for v in prereq.get(u, []):
            if state.get(v) == 1:
                errs.append(f"cycle through {u}->{v}")
            elif v not in state:
                dfs(v)
        state[u] = 2

    for u in prereq:
        if u not in state:
            dfs(u)
    return errs, {"lessons": n_lessons}


def parse_bib(text: str) -> dict[str, dict]:
    out = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        start = m.end()
        depth, i = 1, start
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[start:i - 1]
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}", body):
            fields[fm.group(1).lower()] = fm.group(2)
        out[m.group(2)] = {"type": m.group(1).lower(), **fields}
    return out


def c2_references():
    errs = []
    bib = parse_bib((BOOK / "references.bib").read_text(encoding="utf-8"))
    ver = json.loads((BOOK / "_data" / "verification.json").read_text(encoding="utf-8"))
    used = set()
    for f in book_sources():
        t = text_of(f)
        used |= set(re.findall(r"@([A-Za-z][\w-]*)", re.sub(r"`[^`]*`|\S+@\S+\.\w+", "", t)))
        used |= set(re.findall(r"\{cite[:\w]*\}`([^`]+)`", t))
    used = {u for k in used for u in k.split(",")}
    # Only keys that look like citations (exist in bib or used as [@...])
    cited = set()
    for f in book_sources():
        for grp in re.findall(r"\[([^\]]*@[^\]]*)\]", text_of(f)):
            cited |= set(re.findall(r"@([A-Za-z][\w-]*)", grp))
    for k in sorted(cited):
        if k not in bib:
            errs.append(f"cited key not in bib: {k}")
    for k, e in bib.items():
        v = ver.get(k)
        if not v or v.get("status") != "PASS":
            errs.append(f"bib entry {k} lacks PASS verification")
            continue
        t = re.sub(r"[{}]", "", e.get("title", ""))
        j = jaccard(t, v.get("fetched_title", ""))
        if j < 0.8:
            errs.append(f"{k}: bib title vs fetched title jaccard {j:.2f}")
    return errs, {"bib_entries": len(bib), "cited_keys": len(cited)}


def c3_media():
    errs = []
    media = json.loads((BOOK / "_data" / "media.json").read_text(encoding="utf-8"))
    mv = json.loads((BOOK / "_data" / "media-verification.json").read_text(encoding="utf-8"))
    flat = json.dumps(mv)
    shown = "\n".join(text_of(f) for f in book_sources()) + "\n".join(
        p.read_text(encoding="utf-8") for p in BOOK.glob("media/*.md"))
    ids_in_book = set(re.findall(r"youtube(?:-nocookie)?\.com/embed/([\w-]{11})", shown)) | set(
        re.findall(r"youtube\.com/watch\?v=([\w-]{11})", shown))
    known = {v["id"]: v for v in media["videos"]}
    vrec = {r["id"]: r for r in mv["videos"]}
    precs = mv["podcasts"]
    for vid in ids_in_book:
        if vid not in known:
            errs.append(f"video {vid} shown but not in media.json")
    plain = re.sub(r"\\(.)", r"\1", html.unescape(shown))
    for v in media["videos"]:
        rec = vrec.get(v["id"])
        if rec is None:
            errs.append(f"video {v['id']} lacks verification record")
            continue
        if rec.get("status") != 200:
            errs.append(f"video {v['id']} oEmbed status {rec.get('status')}")
        if rec.get("fetched_title") != v["title"]:
            errs.append(f"video {v['id']} title differs from oEmbed")
        if rec.get("author_name") != v["channel"]:
            errs.append(f"video {v['id']} channel differs from oEmbed")
        if v["id"] in ids_in_book and v["title"] not in plain:
            errs.append(f"video {v['id']} displayed without its exact oEmbed title")
    for pd in media.get("podcasts", []):
        ok = any(r.get("result") == "PASS" and r.get("status") == 200 and r.get("fetched_title") == pd["episode"]
                 and (r.get("trackViewUrl") == pd["url"] or r.get("episodeUrl") == pd["url"] or pd["url"] in json.dumps(r))
                 for r in precs)
        if not ok:
            errs.append(f"podcast '{pd['episode'][:40]}' lacks matching PASS record")
        if pd["episode"] not in plain:
            errs.append(f"podcast '{pd['episode'][:40]}' not displayed with exact title")
    links = BOOK / "_data" / "links.json"
    if links.exists():
        for url, rec in json.loads(links.read_text(encoding="utf-8")).items():
            if rec.get("status") == "DEFERRED" and url.startswith(("https://github.com/pozapas/quantum-causal-ai", "https://colab.research.google.com/github/pozapas/quantum-causal-ai", "https://pozapas.github.io/quantum-causal-ai")):
                continue  # created by the approved deploy step
            if rec.get("status") != "PASS":
                errs.append(f"link {url} status {rec.get('status')}")
    else:
        errs.append("_data/links.json missing (run scripts/verify_links.py)")
    return errs, {"videos": len(media["videos"]), "podcasts": len(media.get("podcasts", [])),
                  "videos_embedded": len(ids_in_book)}


def c4_science():
    r = subprocess.run([PY, "-m", "pytest", "-q", "tests"], cwd=BOOK, capture_output=True, text=True)
    tail = (r.stdout + r.stderr).strip().splitlines()[-1:]
    return ([] if r.returncode == 0 else [f"pytest exit {r.returncode}: {tail}"]), {"pytest": tail}


ALLOWED_IMPORTS = {"numpy", "scipy", "matplotlib", "plotly", "networkx", "pandas", "qcai", "sys",
                   "pathlib", "math", "json", "itertools", "functools", "collections", "IPython",
                   "dataclasses", "typing", "random", "statistics", "time", "textwrap", "warnings",
                   "string", "fractions", "cmath", "__future__", "re", "copy", "operator", "subprocess"}


def c5_notebooks():
    import nbformat
    from nbclient import NotebookClient
    errs, done = [], []
    for f in toc_files():
        if f.suffix != ".ipynb":
            continue
        t = text_of(f)
        if "fig.show(" in t or "ipywidgets" in t:
            errs.append(f"{f.name}: uses fig.show or ipywidgets")
        for mod in re.findall(r"^\s*(?:from|import)\s+([A-Za-z_][\w]*)", t, flags=re.M):
            if mod not in ALLOWED_IMPORTS:
                errs.append(f"{f.name}: import {mod} not allowed")
        nb = nbformat.read(str(f), 4)
        stored = [c for c in nb.cells if c.cell_type == "code"]
        if any(c.get("execution_count") is None for c in stored):
            errs.append(f"{f.name}: saved without executed outputs (run scripts/execute_notebooks.py)")
        if any(o.get("output_type") == "error" for c in stored for o in c.get("outputs", [])):
            errs.append(f"{f.name}: saved outputs contain an error")
        if any(("show(" in c.source or "plt.show" in c.source or "placement(" in c.source or "learning_map(" in c.source)
               and not c.get("outputs") for c in stored):
            errs.append(f"{f.name}: a figure cell has no saved output")
        if f.parent.name == "labs" and "colab-badge.svg" not in text_of(f):
            errs.append(f"{f.name}: no Open in Colab badge")
        try:
            NotebookClient(nb, timeout=300, kernel_name="qcai",
                           resources={"metadata": {"path": str(f.parent)}}).execute()
            bad = [o for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", [])
                   if o.get("output_type") == "error"]
            if bad:
                errs.append(f"{f.name}: error outputs")
            done.append(f.name)
        except Exception as e:  # noqa: BLE001
            errs.append(f"{f.name}: {type(e).__name__}: {str(e).splitlines()[-1][:200]}")
    return errs, {"executed": done}


WARN_RE = re.compile(r"⚠️|⛔|\berror\b|Error:", re.I)
# the last pattern is a warning inside the downloaded MyST theme's own template.yml, not in book content
IGNORE_RE = re.compile(r"DeprecationWarning|ExperimentalWarning|trace-warnings|url\.parse|GET /|errors?=0|template\.yml#template")


def c6_build():
    errs = []
    shutil.rmtree(BOOK / "_build", ignore_errors=True)
    env = dict(os.environ, BASE_URL=BASE_URL, MSYS2_ENV_CONV_EXCL="*",
               PATH=str(VENV_SCRIPTS) + os.pathsep + os.environ.get("PATH", ""))
    jb = shutil.which("jupyter-book", path=env["PATH"])
    r = subprocess.run([jb, "build", "--html"], cwd=BOOK, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600)
    log = r.stdout + r.stderr
    lp = subprocess.run([PY, str(BOOK / "scripts" / "postbuild_light.py")], capture_output=True, text=True)
    log += "\n" + lp.stdout + lp.stderr
    if lp.returncode != 0:
        errs.append("postbuild_light failed: " + (lp.stderr or lp.stdout).strip()[:200])
    (BOOK / "evidence" / "build.log").write_text(log, encoding="utf-8")
    if r.returncode != 0:
        errs.append(f"build exit {r.returncode}")
    bad = [ln for ln in log.splitlines() if WARN_RE.search(ln) and not IGNORE_RE.search(ln)]
    errs += [f"build log: {ln.strip()[:200]}" for ln in bad[:40]]
    html_dir = BOOK / "_build" / "html"
    missing = []
    for f in toc_files():
        rel = f.relative_to(BOOK).with_suffix("")
        slug = re.sub(r"^\d+-", "", rel.name.lower())
        hits = list(html_dir.rglob(f"{slug}/index.html")) + list(html_dir.rglob(f"{slug}.html"))
        if rel.name == "index" and rel.parent == pathlib.Path("."):
            hits = [html_dir / "index.html"] if (html_dir / "index.html").exists() else []
        elif rel.name == "index":
            hits = list(html_dir.rglob(f"{rel.parent.name.lower()}/index.html")) or list(
                html_dir.rglob(f"{rel.parent.name.lower()}*/index.html"))
        if not hits:
            missing.append(str(rel))
    errs += [f"no HTML for {m}" for m in missing]
    return errs, {"warnings": len(bad), "pages": len(list(html_dir.rglob("index.html")))}


def c7_browser():
    script = BOOK / "tests" / "browser_check.mjs"
    r = subprocess.run(["node", str(script)], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=3600)
    out = (r.stdout + r.stderr).strip()
    try:
        res = json.loads(out.splitlines()[-1])
    except Exception:  # noqa: BLE001
        return [f"browser check produced no JSON (exit {r.returncode}): {out[-400:]}"], {}
    return res.get("errors", []), {k: v for k, v in res.items() if k != "errors"}


PLACEHOLDER = re.compile(r"\b(TODO|TBD|lorem ipsum|citation needed|XXX)\b", re.I)


def c8_hygiene():
    errs = []
    for f in book_sources():
        if f.suffix == ".ipynb":  # prose only: code may hold Pauli strings such as "XXX"
            src = "\n".join("".join(c["source"]) for c in json.loads(f.read_text(encoding="utf-8"))["cells"]
                            if c["cell_type"] == "markdown")
        else:
            src = text_of(f)
        body = "\n".join(ln for ln in src.splitlines() if not ln.startswith("| C8"))
        for m in PLACEHOLDER.finditer(body):
            errs.append(f"{f.relative_to(BOOK)}: placeholder '{m.group(0)}'")
    attempts = {}
    p = BOOK / "evidence" / "attempts.jsonl"
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            r = json.loads(ln)
            attempts.setdefault(r["unit"], []).append(r)
    plan = json.loads((BOOK / "PLAN.json").read_text(encoding="utf-8"))
    for u in plan["units"]:
        recs = attempts.get(u["id"], [])
        if u["id"] in ("integrate", "release-check", "style-ui", "round3-ui", "map-viewer", "level0-release", "levels12-release", "levels37-release"):
            continue  # judged by this check itself / gated
        if not recs:
            errs.append(f"unit {u['id']}: no attempts logged")
            continue
        nums = {r["attempt"] for r in recs}
        if max(nums) > 3:
            errs.append(f"unit {u['id']}: more than 3 attempts")
        if recs[-1]["verdict"] != "PASS":
            errs.append(f"unit {u['id']}: last attempt {recs[-1]['verdict']}")
    # scope: files modified since the first logged attempt must be under allowed paths
    acc = json.loads((BOOK / "ACCEPTANCE.json").read_text(encoding="utf-8"))
    first = min(datetime.datetime.fromisoformat(json.loads(l)["at"]) for l in p.read_text(encoding="utf-8").splitlines() if l.strip())
    t0 = first.timestamp() - 3600  # include the setup hour before the first log line
    allowed = tuple(acc["allowedPaths"])
    for f in ROOT.rglob("*"):
        rel = f.relative_to(ROOT).as_posix()
        if f.is_dir() or rel.startswith(("node_modules/", ".venv/")) or f.stat().st_mtime < t0:
            continue
        if not (rel.startswith(allowed) or rel in allowed):
            errs.append(f"out-of-scope file modified: {rel}")
    return errs, {"units_logged": sorted(attempts)}


EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\uFE0F]")


def c9_style():
    errs = []
    files = set(book_sources()) | set(BOOK.glob("media/*.md")) | set(BOOK.glob("qcai/*.py")) | set(BOOK.glob("labs/*.ipynb"))
    em = emo = 0
    for f in sorted(files):
        t = text_of(f) if f.suffix in (".md", ".ipynb") else f.read_text(encoding="utf-8")
        if f.suffix == ".ipynb":
            nb = json.loads(f.read_text(encoding="utf-8"))
            t = "\n".join("".join(c["source"]) for c in nb["cells"])
        n, e = t.count("\u2014"), len(EMOJI_RE.findall(t))
        em += n; emo += e
        if n:
            errs.append(f"{f.relative_to(BOOK)}: {n} em dash(es)")
        if e:
            errs.append(f"{f.relative_to(BOOK)}: {e} emoji")
    icons = sorted(p.name for p in (BOOK / "_static" / "icons").glob("*.svg")) if (BOOK / "_static" / "icons").exists() else []
    if len(icons) < 8:
        errs.append(f"expected >= 8 SVG icons, found {len(icons)}")
    return errs, {"files": len(files), "em_dashes": em, "emoji": emo, "icons": len(icons)}


CHILD_MAX_FK = 3.0
CHILD_MAX_SENTENCE = 22
# common words of 4+ syllables that young readers meet early; anything else must be in the lesson's word box
EASY_LONG_WORDS = {"experiment", "experiments", "everything", "everyone", "anybody", "anything", "usually",
                   "information", "interesting", "television", "watermelon", "caterpillar", "helicopter", "calculator"}


def child_fields(L):
    """Child-facing text of a schema-2 lesson, one string per field."""
    out = [L["big_idea"], *L["i_can"], L["warmup"]["prompt"], L["story_title"], *L["story"], L["activity"]["title"],
           *L["activity"]["materials"], *L["activity"]["steps"], L["activity"]["record"], L["guided"]["prompt"],
           L["guided"]["answer"], *[t[k] for t in L["try_it"] for k in ("prompt", "answer")], *L["talk"], L["connect"],
           *[w["meaning"] for w in L["words"]], *([L["picture"]["caption"]] if L.get("picture") else []),
           *([L["animation"]["caption"], L["animation"]["describe"]] if L.get("animation") else [])]
    for q in L["check"]:
        out += [q["question"], *q["options"], q["explanation"]]
    return [x for x in out if x]


def reading_limits(level_json):
    """Reading limits for child-facing text; Level 0 values are the defaults."""
    r = (level_json.get("unit") or {}).get("reading", {})
    return r.get("max_fk", CHILD_MAX_FK), r.get("max_sentence", CHILD_MAX_SENTENCE), r.get("long_word_syllables", 4)


def reading_errors(L, limits):
    """Reading-level, sentence-length and long-word errors for one lesson's child text."""
    import textstat
    max_fk, max_sent, long_syl = limits
    kid = child_fields(L)
    errs = []
    if any("[@" in x for x in kid):
        errs.append("child-facing text contains a citation")
    fk = textstat.flesch_kincaid_grade(" ".join(kid))
    if fk > max_fk:
        errs.append(f"reading level {fk:.2f} > {max_fk}")
    for x in kid:
        for sent in re.split(r"(?<=[.!?])\s+|(?<=[.!?][\"\u201d])\s+", x):
            if len(sent.split()) > max_sent:
                errs.append(f"sentence of {len(sent.split())} words: {sent[:60]}")
    defined = {w for item in L["words"] for w in re.findall(r"[a-z]+", item["word"].lower())}
    def base(w):  # accept simple plurals of defined words: probabilities -> probability, trials -> trial
        w = w.lower()
        return {w, w[:-3] + "y" if w.endswith("ies") else w, w[:-2] if w.endswith("es") else w, w[:-1] if w.endswith("s") else w}
    hard = sorted({w for w in re.findall(r"[A-Za-z]+", " ".join(kid)) if textstat.syllable_count(w) >= long_syl
                   and not (base(w) & defined) and not (base(w) & EASY_LONG_WORDS)})
    if hard:
        errs.append(f"undefined long words for this age: {', '.join(hard[:8])}")
    return errs, round(fk, 2)


ANIM_MAX_BYTES = 2_500_000


def animation_errors(L):
    """Checks for a lesson animation: scene source, rendered file, codec, length, size, and facts."""
    a = L.get("animation")
    if not a:
        return []
    errs = []
    for k in ("file", "scene", "alt", "describe", "caption"):
        if not a.get(k):
            errs.append(f"animation needs '{k}'")
    if errs:
        return errs
    scene_file, _, cls = a["scene"].partition(":")
    sp = BOOK / scene_file
    if not sp.exists() or f"class {cls}(" not in sp.read_text(encoding="utf-8"):
        errs.append(f"animation scene {a['scene']} not found")
    mp4 = BOOK / "_static" / "animations" / a["file"]
    if not mp4.exists():
        errs.append(f"animation file missing: {a['file']}")
    else:
        if mp4.stat().st_size > ANIM_MAX_BYTES:
            errs.append(f"animation too large: {mp4.stat().st_size // 1000} KB")
        try:
            import av
            c = av.open(str(mp4))
            v = c.streams.video[0]
            dur = float(c.duration / 1e6)
            if v.codec_context.name != "h264" or v.codec_context.pix_fmt != "yuv420p":
                errs.append(f"animation codec {v.codec_context.name}/{v.codec_context.pix_fmt} (need h264/yuv420p)")
            if not 10 <= dur <= 45:
                errs.append(f"animation length {dur:.1f} s (need 10 to 45)")
            c.close()
        except Exception as e:  # noqa: BLE001
            errs.append(f"animation unreadable: {e}")
    # facts the animation shows must also be in the lesson text
    if sp.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"scene_{L['id'].replace('-', '_')}", sp)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            text = " ".join(child_fields(L))
            for fact in getattr(mod, "facts", lambda _L: [])(L):
                if fact not in text:
                    errs.append(f"animation shows '{fact}' but the lesson text does not")
        except Exception as e:  # noqa: BLE001
            errs.append(f"animation scene failed to load: {type(e).__name__}: {e}")
    return errs


def c10_coursebook():
    import textstat
    import coursebook
    import convert
    errs, info = [], {"lessons": 0, "fk": {}}
    for n in range(8):
        lv = json.loads((SRC / f"level{n}.json").read_text(encoding="utf-8"))
        if not lv.get("unit"):
            continue
        u = lv["unit"]
        ids = [L["id"] for L in lv["lessons"]]
        order = {lid: i for i, lid in enumerate(ids)}
        if not 6 <= len(u["outcomes"]) <= 8:
            errs.append(f"level {n}: {len(u['outcomes'])} outcomes (need 6-8)")
        for o in u["outcomes"]:
            if not any(x in ids or x == "PROJECT" for x in o["lessons"]):
                errs.append(f"level {n}: outcome {o['id']} is practised nowhere")
        adv = u.get("tier") == "advanced"
        if len(u["project"]["rubric"]) != 4 or not u["materials"] or not (u.get("readings") if adv else u["safety"]):
            errs.append(f"level {n}: project rubric, materials, and safety (or readings) missing")
        unit_md = (BOOK / "levels" / f"level-{n}" / "index.md").read_text(encoding="utf-8")
        for o in u["outcomes"]:
            if (o["text"] if adv else convert.esc(o["text"])) not in unit_md:
                errs.append(f"level {n}: outcome {o['id']} not on the unit page")
        for L in lv["lessons"]:
            lid = L["id"]
            if L.get("schema") == 3:
                import tempfile
                import nbformat
                import check_lesson_v3
                import lesson_v3
                info["lessons"] += 1
                with tempfile.TemporaryDirectory() as td:
                    tf = pathlib.Path(td) / f"{lid}.json"
                    tf.write_text(json.dumps(L, ensure_ascii=False), encoding="utf-8")
                    errs += [f"{lid}: {e}" for e in check_lesson_v3.check(tf)]
                nbp = BOOK / "levels" / f"level-{n}" / f"{lid}.ipynb"
                if not nbp.exists():
                    errs.append(f"{lid}: lesson notebook missing (run scripts/convert.py)")
                elif nbformat.read(str(nbp), 4).metadata.get("qcai", {}).get("inputs") != lesson_v3.inputs_hash(L):
                    errs.append(f"{lid}: lesson notebook out of date (run scripts/convert.py)")
                continue
            if L.get("schema") != 2:
                errs.append(f"{lid}: not yet in coursebook format")
                continue
            info["lessons"] += 1
            a, gr = L["activity"], L["grownups"]
            need = [
                (2 <= len(L["i_can"]) <= 3, "2-3 I-can statements"), (1 <= len(L["words"]) <= 3, "1-3 words"),
                ((order[lid] == 0 and not L["warmup"].get("recall_of")) or (L["warmup"].get("recall_of") in order and order[L["warmup"]["recall_of"]] < order[lid]), "warm-up recalls an earlier lesson (none for the first lesson)"),
                (len(L["story"]) >= 3, "story of 3+ paragraphs"), (len(a["steps"]) >= 4, "4+ activity steps"),
                (0 < a["minutes"] <= 20, "activity <= 20 minutes"), (bool(a["record"]) and bool(a["safety"]), "record and safety line"),
                (len(L["try_it"]) >= 2, "2+ tries"), (len(L["talk"]) >= 2, "2+ talk prompts"), (len(L["check"]) == 3, "exactly 3 checks"),
                (sum(1 for q in L["check"] if q.get("review_of")) == (0 if order[lid] == 0 else 1), "exactly one review check (none for the first lesson)"),
                (all(order.get(q["review_of"], 99) < order[lid] for q in L["check"] if q.get("review_of")), "review points to an earlier lesson"),
                (all(0 <= q["answer"] < len(q["options"]) and len(set(q["options"])) == len(q["options"]) for q in L["check"]), "valid check answers"),
                (bool(L["connect"]), "where-this-leads box"),
                (bool(gr["why"]) and len(gr["misconceptions"]) >= 2 and bool(gr["simplify"]) and bool(gr["extend"]) and bool(L["caution"]), "full grown-up guide"),
            ]
            errs += [f"{lid}: needs {why}" for ok, why in need if not ok]
            if L.get("picture") and not (BOOK / "_static" / "lessons" / L["picture"]["file"]).exists():
                errs.append(f"{lid}: picture file missing")
            page = (BOOK / "levels" / f"level-{n}" / f"{lid}.md").read_text(encoding="utf-8")
            fields = child_fields(L) + [gr["why"], *gr["misconceptions"], gr["simplify"], gr["extend"], L["caution"]]
            for f in fields:
                if coursebook.esc_cite(f, convert.esc) not in page:
                    errs.append(f"{lid}: field missing from page: {f[:50]}")
            rerrs, fk = reading_errors(L, reading_limits(lv))
            info["fk"][lid] = fk
            errs += [f"{lid}: {e}" for e in rerrs]
            errs += [f"{lid}: {e}" for e in animation_errors(L)]
    return errs, info


CHECKS = {"C1": c1_content, "C2": c2_references, "C3": c3_media, "C4": c4_science,
          "C5": c5_notebooks, "C6": c6_build, "C7": c7_browser, "C8": c8_hygiene, "C9": c9_style, "C10": c10_coursebook}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--skip-build", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, str(BOOK / "scripts"))
    sel = [c for c in CHECKS if not a.only or c in a.only.split(",")]
    if a.skip_build:
        sel = [c for c in sel if c not in ("C5", "C6", "C7")]
    report = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "checks": {}}
    ok = True
    for c in sel:
        try:
            errs, info = CHECKS[c]()
        except Exception as e:  # noqa: BLE001
            errs, info = [f"check crashed: {type(e).__name__}: {e}"], {}
        status = "PASS" if not errs else "FAIL"
        ok &= status == "PASS"
        report["checks"][c] = {"status": status, "info": info, "errors": errs[:100]}
        print(f"{c}: {status} {json.dumps(info, ensure_ascii=False)[:300]}")
        for e in errs[:15]:
            print("   -", e)
    if not a.only and not a.skip_build:
        report["overall"] = "PASS" if ok else "FAIL"
        REPORT.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    else:
        (BOOK / "evidence" / "check-partial.json").write_text(json.dumps(report, indent=1, ensure_ascii=False),
                                                              encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
