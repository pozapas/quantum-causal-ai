"""Figures for L3-08 Entropy and uncertainty."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame


def _h2(p: float) -> float:
    return 0.0 if p in (0.0, 1.0) else -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def _entropy(ps) -> float:
    return float(sum(-p * math.log2(p) for p in ps if p > 0))


def entropy_explorer():
    """A coin with P(heads) = p: probability and surprise of each face (left), binary entropy (right)."""
    ps = [round(0.05 * k, 2) for k in range(1, 20)]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.42, 0.58], horizontal_spacing=0.14,
                        subplot_titles=("Each face: probability and surprise", "Average surprise h(p)"))
    p0 = 0.1

    def bars(p):
        return [round(p, 4), round(1 - p, 4)], [round(-math.log2(p), 4), round(-math.log2(1 - p), 4)]

    pr, su = bars(p0)
    cats = ["heads", "tails"]
    fig.add_trace(go.Bar(x=cats, y=pr, name="probability", marker_color="#3b82f6", text=[f"{v:.2f}" for v in pr],
                         textposition="outside", cliponaxis=False), 1, 1)
    fig.add_trace(go.Bar(x=cats, y=su, name="surprise (bits)", marker_color="#f59e0b", text=[f"{v:.2f}" for v in su],
                         textposition="outside", cliponaxis=False), 1, 1)
    xs = np.linspace(0, 1, 201)
    fig.add_trace(go.Scatter(x=xs.round(3).tolist(), y=[round(_h2(float(x)), 4) for x in xs], mode="lines",
                             line=dict(color="#ef4444", width=3), name="h(p)"), 1, 2)
    fig.add_trace(go.Scatter(x=[p0], y=[round(_h2(p0), 4)], mode="markers", marker=dict(size=13, color="#7c3aed"),
                             name="this coin", hovertemplate="p = %{x}<br>h = %{y:.3f} bits<extra></extra>"), 1, 2)
    steps = []
    for p in ps:
        pr, su = bars(p)
        steps.append(dict(method="restyle", label=f"{p:.2f}",
                          args=[{"y": [pr, su, [round(_h2(p), 4)]], "x": [cats, cats, [p]],
                                 "text": [[f"{v:.2f}" for v in pr], [f"{v:.2f}" for v in su], None]}, [0, 1, 3]]))
    fig.update_layout(template="plotly_white", barmode="group",
                      sliders=[dict(active=ps.index(p0), steps=steps, currentvalue=dict(prefix="P(heads) = p = "))])
    fig.update_yaxes(title="probability or bits", range=[0, 5.2], row=1, col=1)
    fig.update_xaxes(tickangle=0, row=1, col=1)
    fig.update_xaxes(title="P(heads) = p", range=[0, 1], dtick=0.25, row=1, col=2)
    fig.update_yaxes(title="entropy (bits)", range=[0, 1.08], row=1, col=2)
    return frame(fig, height=540, stack=True)


def four_distributions():
    """Four distributions on four outcomes, from certain to uniform, with their entropies."""
    dists = [("certain", [1, 0, 0, 0]), ("one likely", [0.7, 0.1, 0.1, 0.1]),
             ("halving", [0.5, 0.25, 0.125, 0.125]), ("uniform", [0.25, 0.25, 0.25, 0.25])]
    fig, axes = plt.subplots(1, 4, figsize=(10, 3.1), sharey=True)
    for ax, (name, ps) in zip(axes, dists):
        ax.bar(["A", "B", "C", "D"], ps, color="#3b82f6", width=0.6)
        ax.set_title(f"{name}\n$H = {_entropy(ps):.3f}$ bits", fontsize=10)
        ax.set_ylim(0, 1.05)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("probability")
    fig.suptitle("More spread, more entropy: from 0 bits (certain) up to $\\log_2 4 = 2$ bits (uniform)", fontsize=11)
    fig.tight_layout()
    return fig
