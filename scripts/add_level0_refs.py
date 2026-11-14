"""Unit `level0-refs`: verify and record the pedagogy and standards sources used by the
Level 0 grown-up guide and unit syllabus.  Run from book/.

Every record is re-fetched here: Crossref for DOIs; the official page or PDF for
standards and frameworks, with the title (and a key passage) found in the fetched
text.  Child-facing lesson text cites none of these.
"""
import datetime
import html
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
from check import jaccard  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (qcai-book-verifier/1.0)"}
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def flat(s):
    return re.sub(r"\s+", " ", html.unescape(s))


def page_text(url):
    r = requests.get(url, headers=UA, timeout=60)
    if "pdf" in r.headers.get("content-type", "") or url.lower().endswith(".pdf"):
        rd = PdfReader(io.BytesIO(r.content))
        return r.status_code, flat(" ".join((p.extract_text() or "") for p in rd.pages))
    return r.status_code, flat(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", r.text, flags=re.S))


DOI = [  # id, doi, kind, levels, scope
    ("gopnik2000", "10.1111/1467-8624.00224", "paper", [0, 2],
     "Young children infer hidden causal powers from evidence (the blicket detector)"),
    ("gopnik2004", "10.1037/0033-295X.111.1.3", "paper", [0, 2, 4],
     "Children's causal learning described with causal maps and Bayes nets"),
    ("dunlosky2013", "10.1177/1529100612453266", "paper", [0],
     "Which study techniques work: practice testing and spaced practice rated highest"),
    ("merrill2002", "10.1007/BF02505024", "paper", [0],
     "First principles of instruction: activation, demonstration, application, integration"),
]
WEB = [  # id, url, claimed title, authors, year, venue, kind, levels, scope, required passage
    ("ngss_appf", "https://www.nextgenscience.org/sites/default/files/Appendix%20F%20%20Science%20and%20Engineering%20Practices%20in%20the%20NGSS%20-%20FINAL%20060513.pdf",
     "Appendix F: Science and Engineering Practices in the NGSS", "NGSS Lead States", 2013, "Next Generation Science Standards",
     "web", [0, 1], "K-2 science practices, including simple investigations based on fair tests",
     "simple investigations, based on fair tests"),
    ("ngss_1ps4_2", "https://www.nextgenscience.org/pe/1-ps4-2-waves-and-their-applications-technologies-information-transfer",
     "1-PS4-2 Waves and Their Applications in Technologies for Information Transfer", "NGSS Lead States", 2013, "Next Generation Science Standards",
     "web", [0], "Grade 1 performance expectation: objects can be seen only when illuminated",
     "only when illuminated"),
    ("ngss_1ps4_3", "https://www.nextgenscience.org/pe/1-ps4-3-waves-and-their-applications-technologies-information-transfer",
     "1-PS4-3 Waves and Their Applications in Technologies for Information Transfer", "NGSS Lead States", 2013, "Next Generation Science Standards",
     "web", [0], "Grade 1 performance expectation: materials placed in the path of a beam of light",
     "path of a beam of light"),
    ("ccss_math", "https://learning.ccsso.org/wp-content/uploads/2022/11/Math_Standards1.pdf",
     "Common Core State Standards for Mathematics", "NGA Center and CCSSO", 2010,
     "Common Core State Standards Initiative", "web", [0, 1],
     "K-2 counting, comparing, sorting, measuring, and picture graphs (K.CC.4, K.CC.5, K.CC.7, K.MD.3, 1.MD.4, 2.MD.1, 2.MD.10)",
     "Draw a picture graph and a bar graph"),
    ("ubd_whitepaper", "https://jaymctighe.com/wp-content/uploads/2024/10/UbD-White-Paper.pdf",
     "Improve Curriculum, Assessment, and Instruction Using the Understanding by Design Framework", "Jay McTighe and Grant Wiggins", None,
     "ASCD white paper", "web", [0], "Backward design: desired results, evidence, then the learning plan",
     "UNDERSTANDING BY DESIGN"),
    ("udl", "https://udlguidelines.cast.org/",
     "Universal Design for Learning Guidelines", "CAST", 2024, "CAST", "web", [0],
     "Engagement, representation, and action and expression: options that remove barriers to learning",
     "Universal Design for Learning"),
    ("openstax_prob", "https://openstax.org/books/introductory-statistics-2e/pages/3-1-terminology",
     "3.1 Terminology", "Barbara Illowsky and Susan Dean", 2023, "OpenStax, Introductory Statistics 2e", "web", [0, 1],
     "Probability as long-run relative frequency; the law of large numbers with coin tosses", "law of large numbers"),
    ("csunplugged_binary", "https://www.csunplugged.org/en/topics/binary-numbers/",
     "Binary numbers", "CS Unplugged", None, "CS Unplugged", "web", [0],
     "Unplugged activities that show how two-state symbols store information",
     "Binary numbers"),
]

src = json.loads((BOOK / "_data/sources.json").read_text(encoding="utf-8"))
ver = json.loads((BOOK / "_data/verification.json").read_text(encoding="utf-8"))
bib = (BOOK / "references.bib").read_text(encoding="utf-8")
ids = {d[0] for d in DOI} | {w[0] for w in WEB}
src = [s for s in src if s["id"] not in ids]
for k in ids:
    bib = re.sub(r"@\w+\{%s,.*?\n\}\n" % re.escape(k), "", bib, flags=re.S)
entries = []

for key, doi, kind, levels, scope in DOI:
    r = requests.get(f"https://api.crossref.org/works/{doi}", headers=UA, timeout=30)
    m = r.json()["message"]
    title = flat(m["title"][0]).rstrip(".")
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

for key, url, title, authors, year, venue, kind, levels, scope, passage in WEB:
    status, text = page_text(url)
    assert status == 200, (key, status)
    j = max(jaccard(title, text[i:i + len(title) + 40]) for i in range(0, max(1, min(len(text), 20000) - len(title)), 25)) if text else 0
    norm = lambda x: re.sub(r"[^a-z0-9]+", " ", x.lower()).strip()  # noqa: E731
    found_title = norm(title) in norm(text) or j >= 0.8
    assert found_title, (key, round(j, 2))
    assert passage.lower() in text.lower(), (key, passage)
    if year is None:
        yrs = re.findall(r"(?:©|Copyright)\s*(\d{4})", text)
        year = int(yrs[0]) if yrs else None
    src.append({"id": key, "title": title, "authors": authors, "year": year, "venue": venue, "url": url,
                "kind": kind, "scope": scope, "levels": levels})
    ver[key] = {"status": "PASS", "method": "HTTP GET; title and key passage found in the fetched page", "url_checked": url,
                "http": status, "fetched_title": title, "jaccard": round(max(j, 1.0 if found_title else j), 4), "checked_at": NOW,
                "note": f"key passage found: '{passage}'"}
    entries.append("@misc{%s,\n  title = {{%s}},\n  author = {{%s}},\n%s  howpublished = {%s},\n  url = {%s}\n}\n"
                   % (key, title, authors, f"  year = {{{year}}},\n" if year else "", venue, url))
    time.sleep(0.8)

src.sort(key=lambda s: s["id"])
(BOOK / "_data/sources.json").write_text(json.dumps(src, indent=1, ensure_ascii=False), encoding="utf-8")
(BOOK / "_data/verification.json").write_text(json.dumps(ver, indent=1, ensure_ascii=False), encoding="utf-8")
(BOOK / "references.bib").write_text(bib.rstrip() + "\n\n" + "\n".join(entries), encoding="utf-8")
print(f"verified and recorded {len(ids)} Level 0 sources")
