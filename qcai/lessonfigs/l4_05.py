"""Figures for L4-05 Frontdoor identification.

The model (all binary): U ~ Bernoulli(0.5) unmeasured; P(X=1|U) = 0.25 + 0.5U; P(M=1|X) = 0.2 + 0.6X;
P(Y=1|M,U) = 0.6M + 0.4U.  True effect 0.68 - 0.32 = 0.36; the frontdoor formula recovers it exactly.
Two violations are explored with a strength s in [0, 0.5]:
  direct  P(Y=1|M,U,X) = (1-s)(0.6M + 0.4U) + s X           (a direct X -> Y arrow)
  hidden  P(M=1|X,U)   = (1-s)(0.2 + 0.6X) + s U            (an arrow U -> M)
"""
from __future__ import annotations

import itertools

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame


def _probs(kind: str = "none", s: float = 0.0):
    pu = lambda u: 0.5  # noqa: E731
    px = lambda x, u: (0.25 + 0.5 * u) if x else 1 - (0.25 + 0.5 * u)  # noqa: E731

    def pm(m, x, u):
        p = 0.2 + 0.6 * x
        if kind == "hidden":
            p = (1 - s) * p + s * u
        return p if m else 1 - p

    def py(y, m, u, x):
        p = 0.6 * m + 0.4 * u
        if kind == "direct":
            p = (1 - s) * p + s * x
        return p if y else 1 - p
    return pu, px, pm, py


def analyse(kind: str = "none", s: float = 0.0) -> dict:
    """Exact truth, frontdoor formula and naive contrast for the model (or a violated version)."""
    pu, px, pm, py = _probs(kind, s)
    J = {(u, x, m, y): pu(u) * px(x, u) * pm(m, x, u) * py(y, m, u, x) for u, x, m, y in itertools.product((0, 1), repeat=4)}

    def P(**f):
        return sum(v for (u, x, m, y), v in J.items() if all({"u": u, "x": x, "m": m, "y": y}[k] == w for k, w in f.items()))
    PX = {x: P(x=x) for x in (0, 1)}
    pm1 = {x: P(x=x, m=1) / PX[x] for x in (0, 1)}
    py1 = {(m, x): P(m=m, x=x, y=1) / P(m=m, x=x) for m in (0, 1) for x in (0, 1)}
    resp = {m: sum(py1[(m, x)] * PX[x] for x in (0, 1)) for m in (0, 1)}
    fd = {x: pm1[x] * resp[1] + (1 - pm1[x]) * resp[0] for x in (0, 1)}
    true = {x: sum(pu(u) * pm(m, x, u) * py(1, m, u, x) for u in (0, 1) for m in (0, 1)) for x in (0, 1)}
    naive = {x: P(x=x, y=1) / PX[x] for x in (0, 1)}
    return {"true": true[1] - true[0], "frontdoor": fd[1] - fd[0], "naive": naive[1] - naive[0]}


