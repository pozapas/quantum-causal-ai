"""Figures for L7-03 Quantum kernels and data access."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

M = 8
XG = 2 * np.pi * np.arange(M) / M
KG = np.cos((XG[:, None] - XG[None, :]) / 2) ** 2


def _noisy(n, seed=100):
    g = np.random.default_rng(seed)
    kh = np.eye(M)
    iu = np.triu_indices(M, 1)
    v = g.binomial(n, KG[iu]) / n
    kh[iu] = v
    kh[(iu[1], iu[0])] = v
    return kh


def gram_explorer():
    """Slider over shots per entry: the estimated Gram matrix and its eigenvalues against the exact ones."""
    ns = [10, 30, 100, 300, 1000, 3000, 10000, 100000]
    exact_ev = np.sort(np.linalg.eigvalsh(KG))[::-1]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.16,
                        subplot_titles=("Estimated Gram matrix", "Eigenvalues, largest first"))
    k0 = _noisy(ns[0])
    labels = [str(i) for i in range(M)]
    fig.add_trace(go.Heatmap(z=k0.round(3), x=labels, y=labels, zmin=-0.2, zmax=1, colorscale=[[0, "#ef4444"], [0.1667, "#ffffff"], [1, "#7c3aed"]],
                             showscale=False, hovertemplate="i %{y}, j %{x}<br>K̂ %{z:.3f}<extra></extra>"), 1, 1)
    idx = list(range(1, M + 1))
    fig.add_trace(go.Bar(x=idx, y=exact_ev.round(4), marker_color="#cbd5e1", name="exact (4, 2, 2, 0, ...)"), 1, 2)
    fig.add_trace(go.Bar(x=idx, y=np.sort(np.linalg.eigvalsh(k0))[::-1].round(4), marker_color="#7c3aed",
                         name="estimate"), 1, 2)
    steps = []
    for n in ns:
        kh = _noisy(n)
        ev = np.sort(np.linalg.eigvalsh(kh))[::-1]
        steps.append(dict(method="update", label=f"{n:g}",
                          args=[{"z": [kh.round(3)], "y": [labels, ev.round(4)]},
                                {"title.text": f"Shot noise in a quantum Gram matrix<br>N = {n} shots per entry, smallest eigenvalue {ev.min():.3f}"},
                                [0, 2]]))
    fig.update_yaxes(autorange="reversed", title="i", row=1, col=1)
    fig.update_xaxes(title="j", tickangle=0, row=1, col=1)
    fig.update_xaxes(title="eigenvalue index", dtick=1, tickangle=0, row=1, col=2)
    fig.update_yaxes(title="eigenvalue", range=[-0.6, 4.4], row=1, col=2)
    ev0 = np.linalg.eigvalsh(k0).min()
    fig.update_layout(template="plotly_white", barmode="group",
                      title=f"Shot noise in a quantum Gram matrix<br>N = {ns[0]} shots per entry, smallest eigenvalue {ev0:.3f}",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="shots per entry N = "))])
    return frame(fig, height=560, stack=True)


def concentration():
    """Product feature map on n qubits: distribution of k for random input pairs, and E k against shot noise."""
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.7))
    edges = np.linspace(0, 1, 41)
    colors = {1: "#93c5fd", 2: "#3b82f6", 4: "#7c3aed", 8: "#1e1b4b"}
    for n in (1, 2, 4, 8):
        g = np.random.default_rng(5 + n)
        x = g.uniform(0, 2 * math.pi, size=(20000, n))
        z = g.uniform(0, 2 * math.pi, size=(20000, n))
        k = np.prod(np.cos((x - z) / 2) ** 2, axis=1)
        axes[0].hist(k, bins=edges, density=True, histtype="step", lw=2, color=colors[n], label=f"n = {n}, mean {k.mean():.3f}")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("kernel value $k(x, x')$")
    axes[0].set_ylabel("density (log scale)")
    axes[0].set_title("Random input pairs, product map", fontsize=10)
    axes[0].legend(fontsize=8, frameon=False)
    n = np.arange(1, 21)
    mean = 2.0 ** -n
    sd = np.sqrt((3 / 8) ** n - 4.0 ** -n)
    axes[1].semilogy(n, mean, "o-", color="#7c3aed", ms=4, label="$E\\,k = 2^{-n}$")
    axes[1].semilogy(n, sd, "s-", color="#3b82f6", ms=4, label="sd over inputs")
    for N, ls in ((1000, "--"), (100000, ":")):
        axes[1].semilogy(n, np.sqrt(mean * (1 - mean) / N), ls, color="#f59e0b", lw=2, label=f"shot sd at $k = 2^{{-n}}$, N = {N:g}")
    axes[1].set_xlabel("qubits n")
    axes[1].set_title("Typical value against estimation noise", fontsize=10)
    axes[1].legend(fontsize=8, frameon=False, loc="lower left")
    axes[1].set_xticks([1, 5, 10, 15, 20])
    for ax in axes:
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.grid(True, color="#e2e8f0", lw=0.6)
    fig.tight_layout()
    return fig
