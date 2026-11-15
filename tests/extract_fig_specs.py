"""Pull the Plotly specs out of the lab notebooks' stored outputs, for tests/render_figs.mjs.

Usage (from book/): python tests/extract_fig_specs.py OUT.json 01-chance 02-bayes ...
"""
import json
import pathlib
import re
import sys

BOOK = pathlib.Path(__file__).resolve().parents[1]
out = []
for nb in sys.argv[2:]:
    d = json.loads((BOOK / "labs" / f"{nb}.ipynb").read_text(encoding="utf-8"))
    for i, c in enumerate(d["cells"]):
        for o in c.get("outputs", []):
            h = "".join(o.get("data", {}).get("text/html", ""))
            m = re.search(r"var spec = (\{.*?\});\n", h, re.S)
            if m:
                out.append({"name": f"{nb[:2]}_c{i}", "h": int(re.search(r"height:(\d+)px", h).group(1)),
                            "spec": json.loads(m.group(1))})
pathlib.Path(sys.argv[1]).write_text(json.dumps(out), encoding="utf-8")
print(len(out), "figures")
