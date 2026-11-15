"""Figures for L6-09 Quantum counterfactual questions."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

PLUS = np.array([1, 1]) / math.sqrt(2)
MINUS = np.array([1, -1]) / math.sqrt(2)


def _rz(a):
    return np.diag([np.exp(-1j * a / 2), np.exp(1j * a / 2)])


def _branches(alpha):
    """Two-branch dilation R_z(alpha), R_z(alpha + pi) of complete dephasing: posterior and kappa."""
    phis = (alpha, alpha + math.pi)
    lik = np.array([abs(MINUS @ _rz(f) @ PLUS) ** 2 for f in phis])
    post = lik / lik.sum()
    cf = np.array([abs(PLUS @ _rz(f) @ MINUS) ** 2 for f in phis])
    return phis, post, float(post @ cf)


def dilation_explorer():
    """Slider over the dilation angle alpha: branch images of |+> with posterior weights, and kappa(alpha)."""
    degs = list(range(0, 91, 15))
    fig = make_subplots(rows=1, cols=2, column_widths=[0.45, 0.55], horizontal_spacing=0.14,
                        subplot_titles=("Branches on the Bloch equator", "Counterfactual value κ(α)"))
    t = np.linspace(0, 2 * math.pi, 121)
    fig.add_trace(go.Scatter(x=np.cos(t).round(4).tolist(), y=np.sin(t).round(4).tolist(), mode="lines",
                             line=dict(color="#cbd5e1"), hoverinfo="skip", showlegend=False), 1, 1)

    def pts(d):
        phis, post, k = _branches(math.radians(d))
        xs = [round(math.cos(f), 4) for f in phis]
        ys = [round(math.sin(f), 4) for f in phis]
        sizes = [round(float(8 + 30 * w), 2) for w in post]
        text = [f"λ = {i}: posterior {w:.3f}" for i, w in enumerate(post)]
        return xs, ys, sizes, text, k

    xs, ys, sizes, text, k0 = pts(degs[0])
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", marker=dict(size=sizes, color=["#7c3aed", "#ef4444"]),
                             text=text, hovertemplate="%{text}<extra></extra>", name="branch images of |+⟩"), 1, 1)
    fig.add_trace(go.Scatter(x=[1], y=[0], mode="markers+text", text=["|+⟩"], textposition="middle right",
                             marker=dict(size=9, color="#3b82f6", symbol="x"), showlegend=False, hoverinfo="skip"), 1, 1)
    a = np.linspace(0, 90, 91)
    fig.add_trace(go.Scatter(x=a.tolist(), y=(1 - 0.5 * np.sin(np.radians(a)) ** 2).round(4).tolist(), mode="lines",
                             line=dict(color="#7c3aed", width=3), name="κ = 1 − ½ sin²α"), 1, 2)
    fig.add_trace(go.Scatter(x=[0, 90], y=[0.5, 0.5], mode="lines", line=dict(color="#06b6d4", dash="dash"),
                             name="intervention: 1/2"), 1, 2)
    fig.add_trace(go.Scatter(x=[degs[0]], y=[round(k0, 4)], mode="markers", marker=dict(size=13, color="#7c3aed"),
                             showlegend=False, hovertemplate="α = %{x}°<br>κ = %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for d in degs:
        xs, ys, sizes, text, k = pts(d)
        steps.append(dict(method="restyle", label=f"{d}°",
                          args=[{"x": [xs, [d]], "y": [ys, [round(k, 4)]], "marker.size": [sizes, 13],
                                 "text": [text, None]}, [1, 5]]))
    fig.update_xaxes(range=[-1.35, 1.6], title="Bloch x", constrain="domain", row=1, col=1)
    fig.update_yaxes(range=[-1.3, 1.3], title="Bloch y", scaleanchor="x", constrain="domain", row=1, col=1)
    fig.update_xaxes(title="dilation angle α (degrees)", range=[0, 90], dtick=15, row=1, col=2)
    fig.update_yaxes(title="P(+ | input |−⟩, fact)", range=[0.4, 1.05], row=1, col=2)
    fig.update_layout(template="plotly_white",
                      title="Every α gives the same channel Δ,<br>but a different counterfactual answer",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="dilation angle α = "))])
    return frame(fig, height=560, stack=True)


def answers_by_choice():
    """Counterfactual value for the same query under different dilations and abduction rules."""
    rows = [("two-branch, α = 0", 1.0, "#7c3aed"),
            ("two-branch, α = π/6", 0.875, "#7c3aed"),
            ("four phases kπ/2", 0.75, "#7c3aed"),
            ("CZ, I/2, ensemble θ = π/3", 0.625, "#f59e0b"),
            ("CZ, I/2, ensemble θ = π/2", 0.5, "#f59e0b"),
            ("CNOT, |0⟩, hold fixed", 0.5, "#06b6d4"),
            ("CNOT, |0⟩, rewind", 1.0, "#ef4444")]
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    y = np.arange(len(rows))[::-1]
    ax.barh(y, [r[1] for r in rows], color=[r[2] for r in rows], height=0.6)
    for yi, r in zip(y, rows):
        ax.text(r[1] + 0.01, yi, f"{r[1]:g}", va="center", fontsize=9, color="#1e1b4b")
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=9)
    ax.axvline(0.5, color="#06b6d4", ls="--", lw=1.2)
    ax.text(0.505, len(rows) - 0.45, "interventional answer 1/2", fontsize=8, color="#0e7490")
    ax.set_xlim(0, 1.12)
    ax.set_xlabel(r"$\kappa$ = counterfactual P(+ | input $|-\rangle$, fact: $|+\rangle$ gave $-$)", fontsize=9)
    ax.set_title(r"One channel $\Delta$, one query: the answer depends on the dilation and the abduction rule",
                 fontsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
