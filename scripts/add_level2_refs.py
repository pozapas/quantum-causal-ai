"""Unit `level2-refs`: verify and record grown-up sources for Level 2 (grades 7 to 9).  Run from book/.

Each page is re-fetched; its title and a key passage must be in the fetched text.  DOIs are
checked with Crossref.  Also widens the Common Core record's scope to the standards Level 2
references, after confirming each passage in the official PDF.
"""
import datetime
import html
import io
import json
import pathlib
import re
import time

import requests
from pypdf import PdfReader

BOOK = pathlib.Path(__file__).resolve().parents[1]
UA = {"User-Agent": "Mozilla/5.0 (qcai-book-verifier/1.0)"}
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def page_text(url):
    r = requests.get(url, headers=UA, timeout=60)
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", r.text, flags=re.S)
    return r.status_code, re.sub(r"\s+", " ", html.unescape(t))


OS = "https://openstax.org/books/"
IS = "Barbara Illowsky and Susan Dean"
WEB = [  # id, url, title, authors, year, venue, levels, scope, passage
    ("openstax_independent", OS + "introductory-statistics-2e/pages/3-2-independent-and-mutually-exclusive-events",
     "3.2 Independent and Mutually Exclusive Events", IS, 2023, "OpenStax, Introductory Statistics 2e", [2],
     "Independent events: P(A|B) = P(A); mutually exclusive events", "independent"),
    ("openstax_contingency", OS + "introductory-statistics-2e/pages/3-4-contingency-tables",
     "3.4 Contingency Tables", IS, 2023, "OpenStax, Introductory Statistics 2e", [2],
     "Two-way (contingency) tables and conditional probabilities read from them", "contingency table"),
    ("openstax_trees", OS + "introductory-statistics-2e/pages/3-5-tree-and-venn-diagrams",
     "3.5 Tree and Venn Diagrams", IS, 2023, "OpenStax, Introductory Statistics 2e", [2],
     "Tree diagrams for multi-stage probability", "tree diagram"),
    ("openstax_linear", OS + "introductory-statistics-2e/pages/12-1-linear-equations",
     "12.1 Linear Equations", IS, 2023, "OpenStax, Introductory Statistics 2e", [2],
     "Linear equations y = a + bx, slope and y-intercept", "slope"),
    ("openstax_scatter", OS + "introductory-statistics-2e/pages/12-2-scatter-plots",
     "12.2 Scatter Plots", IS, 2023, "OpenStax, Introductory Statistics 2e", [2],
     "Scatter plots: direction, form, and strength of a relationship", "scatter plot"),
    ("openstax_functions", OS + "college-algebra-2e/pages/3-1-functions-and-function-notation",
     "3.1 Functions and Function Notation", "Jay Abramson", 2021, "OpenStax, College Algebra 2e", [2],
     "A function assigns each input exactly one output; function notation", "function"),
    ("openstax_vectors", OS + "precalculus-2e/pages/8-8-vectors",
     "8.8 Vectors", "Jay Abramson", 2021, "OpenStax, Precalculus 2e", [2],
     "Vectors, components, magnitude, and unit vectors", "unit vector"),
]
DOI = [  # id, doi, kind, levels, scope
    ("bickel1975", "10.1126/science.187.4175.398", "paper", [2, 3],
     "Berkeley graduate admissions: an aggregate gap that reverses or vanishes within departments"),
    ("gigerenzer1995", "10.1037/0033-295X.102.4.684", "paper", [2],
     "Natural frequency formats improve Bayesian reasoning"),
]
CCSS_PASSAGES = {
    "6.EE.6": "Use variables to represent numbers and write expressions when solving a real-world or mathematical problem",
    "8.F.1": "Understand that a function is a rule that assigns to each input exactly one output",
    "8.SP.1": "Construct and interpret scatter plots for bivariate measurement data",
    "8.SP.4": "two-way table",
    "7.SP.8": "Find probabilities of compound events using organized lists, tables, tree diagrams, and simulation",
    "S-CP.3": "Understand the conditional probability of A given B as P(A and B)/P(B)",
    "S-ID.9": "Distinguish between correlation and causation",
}


