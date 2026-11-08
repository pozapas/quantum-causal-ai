"""Generate the course icon set (_static/icons/qicon-*.svg).  Run from book/.

One visual language: 48x48 grid, 2.2px round strokes, a violet→cyan gradient,
and a soft tinted disc behind each glyph.  Each level gets a glyph for its topic.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "_static" / "icons"
OUT.mkdir(parents=True, exist_ok=True)

GLYPHS = {
    # Level 0 · counting and fair tests: tally marks with a strike
    "level-0": '<path d="M15 14v20M21 14v20M27 14v20M33 14v20"/><path d="M11 30 37 18"/>',
    # Level 1 · chance and waves: a die face over a wave
    "level-1": '<rect x="12" y="9" width="18" height="18" rx="4"/>'
               '<circle cx="17" cy="14" r="1.4" class="f"/><circle cx="21" cy="18" r="1.4" class="f"/><circle cx="25" cy="22" r="1.4" class="f"/>'
               '<path d="M8 36c4-6 8-6 12 0s8 6 12 0 6-5 8-3"/>',
    # Level 2 · evidence and causal maps: a three-node DAG
    "level-2": '<circle cx="12" cy="14" r="4"/><circle cx="36" cy="14" r="4"/><circle cx="24" cy="35" r="4"/>'
               '<path d="M16 14h15M14.5 17.5l7 13M33.5 17.5l-7 13"/><path d="M28 11.5l3.4 2.5L28 16.5"/>',
    # Level 3 · mathematical tools: matrix brackets around a vector arrow
    "level-3": '<path d="M13 10h-4v28h4M35 10h4v28h-4"/><path d="M17 31 31 17"/><path d="M24.5 17H31v6.5"/>',
    # Level 4 · classical causal AI: an intervention cutting an incoming arrow, do(X)
    "level-4": '<circle cx="12" cy="14" r="4"/><circle cx="24" cy="26" r="4.5"/><circle cx="37" cy="36" r="4"/>'
               '<path d="M15 17l3 3" stroke-dasharray="2 3"/><path d="M27.5 28.5l6 5"/><path d="M18 14l5-5M17 21l7-7"/>'
               '<circle cx="24" cy="26" r="9" stroke-dasharray="3 3" opacity=".7"/>',
    # Level 5 · quantum information: Bloch sphere with a state vector
    "level-5": '<circle cx="24" cy="24" r="14"/><ellipse cx="24" cy="24" rx="14" ry="5" opacity=".7"/>'
               '<path d="M24 24 32 13"/><circle cx="32" cy="13" r="2.2" class="f"/>',
    # Level 6 · quantum causal models: two crossing orders (quantum switch)
    "level-6": '<rect x="8" y="12" width="9" height="9" rx="2"/><rect x="31" y="27" width="9" height="9" rx="2"/>'
               '<rect x="31" y="12" width="9" height="9" rx="2"/><rect x="8" y="27" width="9" height="9" rx="2"/>'
               '<path d="M17 16.5c7 0 7 15 14 15M17 31.5c7 0 7-15 14-15"/>',
    # Level 7 · research frontier: orbit plus a small network
    "level-7": '<ellipse cx="24" cy="24" rx="16" ry="6.5" transform="rotate(-25 24 24)"/>'
               '<circle cx="24" cy="24" r="3.5" class="f"/><circle cx="10" cy="11" r="2.5"/><circle cx="38" cy="37" r="2.5"/>'
               '<circle cx="39" cy="12" r="2.5"/><path d="M12 13l9 8.5M27 26.5l9 8.5M27 21.5l10-7.5"/>',
    # feature icons
    "lab": '<path d="M19 9h10M21 9v10L12 35a3 3 0 0 0 2.6 4.5h18.8A3 3 0 0 0 36 35L27 19V9"/><path d="M15.5 29h17"/>'
           '<circle cx="21" cy="33" r="1.4" class="f"/><circle cx="27" cy="34.5" r="1.2" class="f"/>',
    "verified": '<path d="M24 7 37 12v10c0 9-6 15.5-13 19-7-3.5-13-10-13-19V12z"/><path d="M18 24l4.5 4.5L31 20"/>',
    "media": '<rect x="8" y="12" width="32" height="22" rx="5"/><path d="M21 18.5v9l8-4.5z" class="f"/><path d="M16 39h16"/>',
    "podcast": '<path d="M13 30v-6a11 11 0 0 1 22 0v6"/><rect x="10" y="28" width="6" height="10" rx="2.5"/>'
               '<rect x="32" y="28" width="6" height="10" rx="2.5"/>',
    "video": '<rect x="8" y="13" width="24" height="22" rx="4"/><path d="M32 21l8-5v16l-8-5"/>',
    "map": '<path d="M8 13l10-4 12 4 10-4v26l-10 4-12-4-10 4z"/><path d="M18 9v26M30 13v26"/>',
    "compass": '<circle cx="24" cy="24" r="15"/><path d="M29.5 18.5 26 26l-7.5 3.5L22 22z"/>',
    "code": '<path d="M17 15 8 24l9 9M31 15l9 9-9 9M27 11l-6 26"/>',
}

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" role="img" aria-hidden="true">
<defs><linearGradient id="g-{name}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c3aed"/><stop offset="1" stop-color="#06b6d4"/></linearGradient>
<radialGradient id="b-{name}" cx=".3" cy=".25" r=".9"><stop offset="0" stop-color="#7c3aed" stop-opacity=".16"/><stop offset="1" stop-color="#06b6d4" stop-opacity=".06"/></radialGradient></defs>
<rect width="48" height="48" rx="12" fill="url(#b-{name})"/>
<g fill="none" stroke="url(#g-{name})" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
<style>.f{{fill:url(#g-{name});stroke:none}}</style>
{glyph}
</g></svg>
"""
for name, glyph in GLYPHS.items():
    (OUT / f"qicon-{name}.svg").write_text(TEMPLATE.format(name=name, glyph=glyph), encoding="utf-8")
print(f"{len(GLYPHS)} icons written to {OUT}")
