"""Unit `level0-merge`: merge the ten Level 0 coursebook lessons into the source of truth.

Run from book/:  python scripts/merge_level0.py
Every draft in _data/level0_drafts/ must pass check_lesson_draft.py first; the
merge refuses otherwise.  The unit syllabus block in ../src/data/level0.json is
kept as is; only the lessons list is replaced, in L0-01..L0-10 order.
"""
import json
import pathlib
import sys

BOOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK / "scripts"))
from check_lesson_draft import ORDER, check  # noqa: E402

SRC = BOOK.parent / "src" / "data" / "level0.json"
DRAFTS = BOOK / "_data" / "level0_drafts"

bad = []
lessons = []
for lid in ORDER:
    f = DRAFTS / f"{lid}.json"
    if not f.exists():
        bad.append(f"{lid}: draft missing")
        continue
    res = check(f)
    errs = res if isinstance(res, list) else res[0]
    if errs:
        bad.append(f"{lid}: " + "; ".join(errs[:3]))
    lessons.append(json.loads(f.read_text(encoding="utf-8")))
if bad:
    print("REFUSING TO MERGE:")
    print("\n".join(bad))
    sys.exit(1)

# Shuffle answer positions so the right answer is not always A.  Seeded by lesson and
# question number, so the result is the same on every run.  Explanations never name a letter.
import hashlib
import random
import re
for L in lessons:
    for k, q in enumerate(L["check"]):
        assert not re.search(r"(option|answer) [ABCD]|[ABCD]\)", q["explanation"]), (L["id"], k)
        right = q["options"][q["answer"]]
        rng = random.Random(int(hashlib.sha256(f"{L['id']}-{k}".encode()).hexdigest(), 16))
        opts = q["options"][:]
        while True:
            rng.shuffle(opts)
            if opts.index(right) != 0 or k == 1:  # vary positions across the three checks
                break
        q["options"], q["answer"] = opts, opts.index(right)

d = json.loads(SRC.read_text(encoding="utf-8"))
d["lessons"] = lessons
SRC.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"merged {len(lessons)} lessons into {SRC}")
