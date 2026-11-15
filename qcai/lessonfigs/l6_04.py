"""Figures for L6-04 Operational interventions."""
from __future__ import annotations

import math

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame


def _probs(p):
    """p(b = 0) for conditioning on a = 0, measure-and-discard, do(|0>), do(|1>)."""
    return [1.0, 0.5, round(1 - p / 2, 4), round(p / 2, 4)]


def operations_explorer():
    """Slider over the common-cause weight p: B's statistics and the x-y section of B's Bloch images."""
    ps = [round(0.1 * k, 1) for k in range(11)]
    cats = ["select<br>a = 0", "discard<br>outcome", "do(|0⟩)", "do(|1⟩)"]
    cols = ["#3b82f6", "#7c3aed", "#ef4444", "#f59e0b"]
    t = np.linspace(0, 2 * math.pi, 121)
    fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.14,
                        subplot_titles=("p(b = 0) at B (Z measurement)", "x-y section of B's Bloch images"))
    p0 = 0.5
    fig.add_trace(go.Bar(x=cats, y=_probs(p0), marker_color=cols, showlegend=False, text=[f"{v:.2f}" for v in _probs(p0)],
                         textposition="outside", hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=np.cos(t).round(4).tolist(), y=np.sin(t).round(4).tolist(), mode="lines",
                             line=dict(color="#cbd5e1", dash="dot"), name="A's options", hoverinfo="skip"), 1, 2)

    def cond(p):
        return np.cos(t).round(4).tolist(), ((1 - 2 * p) * np.sin(t)).round(4).tolist()

    def dov(p):
        return ((1 - p) * np.cos(t)).round(4).tolist(), ((1 - p) * np.sin(t)).round(4).tolist()

    cx, cy = cond(p0)
    dx, dy = dov(p0)
    fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines", line=dict(color="#3b82f6", width=3), name="condition on +n",
                             hoverinfo="skip"), 1, 2)
    fig.add_trace(go.Scatter(x=dx, y=dy, mode="lines", line=dict(color="#ef4444", width=3), name="replace by σ",
                             hoverinfo="skip"), 1, 2)
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=10, color="#7c3aed"), name="measure, discard",
                             hoverinfo="skip"), 1, 2)
    steps = []
    for p in ps:
        a, b = cond(p)
        c, d = dov(p)
        pr = _probs(p)
        steps.append(dict(method="restyle", label=f"{p:.1f}",
                          args=[{"x": [cats, a, c], "y": [pr, b, d], "text": [[f"{v:.2f}" for v in pr], None, None]},
                                [0, 2, 3]]))
    fig.update_xaxes(tickangle=0, row=1, col=1)
    fig.update_yaxes(range=[0, 1.12], dtick=0.25, title="probability", row=1, col=1)
    fig.update_xaxes(range=[-1.15, 1.15], dtick=0.5, title="x", constrain="domain", row=1, col=2)
    fig.update_yaxes(range=[-1.15, 1.15], dtick=0.5, title="y", scaleanchor="x2", constrain="domain", row=1, col=2)
    fig.update_layout(template="plotly_white",
                      title="Common-cause weight p: conditioning stays at 1,<br>interventions follow 1 - p/2 and p/2",
                      sliders=[dict(active=5, steps=steps, currentvalue=dict(prefix="common-cause weight p = "))])
    return frame(fig, height=600, xticks_lines=2, stack=True)
