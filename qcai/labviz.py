"""Small layout additions for the lab figures, applied after ``qcai.viz.frame``.

``frame`` stores a wide and a narrow layout in ``fig.layout.meta``; ``show`` switches between them.
The helpers here edit both stored layouts, so a change holds at every page width.
"""
from __future__ import annotations


def tweak(fig, *, both: dict | None = None, wide: dict | None = None, narrow: dict | None = None):
    """Add layout keys (dotted paths, as in ``frame``) to the wide and narrow layouts; returns ``fig``.

    A key that differs between the two layouts must be given in both ``wide`` and ``narrow``.
    """
    meta = fig.layout.meta
    q = meta["qcai"]
    for name, extra in (("wide", wide), ("narrow", narrow)):
        q[name].update(both or {})
        q[name].update(extra or {})
    for k, v in q["wide"].items():
        fig.layout[k] = v
    fig.layout.meta = meta
    return fig


def camera(fig, eye=(1.5, 1.5, 1.35), narrow_scale: float = 1.2):
    """Set the 3-D view; on narrow screens the camera moves back so the axis labels stay inside; returns ``fig``."""
    x, y, z = eye
    k = narrow_scale
    return tweak(fig, wide={"scene.camera.eye": dict(x=x, y=y, z=z)},
                 narrow={"scene.camera.eye": dict(x=k * x, y=k * y, z=k * z)})


def second_slider(fig, gap: int = 82):
    """Place ``sliders[1]`` in its own band under ``sliders[0]``; returns ``fig``.

    The figure grows by ``gap`` pixels at the bottom, so the plot area and every position
    measured from it stay as ``frame`` set them.
    """
    meta = fig.layout.meta
    q = meta["qcai"]
    for g in (q["wide"], q["narrow"]):
        ph = g["height"] - g["margin.t"] - g["margin.b"]
        g["height"] += gap
        g["margin.b"] += gap
        if "title.y" in g:
            fs = g["title.font.size"]
            g["title.y"] = 1 - (10 + fs) / g["height"]
        g.update({"sliders[1].y": g["sliders[0].y"] - gap / ph, "sliders[1].yanchor": "top", "sliders[1].x": 0,
                  "sliders[1].len": 1, "sliders[1].pad.t": 0, "sliders[1].pad.l": g.get("sliders[0].pad.l", 0),
                  "sliders[1].pad.r": g.get("sliders[0].pad.r", 0), "sliders[1].currentvalue.font.size": 13})
    for k, v in q["wide"].items():
        fig.layout[k] = v
    fig.layout.meta = meta
    return fig
