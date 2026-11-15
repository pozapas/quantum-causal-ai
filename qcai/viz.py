"""Render Plotly figures so they work on a static site with no kernel.

Plotly's default notebook HTML calls ``Plotly.newPlot`` before the CDN script
has finished loading when the output is injected after page load. ``show``
waits for ``window.Plotly`` before drawing.

``frame`` lays out the parts of an interactive figure (title, menu, legend,
subplot titles, slider) in fixed pixel bands so they never overlap, and adds a
second layout for narrow screens: one legend item per row, and side-by-side
panels stacked.  ``show`` picks the layout that fits the page width and
switches when the window is resized.
"""
from __future__ import annotations

import json
import math
import re
import uuid

from IPython.display import HTML

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"
NARROW_AT = 520      # figure widths below this (px) get the narrow layout (the book column is 586-614 px)
WIDE_TEXT = 490      # usable width (px) assumed when packing the legend on wide screens


def _plain(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "")


def _legend_items(fig) -> list[str]:
    if fig.layout.showlegend is False:
        return []
    seen, out = set(), []
    for t in fig.data:
        show = getattr(t, "showlegend", False)
        if show is False or not t.name or (t.type == "heatmap" and show is not True):
            continue
        g = getattr(t, "legendgroup", None) or id(t)
        if g not in seen:
            seen.add(g)
            out.append(t.name)
    return out


