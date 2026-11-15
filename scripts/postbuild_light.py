"""Post-build fixes: light mode by default, and pausable lesson videos.  Run after `jupyter-book build --html`.

The MyST theme picks `localStorage["myst:theme"]` if the visitor chose a theme,
otherwise the operating system's color scheme.  This replaces only that fallback
with "light", in every built HTML page.  The sun/moon toggle and a visitor's
saved choice keep working.
"""
import pathlib
import sys

HTML = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[1] / "_build" / "html"
OLD = """const theme = window.matchMedia("(prefers-color-scheme: light)").matches ? 'light' : 'dark';"""
NEW = """const theme = 'light'; /* course default; a saved choice still wins */"""

# Lesson animations play muted and looped; give every video standard controls so it can be
# paused, and start paused for readers who ask for reduced motion (WCAG 2.2.2).
VIDEO_JS = ("<script id=\"qcai-video\">(function(){var rm=window.matchMedia('(prefers-reduced-motion: reduce)').matches;"
            "function fix(){document.querySelectorAll('video').forEach(function(v){if(!v.hasAttribute('controls'))v.setAttribute('controls','');"
            "if(rm&&!v.dataset.qcaiRm){v.dataset.qcaiRm='1';v.removeAttribute('autoplay');v.pause();}});}"
            "new MutationObserver(fix).observe(document.documentElement,{childList:true,subtree:true});"
            "document.addEventListener('DOMContentLoaded',fix);})();</script>")

# Self-links on theorem/definition titles get aria-label "Link to this Definition" while their visible text is
# "Definition 1 (...)"; the mismatch fails WCAG 2.5.3. Drop the label so the visible text names the link.
A11Y_JS = ("<script id=\"qcai-a11y\">(function(){function fix(){document.querySelectorAll('a[aria-label^=\"Link to this\"]')"
           ".forEach(function(a){if(a.textContent.trim())a.removeAttribute('aria-label');});}"
           "new MutationObserver(fix).observe(document.documentElement,{childList:true,subtree:true});"
           "document.addEventListener('DOMContentLoaded',fix);})();</script>")

changed = already = 0
for f in HTML.rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    t2 = t
    if OLD in t2:
        t2 = t2.replace(OLD, NEW)
        changed += 1
    elif NEW in t2:
        already += 1
    if 'id="qcai-video"' not in t2 and "</head>" in t2:
        t2 = t2.replace("</head>", VIDEO_JS + "</head>", 1)
    if 'id="qcai-a11y"' not in t2 and "</head>" in t2:
        t2 = t2.replace("</head>", A11Y_JS + "</head>", 1)
    if t2 != t:
        f.write_text(t2, encoding="utf-8")
print(f"light default applied to {changed} pages ({already} already set)")
if changed + already == 0:
    sys.exit("theme bootstrap script not found: the MyST theme changed, update postbuild_light.py")
