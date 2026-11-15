"""Preview a lesson's interactive (Plotly) or static (Matplotlib) figure as PNG files.  Run from book/.

    python tests/preview_lessonfig.py l3_01 phase_sum OUTDIR

Interactive figures are drawn in headless Edge at the book's real widths, 614 px (desktop) and
346 px (phone), with the same wide/narrow switch the site uses.  Open the PNGs to check that
nothing overlaps.  Matplotlib figures are saved once as PNG.
"""
import importlib
import json
import pathlib
import subprocess
import sys

BOOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BOOK))

mod, func, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
fig = getattr(importlib.import_module(f"qcai.lessonfigs.{mod}"), func)()
if hasattr(fig, "to_json"):
    spec = json.loads(fig.to_json())
    f = out / f"{mod}_{func}_spec.json"
    f.write_text(json.dumps([{"name": f"{mod}_{func}", "h": spec["layout"].get("height", 460), "spec": spec}]), encoding="utf-8")
    subprocess.run(["node", str(BOOK / "tests" / "render_figs.mjs"), str(f), str(out), "614", "346"], check=True, cwd=BOOK)
    print("wrote", out / f"{mod}_{func}_w614.png", "and", out / f"{mod}_{func}_w346.png")
else:
    p = out / f"{mod}_{func}.png"
    fig.savefig(p, dpi=110, bbox_inches="tight")
    print("wrote", p)
