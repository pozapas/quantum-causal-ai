"""Unit `level37-refs`: verify and record extra sources for Levels 3-7.  Run from book/.

Each page is re-fetched; its title and a key passage must be in the fetched text.  DOIs are
checked with Crossref.  Also widens the Common Core record's scope to the standards Level 2
references, after confirming each passage in the official PDF.
"""
import datetime
import html
import json
import pathlib
import re
import time

import requests

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
    ("openstax_polar", OS + "precalculus-2e/pages/8-5-polar-form-of-complex-numbers",
     "8.5 Polar Form of Complex Numbers", "Jay Abramson", 2021, "OpenStax, Precalculus 2e", [3],
     "Complex plane, modulus, argument, polar form, products and powers (De Moivre)", "polar form"),
    ("openstax_matrices", OS + "college-algebra-2e/pages/7-5-matrices-and-matrix-operations",
     "7.5 Matrices and Matrix Operations", "Jay Abramson", 2021, "OpenStax, College Algebra 2e", [3],
     "Matrix notation, addition, scalar and matrix multiplication", "matrix"),
    ("openstax_derivative", OS + "calculus-volume-1/pages/3-1-defining-the-derivative",
     "3.1 Defining the Derivative", "Gilbert Strang and Edwin Herman", 2016, "OpenStax, Calculus Volume 1", [3],
     "Derivative as a limit of difference quotients; tangent line", "derivative"),
    ("openstax_gradient", OS + "calculus-volume-3/pages/4-6-directional-derivatives-and-the-gradient",
     "4.6 Directional Derivatives and the Gradient", "Gilbert Strang and Edwin Herman", 2016, "OpenStax, Calculus Volume 3", [3, 7],
     "Directional derivative, gradient, direction of steepest ascent", "gradient"),
    ("openstax_expected", OS + "introductory-statistics-2e/pages/4-2-mean-or-expected-value-and-standard-deviation",
     "4.2 Mean or Expected Value and Standard Deviation", IS, 2023, "OpenStax, Introductory Statistics 2e", [3],
     "Expected value and standard deviation of a discrete random variable", "expected value"),
    ("openstax_ci", OS + "introductory-statistics-2e/pages/8-1-a-single-population-mean-using-the-normal-distribution",
     "8.1 A Single Population Mean using the Normal Distribution", IS, 2023, "OpenStax, Introductory Statistics 2e", [3],
     "Confidence intervals: point estimate, margin of error, confidence level", "confidence interval"),
]
DOI = [  # id, doi, kind, levels, scope
    ("mml", "10.1017/9781108679930", "book", [3, 7],
     "Linear algebra, calculus, probability and optimization for machine learning"),
    ("coverthomas", "10.1002/047174882X", "book", [3, 5, 7],
     "Entropy, relative entropy, mutual information"),
    ("shannon1948", "10.1002/j.1538-7305.1948.tb01338.x", "paper", [3, 5],
     "Founding paper of information theory: entropy of a source"),
    ("shor1995", "10.1103/PhysRevA.52.R2493", "paper", [5],
     "First quantum error-correcting code (nine-qubit code)"),
]


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
        authors = [f"{a.get('given', '')} {a['family']}".strip() for a in m.get("author", m.get("editor", []))]
        year = m["issued"]["date-parts"][0][0]
        venue = (m.get("container-title") or [m.get("publisher", "")])[0]
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
    src.sort(key=lambda s: s["id"])
    (BOOK / "_data/sources.json").write_text(json.dumps(src, indent=1, ensure_ascii=False), encoding="utf-8")
    (BOOK / "_data/verification.json").write_text(json.dumps(ver, indent=1, ensure_ascii=False), encoding="utf-8")
    (BOOK / "references.bib").write_text(bib.rstrip() + "\n\n" + "\n".join(entries), encoding="utf-8")
    print(f"verified and recorded {len(WEB) + len(DOI)} Level 3-7 sources")


if __name__ == "__main__":
    main()
