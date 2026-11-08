"""Render Plotly figures so they work on a static site with no kernel.

Plotly's default notebook HTML calls ``Plotly.newPlot`` before the CDN script
has finished loading when the output is injected after page load. This helper
waits for ``window.Plotly`` before drawing.
"""
from __future__ import annotations

import json
import uuid

from IPython.display import HTML

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"


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
    window.Plotly.newPlot(el, {{data: spec.data, layout: spec.layout, frames: spec.frames || [], config: {{responsive: true, displaylogo: false}}}});
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
