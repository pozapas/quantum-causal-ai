"""Figures for L4-06 Potential outcomes and randomization.

The science table: eight units with (Y(0), Y(1)) = (0,3), (1,5), (1,7), (2,4), (2,8), (3,6), (3,7), (4,8);
ATE = 6 - 2 = 4.  Self-selection (the four units with the highest Y(0) take the treatment) gives 6.25.
"""
from __future__ import annotations

import itertools
import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

Y0 = np.array([0, 1, 1, 2, 2, 3, 3, 4], float)
Y1 = np.array([3, 5, 7, 4, 8, 6, 7, 8], float)


def _experiments(k: int, reps: int = 2000, seed: int = 5):
    """Complete randomization of N = 8k units (the table copied k times), half treated."""
    y0, y1 = np.tile(Y0, k), np.tile(Y1, k)
    n = len(y0)
    rng = np.random.default_rng(seed + k)
    treat = np.argsort(rng.random((reps, n)), axis=1) < n // 2      # each row: a random half
    est = (y1 * treat).sum(1) / (n // 2) - (y0 * ~treat).sum(1) / (n // 2)
    imb = (y0 * treat).sum(1) / (n // 2) - (y0 * ~treat).sum(1) / (n // 2)
    return est, imb


def randomization_explorer():
    """Slider: number of units.  Histograms of the difference in means and of baseline imbalance."""
    ks = [1, 2, 4, 8, 16, 32]
    e_edges = np.arange(0.875, 7.2, 0.25)
    i_edges = np.arange(-2.125, 2.2, 0.25)
    ec, ic = (e_edges[:-1] + 0.125).round(3).tolist(), (i_edges[:-1] + 0.125).round(3).tolist()
    data = {}
    for k in ks:
        est, imb = _experiments(k)
        data[k] = (np.histogram(est, e_edges)[0] / len(est), np.histogram(imb, i_edges)[0] / len(imb), est.std(), imb.std())
    fig = make_subplots(rows=1, cols=2, column_widths=[0.55, 0.45], horizontal_spacing=0.13,
                        subplot_titles=("Difference in means", "Baseline imbalance in Y(0)"))
    k0 = 1
    fig.add_trace(go.Bar(x=ec, y=data[k0][0].round(4).tolist(), marker_color="#7c3aed", opacity=0.75, width=0.22,
                         name="randomized estimates", hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=[4, 4], y=[0, 1], mode="lines", line=dict(color="#1e1b4b", width=3), name="true ATE = 4"), 1, 1)
    fig.add_trace(go.Scatter(x=[6.25, 6.25], y=[0, 1], mode="lines", line=dict(color="#ef4444", width=3, dash="dash"),
                             name="self-selected 6.25"), 1, 1)
    fig.add_trace(go.Bar(x=ic, y=data[k0][1].round(4).tolist(), marker_color="#f59e0b", opacity=0.75, width=0.22,
                         name="baseline imbalance", hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for k in ks:
        he, hi, se, si = data[k]
        steps.append(dict(method="update", label=str(8 * k),
                          args=[{"y": [he.round(4).tolist(), hi.round(4).tolist()]},
                                {"yaxis.range": [0, round(1.15 * he.max(), 3)], "yaxis2.range": [0, round(1.15 * hi.max(), 3)],
                                 "annotations[0].text": f"Difference in means (sd {se:.2f})",
                                 "annotations[1].text": f"Baseline imbalance (sd {si:.2f})"}, [0, 3]]))
    fig.layout.annotations[0].text = f"Difference in means (sd {data[k0][2]:.2f})"
    fig.layout.annotations[1].text = f"Baseline imbalance (sd {data[k0][3]:.2f})"
    fig.update_xaxes(title="estimate of the ATE", range=[1, 7], dtick=1, tickangle=0, row=1, col=1)
    fig.update_yaxes(title="share of 2000 experiments", range=[0, round(1.15 * data[k0][0].max(), 3)], row=1, col=1)
    fig.update_xaxes(title="treated minus control mean of Y(0)", range=[-2.3, 2.3], dtick=1, tickangle=0, row=1, col=2)
    fig.update_yaxes(range=[0, round(1.15 * data[k0][1].max(), 3)], row=1, col=2)
    fig.update_layout(template="plotly_white", bargap=0,
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="number of units N = "))])
    return frame(fig, height=540, stack=True)


def exact_distribution():
    """All 70 complete randomizations of the eight-unit table: the exact randomization distribution."""
    est = []
    for T in itertools.combinations(range(8), 4):
        t = np.zeros(8, bool)
        t[list(T)] = True
        est.append(Y1[t].mean() - Y0[~t].mean())
    est = np.array(est)
    vals, counts = np.unique(est, return_counts=True)
    sd = math.sqrt(29 / 28)
    fig, ax = plt.subplots(figsize=(8.4, 3.4))
    ax.axvspan(4 - sd, 4 + sd, color="#ede9fe", zorder=0, label=f"mean ± sd ({sd:.2f})")
    ax.bar(vals, counts, width=0.2, color="#7c3aed", zorder=2, label="number of assignments")
    ax.axvline(est.mean(), color="#1e1b4b", lw=2, zorder=3, label=f"mean of all 70 = {est.mean():.2f} = ATE")
    ax.annotate("self-selected\nassignment: 6.25", xy=(6.25, 1), xytext=(5.6, 6.2), fontsize=9, color="#ef4444",
                arrowprops=dict(arrowstyle="-|>", color="#ef4444"))
    ax.set_xlabel("difference in means $\\hat\\tau$")
    ax.set_ylabel("assignments (of 70)")
    ax.set_xticks(np.arange(1.5, 7, 0.5))
    ax.set_title("Exact randomization distribution: 4 of 8 units treated, every split equally likely", fontsize=10)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.set_ylim(0, 9.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
