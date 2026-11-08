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
IGNORE_RE = re.compile(r"DeprecationWarning|ExperimentalWarning|trace-warnings|url\.parse|GET /|errors?=0")


def c6_build():
    errs = []
    shutil.rmtree(BOOK / "_build", ignore_errors=True)
    env = dict(os.environ, BASE_URL=BASE_URL, MSYS2_ENV_CONV_EXCL="*",
               PATH=str(VENV_SCRIPTS) + os.pathsep + os.environ.get("PATH", ""))
    jb = shutil.which("jupyter-book", path=env["PATH"])
    r = subprocess.run([jb, "build", "--html"], cwd=BOOK, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600)
    log = r.stdout + r.stderr
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
        body = "\n".join(ln for ln in text_of(f).splitlines() if not ln.startswith("| C8"))
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
        if u["id"] in ("integrate", "release-check", "style-ui", "round3-ui", "map-viewer"):
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


CHECKS = {"C1": c1_content, "C2": c2_references, "C3": c3_media, "C4": c4_science,
          "C5": c5_notebooks, "C6": c6_build, "C7": c7_browser, "C8": c8_hygiene, "C9": c9_style}


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
