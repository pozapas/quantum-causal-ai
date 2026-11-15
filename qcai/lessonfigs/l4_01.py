"""Figures for L4-01 Structural causal models.

The binary model is the course engine's  Z -> X -> Y <- Z  (qcai.science.causal) with its default
numbers; the linear model is  Z ~ N(0,1), X = Z + N_X, Y = X + 2Z + N_Y.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai import science
from qcai.viz import frame

# binary SCM (course engine defaults): P(Z=1) = 0.5, P(X=1|Z) = 0.8 or 0.2, P(Y=1|X,Z) = 0.1 + 0.2 X + c Z
PREV, LOW, HIGH, BASE, EFFECT, CONF = 0.5, 0.2, 0.8, 0.1, 0.2, 0.5
B = science.causal(PREV, LOW, HIGH, BASE, EFFECT, CONF)
assert abs(B["treated"] - 0.70) < 1e-12 and abs(B["untreated"] - 0.20) < 1e-12
assert abs(B["do1"] - 0.55) < 1e-12 and abs(B["do0"] - 0.35) < 1e-12 and abs(B["observed"] - 0.50) < 1e-12

# linear-Gaussian SCM for the slopes figure
SLOPE_OBS = (2 + 2 * 1) / 2      # Cov(X, Y) / Var(X) = (Var X + 2 Cov(X, Z)) / Var X = (2 + 2) / 2
SLOPE_DO = 1.0
assert SLOPE_OBS == 2.0


def see_vs_do():
    """Seeing versus doing in the binary SCM as the confounding strength c varies (slider)."""
    cs = [round(0.05 * k, 2) for k in range(13)]          # 0 to 0.6, so every probability stays in [0, 1]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.14,
                        subplot_titles=("Risk of Y = 1", "Risk difference"))

    def vals(c):
        r = science.causal(PREV, LOW, HIGH, BASE, EFFECT, c)
        return [r["untreated"], r["treated"]], [r["do0"], r["do1"]], r["observed"]

    s0, d0, o0 = vals(CONF)
    cats = ["X = 0", "X = 1"]
    fig.add_trace(go.Bar(x=cats, y=[round(v, 4) for v in s0], name="seeing P(Y=1 | X=x)", marker_color="#3b82f6",
                         hovertemplate="%{x}: %{y:.3f}<extra>seeing</extra>"), 1, 1)
    fig.add_trace(go.Bar(x=cats, y=[round(v, 4) for v in d0], name="doing P(Y=1 | do(X=x))", marker_color="#f59e0b",
                         hovertemplate="%{x}: %{y:.3f}<extra>doing</extra>"), 1, 1)
    grid = np.linspace(0, 0.6, 61)
    fig.add_trace(go.Scatter(x=grid.round(3).tolist(), y=(EFFECT + (HIGH - LOW) * grid).round(4).tolist(), mode="lines",
                             line=dict(color="#3b82f6", width=3), name="observed contrast", showlegend=True), 1, 2)
    fig.add_trace(go.Scatter(x=[0, 0.6], y=[EFFECT, EFFECT], mode="lines", line=dict(color="#f59e0b", width=3, dash="dash"),
                             name="causal effect (ATE)"), 1, 2)
    fig.add_trace(go.Scatter(x=[CONF], y=[round(o0, 4)], mode="markers", marker=dict(size=13, color="#3b82f6"),
                             showlegend=False, hovertemplate="c = %{x}<br>observed contrast %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for c in cs:
        s, d, o = vals(c)
        steps.append(dict(method="restyle", label=f"{c:.2f}",
                          args=[{"y": [[round(v, 4) for v in s], [round(v, 4) for v in d], [round(o, 4)]],
                                 "x": [cats, cats, [c]]}, [0, 1, 4]]))
    fig.update_yaxes(range=[0, 1], title="probability", row=1, col=1)
    fig.update_xaxes(title="value of X (seen or set)", row=1, col=1)
    fig.update_xaxes(title="confounding strength c", range=[0, 0.6], dtick=0.1, row=1, col=2)
    fig.update_yaxes(title="X = 1 minus X = 0", range=[0, 0.6], row=1, col=2)
    fig.update_layout(template="plotly_white", barmode="group",
                      sliders=[dict(active=cs.index(CONF), steps=steps, currentvalue=dict(prefix="confounding c = "))])
    return frame(fig, height=540, stack=True)


def slopes_figure():
    """Observational cloud (slope 2) versus interventional samples (slope 1) in the linear SCM."""
    g = np.random.default_rng(4)
    n = 600
    z = g.normal(size=n)
    x = z + g.normal(size=n)
    y = x + 2 * z + g.normal(size=n)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9), sharey=True)
    ax = axes[0]
    ax.scatter(x, y, s=8, color="#3b82f6", alpha=0.45, lw=0)
    b = np.polyfit(x, y, 1)
    xs = np.linspace(-4, 4, 2)
    ax.plot(xs, SLOPE_OBS * xs, color="#1e1b4b", lw=2, label="population slope 2")
    ax.set_title(f"Seeing: samples of $(X, Y)$\nfitted slope {b[0]:.2f}, population slope 2", fontsize=10)
    ax.set_xlabel("$X$ as observed")
    ax.set_ylabel("$Y$")
    ax = axes[1]
    for xv in (-2, -1, 0, 1, 2):
        zz = g.normal(size=120)
        yy = xv + 2 * zz + g.normal(size=120)
        ax.scatter(np.full(120, xv) + g.uniform(-0.12, 0.12, 120), yy, s=8, color="#f59e0b", alpha=0.45, lw=0)
        ax.plot([xv - 0.3, xv + 0.3], [xv, xv], color="#7c3aed", lw=2.5)
    ax.plot(xs, SLOPE_DO * xs, color="#1e1b4b", lw=2)
    ax.set_title("Doing: samples under $do(X = x)$\nmeans fall on slope 1", fontsize=10)
    ax.set_xlabel("$x$ as set by the intervention")
    for a in axes:
        a.set_xlim(-4, 4)
        a.set_ylim(-9, 9)
        a.axhline(0, color="#e2e8f0", lw=0.8, zorder=0)
        a.axvline(0, color="#e2e8f0", lw=0.8, zorder=0)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.suptitle("$Z \\sim N(0,1)$,  $X := Z + N_X$,  $Y := X + 2Z + N_Y$", fontsize=10)
    fig.tight_layout()
    return fig
