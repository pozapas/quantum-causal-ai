"""Check the refs unit outputs. Run from book/: ../.venv/Scripts/python.exe scripts/check_refs.py
Exit 0 iff all checks pass. Writes the result into evidence/refs-summary.json under "check"."""
import json
import pathlib
import re
import sys

import bibtexparser

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from verify_refs import jaccard, THRESH  # noqa: E402

BOOK = pathlib.Path(__file__).resolve().parents[1]
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

srcs = json.loads((BOOK / "_data" / "sources.json").read_text(encoding="utf-8"))
ver = json.loads((BOOK / "_data" / "verification.json").read_text(encoding="utf-8"))
orig = [e["id"] for e in json.loads((BOOK.parent / "src" / "data" / "sources.json").read_text(encoding="utf-8"))]
bibtext = (BOOK / "references.bib").read_text(encoding="utf-8")
lib = bibtexparser.parse_string(bibtext)

results = []


def check(name, ok, detail=""):
    results.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))


ids = [s["id"] for s in srcs]
check("sources.json ids unique", len(ids) == len(set(ids)), f"{len(ids)} records")
bad = [i for i in ids if ver.get(i, {}).get("status") != "PASS" or (ver[i].get("jaccard") or 0) < THRESH]
check("every source has verification PASS with jaccard>=0.8", not bad, ", ".join(bad))
miss_fields = [s["id"] for s in srcs if not s.get("title") or not s.get("url") or s.get("kind") not in
               ("paper", "book", "notes", "web", "software") or not s.get("levels")
               or not all(isinstance(x, int) and 0 <= x <= 7 for x in s["levels"])]
check("required fields present (title,url,kind,levels 0-7)", not miss_fields, ", ".join(miss_fields))

check("bib parses with no failed blocks", len(lib.failed_blocks) == 0,
      f"{len(lib.entries)} entries, {len(lib.failed_blocks)} failed blocks")
raw_entries = len(re.findall(r"^@\w+\{", bibtext, flags=re.M))
check("every @entry in file was parsed", raw_entries == len(lib.entries), f"{raw_entries} raw vs {len(lib.entries)} parsed")
keys = [e.key for e in lib.entries]
check("bib keys unique", len(keys) == len(set(keys)))
check("bib keys == sources ids", set(keys) == set(ids),
      f"only in bib: {sorted(set(keys) - set(ids))}; only in sources: {sorted(set(ids) - set(keys))}")


def detex(t):
    t = t.strip()
    while t.startswith("{") and t.endswith("}"):
        t = t[1:-1]
    return re.sub(r"\\([&%#_$])", r"\1", t)


low = []
for e in lib.entries:
    v = ver.get(e.key, {})
    t = e.fields_dict["title"].value if "title" in e.fields_dict else ""
    j = jaccard(detex(t), v.get("fetched_title") or "")
    if j < THRESH:
        low.append(f"{e.key} J={j}")
check("bib title matches verified fetched title (J>=0.8)", not low, "; ".join(low))

unacc = [i for i in orig if i not in ids and ver.get(i, {}).get("status") != "FAIL"]
check("all 35 original ids present or explicitly FAIL with reason", len(orig) == 35 and not unacc and
      all(ver[i]["note"] for i in orig if i not in ids), f"present {sum(i in ids for i in orig)}/35; FAIL: "
      + ", ".join(i for i in orig if i not in ids))
check("verification has record for every attempted id", all(i in ver for i in ids + orig))

ok = all(r["status"] == "PASS" for r in results)
p = BOOK / "evidence" / "refs-summary.json"
summ = json.loads(p.read_text(encoding="utf-8"))
summ["check"] = {"status": "PASS" if ok else "FAIL", "results": results}
p.write_text(json.dumps(summ, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("REFS CHECK:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
