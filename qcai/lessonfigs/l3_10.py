"""Figures for L3-10 Estimation, intervals, and repeated tests."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import binom

from qcai.viz import frame

Z = 1.96


def _wald(k, n):
    ph = k / n
    se = math.sqrt(ph * (1 - ph) / n)
    return ph - Z * se, ph + Z * se


def _coverage(n, p):
    ks = np.arange(n + 1)
    ok = np.array([lo <= p <= hi for lo, hi in (_wald(int(k), n) for k in ks)])
    return float(binom.pmf(ks, n, p)[ok].sum())


def coverage_explorer(n0: int = 100):
    """40 simulated 95% Wald intervals for p = 0.3 (left) and the exact coverage of the recipe against p (right)."""
    ns = [10, 20, 30, 50, 100, 200, 500]
    p_true, m = 0.3, 40
    ps = np.round(np.linspace(0.01, 0.99, 99), 2)
    fig = make_subplots(rows=1, cols=2, column_widths=[0.45, 0.55], horizontal_spacing=0.14,
                        subplot_titles=("40 studies with true p = 0.3", "Exact coverage of the recipe"))

    def sim(n):
        rng = np.random.default_rng(1000 + n)
        ks = rng.binomial(n, p_true, m)
        hit_x, hit_y, miss_x, miss_y = [], [], [], []
        for i, k in enumerate(ks):
            lo, hi = _wald(int(k), n)
            xs, ys = (hit_x, hit_y) if lo <= p_true <= hi else (miss_x, miss_y)
            xs += [round(lo, 4), round(hi, 4), None]
            ys += [i + 1, i + 1, None]
        return hit_x, hit_y, miss_x, miss_y

    def cov(n):
        return [round(_coverage(n, float(p)), 4) for p in ps]


    hx, hy, mx, my = sim(n0)
    fig.add_trace(go.Scatter(x=hx, y=hy, mode="lines+markers", line=dict(color="#3b82f6", width=3), marker=dict(size=4), name="covers p"), 1, 1)
    fig.add_trace(go.Scatter(x=mx, y=my, mode="lines+markers", line=dict(color="#ef4444", width=4), marker=dict(size=6), name="misses p"), 1, 1)
    fig.add_trace(go.Scatter(x=[p_true, p_true], y=[0, m + 1], mode="lines", line=dict(color="#1e1b4b", dash="dash"),
                             showlegend=False, hoverinfo="skip"), 1, 1)
    fig.add_trace(go.Scatter(x=ps.tolist(), y=cov(n0), mode="lines", line=dict(color="#7c3aed", width=2),
                             name="exact coverage", hovertemplate="p = %{x}<br>coverage %{y:.3f}<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=[0, 1], y=[0.95, 0.95], mode="lines", line=dict(color="#f59e0b", dash="dash", width=2),
                             name="95% target"), 1, 2)
    steps = []
    for n in ns:
        hx, hy, mx, my = sim(n)
        steps.append(dict(method="restyle", label=str(n),
                          args=[{"x": [hx, mx, ps.tolist()], "y": [hy, my, cov(n)]}, [0, 1, 3]]))
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=ns.index(n0), steps=steps, currentvalue=dict(prefix="trials per study n = "))])
    fig.update_xaxes(title="estimated p with 95% interval", range=[-0.1, 1.0], dtick=0.2, row=1, col=1)
    fig.update_yaxes(title="study", range=[0, m + 1], showticklabels=False, row=1, col=1)
    fig.update_xaxes(title="true p", range=[0, 1], dtick=0.25, row=1, col=2)
    fig.update_yaxes(title="P(interval contains p)", range=[0, 1.02], dtick=0.25, row=1, col=2)
    return frame(fig, height=540, stack=True)


def repeated_tests():
    """Left: chance of at least one false positive among m true-null tests. Right: trials needed for +/- 0.05."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6))
    m = np.arange(1, 101)
    a1.plot(m, 1 - 0.95 ** m, color="#ef4444", lw=2, label="each at level 0.05")
    a1.plot(m, 1 - (1 - 0.05 / m) ** m, color="#7c3aed", lw=2, label="Bonferroni, level 0.05/m")
    a1.axhline(0.05, color="#94a3b8", lw=1, ls="--")
    a1.scatter([20], [1 - 0.95 ** 20], color="#ef4444", zorder=3)
    a1.annotate(f"m = 20: {1 - 0.95 ** 20:.3f}", (20, 1 - 0.95 ** 20), xytext=(34, 0.5), fontsize=9,
                arrowprops=dict(arrowstyle="-", color="#475569"))
    a1.set_xlabel("number of independent tests $m$ (all nulls true)")
    a1.set_ylabel("P(at least one false positive)")
    a1.set_ylim(0, 1.02)
    a1.legend(frameon=False, fontsize=9, loc="lower right", bbox_to_anchor=(1.0, 0.1))
    a1.set_title("Repeated tests inflate false positives", fontsize=10)

    eps = np.linspace(0.02, 0.1, 81)
    a2.plot(eps, (1.96 / (2 * eps)) ** 2, color="#3b82f6", lw=2, label="normal approximation")
    a2.plot(eps, np.log(2 / 0.05) / (2 * eps ** 2), color="#f59e0b", lw=2, label="Hoeffding bound")
    a2.plot(eps, 1 / (4 * 0.05 * eps ** 2), color="#ef4444", lw=2, label="Chebyshev bound")
    a2.set_yscale("log")
    a2.axvline(0.05, color="#94a3b8", lw=1, ls="--")
    a2.set_xlabel(r"margin $\varepsilon$ (95% confidence, worst case $p = 1/2$)")
    a2.set_ylabel("trials $n$ needed")
    a2.legend(frameon=False, fontsize=9)
    a2.set_title("At $\\varepsilon = 0.05$: 385, 738, or 2000 trials", fontsize=10)
    for ax in (a1, a2):
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
