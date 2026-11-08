"""Unit `pages`: generate data-driven pages from verified records.  Run from book/.

Writes reference/bibliography.md, reference/about.md,
media/watch-listen.md and media/_level-N.md.  Titles of videos and podcast
episodes are copied verbatim from the verified records.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

BOOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / "scripts"))
from convert import esc, STAGE, icon  # noqa: E402

src = json.loads((BOOK / "_data/sources.json").read_text(encoding="utf-8"))
ver = json.loads((BOOK / "_data/verification.json").read_text(encoding="utf-8"))
media_path = BOOK / "_data/media.json"
media = json.loads(media_path.read_text(encoding="utf-8")) if media_path.exists() else {"videos": [], "podcasts": []}
levels = [json.loads((BOOK / f"_data/levels/level{n}.json").read_text(encoding="utf-8")) for n in range(8)]

KIND = {"paper": "Research papers", "book": "Books", "notes": "Lecture notes and courses",
        "web": "Web resources", "software": "Software"}


def bibliography():
    out = ["---", "title: Bibliography", "subtitle: Every source used in the book, grouped by type", "---", "",
           "Each entry was checked by a script against arXiv, Crossref, or the publisher's page before it was cited. "
           "Hover a citation key to preview it; the full formatted list is at the bottom of this page.", ""]
    by = collections.defaultdict(list)
    for r in src:
        by[r.get("kind", "web")].append(r)
    for k in ["paper", "book", "notes", "software", "web"]:
        if not by.get(k):
            continue
        out += [f"## {KIND[k]}", "", "| Source | Levels | Scope |", "|---|---|---|"]
        for r in sorted(by[k], key=lambda r: (min(r.get("levels") or [9]), r["id"])):
            lv = ", ".join(str(x) for x in r.get("levels", []))
            out.append(f"| [@{r['id']}] | {lv} | {esc(r.get('scope', ''))} |")
        out.append("")
    return "\n".join(out)


def about():
    n_src, n_vid, n_pod = len(src), len(media.get("videos", [])), len(media.get("podcasts", []))
    rows = "\n".join(f"| {icon(f'level-{k}', '../')} Level {k} | {esc(levels[k]['title'])} | {STAGE[k]} |" for k in range(8))
    return "\n".join([
        "---", "title: About this book", "subtitle: What it covers, how it is built, and how to cite it", "---", "",
        "Quantum Causal AI is a free, open course written by [Amir Rafe](https://pozapas.github.io/). "
        "It asks one question at every level: what does it take to say that one thing causes another, and what changes "
        "when the things involved are quantum systems? A reader can start with no background and finish at current research.", "",
        "::::{grid} 1 1 2 2", "",
        ":::{card} The course in numbers", f"{icon('compass', '../')}", "",
        f"80 lessons in 8 levels, 11 interactive labs, {n_src} checked references, {n_vid} videos, and {n_pod} podcast episodes.", ":::", "",
        ":::{card} The core textbook", f"{icon('verified', '../')}", "",
        "For causal AI, the course follows Elias Bareinboim's *Causal Artificial Intelligence* [@bareinboim]. "
        "Lessons point to its chapters where they match.", ":::", "",
        ":::{card} Runs anywhere", f"{icon('code', '../')}", "",
        "Every lab shows its results on the page. You can also open it in Google Colab or Binder, or download it, "
        "and run it again with only standard scientific Python.", ":::", "",
        ":::{card} Open licence", f"{icon('lab', '../')}", "",
        "Text and figures are CC BY 4.0, and code is MIT. Use them in your own teaching with attribution.", ":::", "",
        "::::", "",
        "## The eight levels", "",
        "| Level | Topic | Written for |", "|---|---|---|", rows, "",
        "## How the course is checked", "",
        "Programs, not opinions, decide what goes in. A unit-test suite compares the simulation code with exact formulas, "
        "every notebook runs during the build, and `assert` cells check the key numbers. Every reference, video, and link "
        "was fetched from its source before it was listed, and a browser test opens every page. "
        "None of this is peer review, so please report anything that looks wrong.", "",
        "## How to cite", "",
        "```bibtex",
        "@misc{rafe_quantum_causal_ai,",
        "  author = {Amir Rafe},",
        "  title  = {Quantum Causal AI: An Open Course from Counting to the Research Frontier},",
        "  year   = {2026},",
        "  url    = {https://pozapas.github.io/quantum-causal-ai/}",
        "}",
        "```", "",
        "## Corrections and contributions", "",
        "Open an issue or a pull request at [github.com/pozapas/quantum-causal-ai](https://github.com/pozapas/quantum-causal-ai). "
        "Corrections to the science are the most welcome contributions.", "",
        "## Built with", "",
        "[Jupyter Book 2](https://jupyterbook.org) and [MyST](https://mystmd.org). Figures use Plotly and Matplotlib. "
        "The learning map and the placement check are small, dependency-free scripts that run in your browser.", ""])


def fmt_dur(s):
    if not s:
        return ""
    s = int(s)
    return f"{s // 3600}h {s % 3600 // 60:02d}m" if s >= 3600 else f"{s // 60} min"


def video_card(v, embed=False):
    meta = " · ".join(x for x in [esc(v["channel"]), fmt_dur(v.get("duration_s")), str(v.get("published", ""))[:4]] if x)
    if embed:
        return "\n".join([f":::{{iframe}} https://www.youtube-nocookie.com/embed/{v['id']}", ":width: 100%",
                          f"**{esc(v['title'])}**. {meta}. {esc(v.get('why', ''))}", ":::", ""])
    return "\n".join([f":::{{card}} {esc(v['title'])}", f":link: https://www.youtube.com/watch?v={v['id']}",
                      f":header: Level {v['level']} · {esc(v.get('topic', ''))}",
                      f"{meta}", "", esc(v.get("why", "")), ":::", ""])


UP = "../"


def pod_line(p):
    dur = f", {p['duration_min']} min" if p.get("duration_min") else ""
    rel = f" ({str(p.get('released', ''))[:10]})" if p.get("released") else ""
    return f"- {icon('podcast', UP)} **{esc(p['show'])}**: [{esc(p['episode'])}]({p['url']}){rel}{dur}. {esc(p.get('why', ''))}"


def media_pages():
    vids, pods = media.get("videos", []), media.get("podcasts", [])
    out = ["---", "title: Watch and listen", "subtitle: Verified lectures, explainers, and podcast episodes for every level", "---", "",
           "Every item below was confirmed to exist with its exact title and channel before it was listed. "
           "Videos open on YouTube; podcast links open the episode page.", ""]
    ap = media.get("author_podcast")
    if ap:
        eps = [q for q in pods if q.get("author")]
        out += [":::{admonition} From the course author: Decoding Causality", ":class: tip", "",
                f"{icon('podcast', '../')} A podcast series by the author of this course that walks through the ideas of "
                f"*The Book of Why*. Listen on the [show page]({ap['page']}) or watch the "
                f"[audiogram playlist on YouTube]({ap['playlist']}). Each episode below is also listed under the level it supports.", ""]
        out += [f"{k}. [{esc(q['episode'])}]({q['url']}) · Level {q['level']}, {esc(q['topic'])}" for k, q in enumerate(eps, 1)]
        out += ["", ":::", ""]
    for n in range(8):
        vs = [v for v in vids if v["level"] == n]
        ps = [p for p in pods if p["level"] == n]
        if not vs and not ps:
            continue
        out += [f"## Level {n} · {esc(levels[n]['title'])}", "", f"{icon(f'level-{n}', '../')} *{STAGE[n]}*", ""]
        if vs:
            out += ["::::{grid} 1 1 2 2", ""] + [video_card(v) for v in vs] + ["::::", ""]
        out += [pod_line(p) for p in ps] + ([""] if ps else [])
    (BOOK / "media/watch-listen.md").write_text("\n".join(out), encoding="utf-8")
    for n in range(8):
        vs = [v for v in vids if v["level"] == n]
        ps = [p for p in pods if p["level"] == n]
        part = ["## Watch & listen", ""]
        if vs:
            part.append(video_card(vs[0], embed=True))
            for v in vs[1:]:
                part.append(f"- {icon('video', '../../')} [{esc(v['title'])}](https://www.youtube.com/watch?v={v['id']}): {esc(v['channel'])}")
            part.append("")
        part += [pod_line(p).replace("(../_static", "(../../_static") for p in ps]
        if not vs and not ps:
            part = []
        part += ["", f"More for every level on the [Watch and listen](../../media/watch-listen.md) page.", ""]
        (BOOK / f"media/_level-{n}.md").write_text("\n".join(part), encoding="utf-8")


(BOOK / "reference/bibliography.md").write_text(bibliography(), encoding="utf-8")
(BOOK / "reference/about.md").write_text(about(), encoding="utf-8")
media_pages()
print(f"pages written; {len(src)} sources, {len(media['videos'])} videos, {len(media['podcasts'])} podcasts")
