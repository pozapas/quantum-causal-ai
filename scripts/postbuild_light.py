"""Make light mode the default for first-time visitors.  Run after `jupyter-book build --html`.

The MyST theme picks `localStorage["myst:theme"]` if the visitor chose a theme,
otherwise the operating system's color scheme.  This replaces only that fallback
with "light", in every built HTML page.  The sun/moon toggle and a visitor's
saved choice keep working.
"""
import pathlib
import sys

HTML = pathlib.Path(__file__).resolve().parents[1] / "_build" / "html"
OLD = """const theme = window.matchMedia("(prefers-color-scheme: light)").matches ? 'light' : 'dark';"""
NEW = """const theme = 'light'; /* course default; a saved choice still wins */"""

changed = already = 0
for f in HTML.rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    if OLD in t:
        f.write_text(t.replace(OLD, NEW), encoding="utf-8")
        changed += 1
    elif NEW in t:
        already += 1
print(f"light default applied to {changed} pages ({already} already set)")
if changed + already == 0:
    sys.exit("theme bootstrap script not found: the MyST theme changed, update postbuild_light.py")
