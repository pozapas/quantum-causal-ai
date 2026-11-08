"""Every chapter pointer to Bareinboim's Causal AI book must be backed by the book site's own text."""
import html
import json
import re
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]


def test_every_pointer_has_evidence_in_snapshot():
    m = json.loads((BOOK / "_data" / "textbook_map.json").read_text(encoding="utf-8"))
    raw = (BOOK / m["snapshot"]).read_text(encoding="utf-8")
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->|<[^>]+>", " ", raw, flags=re.S)))
    ids = {L["id"] for n in range(8) for L in json.loads((BOOK / "_data" / "levels" / f"level{n}.json").read_text(encoding="utf-8"))["lessons"]}
    assert m["lessons"]
    for e in m["lessons"]:
        assert e["lesson"] in ids
        assert e["evidence"] in text, e
