"""Figures and shared numbers for L7-06 Sample complexity and resource accounting."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame


# ------------------------------------------------------------------------------------------------
# concentration
# ------------------------------------------------------------------------------------------------
def n_hoeffding(eps: float, delta: float, width: float = 2.0, m: int = 1) -> int:
    """Samples so that a mean of variables in an interval of length `width` is within eps with prob >= 1 - delta,
    simultaneously for m means (union bound): N >= width^2 ln(2m/delta) / (2 eps^2)."""
    return math.ceil(width ** 2 * math.log(2 * m / delta) / (2 * eps ** 2))


def n_chebyshev(eps: float, delta: float, var: float = 1.0) -> int:
    return math.ceil(var / (delta * eps ** 2))


def n_normal(eps: float, delta: float, var: float = 1.0) -> int:
    """Normal approximation (a heuristic, not a bound)."""
    from statistics import NormalDist
    z = NormalDist().inv_cdf(1 - delta / 2)
    return math.ceil(z * z * var / eps ** 2)


def band_hoeffding(n, delta):
    return np.sqrt(2 * np.log(2 / delta) / np.asarray(n, dtype=float))


def band_chebyshev(n, delta):
    return np.sqrt(1 / (delta * np.asarray(n, dtype=float)))


EPS, DELTA = 0.1, 0.05
N_H = n_hoeffding(EPS, DELTA)          # 738
N_C = n_chebyshev(EPS, DELTA)          # 2000
N_Z = n_normal(EPS, DELTA)             # 385
N_H_100 = n_hoeffding(EPS, DELTA, m=100)   # 1659
assert N_H == 738 and N_C == 2000 and N_Z == 385 and N_H_100 == 1659
assert abs(200 * math.log(40) - 737.78) < 0.01

MU = 0.2                                # mean of the +-1 outcomes in the band demonstration


def mean_paths(paths: int, nmax: int, seed: int = 11) -> np.ndarray:
    """Running means of +-1 outcomes with mean MU; shape (paths, nmax)."""
    g = np.random.default_rng(seed)
    x = np.where(g.random((paths, nmax)) < (1 + MU) / 2, 1.0, -1.0)
    return np.cumsum(x, axis=1) / np.arange(1, nmax + 1)


def band_exit_stats(paths: int = 400, nmin: int = 10, nmax: int = 10000, delta: float = DELTA, seed: int = 11):
    """Fraction of independent means outside the Hoeffding band at fixed N = nmax, and fraction of running-mean
    paths that leave the band somewhere in [nmin, nmax]."""
    m = mean_paths(paths, nmax, seed)
    ns = np.arange(1, nmax + 1)
    out = np.abs(m - MU) >= band_hoeffding(ns, delta)
    ever = out[:, nmin - 1:].any(axis=1).mean()
    fixed = out[:, -1].mean()
    return float(fixed), float(ever)


# ------------------------------------------------------------------------------------------------
# Grover and the ledger
# ------------------------------------------------------------------------------------------------
def grover(n_items: int):
    th = math.asin(1 / math.sqrt(n_items))
    k = math.floor(math.pi / (4 * th))
    return k, math.sin((2 * k + 1) * th) ** 2


N_ITEMS = 2 ** 20                       # 1,048,576
K_GROVER, P_GROVER = grover(N_ITEMS)    # 804 iterations
CLASSICAL_WORST = N_ITEMS - 1           # 1,048,575 queries (deterministic, one marked item)
assert K_GROVER == 804 and P_GROVER > 0.999999
K10, P10 = grover(2 ** 10)
assert K10 == 25


# ------------------------------------------------------------------------------------------------
# phase estimation with dephasing: Fisher information
# ------------------------------------------------------------------------------------------------
def fisher_per_query(k, gamma):
    """Fisher information per query for k sequential queries per shot at the best working point: k exp(-2 gamma k)."""
    k = np.asarray(k, dtype=float)
    return k * np.exp(-2 * gamma * k)


GAMMA = 0.01
K_OPT = 1 / (2 * GAMMA)                 # 50
F_OPT = 1 / (2 * math.e * GAMMA)        # 18.39 per query
assert abs(F_OPT - 18.394) < 1e-3


# ------------------------------------------------------------------------------------------------
# interactive 1: sample size against accuracy
# ------------------------------------------------------------------------------------------------
def sample_size_explorer():
    eps = np.geomspace(0.005, 0.5, 60)
    deltas = [0.2, 0.1, 0.05, 0.01, 0.001, 1e-4, 1e-6]
    d0 = deltas[2]

    def curves(d):
        return ([n_hoeffding(e, d) for e in eps], [n_chebyshev(e, d) for e in eps], [n_normal(e, d) for e in eps],
                [n_hoeffding(e, d, m=100) for e in eps])

    h, c, z, u = curves(d0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=eps.tolist(), y=h, mode="lines", name="Hoeffding (bound)", line=dict(color="#7c3aed", width=3),
                             hovertemplate="ε = %{x:.3f}<br>N = %{y:,}<extra></extra>"))
    fig.add_trace(go.Scatter(x=eps.tolist(), y=c, mode="lines", name="Chebyshev (bound)", line=dict(color="#f59e0b", width=3),
                             hovertemplate="ε = %{x:.3f}<br>N = %{y:,}<extra></extra>"))
    fig.add_trace(go.Scatter(x=eps.tolist(), y=z, mode="lines", name="normal approx. (no bound)", line=dict(color="#475569", dash="dot"),
                             hovertemplate="ε = %{x:.3f}<br>N ≈ %{y:,}<extra></extra>"))
    fig.add_trace(go.Scatter(x=eps.tolist(), y=u, mode="lines", name="Hoeffding, 100 means", line=dict(color="#06b6d4", dash="dash"),
                             hovertemplate="ε = %{x:.3f}<br>N per mean = %{y:,}<extra></extra>"))
    steps = []
    for d in deltas:
        h, c, z, u = curves(d)
        steps.append(dict(method="restyle", label=f"{d:g}", args=[{"y": [h, c, z, u]}, [0, 1, 2, 3]]))
    fig.update_xaxes(type="log", title="accuracy ε (outcomes in [−1, 1])", tickangle=0)
    fig.update_yaxes(type="log", title="samples N", range=[0.5, 8.5], exponentformat="power")
    fig.update_layout(template="plotly_white", title="Samples needed for |mean − μ| < ε<br>with probability at least 1 − δ",
                      sliders=[dict(active=2, steps=steps, currentvalue=dict(prefix="failure probability δ = "))])
    return frame(fig, height=540, narrow_plot=330)


# ------------------------------------------------------------------------------------------------
# interactive 2: queries per shot under dephasing
# ------------------------------------------------------------------------------------------------
def fisher_explorer():
    ks = np.geomspace(1, 5000, 160)
    gammas = [0.0, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1]
    g0 = 0.01
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ks.tolist(), y=ks.tolist(), mode="lines", name="no dephasing: F/Q = k",
                             line=dict(color="#94a3b8", dash="dash"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=ks.tolist(), y=fisher_per_query(ks, g0).tolist(), mode="lines", name="with dephasing γ",
                             line=dict(color="#7c3aed", width=3), hovertemplate="k = %{x:.0f}<br>F/Q = %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[1 / (2 * g0)], y=[1 / (2 * math.e * g0)], mode="markers", name="optimum k = 1/(2γ)",
                             marker=dict(size=12, color="#ef4444"), hovertemplate="k* = %{x:.0f}<br>F/Q = %{y:.2f}<extra></extra>"))
    steps = []
    for g in gammas:
        if g == 0:
            steps.append(dict(method="restyle", label="0", args=[{"x": [ks.tolist(), [5000]], "y": [ks.tolist(), [5000]]}, [1, 2]]))
        else:
            steps.append(dict(method="restyle", label=f"{g:g}",
                              args=[{"x": [ks.tolist(), [1 / (2 * g)]], "y": [fisher_per_query(ks, g).tolist(), [1 / (2 * math.e * g)]]}, [1, 2]]))
    fig.update_xaxes(type="log", title="queries per shot k", tickangle=0)
    fig.update_yaxes(type="log", title="Fisher information per query", range=[-1, 3.8], exponentformat="power")
    fig.update_layout(template="plotly_white", title="Total budget Q queries: deeper shots help only<br>until dephasing wins",
                      sliders=[dict(active=gammas.index(g0), steps=steps, currentvalue=dict(prefix="dephasing per query γ = "))])
    return frame(fig, height=540, narrow_plot=330)


# ------------------------------------------------------------------------------------------------
# static figure: Grover success probability is not monotone in queries
# ------------------------------------------------------------------------------------------------
def grover_success():
    n_items = 2 ** 10
    th = math.asin(1 / math.sqrt(n_items))
    k = np.arange(0, 81)
    p = np.sin((2 * k + 1) * th) ** 2
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.plot(k, p, "o-", ms=3, lw=1.2, color="#7c3aed", label="Grover, $N = 2^{10}$")
    ax.plot(k, np.minimum(k / n_items, 1), color="#f59e0b", lw=2, label="classical: $k$ queries find it w.p. $k/N$")
    ax.axvline(K10, color="#475569", ls=":", lw=1)
    ax.text(K10 + 1, 0.15,f"k = {K10}: success {P10:.4f}", fontsize=9, color="#475569")
    ax.set_xlabel("oracle queries $k$")
    ax.set_ylabel("probability of finding the marked item")
    ax.set_ylim(-0.03, 1.05)
    ax.set_title("Success probability $\\sin^2((2k+1)\\theta)$ with $\\sin\\theta = 1/\\sqrt{N}$: more queries can hurt", fontsize=10)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=9, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig


_ = make_subplots
