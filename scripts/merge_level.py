"""Merge coursebook lesson drafts into a level's source of truth.  Run from book/.

    python scripts/merge_level.py 1

Every draft in _data/level<N>_drafts/ must pass check_lesson_draft.py, or nothing is
merged.  Lessons with a draft are replaced; lessons without one are kept, so a
level can be converted one lesson at a time.  Answer positions are shuffled with a
fixed seed per question, so the right answer is not always the same letter.
"""
import hashlib
import json
import pathlib
import random
import re
import sys

BOOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / "scripts"))
from check_lesson_draft import check as check_v2  # noqa: E402
from check_lesson_v3 import check as check_v3  # noqa: E402


def check(f):
    return check_v3(f) if json.loads(pathlib.Path(f).read_text(encoding="utf-8")).get("schema") == 3 else check_v2(f)

n = int(sys.argv[1])
SRC = BOOK.parent / "src" / "data" / f"level{n}.json"
DRAFTS = BOOK / "_data" / f"level{n}_drafts"
d = json.loads(SRC.read_text(encoding="utf-8"))
drafts = {f.stem: f for f in sorted(DRAFTS.glob(f"L{n}-*.json"))}

bad = []
for lid, f in drafts.items():
    res = check(f)
    errs = res if isinstance(res, list) else res[0]
    if errs:
        bad.append(f"{lid}: " + "; ".join(errs[:3]))
if bad:
    print("REFUSING TO MERGE:\n" + "\n".join(bad))
    sys.exit(1)


LETTER_RE = re.compile(r"(option|answer) [ABCD]\b|(?<![|(] )(?<!\()\b[ABCD]\)", re.I)  # letter labels, not P(A | B)

LETTER_V3 = re.compile(r"(option|answer) [ABCD]", re.I)


def shuffle(L):
    for k, q in enumerate(L["check"]):
        pat = LETTER_V3 if L.get("schema") == 3 else LETTER_RE  # schema 3 explanations contain math such as I(A:B)
        assert not pat.search(q["explanation"]), (L["id"], k)
        right = q["options"][q["answer"]]
        rng = random.Random(int(hashlib.sha256(f"{L['id']}-{k}".encode()).hexdigest(), 16))
        opts = q["options"][:]
        while True:
            rng.shuffle(opts)
            if opts.index(right) != 0 or k == 1:
                break
        q["options"], q["answer"] = opts, opts.index(right)
    return L


out = []
for L in d["lessons"]:
    if L["id"] in drafts:
        out.append(shuffle(json.loads(drafts[L["id"]].read_text(encoding="utf-8"))))
    else:
        out.append(L)
d["lessons"] = out
SRC.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"level {n}: merged {len(drafts)} coursebook lessons, kept {len(out) - len(drafts)} others")
