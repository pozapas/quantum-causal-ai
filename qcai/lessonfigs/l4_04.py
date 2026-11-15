"""Figures for L4-04 Backdoor adjustment.

The running model: Z ~ Bernoulli(0.5); P(X=1|Z=0) = 0.5 - c, P(X=1|Z=1) = 0.5 + c (c = 0.3 in the text);
P(Y=1|X,Z) = 0.2, 0.8 (X=1) and 0.1, 0.6 (X=0) for Z = 0, 1.  The true effect is 0.50 - 0.35 = 0.15.
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

RISK = {(1, 0): 0.2, (1, 1): 0.8, (0, 0): 0.1, (0, 1): 0.6}
PZ1 = 0.5


def _model(c: float) -> dict:
    """Observed and standardized risks when P(X=1|Z=z) = 0.5 - c, 0.5 + c."""
    px1 = {0: 0.5 - c, 1: 0.5 + c}
    pz = {0: 1 - PZ1, 1: PZ1}
    out = {}
    for x in (0, 1):
        w = {z: (px1[z] if x else 1 - px1[z]) * pz[z] for z in (0, 1)}
        tot = sum(w.values())
        out[f"obs{x}"] = sum(RISK[(x, z)] * w[z] / tot for z in (0, 1))
        out[f"std{x}"] = sum(RISK[(x, z)] * pz[z] for z in (0, 1))
        out[f"pz1_x{x}"] = w[1] / tot
    return out


def confounding_explorer():
    """Slider: confounding strength c.  Observed vs standardized risks, and the two contrasts."""
    cs = [round(0.05 * k, 2) for k in range(10)]            # 0.00 ... 0.45
    grid = np.linspace(0, 0.45, 46)
    fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.14,
                        subplot_titles=("Risk of Y = 1 in each arm", "Treated minus untreated"))
    cats = ["X = 1", "X = 0"]
    m0 = _model(0.3)
    fig.add_trace(go.Bar(x=cats, y=[round(m0["obs1"], 4), round(m0["obs0"], 4)], name="observed (naive)",
                         marker_color="#ef4444", text=[f"{m0['obs1']:.2f}", f"{m0['obs0']:.2f}"], textposition="outside",
                         cliponaxis=False), 1, 1)
    fig.add_trace(go.Bar(x=cats, y=[round(m0["std1"], 4), round(m0["std0"], 4)], name="standardized",
                         marker_color="#06b6d4", text=[f"{m0['std1']:.2f}", f"{m0['std0']:.2f}"], textposition="outside",
                         cliponaxis=False), 1, 1)
    naive = [_model(c)["obs1"] - _model(c)["obs0"] for c in grid]
    fig.add_trace(go.Scatter(x=grid.round(3).tolist(), y=np.round(naive, 4).tolist(), mode="lines",
                             line=dict(color="#ef4444", width=3), name="naive contrast"), 1, 2)
    fig.add_trace(go.Scatter(x=[0, 0.45], y=[0.15, 0.15], mode="lines", line=dict(color="#06b6d4", width=3, dash="dash"),
                             name="adjusted = true 0.15"), 1, 2)
    fig.add_trace(go.Scatter(x=[0.3], y=[round(m0["obs1"] - m0["obs0"], 4)], mode="markers",
                             marker=dict(size=13, color="#ef4444", line=dict(color="white", width=2)), showlegend=False,
                             hovertemplate="c = %{x}<br>naive contrast %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for c in cs:
        m = _model(c)
        steps.append(dict(method="restyle", label=f"{c:.2f}",
                          args=[{"y": [[round(m["obs1"], 4), round(m["obs0"], 4)], [round(m["std1"], 4), round(m["std0"], 4)],
                                       [round(m["obs1"] - m["obs0"], 4)]],
                                 "x": [cats, cats, [c]],
                                 "text": [[f"{m['obs1']:.2f}", f"{m['obs0']:.2f}"], [f"{m['std1']:.2f}", f"{m['std0']:.2f}"], None]},
                                [0, 1, 4]]))
    fig.update_yaxes(range=[0, 1.0], title="probability", row=1, col=1)
    fig.update_xaxes(tickangle=0, row=1, col=1)
    fig.update_xaxes(title="confounding strength c", range=[-0.02, 0.47], dtick=0.1, tickangle=0, row=1, col=2)
    fig.update_yaxes(title="risk difference", range=[0, 0.75], row=1, col=2)
    fig.update_layout(template="plotly_white", barmode="group",
                      sliders=[dict(active=cs.index(0.3), steps=steps, currentvalue=dict(prefix="strength c = "))])
    return frame(fig, height=540, stack=True)


def balance_before_after():
    """A continuous confounder in the two arms, before and after inverse probability weighting."""
    rng = np.random.default_rng(4)
    n = 40_000
    z = rng.normal(0, 1, n)
    e = 1 / (1 + np.exp(-1.5 * z))                     # propensity P(X=1 | Z = z)
    x = rng.random(n) < e
    w = np.where(x, 1 / e, 1 / (1 - e))
    bins = np.linspace(-4, 4, 41)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.5), sharey=True)
    for ax, weighted in zip(axes, (False, True)):
        for arm, col, name in ((True, "#7c3aed", "treated"), (False, "#3b82f6", "untreated")):
            sel = x == arm
            ww = w[sel] if weighted else None
            ax.hist(z[sel], bins=bins, weights=ww, density=True, histtype="stepfilled", alpha=0.3, color=col)
            ax.hist(z[sel], bins=bins, weights=ww, density=True, histtype="step", lw=1.8, color=col, label=name)
            mean = np.average(z[sel], weights=ww)
            ax.axvline(mean, color=col, lw=1.2, ls="--")
        t = np.linspace(-4, 4, 200)
        if weighted:
            ax.plot(t, np.exp(-t ** 2 / 2) / math.sqrt(2 * math.pi), color="#1e1b4b", lw=1.2, label="population N(0, 1)")
        m1 = np.average(z[x], weights=w[x] if weighted else None)
        m0 = np.average(z[~x], weights=w[~x] if weighted else None)
        ax.set_title(("after weighting by $1/P(X=x\\mid Z)$" if weighted else "observed data")
                     + f"\nmean of Z: treated {m1:+.2f}, untreated {m0:+.2f}", fontsize=10)
        ax.set_xlabel("confounder Z")
        ax.set_xlim(-4, 4)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("density")
    axes[1].legend(frameon=False, fontsize=8, loc="upper left")
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    return fig
