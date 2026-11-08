"""Unit `textbook`: add Bareinboim's *Causal Artificial Intelligence* (causalai-book.net) as a
verified source and map course lessons to its chapters.  Run from book/.

Every chapter pointer is backed by an evidence phrase that must appear in the
book's own website text (snapshot saved to evidence/sources/causalai-book.html).
tests/test_textbook.py re-checks every phrase against that snapshot.
"""
import datetime
import html
import json
import pathlib
import re
import sys

import requests

BOOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / "scripts"))
from check import jaccard  # noqa: E402

URL = "https://causalai-book.net/"
PDF = "https://causalai.net/r102.pdf"
UA = {"User-Agent": "Mozilla/5.0 (qcai-book-verifier/1.0)"}
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

r = requests.get(URL, headers=UA, timeout=30)
snap = BOOK / "evidence" / "sources" / "causalai-book.html"
snap.parent.mkdir(parents=True, exist_ok=True)
snap.write_text(r.text, encoding="utf-8")
text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->|<[^>]+>", " ", r.text, flags=re.S)))
pdf = requests.head(PDF, headers=UA, timeout=30, allow_redirects=True)

TITLE = "Causal Artificial Intelligence: A Roadmap for Building Causally Intelligent Systems"
heading = "Causal Artificial Intelligence A Roadmap for Building Causally Intelligent Systems"
assert heading in text and "Elias Bareinboim" in text and "Draft version (Oct/11/25)" in text
j = jaccard(TITLE, heading)
assert j >= 0.8 and r.status_code == 200 and pdf.status_code == 200

# Lesson -> chapter pointers.  "evidence" must occur verbatim in the site text.
MAP = [
    ("L2-07", "Ch. 2: structural causal models and causal diagrams", "Ch. 2 Structural Causal Models; Causal Diagrams."),
    ("L2-08", "Ch. 1: Pearl's causal hierarchy (seeing, doing, imagining)", "Pearl's Causal Hierarchy."),
    ("L4-01", "Ch. 2: structural causal models", "Ch. 2 Structural Causal Models; Causal Diagrams."),
    ("L4-02", "Ch. 2: causal diagrams", "Ch. 2 Structural Causal Models; Causal Diagrams."),
    ("L4-03", "Sec. 4.2.1: identifiable and non-identifiable effects, confounding bias", "Sec. 4.2.1 Identifiable and non-identifiable effects. Confounding Bias."),
    ("L4-04", "Secs. 4.2.1 to 4.2.3: the back-door criterion and inverse probability weighting", "The Backdoor Criterion. Inverse probability Weighting/Propensity Score."),
    ("L4-05", "Secs. 4.2.5 to 4.3: the front-door case and the do-calculus", "The Front-door Case. The interventional calculus (do-calculus)."),
    ("L4-06", "Ch. 4, Secs. 4.1 and 4.2: what a causal effect is, and the identification problem", "Intuition and Definition of Causal Effects."),
    ("L4-07", "Ch. 4 (identification) and Ch. 20 (causal estimation)", "The Identification Problem"),
    ("L4-08", "Chs. 16 and 17: equivalence classes and multi-domain structure learning", "Observational Equivalence Class. Interventional Equivalence Class."),
    ("L4-09", "Ch. 5: counterfactual reasoning and the counterfactual calculus", "Ch. 5, Sec. 5.1, 5.2 Counterfactual's definition."),
    ("L4-10", "Ch. 6 (fairness), Chs. 10 to 12 (transportability), Ch. 18 (causal representation learning)", "Transportability Foundations"),
    ("L7-02", "Ch. 18: causal representation learning", "Ch. 18 Causal Representation Learning."),
]
for lesson, chap, ev in MAP:
    assert ev in text, (lesson, ev)
(BOOK / "_data" / "textbook_map.json").write_text(json.dumps(
    {"source": "bareinboim", "url": URL, "pdf": PDF, "snapshot": "evidence/sources/causalai-book.html",
     "lessons": [{"lesson": l, "chapters": c, "evidence": e} for l, c, e in MAP]}, indent=1, ensure_ascii=False), encoding="utf-8")

src = [s for s in json.loads((BOOK / "_data/sources.json").read_text(encoding="utf-8")) if s["id"] != "bareinboim"]
src.append({"id": "bareinboim", "title": TITLE, "authors": "Elias Bareinboim", "year": 2025,
            "venue": "Draft textbook (version of Oct 11, 2025), causalai-book.net", "url": URL, "kind": "book",
            "scope": "Core textbook for causal AI: SCMs, Pearl's causal hierarchy, identification, counterfactuals, fairness, transportability, causal decision-making and learning",
            "levels": [2, 4, 7]})
src.sort(key=lambda s: s["id"])
(BOOK / "_data/sources.json").write_text(json.dumps(src, indent=1, ensure_ascii=False), encoding="utf-8")
ver = json.loads((BOOK / "_data/verification.json").read_text(encoding="utf-8"))
ver["bareinboim"] = {"status": "PASS", "method": "HTTP GET; title and author found in page text; draft PDF HEAD 200",
                     "url_checked": URL, "http": r.status_code, "fetched_title": heading, "jaccard": round(j, 4),
                     "checked_at": now, "note": f"Draft version (Oct/11/25); PDF {PDF} HTTP {pdf.status_code}, {pdf.headers.get('Content-Length')} bytes"}
(BOOK / "_data/verification.json").write_text(json.dumps(ver, indent=1, ensure_ascii=False), encoding="utf-8")
bib = (BOOK / "references.bib").read_text(encoding="utf-8")
bib = re.sub(r"@\w+\{bareinboim,.*?\n\}\n", "", bib, flags=re.S).rstrip() + "\n\n"
bib += ("@book{bareinboim,\n  title = {{Causal Artificial Intelligence: A Roadmap for Building Causally Intelligent Systems}},\n"
        "  author = {Elias Bareinboim},\n  year = {2025},\n  note = {Draft version, October 11, 2025},\n"
        f"  url = {{{URL}}}\n}}\n")
(BOOK / "references.bib").write_text(bib, encoding="utf-8")
print(f"bareinboim verified (J={j:.2f}); {len(MAP)} lesson pointers backed by site text")
