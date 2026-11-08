"""Check that a prose rewrite of a notebook changed only prose.

Usage: python scripts/prose_invariants.py BEFORE.ipynb AFTER.ipynb
Exit 0 only if:
  * every code cell is byte-identical and in the same order (cell tags too);
  * the markdown keeps the same multiset of citation keys, math spans,
    directive openers (:::{...}), labels and numbers (digits in prose);
  * no em dash (U+2014) and no emoji remain in the AFTER markdown.
"""
from __future__ import annotations

import collections
import json
import re
import sys

import nbformat

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐️]")
MATH = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$", re.S)


def parts(nb):
    code = [(c.source, tuple(c.metadata.get("tags", []))) for c in nb.cells if c.cell_type == "code"]
    md = "\n\n".join(c.source for c in nb.cells if c.cell_type == "markdown")
    maths = collections.Counter(m.strip() for m in MATH.findall(md))
    prose = MATH.sub(" ", md)
    cites = collections.Counter(re.findall(r"@([A-Za-z][\w-]*)", prose))
    directives = collections.Counter(re.findall(r":{3,}\{([a-z-]+)\}", prose))
    labels = collections.Counter(re.findall(r":label:\s*(\S+)", prose))
    nums = collections.Counter(re.findall(r"(?<![\w.])\d+(?:[.,]\d+)?", prose))
    return code, md, maths, cites, directives, labels, nums


def main(a, b) -> int:
    A, B = parts(nbformat.read(a, 4)), parts(nbformat.read(b, 4))
    errs = []
    if A[0] != B[0]:
        errs.append("code cells changed")
    for name, i in [("math spans", 2), ("citations", 3), ("directives", 4), ("labels", 5), ("numbers", 6)]:
        if A[i] != B[i]:
            lost = A[i] - B[i]
            added = B[i] - A[i]
            errs.append(f"{name} differ: lost {dict(lost)} added {dict(added)}")
    if "—" in B[1]:
        errs.append(f"em dashes remain: {B[1].count(chr(0x2014))}")
    if EMOJI.search(B[1]):
        errs.append("emoji remain")
    print(json.dumps({"before": a, "after": b, "ok": not errs, "errors": errs}, ensure_ascii=False))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