def _legend_grid(items: list[str], width: int) -> tuple[int, int]:
    """Columns and rows for a horizontal legend; every entry gets 1/cols of the plot width."""
    w = [44 + 7 * len(_plain(n)) for n in items]
    if sum(w) <= width:
        return len(items), 1
    cols = max(1, min(len(items), width // max(w)))
    return cols, math.ceil(len(items) / cols)


def frame(fig, *, height: int, xticks_lines: int = 1, stack: bool = False, narrow_plot: int | None = None,
          panel: int = 230, menu_x: float = 0.0, axes: bool = True):
    """Give ``fig`` a collision-free layout for wide and narrow screens; returns ``fig``.

    height        total height (px) on wide screens
    xticks_lines  lines of x tick labels (2 when labels contain <br>)
    stack         stack a 1x2 subplot grid vertically on narrow screens
    narrow_plot   plot-area height (px) on narrow screens when not stacked
    panel         height (px) of each stacked panel on narrow screens
    axes          False for figures without axes (diagrams), which need only thin side margins
    """
    lay = fig.layout
    title = lay.title.text or ""
    tlines = title.count("<br>") + 1 if title else 0
    items = _legend_items(fig)
    menu = bool(lay.updatemenus)
    slider = bool(lay.sliders)
    subs = [i for i, a in enumerate(lay.annotations)
            if a.showarrow is False and a.yanchor == "bottom" and a.xref == "paper" and a.yref == "paper"]
    xtitle = any(getattr(lay, k).title.text for k in lay if k.startswith("xaxis") and getattr(lay, k) is not None)
    x_band = 10 + 17 * xticks_lines + (26 if xtitle else 0)          # tick labels and axis title under a plot
    two = stack and "xaxis2" in lay and lay.xaxis2 is not None
    orig = {}
    if two:
        orig = {"xaxis.domain": list(lay.xaxis.domain), "xaxis2.domain": list(lay.xaxis2.domain),
                "yaxis.domain": list(lay.yaxis.domain), "yaxis2.domain": list(lay.yaxis2.domain)}
        for i in subs:
            orig[f"annotations[{i}].x"] = lay.annotations[i].x
            orig[f"annotations[{i}].y"] = lay.annotations[i].y

    def geom(narrow: bool) -> dict:
        line = 18 if narrow else 20
        top = 12 + (tlines * line + 8 if tlines else 0)
        menu_at = top
        if menu:
            top += 38
        legend_at = top
        if items:
            cols, rows = (1, len(items)) if narrow else _legend_grid(items, WIDE_TEXT)
            top += rows * 21 + 6
        stacked = narrow and two
        if subs:
            top += 26
        bottom = x_band + (86 if slider else 8)
        if not narrow:
            H = height
        elif stacked:
            H = top + 2 * panel + x_band + 30 + bottom
        else:
            H = top + (narrow_plot or min(height - top - bottom, 320)) + bottom
        ph = H - top - bottom
        paper = lambda px_from_top: (H - px_from_top - bottom) / ph  # noqa: E731
        g = {"height": H, "margin.t": top, "margin.b": bottom, "margin.l": (52 if narrow else 64) if axes else 12,
             "margin.r": (14 if narrow else 24) if axes else 12, "margin.autoexpand": False}
        if tlines:
            fs = 13 if narrow else 15         # Plotly anchors a multi-line title by its first line
            g.update({"title.y": 1 - (10 + fs) / H, "title.yref": "container", "title.yanchor": "bottom",
                      "title.x": 0, "title.xref": "container" if narrow else "paper", "title.xanchor": "left",
                      "title.pad.l": 12 if narrow else 0,
                      "title.font.size": fs})
        if menu:
            g.update({"updatemenus[0].y": paper(menu_at), "updatemenus[0].yanchor": "top",
                      "updatemenus[0].x": 0 if narrow else menu_x, "updatemenus[0].xanchor": "left",
                      "updatemenus[0].pad.t": 0, "updatemenus[0].pad.l": 0})
        if items:
            g.update({"legend.orientation": "v" if narrow else "h", "legend.x": 0, "legend.xanchor": "left",
                      "legend.y": paper(legend_at), "legend.yanchor": "top", "legend.traceorder": "normal",
                      "legend.font.size": 12, "legend.itemsizing": "constant",
                      "legend.entrywidthmode": "fraction", "legend.entrywidth": 0 if narrow else 1 / cols})
        if slider:
            g.update({"sliders[0].y": -x_band / ph, "sliders[0].yanchor": "top", "sliders[0].x": 0,
                      "sliders[0].len": 1, "sliders[0].pad.t": 0, "sliders[0].pad.l": 0, "sliders[0].pad.r": 0,
                      "sliders[0].currentvalue.font.size": 13})
        if two:
            if stacked:
                top_lo = paper(top + panel)
                bot_hi = paper(top + panel + x_band + 30)
                g.update({"xaxis.domain": [0, 1], "xaxis2.domain": [0, 1],
                          "yaxis.domain": [top_lo, 1], "yaxis2.domain": [0, bot_hi]})
                for k, i in enumerate(subs[:2]):
                    g[f"annotations[{i}].x"] = 0.5
                    g[f"annotations[{i}].y"] = 1 if k == 0 else bot_hi
            else:
                g.update(orig)
        for i in subs:
            g[f"annotations[{i}].font.size"] = 14
        return g

    wide, narrow = geom(False), geom(True)
    for k, v in wide.items():                  # also apply the wide layout to the figure itself
        fig.layout[k] = v
    fig.layout.meta = {"qcai": {"narrowAt": NARROW_AT, "wide": wide, "narrow": narrow}}
    return fig


def show(fig, height: int | None = None) -> HTML:
    """Return an HTML output that draws ``fig`` once Plotly is available."""
    div_id = "qcai-" + uuid.uuid4().hex[:10]
    spec = json.loads(fig.to_json())
    h = height or spec.get("layout", {}).get("height") or 460
    payload = json.dumps(spec)
    html = f"""
<div id="{div_id}" style="width:100%;height:{h}px"></div>
<script>
(function draw(){{
  var el = document.getElementById("{div_id}");
  if (!el) {{ return setTimeout(draw, 100); }}
  if (window.Plotly && window.Plotly.newPlot) {{
    var spec = {payload};
    var m = (spec.layout.meta || {{}}).qcai, cur = null;
    var pick = function () {{ return m ? (el.clientWidth < m.narrowAt ? m.narrow : m.wide) : null; }};
    var fit = function (g) {{ var u = Object.assign({{}}, g, {{autosize: true, width: null}}); return u; }};
    cur = pick();
    if (cur) {{ el.style.height = cur.height + "px"; }}
    window.Plotly.newPlot(el, {{data: spec.data, layout: spec.layout, frames: spec.frames || [], config: {{responsive: true, displaylogo: false}}}})
      .then(function () {{ if (cur && cur !== m.wide) {{ window.Plotly.relayout(el, fit(cur)); }} }});
    if (m) {{
      var t = null;
      window.addEventListener("resize", function () {{
        clearTimeout(t);
        t = setTimeout(function () {{
          var n = pick();
          if (n !== cur) {{
            cur = n; el.style.height = n.height + "px";
            window.Plotly.relayout(el, fit(n)).then(function () {{ window.Plotly.Plots.resize(el); }});
          }}
        }}, 150);
      }});
    }}
    return;
  }}
  if (!document.getElementById("qcai-plotly-cdn")) {{
    var s = document.createElement("script");
    s.id = "qcai-plotly-cdn"; s.src = "{PLOTLY_CDN}"; s.charset = "utf-8";
    document.head.appendChild(s);
  }}
  setTimeout(draw, 100);
}})();
</script>
"""
    return HTML(html)
