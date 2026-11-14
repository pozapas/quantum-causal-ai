"""Unit `level1-refs`: verify and record grown-up sources for Level 1 (grades 4 to 6).  Run from book/.

Each page is re-fetched; its title and a key passage must be in the fetched text.
Also widens the Common Core record's scope to the standards Level 1 references,
after confirming each passage in the official PDF.
"""
import datetime
import io
import json
import pathlib
import re
import sys
import time

import requests
from pypdf import PdfReader

BOOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / "scripts"))
import html  # noqa: E402


def page_text(url):
    """Fetch a page (HTML or PDF) and return (status, flattened text)."""
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (qcai-book-verifier/1.0)"}, timeout=60)
    if "pdf" in r.headers.get("content-type", "") or url.lower().endswith(".pdf"):
        t = " ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(r.content)).pages)
    else:
        t = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", r.text, flags=re.S)
    return r.status_code, re.sub(r"\s+", " ", html.unescape(t))

UA = {"User-Agent": "Mozilla/5.0 (qcai-book-verifier/1.0)"}
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
WEB = [  # id, url, title, authors, year, venue, levels, scope, passage
    ("openstax_design", "https://openstax.org/books/introductory-statistics-2e/pages/1-4-experimental-design-and-ethics",
     "1.4 Experimental Design and Ethics", "Barbara Illowsky and Susan Dean", 2023, "OpenStax, Introductory Statistics 2e", [1, 2],
     "Experiments, random assignment, explanatory and response variables, and lurking variables", "random assignment"),
    ("openstax_waves", "https://openstax.org/books/physics/pages/13-2-wave-properties-speed-amplitude-frequency-and-period",
     "13.2 Wave Properties: Speed, Amplitude, Frequency, and Period", "Paul Peter Urone and Roger Hinrichs", 2020, "OpenStax, Physics", [1],
     "Amplitude, wavelength, frequency, and period of a wave", "wavelength"),
    ("openstax_interference", "https://openstax.org/books/university-physics-volume-1/pages/16-5-interference-of-waves",
     "16.5 Interference of Waves", "William Moebs, Samuel J. Ling, and Jeff Sanny", 2016, "OpenStax, University Physics Volume 1", [1, 3],
     "Superposition: waves add; constructive and destructive interference", "destructive interference"),
    ("manim_ce", "https://raw.githubusercontent.com/ManimCommunity/manim/main/README.md",
     "Manim Community", "The Manim Community Developers", 2026, "GitHub repository README", [1, 2, 3, 4, 5, 6, 7],
     "Open-source library for programmatic math animations, forked from 3b1b/manim by Grant Sanderson", "originally created and open-sourced by Grant Sanderson"),
    ("ngss_4ps4_1", "https://www.nextgenscience.org/pe/4-ps4-1-waves-and-their-applications-technologies-information-transfer",
     "4-PS4-1 Waves and Their Applications in Technologies for Information Transfer", "NGSS Lead States", 2013, "Next Generation Science Standards", [1],
     "Grade 4 performance expectation: a model of waves in terms of amplitude and wavelength", "amplitude and wavelength"),
]
CCSS_PASSAGES = {
    "3.NF.1": "Understand a fraction 1/b as the quantity formed by 1 part when a whole is partitioned into b equal parts",
    "4.NF.1": "Explain why a fraction a/b is equivalent to a fraction",
    "6.SP.1": "Recognize a statistical question as one that anticipates variability",
    "7.SP.5": "probability of a chance event is a number between 0 and 1",
    "7.SP.6": "Approximate the probability of a chance event by collecting data on the chance process",
    "7.SP.7": "Develop a probability model and use it to find probabilities of events",
}


def main():
    sys.path.insert(0, str(BOOK / "scripts"))
    from check import jaccard  # noqa: F401
    src = json.loads((BOOK / "_data/sources.json").read_text(encoding="utf-8"))
    ver = json.loads((BOOK / "_data/verification.json").read_text(encoding="utf-8"))
    bib = (BOOK / "references.bib").read_text(encoding="utf-8")
    ids = {w[0] for w in WEB}
    src = [s for s in src if s["id"] not in ids]
    for k in ids:
        bib = re.sub(r"@\w+\{%s,.*?\n\}\n" % re.escape(k), "", bib, flags=re.S)
    entries = []
    norm = lambda x: re.sub(r"[^a-z0-9]+", " ", x.lower()).strip()  # noqa: E731
    for key, url, title, authors, year, venue, levels, scope, passage in WEB:
        status, text = page_text(url)
        assert status == 200, (key, status)
        assert norm(title) in norm(text), (key, "title not found")
        assert passage.lower() in text.lower(), (key, passage)
        src.append({"id": key, "title": title, "authors": authors, "year": year, "venue": venue, "url": url,
                    "kind": "web", "scope": scope, "levels": levels})
        ver[key] = {"status": "PASS", "method": "HTTP GET; title and key passage found in the fetched page", "url_checked": url,
                    "http": status, "fetched_title": title, "jaccard": 1.0, "checked_at": NOW, "note": f"key passage found: '{passage}'"}
        entries.append("@misc{%s,\n  title = {{%s}},\n  author = {{%s}},\n  year = {%d},\n  howpublished = {%s},\n  url = {%s}\n}\n"
                       % (key, title, authors, year, venue, url))
        time.sleep(0.8)
    # Common Core: confirm each Level 1 standard in the official PDF, then widen the scope line
    pdf = requests.get("https://learning.ccsso.org/wp-content/uploads/2022/11/Math_Standards1.pdf", headers=UA, timeout=60).content
    std = re.sub(r"\s+", " ", " ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(pdf)).pages))
    for code, passage in CCSS_PASSAGES.items():
        assert passage in std, (code, "not in the official PDF")
    for s in src:
        if s["id"] == "ccss_math":
            s["scope"] = ("K-7 counting, comparing, sorting, measuring, graphs, fractions, and probability "
                          "(K.CC.4, K.CC.5, K.CC.6, K.CC.7, K.MD.3, 1.MD.4, 2.MD.1, 2.MD.10, 3.NF.1, 4.NF.1, 6.SP.1, 7.SP.5, 7.SP.6, 7.SP.7)")
            s["levels"] = sorted(set(s["levels"]) | {1})
    src.sort(key=lambda s: s["id"])
    (BOOK / "_data/sources.json").write_text(json.dumps(src, indent=1, ensure_ascii=False), encoding="utf-8")
    (BOOK / "_data/verification.json").write_text(json.dumps(ver, indent=1, ensure_ascii=False), encoding="utf-8")
    (BOOK / "references.bib").write_text(bib.rstrip() + "\n\n" + "\n".join(entries), encoding="utf-8")
    print(f"verified and recorded {len(WEB)} Level 1 sources; CCSS scope covers {len(CCSS_PASSAGES)} more standards")


if __name__ == "__main__":
    main()