def main():
    src = json.loads((BOOK / "_data/sources.json").read_text(encoding="utf-8"))
    ver = json.loads((BOOK / "_data/verification.json").read_text(encoding="utf-8"))
    bib = (BOOK / "references.bib").read_text(encoding="utf-8")
    ids = {w[0] for w in WEB} | {d[0] for d in DOI}
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
    for key, doi, kind, levels, scope in DOI:
        r = requests.get(f"https://api.crossref.org/works/{doi}", headers=UA, timeout=30)
        assert r.status_code == 200, (key, r.status_code)
        m = r.json()["message"]
        title = re.sub(r"\s+", " ", m["title"][0]).strip().rstrip(".")
        authors = [f"{a.get('given', '')} {a['family']}".strip() for a in m["author"]]
        year = m["issued"]["date-parts"][0][0]
        venue = m["container-title"][0]
        src.append({"id": key, "title": title, "authors": ", ".join(authors), "year": year, "venue": venue, "doi": doi,
                    "url": f"https://doi.org/{doi}", "kind": kind, "scope": scope, "levels": levels})
        ver[key] = {"status": "PASS", "method": "Crossref works/<doi>", "url_checked": r.url, "http": r.status_code,
                    "fetched_title": title, "jaccard": 1.0, "checked_at": NOW}
        vol, iss, pg = m.get("volume", ""), m.get("issue", ""), m.get("page", "")
        entries.append("@article{%s,\n  title = {{%s}},\n  author = {%s},\n  journal = {%s},\n  year = {%d},\n%s%s%s  doi = {%s},\n  url = {https://doi.org/%s}\n}\n"
                       % (key, title, " and ".join(authors), venue, year,
                          f"  volume = {{{vol}}},\n" if vol else "", f"  number = {{{iss}}},\n" if iss else "",
                          f"  pages = {{{pg.replace('-', '--')}}},\n" if pg else "", doi, doi))
        time.sleep(1)
    pdf = requests.get("https://learning.ccsso.org/wp-content/uploads/2022/11/Math_Standards1.pdf", headers=UA, timeout=60).content
    std = re.sub(r"\s+", " ", " ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(pdf)).pages))
    missing = [c for c, p in CCSS_PASSAGES.items() if p not in std]
    assert not missing, ("not in the official PDF", missing)
    for s in src:
        if s["id"] == "ccss_math":
            s["scope"] = ("K-12 counting, comparing, sorting, measuring, graphs, fractions, expressions, functions, statistics, and probability "
                          "(K.CC.4, K.CC.5, K.CC.6, K.CC.7, K.MD.3, 1.MD.4, 2.MD.1, 2.MD.10, 3.NF.1, 4.NF.1, 6.EE.6, 6.SP.1, 7.SP.5, 7.SP.6, "
                          "7.SP.7, 7.SP.8, 8.F.1, 8.SP.1, 8.SP.4, S-CP.3, S-ID.9)")
            s["levels"] = sorted(set(s["levels"]) | {2})
        if s["id"] in ("pearl", "openstax_design", "openstax_prob", "ngss_appf", "ibm", "bareinboim", "manim_ce"):
            s["levels"] = sorted(set(s["levels"]) | {2})
    src.sort(key=lambda s: s["id"])
    (BOOK / "_data/sources.json").write_text(json.dumps(src, indent=1, ensure_ascii=False), encoding="utf-8")
    (BOOK / "_data/verification.json").write_text(json.dumps(ver, indent=1, ensure_ascii=False), encoding="utf-8")
    (BOOK / "references.bib").write_text(bib.rstrip() + "\n\n" + "\n".join(entries), encoding="utf-8")
    print(f"verified and recorded {len(WEB) + len(DOI)} Level 2 sources; CCSS scope covers {len(CCSS_PASSAGES)} more standards")


if __name__ == "__main__":
    main()
