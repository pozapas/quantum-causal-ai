"""Figures for L7-01 Define the learning task."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai import science as s
from qcai.viz import frame


def _adjusted(c):
    """Backdoor adjustment over Z for the SCM of science.causal (prevalence 0.5)."""
    base, effect = 0.1, 0.2
    return sum(0.5 * ((base + effect + c * z) - (base + c * z)) for z in (0, 1))


def confounding_explorer():
    """Slider over the confounding strength c: observed contrast, backdoor-adjusted contrast, true effect."""
    cs = [round(0.05 * i, 2) for i in range(11)]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.45, 0.55], horizontal_spacing=0.16,
                        subplot_titles=("Three numbers at strength c", "Observed contrast as c grows"))
    names = ["observed<br>contrast", "adjusted<br>for Z", "true<br>effect τ"]

    def vals(c):
        r = s.causal(confound=c)
        return [round(r["observed"], 4), round(_adjusted(c), 4), round(r["ate"], 4)]

    c0 = cs[-1]
    fig.add_trace(go.Bar(x=names, y=vals(c0), marker_color=["#3b82f6", "#06b6d4", "#7c3aed"], showlegend=False,
                         text=[f"{v:.2f}" for v in vals(c0)], textposition="outside",
                         hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 1)
    grid = np.linspace(0, 0.5, 51)
    fig.add_trace(go.Scatter(x=grid.round(3).tolist(), y=[round(s.causal(confound=c)["observed"], 4) for c in grid],
                             mode="lines", line=dict(color="#3b82f6", width=3), name="observed = 0.2 + 0.6c"), 1, 2)
    fig.add_trace(go.Scatter(x=[0, 0.5], y=[0.2, 0.2], mode="lines", line=dict(color="#7c3aed", width=3, dash="dash"),
                             name="true effect τ = 0.2"), 1, 2)
    fig.add_trace(go.Scatter(x=[c0], y=[vals(c0)[0]], mode="markers", marker=dict(size=12, color="#3b82f6"),
                             showlegend=False, hovertemplate="c = %{x}<br>observed %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for c in cs:
        v = vals(c)
        steps.append(dict(method="restyle", label=f"{c:g}",
                          args=[{"y": [v, [v[0]]], "x": [names, [c]], "text": [[f"{u:.2f}" for u in v], None]}, [0, 3]]))
    fig.update_yaxes(range=[0, 0.62], title="difference in P(Y = 1)", row=1, col=1)
    fig.update_xaxes(tickangle=0, row=1, col=1)
    fig.update_xaxes(title="confounding strength c", range=[-0.01, 0.51], dtick=0.1, row=1, col=2)
    fig.update_yaxes(range=[0, 0.62], row=1, col=2)
    fig.update_layout(template="plotly_white", title="Confounding moves the prediction contrast, not the effect",
                      sliders=[dict(active=len(cs) - 1, steps=steps, currentvalue=dict(prefix="strength c = "))])
    return frame(fig, height=540, xticks_lines=2, stack=True)


def access_grid():
    """Data and processing: four combinations, each with an example and the claim it can support."""
    fig, ax = plt.subplots(figsize=(8.8, 5.0))
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.axis("off")
    cells = {
        (0, 1): ("classical data, classical processing",
                 "tabular records, gradient boosting\nbaseline for every claim"),
        (1, 1): ("classical data, quantum processing",
                 "records loaded by circuits (kernels, VQCs)\ncount encoding and shots; compare\nwith tuned classical learners"),
        (0, 0): ("quantum data, classical processing",
                 "measurement records from a device\n(shadows, tomography) analyzed\nclassically"),
        (1, 0): ("quantum data, quantum processing",
                 "copies of states or calls to a process,\nprocessed coherently; count copies,\nqueries and memory"),
    }
    colors = {(0, 1): "#e2e8f0", (1, 1): "#ede9fe", (0, 0): "#cffafe", (1, 0): "#fef3c7"}
    for (cx, cy), (head, body) in cells.items():
        ax.add_patch(plt.Rectangle((cx + 0.03, cy + 0.03), 0.94, 0.94, color=colors[(cx, cy)], ec="#475569", lw=1))
        ax.text(cx + 0.5, cy + 0.84, head, ha="center", va="center", fontsize=10, weight="bold", color="#1e1b4b")
        ax.text(cx + 0.5, cy + 0.42, body, ha="center", va="center", fontsize=9, color="#1e1b4b", linespacing=1.4)
    ax.set_title("Specify the data and the processing before the method", fontsize=11, color="#1e1b4b")
    fig.tight_layout()
    return fig