def frontdoor_violations():
    """Slider: strength of a violation.  Bars: truth, frontdoor formula, naive; curves: frontdoor bias."""
    ss = [round(0.05 * k, 2) for k in range(11)]
    grid = np.linspace(0, 0.5, 51)
    cats = ["direct X→Y<br>arrow added", "hidden U→M<br>arrow added"]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.14,
                        subplot_titles=("Risk difference at strength s", "Frontdoor formula minus truth"))

    def bars(s):
        a, b = analyse("direct", s), analyse("hidden", s)
        return ([round(a["true"], 4), round(b["true"], 4)], [round(a["frontdoor"], 4), round(b["frontdoor"], 4)],
                [round(a["naive"], 4), round(b["naive"], 4)])
    t0, f0, n0 = bars(0.2)
    fig.add_trace(go.Bar(x=cats, y=t0, name="truth", marker_color="#1e1b4b"), 1, 1)
    fig.add_trace(go.Bar(x=cats, y=f0, name="frontdoor formula", marker_color="#06b6d4"), 1, 1)
    fig.add_trace(go.Bar(x=cats, y=n0, name="naive contrast", marker_color="#ef4444"), 1, 1)
    bias_d = [analyse("direct", s)["frontdoor"] - analyse("direct", s)["true"] for s in grid]
    bias_h = [analyse("hidden", s)["frontdoor"] - analyse("hidden", s)["true"] for s in grid]
    fig.add_trace(go.Scatter(x=grid.round(3).tolist(), y=np.round(bias_d, 4).tolist(), mode="lines",
                             line=dict(color="#7c3aed", width=3), name="bias: direct arrow"), 1, 2)
    fig.add_trace(go.Scatter(x=grid.round(3).tolist(), y=np.round(bias_h, 4).tolist(), mode="lines",
                             line=dict(color="#f59e0b", width=3), name="bias: U→M arrow"), 1, 2)

    def marks(s):
        a, b = analyse("direct", s), analyse("hidden", s)
        return [s, s], [round(a["frontdoor"] - a["true"], 4), round(b["frontdoor"] - b["true"], 4)]
    mx, my = marks(0.2)
    fig.add_trace(go.Scatter(x=mx, y=my, mode="markers", marker=dict(size=12, color=["#7c3aed", "#f59e0b"],
                             line=dict(color="white", width=2)), showlegend=False,
                             hovertemplate="s = %{x}<br>bias %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for s in ss:
        t, f, n = bars(s)
        x2, y2 = marks(s)
        steps.append(dict(method="restyle", label=f"{s:.2f}", args=[{"y": [t, f, n, y2], "x": [cats, cats, cats, x2]}, [0, 1, 2, 5]]))
    fig.update_yaxes(title="risk difference", range=[0, 0.75], row=1, col=1)
    fig.update_xaxes(tickangle=0, row=1, col=1)
    fig.update_xaxes(title="violation strength s", range=[-0.02, 0.52], dtick=0.1, tickangle=0, row=1, col=2)
    fig.update_yaxes(title="bias", range=[-0.55, 0.32], zeroline=True, zerolinecolor="#94a3b8", row=1, col=2)
    fig.update_layout(template="plotly_white", barmode="group",
                      sliders=[dict(active=ss.index(0.2), steps=steps, currentvalue=dict(prefix="strength s = "))])
    return frame(fig, height=560, xticks_lines=2, stack=True)


def sampling_distributions():
    """Naive contrast and frontdoor estimate across 400 simulated studies of 2000 units each."""
    rng = np.random.default_rng(11)
    reps, n = 400, 2000
    u = rng.random((reps, n)) < 0.5
    x = rng.random((reps, n)) < 0.25 + 0.5 * u
    m = rng.random((reps, n)) < 0.2 + 0.6 * x
    y = rng.random((reps, n)) < 0.6 * m + 0.4 * u

    def mean_where(v, w):
        return (v * w).sum(1) / w.sum(1)
    naive = mean_where(y, x) - mean_where(y, ~x)
    px1 = x.mean(1)
    pm1 = {1: mean_where(m, x), 0: mean_where(m, ~x)}
    resp = {}
    for mv in (0, 1):
        sel_m = m if mv else ~m
        resp[mv] = mean_where(y, sel_m & x) * px1 + mean_where(y, sel_m & ~x) * (1 - px1)
    fd = {xv: pm1[xv] * resp[1] + (1 - pm1[xv]) * resp[0] for xv in (0, 1)}
    front = fd[1] - fd[0]
    fig, ax = plt.subplots(figsize=(8.4, 3.4))
    bins = np.linspace(0.2, 0.7, 61)
    ax.hist(front, bins=bins, color="#06b6d4", alpha=0.55, label="frontdoor estimate")
    ax.hist(naive, bins=bins, color="#ef4444", alpha=0.55, label="naive contrast")
    ax.axvline(0.36, color="#1e1b4b", lw=2, label="true effect 0.36")
    ax.axvline(0.56, color="#ef4444", lw=1.2, ls="--")
    ax.set_xlabel("estimated risk difference")
    ax.set_ylabel("number of studies")
    ax.set_title(f"400 studies of n = 2000: frontdoor mean {front.mean():.3f} (sd {front.std():.3f}), "
                 f"naive mean {naive.mean():.3f}", fontsize=10)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    fig.tight_layout()
    return fig
