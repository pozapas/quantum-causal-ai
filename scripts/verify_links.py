"""Check every external link in the book's pages (C3).  Run from book/.

YouTube links are verified by verify_media.py and references by verify_refs.py;
this script covers everything else.  The course's own repository does not
exist until the approved deploy step, so links into it are recorded as
DEFERRED (allowed by check.py only for that prefix).
"""
import datetime
import json
import pathlib
import re
import sys
import time

import requests

BOOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / "scripts"))
from check import book_sources, text_of  # noqa: E402

OWN_REPO = "https://github.com/pozapas/quantum-causal-ai"
SKIP = re.compile(r"youtube\.com/(watch|embed)|youtube-nocookie\.com/embed|i\.ytimg\.com")
UA = {"User-Agent": "Mozilla/5.0 (qcai-book-link-check/1.0)"}

urls = set()
for f in book_sources():
    t = text_of(f)
    urls |= set(re.findall(r"https?://[^\s)\]>\"'`|]+", t))
for f in BOOK.glob("media/*.md"):
    urls |= set(re.findall(r"https?://[^\s)\]>\"'`|]+", f.read_text(encoding="utf-8")))
urls = {u.rstrip(".,;:}") for u in urls if not SKIP.search(u)}

out = {}
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
for u in sorted(urls):
    if "--live" not in sys.argv and u.startswith((OWN_REPO, "https://colab.research.google.com/github/pozapas/quantum-causal-ai", "https://pozapas.github.io/quantum-causal-ai")):
        out[u] = {"status": "DEFERRED", "note": "course repository and site are created in the approved deploy step", "checked_at": now}
        continue
    rec = {"checked_at": now}
    try:
        r = requests.get(u, headers=UA, timeout=30, allow_redirects=True)
        rec.update(http=r.status_code, final_url=r.url)
        rec["status"] = "PASS" if r.status_code < 400 else "FAIL"
        if r.status_code in (403, 429) and ("cloudflare" in r.text.lower() or "captcha" in r.text.lower()):
            rec["note"] = "bot challenge; not counted as PASS"
    except Exception as e:  # noqa: BLE001
        rec.update(status="FAIL", error=f"{type(e).__name__}: {e}"[:200])
    out[u] = rec
    print(rec["status"], rec.get("http", ""), u)
    time.sleep(0.5)
(BOOK / "_data/links.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
bad = [u for u, r in out.items() if r["status"] == "FAIL"]
print(f"{len(out)} links; {len(bad)} failing")
sys.exit(1 if bad else 0)
