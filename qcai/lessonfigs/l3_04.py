"""Figures for L3-04 Tensor products and joint systems."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame


def entangle_explorer():
    """c(theta) = cos(theta)|00> + sin(theta)|11> as a 2 x 2 table, and its determinant against theta."""
    degs = [round(7.5 * k, 1) for k in range(13)]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.42, 0.58], horizontal_spacing=0.16,
                        subplot_titles=("Amplitude table c<sub>ab</sub>", "det = cos θ sin θ"))

    def table(d):
        t = math.radians(d)
        z = [[round(math.cos(t), 4), 0.0], [0.0, round(math.sin(t), 4)]]
        txt = [[f"{v:.3f}" for v in row] for row in z]
        return z, txt

    z, txt = table(degs[0])
    fig.add_trace(go.Heatmap(z=z, x=["b = 0", "b = 1"], y=["a = 0", "a = 1"], text=txt, texttemplate="%{text}",
                             textfont=dict(size=16), zmin=0, zmax=1, showscale=False,
                             colorscale=[[0, "#f8fafc"], [1, "#7c3aed"]], hoverinfo="skip"), 1, 1)
    xs = np.linspace(0, 90, 91)
    fig.add_trace(go.Scatter(x=xs.tolist(), y=(np.cos(np.radians(xs)) * np.sin(np.radians(xs))).round(4).tolist(),
                             mode="lines", line=dict(color="#7c3aed"), name="cos θ sin θ"), 1, 2)
    fig.add_trace(go.Scatter(x=[0, 90], y=[0, 0], mode="markers", marker=dict(size=10, color="#06b6d4", symbol="diamond"),
                             name="product state"), 1, 2)
    fig.add_trace(go.Scatter(x=[degs[0]], y=[0.0], mode="markers", marker=dict(size=13, color="#ef4444"), showlegend=False,
                             hovertemplate="θ = %{x}°<br>det = %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for d in degs:
        z, txt = table(d)
        t = math.radians(d)
        det = round(math.cos(t) * math.sin(t), 4)
        steps.append(dict(method="restyle", label=f"{d:g}°",
                          args=[{"z": [z, z], "text": [txt, [f"{det:.3f}"]],
                                 "x": [["b = 0", "b = 1"], [d]], "y": [["a = 0", "a = 1"], [det]]}, [0, 3]]))
    fig.update_yaxes(autorange="reversed", row=1, col=1)
    fig.update_xaxes(tickangle=0, row=1, col=1)
    fig.update_xaxes(title="θ (degrees)", range=[-3, 93], dtick=15, tickangle=0, row=1, col=2)
    fig.update_yaxes(title="determinant", range=[-0.03, 0.55], dtick=0.1, row=1, col=2)
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="θ = "))])
    return frame(fig, height=500, stack=True)


def kron_blocks():
    """A (2 x 2) and B (3 x 3) and their Kronecker product A (x) B (6 x 6), block by block."""
    A = np.array([[1, 2], [3, -1]])
    B = np.array([[0, 1, 0], [1, 0, 1], [2, 0, 0]])
    K = np.kron(A, B)
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.9), gridspec_kw=dict(width_ratios=[2, 3, 6]))
    shades = ["#ede9fe", "#cffafe", "#fef3c7", "#fee2e2"]

    def draw(ax, M, title, blocks=False):
        n, m = M.shape
        for i in range(n):
            for j in range(m):
                fc = shades[(i // 3) * 2 + (j // 3)] if blocks else "#f8fafc"
                ax.add_patch(plt.Rectangle((j, n - 1 - i), 1, 1, fc=fc, ec="#cbd5e1", lw=0.8))
                ax.text(j + 0.5, n - 0.5 - i, f"{M[i, j]:g}", ha="center", va="center", fontsize=11,
                        color="#1e1b4b" if M[i, j] != 0 else "#94a3b8")
        if blocks:
            for k in (3,):
                ax.plot([k, k], [0, n], color="#7c3aed", lw=2)
                ax.plot([0, m], [n - k, n - k], color="#7c3aed", lw=2)
            for bi in range(2):
                for bj in range(2):
                    yy, va = (n + 0.12, "bottom") if bi == 0 else (-0.12, "top")
                    ax.text(bj * 3 + 1.5, yy, f"{A[bi, bj]:g}·B", ha="center", va=va, fontsize=10, color="#7c3aed")
        ax.set_xlim(-0.1, m + 0.1)
        ax.set_ylim(-0.7 if blocks else -0.1, n + (0.7 if blocks else 0.1))
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=11)

    draw(axes[0], A, "$A$ (2 × 2)")
    draw(axes[1], B, "$B$ (3 × 3)")
    draw(axes[2], K, "$A \\otimes B$ (6 × 6): block $(j, k)$ is $A_{jk}B$", blocks=True)
    fig.tight_layout()
    return fig
