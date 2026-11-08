"""Verify bibliography records against primary APIs and write book/_data + references.bib.

Run from book/:  ../.venv/Scripts/python.exe scripts/verify_refs.py [--cache DIR]

Rules
- Every title/author/year/venue/DOI/arXiv id written to the outputs is taken from a response
  fetched in this run (arXiv API, Crossref API, Google Books API, or the fetched page itself).
  Claimed values below are used only as search keys and for matching.
- Title match: normalized token Jaccard >= 0.8 between the claimed title and the fetched title.
  The single exception is a claimed title that ends in "..." (deliberately truncated): then the
  Jaccard is computed between the claimed prefix and the fetched main title (text before ':'),
  and the note says so.
- Web pages: HTTP GET (redirects followed), status < 400, and a title candidate taken from the
  page (<title>, og:title, citation_title, h1-h3, or for PDFs a line window of the first pages)
  with Jaccard >= 0.8. On failure a second official source (Crossref search, Google Books) is
  tried; both attempts are recorded, PASS only if the second source confirms the title.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import io
import json
import pathlib
import re
import sys
import time
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET

import requests

BOOK = pathlib.Path(__file__).resolve().parents[1]
SRC = BOOK.parent / "src" / "data" / "sources.json"
UA_API = "qcai-book-verifier/1.0"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIVNS = "{http://arxiv.org/schemas/atom}"
THRESH = 0.8

# ---------------------------------------------------------------- judgment data (not metadata)
LEVELS = {
    "advantage": [6, 7], "allen": [6, 7], "barrett": [6, 7], "bell": [4, 5, 6], "chaves": [6, 7],
    "chiribella": [6, 7], "chsh": [4, 5, 6], "costa": [6, 7], "feynman": [3, 4, 5],
    "frontdoor": [4, 5, 6], "hernan": [4, 5, 6], "hypothesis": [6, 7], "ibm": [3, 4, 5],
    "invariant": [5, 6, 7], "kernels": [5, 6], "leifer": [6, 7], "mitarai": [5, 6],
    "noise": [5, 6, 7], "notears": [5, 6], "ocb": [6, 7], "openstax": [1, 2, 3],
    "pearl": [4, 5, 6], "peters": [5, 6], "petz": [7], "plateaus": [5, 6, 7], "preskill": [5, 6],
    "process": [6, 7], "qml": [5, 6], "scholkopf": [5, 6, 7], "schuld": [5, 6], "seeing": [3, 4, 5],
    "shadows": [6, 7], "spirtes": [5, 6, 7], "switch": [6, 7], "watrous": [6, 7],
    # new
    "ried2015": [6, 7], "inflation": [6, 7], "hlp2014": [6, 7], "woodspekkens": [6, 7],
    "fritz2012": [6, 7], "pienaar": [6, 7], "giarmatzi": [6, 7], "unravelling": [7],
    "procopio": [5, 6, 7], "rubino": [5, 6, 7], "maclean": [6, 7], "hensen": [3, 4, 5, 6],
    "vqa": [5, 6], "encoding": [5, 6], "nisq": [3, 4, 5], "dowhy": [4, 5], "causallearn": [4, 5, 6],
    "pennylane": [4, 5], "nielsenchuang": [4, 5, 6], "pearlcausality": [5, 6, 7],
    "pearlprimer": [3, 4, 5], "aspect1982": [3, 4, 5], "nobel2022": [0, 1, 2, 3],
    "bradyneal": [3, 4, 5],
}
KIND_EXISTING = {
    "feynman": "book", "hernan": "book", "ibm": "notes", "openstax": "book", "peters": "book",
    "preskill": "notes", "seeing": "book", "spirtes": "book", "watrous": "book",
    "frontdoor": "paper", "pearl": "paper",
}

# Candidate new references: claims are UNTRUSTED search keys only.
NEW = [
    dict(id="ried2015", title="A quantum advantage for inferring causal structure", first="Ried", arxiv="1406.5036", kind="paper",
         scope="Quantum interventions and observations for inferring causal structure"),
    dict(id="inflation", title="The Inflation Technique for Causal Inference with Latent Variables", first="Wolfe", arxiv="1609.00672", kind="paper",
         scope="Inflation technique for testing causal structures with latent variables"),
    dict(id="hlp2014", title="Theory-independent limits on correlations from generalized Bayesian networks", first="Henson", arxiv="1405.2572", kind="paper",
         scope="Generalized Bayesian networks and theory-independent correlation limits"),
    dict(id="woodspekkens", title="The lesson of causal discovery algorithms for quantum correlations: ...", first="Wood", arxiv="1208.4119", kind="paper",
         scope="Classical causal discovery applied to Bell correlations and fine-tuning"),
    dict(id="fritz2012", title="Beyond Bell's Theorem: Correlation Scenarios", first="Fritz", arxiv="1206.5115", kind="paper",
         scope="Correlation scenarios beyond the Bell setting"),
    dict(id="pienaar", title="A graph-separation theorem for quantum causal models", first="Pienaar", arxiv="1406.0430", kind="paper",
         scope="Graph separation (d-separation analogue) for quantum causal models"),
    dict(id="giarmatzi", title="A quantum causal discovery algorithm", first="Giarmatzi", arxiv="1704.00800", kind="paper",
         scope="Algorithm for discovering quantum causal structure from process matrices"),
    dict(id="unravelling", title="Quantum causal unravelling", first="Bai", arxiv="2109.13166", kind="paper",
         scope="Learning causal structure of quantum processes from interventions"),
    dict(id="procopio", title="Experimental superposition of orders of quantum gates", first="Procopio", arxiv="1412.4006", kind="paper",
         scope="Photonic experiment on superposed gate orders"),
    dict(id="rubino", title="Experimental verification of an indefinite causal order", first="Rubino", arxiv="1608.01683", kind="paper",
         scope="Experimental causal witness for indefinite causal order"),
    dict(id="maclean", title="Quantum-coherent mixtures of causal relations", first="MacLean", arxiv="1606.04523", kind="paper",
         scope="Experiment on coherent mixtures of common-cause and cause-effect relations"),
    dict(id="hensen", title="Loophole-free Bell inequality violation using electron spins separated by 1.3 kilometres", first="Hensen", arxiv="1508.05949", kind="paper",
         scope="Loophole-free Bell test"),
    dict(id="vqa", title="Variational Quantum Algorithms", first="Cerezo", arxiv="2012.09265", kind="paper",
         scope="Review of variational quantum algorithms"),
    dict(id="encoding", title="The effect of data encoding on the expressive power of variational quantum machine learning models", first="Schuld", arxiv="2008.08605", kind="paper",
         scope="Data encoding and expressivity of variational quantum models"),
    dict(id="nisq", title="Quantum Computing in the NISQ era and beyond", first="Preskill", arxiv="1801.00862", kind="paper",
         scope="Overview of noisy intermediate-scale quantum computing"),
    dict(id="dowhy", title="DoWhy: An End-to-End Library for Causal Inference", first="Sharma", arxiv="2011.04216", kind="software",
         scope="Python library for causal effect estimation"),
    dict(id="causallearn", title="Causal-learn: Causal Discovery in Python", first="Zheng", arxiv="2307.16405", kind="software",
         scope="Python library for causal discovery"),
    dict(id="pennylane", title="PennyLane: Automatic differentiation of hybrid quantum-classical computations", first="Bergholm", arxiv="1811.04968", kind="software",
         scope="Python library for differentiable quantum programming"),
    dict(id="nielsenchuang", title="Quantum Computation and Quantum Information", first="Nielsen", doi="10.1017/CBO9780511976667", kind="book",
         scope="Standard textbook on quantum computation and information"),
    dict(id="pearlcausality", title="Causality", first="Pearl", doi="10.1017/CBO9780511803161", kind="book",
         scope="Monograph on causal models, reasoning and inference"),
    dict(id="pearlprimer", title="Causal Inference in Statistics: A Primer", first="Pearl", crossref_search=True, kind="book",
         scope="Introductory primer on causal inference"),
    dict(id="aspect1982", title="Experimental Realization of Einstein-Podolsky-Rosen-Bohm Gedankenexperiment: A New Violation of Bell's Inequalities", first="Aspect", doi="10.1103/PhysRevLett.49.91", kind="paper",
         scope="Early photonic Bell-inequality experiment"),
    dict(id="nobel2022", title="The Nobel Prize in Physics 2022", first=None, url="https://www.nobelprize.org/prizes/physics/2022/press-release/", kind="web",
         scope="Press release for the 2022 physics prize on entangled-photon experiments"),
    dict(id="bradyneal", title="Introduction to Causal Inference", first="Neal", url="https://www.bradyneal.com/causal-inference-course", kind="notes",
         scope="Free online course on causal inference"),
]
SKIPPED = {"spekkens_contextuality": "skipped: no independently confirmed arXiv entry (instruction: do not guess)"}


# ---------------------------------------------------------------- utilities
def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def norm_tokens(s: str) -> set[str]:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)                 # html tags (Crossref)
    s = re.sub(r"\\[a-zA-Z]+", " ", s)             # TeX commands
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("'s", "s").replace("’s", "s")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return set(s.split())


def jaccard(a: str, b: str) -> float:
    A, B = norm_tokens(a), norm_tokens(b)
    if not A or not B:
        return 0.0
    return round(len(A & B) / len(A | B), 4)


def match_score(claimed: str, fetched: str) -> tuple[float, str]:
    if claimed.rstrip().endswith("..."):
        prefix = claimed.rstrip()[:-3].rstrip(" :")
        main = fetched.split(":")[0]
        return jaccard(prefix, main), "claimed title truncated with '...'; Jaccard on claimed prefix vs fetched main title (before ':')"
    j = jaccard(claimed, fetched)
    if j < THRESH and ":" in fetched and ":" not in claimed:
        jm = jaccard(claimed, fetched.split(":")[0])
        if jm > j:
            return jm, "claimed short title; Jaccard on fetched main title (before ':'); fetched full title kept in output"
    return j, ""


def clean_ws(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()


def strip_tags(s: str) -> str:
    return clean_ws(re.sub(r"<[^>]+>", " ", s or ""))


class Fetcher:
    def __init__(self, cache_dir: str | None):
        self.cache_dir = pathlib.Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.last_arxiv = 0.0
        self.s = requests.Session()

    def get(self, url: str, api: bool = True, pdf_pages: int = 3) -> dict:
        key = hashlib.sha256(url.encode()).hexdigest()[:24]
        if self.cache_dir and (self.cache_dir / f"{key}.json").exists():
            return json.loads((self.cache_dir / f"{key}.json").read_text(encoding="utf-8"))
        if "export.arxiv.org" in url:
            wait = 3.2 - (time.time() - self.last_arxiv)
            if wait > 0:
                time.sleep(wait)
        headers = {"User-Agent": UA_API, "Accept-Language": "en"}
        out = {"url": url, "fetched_at": now()}
        try:
            r = self.s.get(url, headers=headers, timeout=60, allow_redirects=True)
            out.update(status=r.status_code, final_url=r.url, content_type=r.headers.get("content-type", ""))
            if "pdf" in out["content_type"].lower() or r.content[:5] == b"%PDF-":
                from pypdf import PdfReader
                try:
                    rd = PdfReader(io.BytesIO(r.content))
                    out["text"] = "\n".join((rd.pages[i].extract_text() or "") for i in range(min(pdf_pages, len(rd.pages))))
                    out["pdf"] = True
                except Exception as e:  # noqa: BLE001
                    out["text"], out["error"] = "", f"pdf parse: {e}"
            else:
                if "charset" not in out["content_type"].lower():
                    r.encoding = "utf-8"
                out["text"] = r.text
        except Exception as e:  # noqa: BLE001
            out.update(status=None, error=str(e), text="")
        if "export.arxiv.org" in url:
            self.last_arxiv = time.time()
        if self.cache_dir and out.get("status") and out["status"] < 500:
            (self.cache_dir / f"{key}.json").write_text(json.dumps(out), encoding="utf-8")
        return out


# ---------------------------------------------------------------- arXiv
def parse_arxiv(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    recs = []
    for e in root.findall(f"{ATOM}entry"):
        idurl = (e.findtext(f"{ATOM}id") or "").strip()
        title = clean_ws(e.findtext(f"{ATOM}title") or "")
        if not idurl or title.lower() == "error":
            continue
        aid = re.sub(r"v\d+$", "", idurl.split("/abs/")[-1])
        recs.append({
            "arxiv": aid,
            "title": title,
            "authors": [clean_ws(a.findtext(f"{ATOM}name") or "") for a in e.findall(f"{ATOM}author")],
            "published": (e.findtext(f"{ATOM}published") or "")[:10],
            "journal_ref": clean_ws(e.findtext(f"{ARXIVNS}journal_ref") or "") or None,
            "doi": clean_ws(e.findtext(f"{ARXIVNS}doi") or "") or None,
        })
    return recs


def arxiv_batch(F: Fetcher, ids: list[str]) -> tuple[dict, dict]:
    url = "http://export.arxiv.org/api/query?id_list=" + ",".join(ids) + f"&max_results={len(ids)}"
    r = F.get(url)
    recs = parse_arxiv(r["text"]) if r.get("status") == 200 else []
    return {x["arxiv"]: x for x in recs}, r


def arxiv_title_search(F: Fetcher, title: str) -> tuple[list[dict], dict]:
    q = re.sub(r"[^A-Za-z0-9 \-]+", " ", title.rstrip(". "))
    q = re.sub(r"\s+", " ", q).strip()
    url = "http://export.arxiv.org/api/query?search_query=" + urllib.parse.quote(f'ti:"{q}"') + "&max_results=5"
    r = F.get(url)
    return (parse_arxiv(r["text"]) if r.get("status") == 200 else []), r


# ---------------------------------------------------------------- Crossref / Google Books
def crossref_meta(m: dict) -> dict:
    title = strip_tags((m.get("title") or [""])[0]).replace(" :", ":")
    sub = strip_tags((m.get("subtitle") or [""])[0]) if m.get("subtitle") else ""
    authors = []
    for a in m.get("author", []) or []:
        if a.get("family"):
            authors.append({"given": a.get("given", ""), "family": a["family"]})
        elif a.get("name"):
            authors.append({"given": "", "family": a["name"]})
    year = None
    for k in ("published-print", "issued", "published-online", "published"):
        dp = (m.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            year = int(dp[0][0])
            break
    container = strip_tags((m.get("container-title") or [""])[0]) if m.get("container-title") else ""
    return {
        "title": title, "subtitle": sub, "authors": authors, "year": year,
        "container": container or None, "publisher": m.get("publisher"), "type": m.get("type"),
        "doi": m.get("DOI"), "volume": m.get("volume"), "issue": m.get("issue"), "page": m.get("page"),
        "isbn": m.get("ISBN"),
    }


def crossref_doi(F: Fetcher, doi: str) -> tuple[dict | None, dict]:
    r = F.get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    if r.get("status") != 200:
        return None, r
    try:
        return crossref_meta(json.loads(r["text"])["message"]), r
    except Exception:  # noqa: BLE001
        return None, r


def crossref_search(F: Fetcher, title: str, author: str | None, rows: int = 3) -> tuple[list[dict], dict]:
    q = title + (" " + author if author else "")
    url = "https://api.crossref.org/works?query.bibliographic=" + urllib.parse.quote(q) + f"&rows={rows}"
    r = F.get(url)
    if r.get("status") != 200:
        return [], r
    try:
        return [crossref_meta(m) for m in json.loads(r["text"])["message"]["items"]], r
    except Exception:  # noqa: BLE001
        return [], r


def gbooks_search(F: Fetcher, title: str, author: str | None) -> tuple[list[dict], dict]:
    q = f'intitle:"{title}"' + (f" inauthor:{author}" if author else "")
    url = "https://www.googleapis.com/books/v1/volumes?q=" + urllib.parse.quote(q) + "&maxResults=5"
    r = F.get(url)
    out = []
    if r.get("status") == 200:
        try:
            for it in json.loads(r["text"]).get("items", []):
                v = it.get("volumeInfo", {})
                t = clean_ws(v.get("title", ""))
                full = t + (": " + clean_ws(v["subtitle"]) if v.get("subtitle") else "")
                y = re.match(r"\d{4}", v.get("publishedDate", "") or "")
                out.append({"title": t, "full_title": full, "authors": v.get("authors", []),
                            "publisher": v.get("publisher"), "year": int(y.group()) if y else None,
                            "id": it.get("id")})
        except Exception:  # noqa: BLE001
            pass
    return out, r


def fam_in(first: str | None, names: list[str]) -> bool:
    if not first:
        return True
    f = first.lower()
    return any(f in n.lower() for n in names)


# ---------------------------------------------------------------- web pages
def title_candidates(text: str, is_pdf: bool) -> list[str]:
    c: list[str] = []
    if is_pdf:
        lines = [clean_ws(x) for x in text.splitlines() if clean_ws(x)][:80]
        for i in range(len(lines)):
            for w in (1, 2, 3):
                if i + w <= len(lines):
                    c.append(" ".join(lines[i:i + w]))
        return c
    for pat in (r"<title[^>]*>(.*?)</title>",
                r'<meta[^>]+(?:property|name)=["\'](?:og:title|citation_title|twitter:title|dc\.title)["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:title|citation_title|twitter:title)',
                r"<h[1-3][^>]*>(.*?)</h[1-3]>"):
        for m in re.findall(pat, text, flags=re.S | re.I):
            t = strip_tags(m)
            if t and len(t) < 300:
                for v in {t, clean_ws(re.sub(r"\([^)]*\)", " ", t))}:
                    c.append(v)
                    c.extend(p.strip() for p in re.split(r" [|\-\u2013\u2014\u00b7] ", v) if p.strip())
    return c


def best_candidate(claimed: str, cands: list[str]) -> tuple[str | None, float]:
    best, bj = None, 0.0
    for c in cands:
        j = jaccard(claimed, c)
        if j > bj:
            best, bj = c, j
    return best, bj


def norm_seq(s: str) -> str:
    s = html.unescape(s or "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower().replace("'s", "s").replace("\u2019s", "s")
    return " " + " ".join(re.sub(r"[^a-z0-9]+", " ", s).split()) + " "


def page_plain(text: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    return strip_tags(text)


def meta_authors(text: str) -> list[str]:
    a = re.findall(r'<meta[^>]+name=["\'](?:citation_author|author|dc\.creator)["\'][^>]+content=["\']([^"\']+)', text, flags=re.I)
    return [clean_ws(x) for x in a if clean_ws(x)]


# ---------------------------------------------------------------- record builders
def vrec(status, method, url_checked, http, fetched_title, jac, note="", **extra):
    d = {"status": status, "method": method, "url_checked": url_checked, "http": http,
         "fetched_title": fetched_title, "jaccard": jac, "checked_at": now(), "note": note}
    d.update(extra)
    return d


def authors_str(names: list[str]) -> str:
    return ", ".join(names)


def verify_arxiv(F, cid, claimed, first, aid, batch, scope, kind, url=None):
    """Returns (verification, source_or_None, extra_crossref)"""
    rec = batch.get(aid)
    note = ""
    method = "arXiv API id_list"
    checked = f"http://export.arxiv.org/api/query?id_list={aid}"
    jac, how = (match_score(claimed, rec["title"]) if rec else (0.0, ""))
    if rec is not None and jac < THRESH and rec["doi"]:
        # arXiv title can differ from the published title: check the DOI the arXiv record itself lists
        cm, cr = crossref_doi(F, rec["doi"])
        if cm:
            jc, hc = match_score(claimed, cm["title"] + (": " + cm["subtitle"] if cm["subtitle"] else ""))
            if jc >= THRESH:
                names = [(a["given"] + " " + a["family"]).strip() for a in cm["authors"]]
                note = (f"arXiv title '{rec['title']}' (J={jac}) differs from published title; claimed title matches "
                        f"Crossref record of DOI {rec['doi']} listed in the arXiv entry. {hc}").strip()
                if first and not fam_in(first, names):
                    note += f" Claimed first author '{first}' not in Crossref authors."
                src = {"id": cid, "title": cm["title"] + (": " + cm["subtitle"] if cm["subtitle"] else ""),
                       "authors": authors_str(names), "year": cm["year"], "venue": cm["container"], "doi": cm["doi"],
                       "arxiv": rec["arxiv"], "url": url or f"https://arxiv.org/abs/{rec['arxiv']}", "kind": kind,
                       "scope": scope, "levels": LEVELS.get(cid, []), "_authors_list": names,
                       "_authors_bib": [f"{a['family']}, {a['given']}".strip(", ") for a in cm["authors"]],
                       "_bib": {"volume": cm["volume"], "number": cm["issue"], "pages": cm["page"]}}
                return vrec("PASS", "arXiv API id_list + Crossref works/<doi from arXiv entry>", cr["url"], cr.get("status"),
                            src["title"], jc, note, arxiv_title=rec["title"], arxiv_published=rec["published"],
                            journal_ref=rec["journal_ref"], doi=rec["doi"]), src
    if rec is None or jac < THRESH:
        prior = f"id {aid}: " + ("not found" if rec is None else f"title mismatch ('{rec['title']}', J={jac})")
        hits, r = arxiv_title_search(F, claimed.rstrip(". ").rstrip(":") if not claimed.endswith("...") else claimed[:-3])
        checked = r["url"]
        method = "arXiv API title search (id_list failed)"
        best, bj, bh = None, 0.0, ""
        for h in hits:
            j, hw = match_score(claimed, h["title"])
            if j > bj and fam_in(first, h["authors"]):
                best, bj, bh = h, j, hw
        if best is None or bj < THRESH:
            return vrec("FAIL", method, checked, r.get("status"), best["title"] if best else None, bj,
                        prior + "; title search found no match with Jaccard>=0.8 and matching first author"), None
        rec, jac, how = best, bj, bh
        note = prior + f"; corrected arXiv id {best['arxiv']} found by title search. "
    if first and not fam_in(first, rec["authors"]):
        note += f"claimed first author '{first}' not in fetched authors. "
    note += how
    src = {"id": cid, "title": rec["title"], "authors": authors_str(rec["authors"]),
           "year": int(rec["published"][:4]), "venue": rec["journal_ref"], "doi": rec["doi"],
           "arxiv": rec["arxiv"], "url": url or f"https://arxiv.org/abs/{rec['arxiv']}", "kind": kind,
           "scope": scope, "levels": LEVELS.get(cid, []),
           "_authors_list": rec["authors"], "_bib": {}}
    xr = None
    if rec["doi"]:
        cm, cr = crossref_doi(F, rec["doi"])
        if cm and jaccard(rec["title"], cm["title"] + (" " + cm["subtitle"] if cm["subtitle"] else "")) >= 0.5:
            xr = cm
            if cm["container"]:
                src["venue"] = cm["container"]
            if cm["year"]:
                src["year"] = cm["year"]
            src["_bib"] = {"volume": cm["volume"], "number": cm["issue"], "pages": cm["page"]}
            note += f" Venue/year from Crossref DOI {rec['doi']}."
        else:
            note += f" Crossref lookup for arXiv DOI {rec['doi']} returned HTTP {cr.get('status')}; venue from journal_ref."
    return vrec("PASS", method, checked, 200, rec["title"], jac, note.strip(), arxiv_published=rec["published"],
                journal_ref=rec["journal_ref"], doi=rec["doi"]), src


def crossref_to_src(cid, cm, claimed, url, kind, scope):
    full = cm["title"] + (": " + cm["subtitle"] if cm["subtitle"] else "")
    j1, j2 = jaccard(claimed, cm["title"]), jaccard(claimed, full)
    title = full if j2 >= j1 else cm["title"]
    names = [(a["given"] + " " + a["family"]).strip() for a in cm["authors"]]
    venue = cm["container"] if kind == "paper" else (cm["publisher"] or cm["container"])
    src = {"id": cid, "title": title, "authors": authors_str(names) or None, "year": cm["year"],
           "venue": venue, "doi": cm["doi"], "arxiv": None, "url": url, "kind": kind, "scope": scope,
           "levels": LEVELS.get(cid, []), "_authors_list": names,
           "_authors_bib": [f"{a['family']}, {a['given']}".strip(", ") for a in cm["authors"]],
           "_bib": {"volume": cm["volume"], "number": cm["issue"], "pages": cm["page"],
                    "publisher": cm["publisher"], "isbn": (cm["isbn"] or [None])[0]}}
    return src, max(j1, j2)


def verify_doi(F, cid, claimed, first, doi, url, kind, scope):
    cm, r = crossref_doi(F, doi)
    checked = r["url"]
    if not cm:
        return vrec("FAIL", "Crossref works/<doi>", checked, r.get("status"), None, 0.0, "DOI not found in Crossref"), None
    src, j = crossref_to_src(cid, cm, claimed, url, kind, scope)
    note = ""
    if first and not fam_in(first, src["_authors_list"]):
        note = f"claimed first author '{first}' not in Crossref authors. "
    if j < THRESH:
        return vrec("FAIL", "Crossref works/<doi>", checked, 200, src["title"], j, note + "title mismatch"), None
    return vrec("PASS", "Crossref works/<doi>", checked, 200, src["title"], j, note.strip(), crossref_type=cm["type"]), src


def second_source(F, cid, claimed, first, url, kind, scope, attempts):
    """Crossref bibliographic search, then Google Books. Returns (vrec_fields, src) or (None, None)."""
    hits, r = crossref_search(F, claimed, first, rows=3)
    best, bj, qual = None, 0.0, []
    for h in hits:
        names = [a["family"] for a in h["authors"]]
        full = h["title"] + (": " + h["subtitle"] if h["subtitle"] else "")
        j = max(jaccard(claimed, h["title"]), jaccard(claimed, full))
        if fam_in(first, names) and h["type"] not in ("book-chapter", "component", "peer-review"):
            if j >= THRESH:
                qual.append(h["doi"])
            if j > bj:
                best, bj = h, j
    ambiguous = len(set(qual)) > 1
    attempts.append({"source": "Crossref query.bibliographic", "url": r["url"], "http": r.get("status"),
                     "fetched_title": (best["title"] if best else None), "jaccard": bj,
                     "note": f"ambiguous: {len(set(qual))} matching DOIs {qual}; rejected" if ambiguous else ""})
    if best and bj >= THRESH and not ambiguous:
        src, j = crossref_to_src(cid, best, claimed, url, kind, scope)
        src["_doi_from_search"] = True
        return {"method": "Crossref query.bibliographic (second source)", "url_checked": r["url"], "http": r.get("status"),
                "fetched_title": src["title"], "jaccard": j}, src
    gh, g = gbooks_search(F, claimed.split(":")[0], first)
    best, bj = None, 0.0
    for h in gh:
        j = max(jaccard(claimed, h["title"]), jaccard(claimed, h["full_title"]))
        if j > bj and fam_in(first, h["authors"]):
            best, bj = h, j
    attempts.append({"source": "Google Books API", "url": g["url"], "http": g.get("status"),
                     "fetched_title": (best["full_title"] if best else None), "jaccard": bj})
    if best and bj >= THRESH:
        t = best["full_title"] if jaccard(claimed, best["full_title"]) >= jaccard(claimed, best["title"]) else best["title"]
        src = {"id": cid, "title": t, "authors": authors_str(best["authors"]) or None, "year": best["year"],
               "venue": best["publisher"], "doi": None, "arxiv": None, "url": url, "kind": kind, "scope": scope,
               "levels": LEVELS.get(cid, []), "_authors_list": best["authors"],
               "_bib": {"publisher": best["publisher"]}}
        return {"method": "Google Books API (second source)", "url_checked": g["url"], "http": g.get("status"),
                "fetched_title": t, "jaccard": bj}, src
    ol_hits, o = openlibrary_search(F, claimed, first)
    best, bj = None, 0.0
    for h in ol_hits:
        j = jaccard(claimed, h["title"])
        if j > bj and fam_in(first, h["authors"]):
            best, bj = h, j
    attempts.append({"source": "Open Library search API", "url": o["url"], "http": o.get("status"),
                     "fetched_title": (best["title"] if best else None), "jaccard": bj})
    if best and bj >= THRESH:
        src = {"id": cid, "title": best["title"], "authors": authors_str(best["authors"]) or None, "year": best["year"],
               "venue": None, "doi": None, "arxiv": None, "url": url, "kind": kind, "scope": scope,
               "levels": LEVELS.get(cid, []), "_authors_list": best["authors"], "_bib": {}}
        return {"method": "Open Library search API (second source)", "url_checked": o["url"], "http": o.get("status"),
                "fetched_title": best["title"], "jaccard": bj}, src
    return None, None


def openlibrary_search(F, title, author):
    url = "https://openlibrary.org/search.json?title=" + urllib.parse.quote(title) + \
          ("&author=" + urllib.parse.quote(author) if author else "") + \
          "&limit=10&fields=title,subtitle,author_name,first_publish_year,key"
    r = F.get(url)
    out = []
    if r.get("status") == 200:
        try:
            for d in json.loads(r["text"]).get("docs", []):
                t = clean_ws(d.get("title", ""))
                full = t + (": " + clean_ws(d["subtitle"]) if d.get("subtitle") else "")
                out.append({"title": full, "authors": d.get("author_name", []), "year": d.get("first_publish_year")})
        except Exception:  # noqa: BLE001
            pass
    return out, r


def verify_web(F, cid, claimed, first, url, kind, scope, claimed_year=None, claimed_author=None):
    attempts = []
    r = F.get(url, api=False)
    st = r.get("status")
    is_pdf = bool(r.get("pdf"))
    cand, j = (None, 0.0)
    method = "HTTP GET; page title/heading candidate"
    plain = ""
    if st and st < 400:
        cand, j = best_candidate(claimed, title_candidates(r.get("text", ""), is_pdf))
        plain = r["text"] if is_pdf else page_plain(r["text"])
        if j < THRESH and norm_seq(claimed) in norm_seq(plain):
            cand, j = claimed, 1.0
            method = "HTTP GET; full claimed title found as contiguous phrase in page text"
    attempts.append({"source": "HTTP GET" + (" (PDF text, first pages)" if is_pdf else ""), "url": url,
                     "final_url": r.get("final_url"), "http": st, "fetched_title": cand, "jaccard": j,
                     "error": r.get("error"), "method": method})
    if st and st < 400 and j >= THRESH and is_pdf:
        dm = re.search(r"DOI:\s*(10\.\d{4,9}/[^\s]+)", plain)
        if dm:
            cm, cr = crossref_doi(F, dm.group(1).rstrip(".,;"))
            attempts.append({"source": "Crossref works/<doi> (DOI printed in PDF)", "url": cr["url"], "http": cr.get("status"),
                             "fetched_title": cm["title"] if cm else None})
            if cm:
                src2, j2 = crossref_to_src(cid, cm, claimed, url, kind, scope)
                if j2 >= THRESH:
                    return vrec("PASS", "HTTP GET (PDF) + Crossref works/<doi> for DOI printed in PDF", cr["url"], cr.get("status"),
                                src2["title"], j2, f"PDF HTTP {st}; title in PDF J={j}", attempts=attempts), src2
    if st and st < 400 and j >= THRESH:
        ptoks = norm_tokens(plain + " " + r.get("final_url", ""))
        notes = []
        authors = meta_authors(r["text"]) if not is_pdf else []
        if authors:
            notes.append("authors from page meta tags")
        elif claimed_author:
            people = [s.strip() for s in re.split(r",\s*(?:and\s+)?|\s+and\s+", claimed_author) if s.strip()]
            surn = [s.split()[-1] for s in people]
            if surn and all(norm_tokens(s) <= ptoks for s in surn):
                # keep a full name only if every token of it occurs in the page; else only the confirmed surname
                authors = [p if norm_tokens(p) <= ptoks else p.split()[-1] for p in people]
                notes.append("author names checked token-by-token against fetched page text (unconfirmed given names dropped)")
        year = None
        if claimed_year and str(claimed_year) in ptoks:
            year = int(claimed_year)
            notes.append(f"year {claimed_year} found in fetched page text/URL")
        src = {"id": cid, "title": cand, "authors": authors_str(authors) or None, "year": year, "venue": None,
               "doi": None, "arxiv": None, "url": url, "kind": kind, "scope": scope, "levels": LEVELS.get(cid, []),
               "_authors_list": authors, "_bib": {}}
        return vrec("PASS", method, url, st, cand, j, "; ".join(notes), attempts=attempts), src
    sec, src = second_source(F, cid, claimed, first, url, kind, scope, attempts)
    why = f"primary HTTP {st}" + (f", best page title J={j}" if st and st < 400 else "")
    if sec:
        return vrec("PASS", sec["method"], sec["url_checked"], sec["http"], sec["fetched_title"], sec["jaccard"],
                    why + "; title confirmed by second source", attempts=attempts, http_primary=st), src
    return vrec("FAIL", "HTTP GET + second sources", url, st, cand, j, why + "; no second source confirmed the title",
                attempts=attempts), None


# ---------------------------------------------------------------- BibTeX
def tex_escape(s: str) -> str:
    parts = re.split(r"(\$[^$]+\$)", s)
    out = []
    for p in parts:
        if p.startswith("$") and p.endswith("$") and len(p) > 1:
            out.append(p)
            continue
        p = p.replace("\\", r"\textbackslash{}")
        p = re.sub(r"([&%#_$])", r"\\\1", p)
        p = p.replace("{", r"\{").replace("}", r"\}").replace(r"\textbackslash\{\}", r"\textbackslash{}")
        p = p.replace("~", r"\textasciitilde{}").replace("^", r"\textasciicircum{}")
        out.append(p)
    return "".join(out)


def bib_entry(s: dict) -> str:
    b = s.get("_bib", {})
    kind = s["kind"]
    if kind == "book" and (b.get("publisher") or s.get("venue")):
        et = "book"
    elif s.get("doi") and s.get("venue") and kind in ("paper", "software"):
        et = "article"
    else:
        et = "misc"
    f = [("title", "{" + tex_escape(s["title"]) + "}")]
    names = s.get("_authors_bib") or s.get("_authors_list") or []
    if names:
        f.append(("author", tex_escape(" and ".join(names))))
    else:
        f.append(("key", s["id"]))
    if s.get("year"):
        f.append(("year", str(s["year"])))
    if et == "article":
        f.append(("journal", tex_escape(s["venue"])))
        for k in ("volume", "number", "pages"):
            if b.get(k):
                f.append((k, tex_escape(str(b[k]).replace("-", "--") if k == "pages" else str(b[k]))))
    elif et == "book":
        pub = b.get("publisher") or s.get("venue")
        if pub:
            f.append(("publisher", tex_escape(pub)))
        if b.get("isbn"):
            f.append(("isbn", b["isbn"]))
    elif s.get("venue") and s.get("arxiv"):
        f.append(("note", tex_escape(s["venue"])))
    if s.get("doi"):
        f.append(("doi", s["doi"]))
    if s.get("arxiv"):
        f += [("eprint", s["arxiv"]), ("archivePrefix", "arXiv")]
    f.append(("url", s["url"]))
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in f)
    return f"@{et}{{{s['id']},\n{body}\n}}\n"


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=None, help="directory to cache raw responses (reruns)")
    args = ap.parse_args()
    F = Fetcher(args.cache)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    existing = json.loads(SRC.read_text(encoding="utf-8"))
    existing_ids = [e["id"] for e in existing]
    ver: dict[str, dict] = {}
    srcs: list[dict] = []

    arx_ids = []
    for e in existing:
        m = re.search(r"arxiv\.org/abs/([\w.\-/]+)", e["url"])
        if m:
            arx_ids.append(re.sub(r"v\d+$", "", m.group(1)))
    arx_ids += [n["arxiv"] for n in NEW if n.get("arxiv")]
    batch, br = arxiv_batch(F, arx_ids)
    print(f"arXiv batch: HTTP {br.get('status')}, {len(batch)}/{len(arx_ids)} entries", flush=True)

    def add(cid, v, s):
        ver[cid] = v
        if s and v["status"] == "PASS":
            srcs.append(s)
        print(f"{cid:16s} {v['status']:5s} J={v['jaccard']} {v['method']} :: {v['fetched_title']}", flush=True)

    for e in existing:
        cid, url, claimed = e["id"], e["url"], e["title"]
        # surname of the first listed author (search key only), e.g. "Miguel Hernan and ..." -> "Hernan"
        lead = re.split(r",|;|\s+and\s+", e.get("author", ""))[0].strip()
        first = lead.split()[-1] if lead and lead not in ("OpenStax",) else None
        kind = KIND_EXISTING.get(cid, "paper")
        m = re.search(r"arxiv\.org/abs/([\w.\-/]+)", url)
        d = re.search(r"doi\.org/(10\.[^\s]+)", url)
        if m:
            v, s = verify_arxiv(F, cid, claimed, None, re.sub(r"v\d+$", "", m.group(1)), batch, e["scope"], kind, url=url)
            if v["status"] == "PASS" and v["fetched_title"] and "corrected arXiv id" in v["note"]:
                v["status"] = "FAIL"   # existing record points at the wrong id; do not silently swap
                v["note"] += " Existing URL points to a different id; not auto-corrected."
                s = None
        elif d:
            v, s = verify_doi(F, cid, claimed, None, d.group(1), url, kind, e["scope"])
        else:
            v, s = verify_web(F, cid, claimed, first, url, kind, e["scope"], claimed_year=e.get("year"),
                              claimed_author=e.get("author"))
        add(cid, v, s)

    for n in NEW:
        cid = n["id"]
        if n.get("arxiv"):
            v, s = verify_arxiv(F, cid, n["title"], n["first"], n["arxiv"], batch, n["scope"], n["kind"])
        elif n.get("doi"):
            v, s = verify_doi(F, cid, n["title"], n["first"], n["doi"], "https://doi.org/" + n["doi"], n["kind"], n["scope"])
        elif n.get("crossref_search"):
            hits, r = crossref_search(F, n["title"], n["first"], rows=3)
            target = norm_tokens(n["title"])
            hit = None
            for h in hits:
                full = h["title"] + (": " + h["subtitle"] if h["subtitle"] else "")
                if h["type"] in ("book", "monograph", "edited-book") and (norm_tokens(full) == target or norm_tokens(h["title"]) == target) \
                        and fam_in(n["first"], [a["family"] for a in h["authors"]]):
                    hit = h
                    break
            if hit:
                s, j = crossref_to_src(cid, hit, n["title"], "https://doi.org/" + hit["doi"], n["kind"], n["scope"])
                v = vrec("PASS", "Crossref query.bibliographic (exact normalized title, type book)", r["url"], r.get("status"),
                         s["title"], j, f"DOI {hit['doi']} taken from Crossref search result",
                         candidates=[{"title": h["title"], "subtitle": h["subtitle"], "type": h["type"], "doi": h["doi"]} for h in hits])
            else:
                s = None
                v = vrec("FAIL", "Crossref query.bibliographic", r["url"], r.get("status"), hits[0]["title"] if hits else None,
                         jaccard(n["title"], hits[0]["title"]) if hits else 0.0, "no exact title match of type book",
                         candidates=[{"title": h["title"], "subtitle": h["subtitle"], "type": h["type"], "doi": h["doi"]} for h in hits])
        else:
            v, s = verify_web(F, cid, n["title"], n["first"], n["url"], n["kind"], n["scope"],
                              claimed_year=2022 if cid == "nobel2022" else None,
                              claimed_author="Brady Neal" if cid == "bradyneal" else None)
        add(cid, v, s)

    for cid, why in SKIPPED.items():
        ver[cid] = vrec("SKIPPED", "none", None, None, None, None, why)

    # dedupe by title/doi/arxiv against earlier records
    seen, final = {}, []
    for s in srcs:
        keys = [("t", " ".join(sorted(norm_tokens(s["title"]))))] + ([("d", s["doi"].lower())] if s.get("doi") else []) + \
               ([("a", s["arxiv"])] if s.get("arxiv") else [])
        dup = next((seen[k] for k in keys if k in seen), None)
        if dup:
            ver[s["id"]]["status"] = "FAIL"
            ver[s["id"]]["note"] += f" Duplicate of existing record '{dup}'; dropped."
            continue
        for k in keys:
            seen[k] = s["id"]
        final.append(s)

    out_sources = [{k: v for k, v in s.items() if not k.startswith("_")} for s in final]
    (BOOK / "_data").mkdir(exist_ok=True)
    (BOOK / "_data" / "sources.json").write_text(json.dumps(out_sources, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (BOOK / "_data" / "verification.json").write_text(json.dumps(ver, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    header = "% Generated by scripts/verify_refs.py from fetched API/page metadata. Do not edit by hand.\n\n"
    (BOOK / "references.bib").write_text(header + "\n".join(bib_entry(s) for s in final), encoding="utf-8")

    new_ids = {n["id"] for n in NEW} | set(SKIPPED)
    dropped = [{"id": k, "reason": v["note"] or v["status"]} for k, v in ver.items() if v["status"] != "PASS"]
    summary = {"generated_at": now(), "attempted": len(ver), "pass": sum(v["status"] == "PASS" for v in ver.values()),
               "fail": sum(v["status"] == "FAIL" for v in ver.values()),
               "skipped": sum(v["status"] == "SKIPPED" for v in ver.values()),
               "original_ids": len(existing_ids),
               "original_pass": sum(ver[i]["status"] == "PASS" for i in existing_ids),
               "new_pass": sum(ver[i]["status"] == "PASS" for i in new_ids if i in ver),
               "dropped": dropped}
    (BOOK / "evidence").mkdir(exist_ok=True)
    (BOOK / "evidence" / "refs-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "dropped"}))
    for d in dropped:
        print("  NOT PASS:", d["id"], "-", d["reason"])


if __name__ == "__main__":
    sys.exit(main())
