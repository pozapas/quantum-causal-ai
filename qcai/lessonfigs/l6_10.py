"""Figures for L6-10 Design a quantum causal experiment."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from scipy.stats import binom

from qcai.viz import frame

ALPHA, BETA, V = 0.025, 0.10, 0.9


def t_n(n):
    """One-sided Hoeffding margin for S_hat with N shots in each of the three settings."""
    return math.sqrt(6 * math.log(1 / ALPHA) / n)


def power(S, n):
    """Exact P(S_hat > 1 + t_N) when c = (S/3)(1, 1, 1)."""
    thr = n * (4 + t_n(n)) / 2
    return float(binom.sf(math.floor(thr), 3 * n, (1 + S / 3) / 2))


def statistic_vs_mixing():
    """Seeded estimates of S against the mixing weight p, with Hoeffding margins, for several shot counts."""
    ps = np.round(np.linspace(0, 1, 21), 2)
    Ns = [30, 100, 300, 579, 1000, 3000]
    g = np.random.default_rng(2026)
    data = {}
    for n in Ns:
        s_true = 3 * V * (2 * ps - 1)
        K = g.binomial(3 * n, (1 + s_true / 3) / 2)
        est = (2 * K - 3 * n) / n
        t = t_n(n)
        col = ["#ef4444" if e > 1 + t else ("#3b82f6" if e < -1 - t else "#64748b") for e in est]
        data[n] = (est.round(4).tolist(), round(t, 4), col)
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, x1=1, y0=-1, y1=1, fillcolor="#e2e8f0", opacity=0.5, line_width=0, layer="below")
    pp = np.linspace(0, 1, 101)
    fig.add_trace(go.Scatter(x=pp.tolist(), y=(3 * V * (2 * pp - 1)).round(4).tolist(), mode="lines",
                             line=dict(color="#7c3aed", width=2), name="true S = 3v(2p − 1)"))
    n0 = 579
    est, t, col = data[n0]
    fig.add_trace(go.Scatter(x=ps.tolist(), y=est, mode="markers", marker=dict(size=9, color=col),
                             error_y=dict(type="constant", value=t, color="#94a3b8", thickness=1.5),
                             name="estimate ± t<sub>N</sub>", hovertemplate="p = %{x}<br>Ŝ = %{y:.3f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[0, 1], y=[1 + t, 1 + t], mode="lines", line=dict(color="#ef4444", dash="dash"),
                             name="reject common cause"))
    fig.add_trace(go.Scatter(x=[0, 1], y=[-1 - t, -1 - t], mode="lines", line=dict(color="#3b82f6", dash="dash"),
                             name="reject cause-effect"))
    steps = []
    for n in Ns:
        est, t, col = data[n]
        steps.append(dict(method="restyle", label=str(n),
                          args=[{"y": [est, [1 + t, 1 + t], [-1 - t, -1 - t]], "error_y.value": [t, None, None],
                                 "marker.color": [col, None, None]}, [1, 2, 3]]))
    fig.update_xaxes(title="mixing weight p of the direct channel", range=[-0.03, 1.03], dtick=0.25)
    fig.update_yaxes(title="S = c<sub>x</sub> + c<sub>y</sub> + c<sub>z</sub>", range=[-3.6, 3.6], dtick=1)
    fig.update_layout(template="plotly_white",
                      title="Seeded estimates of S (v = 0.9)<br>Gray band: no verdict, even with<br>infinite data",
                      sliders=[dict(active=Ns.index(n0), steps=steps, currentvalue=dict(prefix="shots per setting N = "))])
    return frame(fig, height=560)


def power_curves():
    """Exact power and the Hoeffding guarantee against N, for three alternatives, plus the exact type I error."""
    ns = np.arange(10, 1201, 5)
    fig, ax = plt.subplots(figsize=(8.6, 3.9))
    for S, c in ((1.2, "#f59e0b"), (1.35, "#ef4444"), (1.6, "#7c3aed")):
        ax.plot(ns, [power(S, int(n)) for n in ns], color=c, lw=2, label=f"exact, S = {S}")
        lb = [1 - math.exp(-n * (S - 1 - t_n(n)) ** 2 / 6) if S - 1 > t_n(n) else 0 for n in ns]
        ax.plot(ns, lb, color=c, lw=1.4, ls="--")
    ax.plot(ns, [power(1.0, int(n)) for n in ns], color="#3b82f6", lw=1.6, label="exact type I at S = 1")
    ax.axhline(0.9, color="#94a3b8", lw=0.8)
    ax.axhline(ALPHA, color="#3b82f6", lw=0.8, ls=":")
    ax.axvline(579, color="#475569", lw=1, ls=":")
    ax.text(585, 0.45, "N = 579", fontsize=9, color="#475569")
    ax.text(1195, 0.915, "power 0.9", fontsize=8, color="#64748b", ha="right")
    ax.text(1195, 0.04, r"$\alpha = 0.025$", fontsize=8, color="#3b82f6", ha="right")
    ax.set_xlabel("shots per setting N")
    ax.set_ylabel("P(reject common cause)")
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlim(0, 1200)
    ax.set_title("Solid: exact binomial power. Dashed: Hoeffding guarantee (same color)", fontsize=10)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
