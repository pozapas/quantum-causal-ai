"""Figures for L4-09 Counterfactual reasoning.

Running model: X := U_X, Y := 2X + U_Y with U_X ~ N(0, 1) and U_Y ~ N(1, 1) independent.
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

BETA, MU_UX, VAR_UX, MU_UY, VAR_UY = 2.0, 0.0, 1.0, 1.0, 1.0
VAR_Y = BETA ** 2 * VAR_UX + VAR_UY        # 5
MEAN_Y = BETA * MU_UX + MU_UY              # 1


def _post(y):
    """Posterior of (U_X, U_Y) given Y = y only: means and the variance of U_Y."""
    mx = MU_UX + BETA * VAR_UX / VAR_Y * (y - MEAN_Y)
    my = MU_UY + VAR_UY / VAR_Y * (y - MEAN_Y)
    return mx, my, VAR_UY - VAR_UY ** 2 / VAR_Y


def _pdf(t, m, v):
    return np.exp(-(t - m) ** 2 / (2 * v)) / math.sqrt(2 * math.pi * v)


def evidence_explorer():
    """Slider over the observed Y: the evidence line in the noise plane and the law of Y_{X=0}."""
    ys = list(range(1, 10))
    fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.14,
                        subplot_titles=("Abduction in the noise plane", "What Y would have been at X = 0"))
    th = np.linspace(0, 2 * math.pi, 121)
    for r, op in ((1, 0.9), (2, 0.5)):
        fig.add_trace(go.Scatter(x=(MU_UX + r * np.cos(th)).round(4).tolist(), y=(MU_UY + r * np.sin(th)).round(4).tolist(),
                                 mode="lines", line=dict(color="#94a3b8", dash="dot"), opacity=op, hoverinfo="skip",
                                 showlegend=False), 1, 1)
    ux = np.array([-3.5, 3.5])
    t = np.linspace(-3, 7, 251)

    def parts(y):
        mx, my, pv = _post(y)
        line_y = (y - BETA * ux).round(4).tolist()
        return line_y, (mx, my), (1.0, y - BETA * 1.0), _pdf(t, my, pv).round(5).tolist(), y - BETA

    y0 = 5
    ly, (mx, my), full, dens, cf = parts(y0)
    fig.add_trace(go.Scatter(x=ux.tolist(), y=ly, mode="lines", line=dict(color="#3b82f6", width=3),
                             name="evidence Y = y"), 1, 1)
    fig.add_trace(go.Scatter(x=[mx], y=[my], mode="markers", marker=dict(size=11, color="#3b82f6"),
                             name="posterior mean", hovertemplate="u<sub>X</sub> %{x:.2f}, u<sub>Y</sub> %{y:.2f}<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=[full[0]], y=[full[1]], mode="markers", marker=dict(size=12, color="#06b6d4", symbol="diamond"),
                             name="also seen X = 1", hovertemplate="u<sub>X</sub> %{x:.2f}, u<sub>Y</sub> %{y:.2f}<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=t.round(3).tolist(), y=_pdf(t, MU_UY, VAR_UY).round(5).tolist(), mode="lines",
                             line=dict(color="#7c3aed", dash="dash"), name="no evidence: N(1, 1)"), 1, 2)
    fig.add_trace(go.Scatter(x=t.round(3).tolist(), y=dens, mode="lines", line=dict(color="#3b82f6", width=3),
                             showlegend=False, hovertemplate="value %{x:.2f}<br>density %{y:.3f}<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=[cf, cf], y=[0, 0.62], mode="lines", line=dict(color="#06b6d4", width=4),
                             showlegend=False, hovertemplate="X = 1 also seen: Y<sub>X=0</sub> = %{x:.1f}<extra></extra>"), 1, 2)
    steps = []
    for y in ys:
        ly, (mx, my), full, dens, cf = parts(y)
        steps.append(dict(method="restyle", label=f"{y}",
                          args=[{"x": [ux.tolist(), [round(mx, 4)], [full[0]], t.round(3).tolist(), [cf, cf]],
                                 "y": [ly, [round(my, 4)], [full[1]], dens, [0, 0.62]]}, [2, 3, 4, 6, 7]]))
    fig.update_xaxes(range=[-3.5, 3.5], title="u<sub>X</sub>", dtick=1, constrain="domain", row=1, col=1)
    fig.update_yaxes(range=[-2.5, 8.5], title="u<sub>Y</sub>", dtick=2, row=1, col=1)
    fig.update_xaxes(range=[-3, 7], title="Y<sub>X=0</sub>", dtick=1, row=1, col=2)
    fig.update_yaxes(range=[0, 0.65], title="density", row=1, col=2)
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=ys.index(y0), steps=steps, currentvalue=dict(prefix="observed Y = "))])
    return frame(fig, height=600, stack=True)


def pn_bounds():
    """Bounds on the probability of necessity under exogeneity, as P(y | x) varies."""
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.7), sharey=True)
    for ax, q in zip(axes, (0.2, 0.5)):
        p = np.linspace(0.1, 1.0, 300)
        lo = np.maximum(0, (p - q) / p)
        hi = np.minimum(1, (1 - q) / p)
        ax.fill_between(p, lo, hi, color="#c4b5fd", alpha=0.6, lw=0)
        ax.plot(p, lo, color="#7c3aed", lw=2, label="lower bound (equals PN under monotonicity)")
        ax.plot(p, hi, color="#f59e0b", lw=2, label="upper bound")
        ax.set_title(f"$P(y \\mid x') = {q}$", fontsize=11)
        ax.set_xlabel("$P(y \\mid x)$")
        ax.set_xlim(0, 1.02)
        ax.set_ylim(-0.03, 1.05)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("probability of necessity PN")
    axes[1].scatter([0.5], [0], color="#3b82f6", zorder=4, s=36)
    axes[1].scatter([0.5], [1], color="#f59e0b", zorder=4, s=36)
    axes[1].annotate("model A", (0.5, 0.0), xytext=(0.62, 0.06), fontsize=9, color="#3b82f6",
                     arrowprops=dict(arrowstyle="-", color="#3b82f6", lw=0.8))
    axes[1].annotate("model B", (0.5, 1.0), xytext=(0.62, 0.95), fontsize=9, color="#b45309",
                     arrowprops=dict(arrowstyle="-", color="#b45309", lw=0.8))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, fontsize=9)
    fig.suptitle("Experiments bound PN but rarely pin it down: the shaded band is every value the data allow", fontsize=10)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    return fig
