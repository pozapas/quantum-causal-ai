"""Unit `refs-repair`: fix only the two cited records that failed verification.

preskill: the claimed title is not on the page; use the title the page itself
          shows (fetched now) — the page links John Preskill's lecture notes.
seeing:   the old URL now serves the 2nd edition; cite the 1st edition by its
          Crossref DOI (title + subtitle fetched now).
Run from book/.  Rewrites both records in _data/sources.json,
_data/verification.json and references.bib from freshly fetched data.
"""
import datetime
import html as htmllib
import json
import pathlib
import re
import sys

import requests

BOOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / "scripts"))
from check import jaccard  # noqa: E402

UA = {"User-Agent": "qcai-book-verifier/1.0"}
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
src = json.loads((BOOK / "_data/sources.json").read_text(encoding="utf-8"))
ver = json.loads((BOOK / "_data/verification.json").read_text(encoding="utf-8"))
old = {r["id"]: r for r in json.loads((BOOK.parent / "src/data/sources.json").read_text(encoding="utf-8"))}
bib = (BOOK / "references.bib").read_text(encoding="utf-8")
new_records, new_bib = [], []

# --- preskill ---------------------------------------------------------------
url = "https://www.preskill.caltech.edu/ph219/"
r = requests.get(url, headers=UA, timeout=30)
page = r.text
h = re.search(r"<title>\s*([^<]+?)\s*</title>", page, re.I).group(1)
heads = [re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", x)).replace("\xa0", " ")).strip() for x in re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", page, re.I | re.S)]
title = next((x for x in heads if "219" in x and "Quantum" in x), h)
assert "John Preskill" in page and re.search(r"lecture notes", page, re.I), "page must name Preskill and lecture notes"
new_records.append({"id": "preskill", "title": title, "authors": "John Preskill", "year": None,
                    "venue": "California Institute of Technology (course page with lecture notes)",
                    "url": url, "kind": "notes", "scope": old["preskill"]["scope"], "levels": [5, 6, 7]})
ver["preskill"] = {"status": "PASS", "method": "HTTP GET; record retitled to the page's own heading",
                   "url_checked": url, "http": r.status_code, "fetched_title": title,
                   "jaccard": round(jaccard(title, title), 4), "checked_at": now,
                   "note": f"Earlier claimed title 'Lecture Notes for Physics 219: Quantum Computation' was not on the page (J=0.45); "
                           f"<title> is '{h}'. Page names John Preskill and links lecture notes."}
new_bib.append("@misc{preskill,\n  title = {{%s}},\n  author = {John Preskill},\n  howpublished = {California Institute of Technology course page with lecture notes},\n  url = {%s}\n}\n" % (title, url))

# --- seeing (Cunningham, The Mixtape) -----------------------------------------
doi = "10.12987/9780300255881"
r2 = requests.get(f"https://api.crossref.org/works/{doi}", headers=UA, timeout=30)
m = r2.json()["message"]
title2 = m["title"][0] + (": " + m["subtitle"][0] if m.get("subtitle") else "")
auth = " and ".join(f"{a['given']} {a['family']}" for a in m["author"])
year = m["issued"]["date-parts"][0][0]
j = jaccard("Causal Inference: The Mixtape", title2)
assert j >= 0.8, j
new_records.append({"id": "seeing", "title": title2, "authors": auth.replace(" and ", ", "), "year": year,
                    "venue": m.get("publisher"), "doi": doi, "url": f"https://doi.org/{doi}", "kind": "book",
                    "scope": old["seeing"]["scope"], "levels": [2, 3, 4]})
ver["seeing"] = {"status": "PASS", "method": "Crossref DOI", "url_checked": f"https://api.crossref.org/works/{doi}",
                 "http": r2.status_code, "fetched_title": title2, "jaccard": round(j, 4), "checked_at": now,
                 "note": "Old URL mixtape.scunning.com now serves the 2nd edition ('The Remix'); cite the 1st edition by DOI."}
new_bib.append("@book{seeing,\n  title = {{%s}},\n  author = {%s},\n  year = {%d},\n  publisher = {%s},\n  doi = {%s},\n  url = {https://doi.org/%s}\n}\n"
               % (title2, auth, year, m.get("publisher"), doi, doi))

ids = {r["id"] for r in new_records}
src = [r for r in src if r["id"] not in ids] + new_records
src.sort(key=lambda r: r["id"])
for k in ids:
    bib = re.sub(r"@\w+\{%s,.*?\n\}\n" % k, "", bib, flags=re.S)
bib = bib.rstrip() + "\n\n" + "\n".join(new_bib)
(BOOK / "_data/sources.json").write_text(json.dumps(src, indent=1, ensure_ascii=False), encoding="utf-8")
(BOOK / "_data/verification.json").write_text(json.dumps(ver, indent=1, ensure_ascii=False), encoding="utf-8")
(BOOK / "references.bib").write_text(bib, encoding="utf-8")
print("repaired:", {r["id"]: r["title"] for r in new_records})
