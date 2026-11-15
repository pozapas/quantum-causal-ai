"""Figures for L3-07 Expectation and variance."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

P = 0.25                       # chance of a 1 in each draw (the lesson's running Bernoulli example)
SIG = math.sqrt(P * (1 - P))   # 0.4330


def _binom_pmf(n, p):
    out = np.zeros(n + 1)
    for k in range(n + 1):
        out[k] = math.comb(n, k) * p ** k * (1 - p) ** (n - k)
    return out


def bernoulli_means():
    """Exact distribution of the mean of n independent 0/1 draws with P(1) = 0.25, and its spread against n."""
    ns = [1, 2, 4, 8, 16, 32, 64, 128]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.6, 0.4], horizontal_spacing=0.14,
                        subplot_titles=("Distribution of the sample mean", "Spread of the mean"))

    def dist(n):
        pm = _binom_pmf(n, P)
        x = (np.arange(n + 1) / n)
        keep = pm > 1e-5
        return x[keep].round(5).tolist(), pm[keep].round(6).tolist()

    x0, y0 = dist(ns[0])
    fig.add_trace(go.Bar(x=x0, y=y0, marker_color="#7c3aed", name="P(mean = value)", width=0.06,
                         hovertemplate="mean %{x:.3f}<br>probability %{y:.4f}<extra></extra>"), 1, 1)
    top0 = round(max(y0) * 1.3, 4)
    fig.add_trace(go.Scatter(x=[P, P], y=[0, top0], mode="lines", line=dict(color="#ef4444", dash="dash"),
                             name="expectation 0.25", hoverinfo="skip"), 1, 1)
    sd0 = SIG / math.sqrt(ns[0])
    fig.add_trace(go.Scatter(x=[P - sd0, P + sd0], y=[round(top0 * 0.9, 4)] * 2, mode="lines+markers",
                             line=dict(color="#f59e0b", width=4), name="mean ± σ/√n", hoverinfo="skip"), 1, 1)
    nn = np.arange(1, 129)
    fig.add_trace(go.Scatter(x=nn.tolist(), y=(SIG / np.sqrt(nn)).round(5).tolist(), mode="lines", line=dict(color="#f59e0b"),
                             showlegend=False, hovertemplate="n = %{x}<br>σ/√n = %{y:.4f}<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=[ns[0]], y=[round(sd0, 5)], mode="markers", marker=dict(size=12, color="#f59e0b"),
                             showlegend=False, hovertemplate="n = %{x}<br>σ/√n = %{y:.4f}<extra></extra>"), 1, 2)
    steps = []
    for n in ns:
        x, y = dist(n)
        sd = SIG / math.sqrt(n)
        top = round(max(y) * 1.3, 4)
        steps.append(dict(method="update", label=str(n),
                          args=[{"x": [x, [P, P], [round(P - sd, 5), round(P + sd, 5)], [n]],
                                 "y": [y, [0, top], [round(top * 0.9, 4)] * 2, [round(sd, 5)]],
                                 "width": [min(0.9 / n, 0.06), None, None, None]},
                                {"yaxis.range": [0, top]}, [0, 1, 2, 4]]))
    fig.update_xaxes(title="sample mean", range=[-0.03, 1.03], dtick=0.25, row=1, col=1)
    fig.update_yaxes(title="probability", range=[0, round(max(y0) * 1.3, 4)], row=1, col=1)
    fig.update_xaxes(title="number of draws n", type="log", range=[-0.05, 2.2], tickvals=[1, 4, 16, 64], row=1, col=2)
    fig.update_yaxes(title="σ/√n", range=[0, 0.46], row=1, col=2)
    fig.update_layout(template="plotly_white", bargap=0,
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="number of draws n = "))])
    return frame(fig, height=560, stack=True)


def same_mean_spread():
    """Three distributions with the same mean 2 and different spreads."""
    cases = [([1, 2, 3], [0.25, 0.5, 0.25]), ([0, 1, 2, 3, 4], [0.2] * 5), ([0, 4], [0.5, 0.5])]
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.5), sharey=True)
    for ax, (xs, ps) in zip(axes, cases):
        xs, ps = np.array(xs, float), np.array(ps)
        mu = float(xs @ ps)
        var = float(((xs - mu) ** 2) @ ps)
        sd = math.sqrt(var)
        ax.vlines(xs, 0, ps, color="#7c3aed", lw=3)
        ax.scatter(xs, ps, color="#7c3aed", zorder=3, s=30)
        ax.axvline(mu, color="#ef4444", ls="--", lw=1.2)
        ax.annotate("", xy=(mu + sd, 0.62), xytext=(mu - sd, 0.62),
                    arrowprops=dict(arrowstyle="<->", color="#f59e0b", lw=2))
        ax.text(mu, 0.66, f"μ ± σ, σ = {sd:.3g}", ha="center", color="#b45309", fontsize=9, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
        ax.set_title(f"mean {mu:g}, variance {var:g}", fontsize=10)
        ax.set_xlim(-0.6, 4.6)
        ax.set_ylim(0, 0.75)
        ax.set_xticks(range(5))
        ax.set_xlabel("outcome x")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("P(X = x)")
    fig.suptitle("Same mean, different spread: the mean alone does not describe a distribution", fontsize=10)
    fig.tight_layout()
    return fig
