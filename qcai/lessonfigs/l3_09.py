"""Figures for L3-09 Optimization and learning."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from numpy.polynomial import Polynomial
from plotly.subplots import make_subplots

from qcai.viz import frame

W0 = (-4.0, 1.2)
SEED = 132


def _loss(w1, w2):
    return w1 ** 2 + 4 * w2 ** 2


def _gd(eta, steps=15):
    pts = [W0]
    for _ in range(steps):
        w1, w2 = pts[-1]
        pts.append((w1 - eta * 2 * w1, w2 - eta * 8 * w2))
    return pts


def step_size_explorer(eta0: float = 0.1):
    """Gradient descent on L = w1^2 + 4 w2^2: path on the contour map (left) and loss per step (right)."""
    etas = [0.02, 0.05, 0.1, 0.15, 0.2, 0.24, 0.26]
    g1 = np.linspace(-5, 5, 81)
    g2 = np.linspace(-4, 4, 65)
    Z = np.array([[_loss(a, b) for a in g1] for b in g2])
    fig = make_subplots(rows=1, cols=2, column_widths=[0.55, 0.45], horizontal_spacing=0.14,
                        subplot_titles=("Path on the contour map", "Loss after each step"))
    fig.add_trace(go.Contour(x=g1.round(3).tolist(), y=g2.round(3).tolist(), z=Z.round(3).tolist(), showscale=False,
                             contours=dict(start=1, end=49, size=4, coloring="lines"), colorscale=[[0, "#06b6d4"], [1, "#06b6d4"]],
                             line=dict(width=1), hoverinfo="skip", showlegend=False), 1, 1)

    pts = _gd(eta0)
    fig.add_trace(go.Scatter(x=[round(p[0], 4) for p in pts], y=[round(p[1], 4) for p in pts], mode="lines+markers",
                             line=dict(color="#7c3aed", width=3), marker=dict(size=6), name="descent path",
                             hovertemplate="w₁ = %{x:.3f}<br>w₂ = %{y:.3f}<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=10, color="#1e1b4b", symbol="x"),
                             name="minimum"), 1, 1)
    ks = list(range(len(pts)))
    fig.add_trace(go.Scatter(x=ks, y=[round(_loss(*p), 6) for p in pts], mode="lines+markers",
                             line=dict(color="#ef4444", width=3), name="loss L(w)",
                             hovertemplate="step %{x}<br>L = %{y:.4g}<extra></extra>"), 1, 2)
    steps = []
    for eta in etas:
        p = _gd(eta)
        steps.append(dict(method="restyle", label=f"{eta}",
                          args=[{"x": [[round(q[0], 4) for q in p], ks], "y": [[round(q[1], 4) for q in p],
                                                                                 [round(_loss(*q), 6) for q in p]]}, [1, 3]]))
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=etas.index(eta0), steps=steps, currentvalue=dict(prefix="step size η = "))])
    fig.update_xaxes(title="w₁", range=[-5, 5], constrain="domain", row=1, col=1)
    fig.update_yaxes(title="w₂", range=[-4, 4], scaleanchor="x", constrain="domain", row=1, col=1)
    fig.update_xaxes(title="step k", range=[-0.5, 15.5], dtick=5, row=1, col=2)
    fig.update_yaxes(title="loss (log scale)", type="log", range=[-6, 2.5], tickvals=[1e-6, 1e-4, 1e-2, 1, 100],
                     ticktext=["10<sup>-6</sup>", "10<sup>-4</sup>", "0.01", "1", "100"], row=1, col=2)
    return frame(fig, height=520, stack=True)


def poly_data():
    rng = np.random.default_rng(SEED)
    xt = np.linspace(0, 1, 10)
    yt = np.sin(2 * np.pi * xt) + rng.normal(0, 0.3, 10)
    xv = rng.uniform(0, 1, 50)
    yv = np.sin(2 * np.pi * xv) + rng.normal(0, 0.3, 50)
    return xt, yt, xv, yv


def polynomial_fits():
    """Degree 1, 3 and 9 fits to the same 10 training points, with training and validation errors."""
    xt, yt, xv, yv = poly_data()
    xs = np.linspace(0, 1, 400)
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.3), sharey=True)
    for ax, d in zip(axes, (1, 3, 9)):
        p = Polynomial.fit(xt, yt, d)
        tr = np.mean((p(xt) - yt) ** 2)
        va = np.mean((p(xv) - yv) ** 2)
        ax.plot(xs, np.sin(2 * np.pi * xs), color="#94a3b8", lw=1.2, ls="--")
        ax.scatter(xv, yv, s=12, color="#f59e0b", alpha=0.7)
        ax.scatter(xt, yt, s=30, color="#3b82f6", zorder=3)
        ax.plot(xs, p(xs), color="#7c3aed", lw=2)
        ax.set_ylim(-3.5, 3.5)
        ax.set_title(f"degree {d}\ntraining {tr:.3f}, validation {va:.2f}", fontsize=10)
        ax.set_xlabel("$x$")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("$y$")
    fig.suptitle("Blue: 10 training points. Orange: 50 validation points. Dashed: the true curve $\\sin 2\\pi x$.",
                 fontsize=10)
    fig.tight_layout()
    return fig
