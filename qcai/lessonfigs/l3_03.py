"""Figures for L3-03 Matrices as transformations."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

from qcai.viz import frame

C30, S30 = math.cos(math.pi / 6), math.sin(math.pi / 6)
H = np.array([[1, 1], [1, -1]]) / math.sqrt(2)
PRESETS = [
    ("Identity", np.eye(2)),
    ("Rotation 30°", np.array([[C30, -S30], [S30, C30]])),
    ("Shear S", np.array([[1.0, 1.0], [0.0, 1.0]])),
    ("Reflection F", np.array([[1.0, 0.0], [0.0, -1.0]])),
    ("Collapse C", np.array([[1.0, 2.0], [0.5, 1.0]])),
    ("Stretch", np.array([[2.0, 0.0], [0.0, 0.5]])),
    ("Hadamard H", H),
]
SQUARE = np.array([[0, 1, 1, 0, 0], [0, 0, 1, 1, 0]], dtype=float)
T = np.linspace(0, 2 * math.pi, 97)
CIRCLE = np.vstack([np.cos(T), np.sin(T)])


def _num(x):
    x = 0.0 if abs(x) < 5e-10 else float(x)
    return f"{x:.3f}".rstrip("0").rstrip(".") if abs(x - round(x)) > 5e-10 else str(int(round(x)))


def _title(name, M):
    det = float(np.linalg.det(M))
    keeps = np.allclose(M.T @ M, np.eye(2))
    rows = f"[[{_num(M[0, 0])}, {_num(M[0, 1])}], [{_num(M[1, 0])}, {_num(M[1, 1])}]]"
    return (f"{name}: M = {rows}<br>det M = {_num(det)} (area ×{_num(abs(det))}); "
            f"keeps lengths: {'yes' if keeps else 'no'}")


def _data(M):
    sq, ci = M @ SQUARE, M @ CIRCLE
    r = lambda a: [round(float(v), 4) for v in a]  # noqa: E731
    return ([r(sq[0]), r(ci[0]), [0, r([M[0, 0]])[0]], [0, r([M[0, 1]])[0]]],
            [r(sq[1]), r(ci[1]), [0, r([M[1, 0]])[0]], [0, r([M[1, 1]])[0]]])


def matrix_explorer():
    """Pick a 2x2 matrix: the images of the unit square, the unit circle and the two basis vectors."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=SQUARE[0].tolist(), y=SQUARE[1].tolist(), mode="lines", line=dict(color="#cbd5e1", dash="dot"),
                             hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=CIRCLE[0].round(4).tolist(), y=CIRCLE[1].round(4).tolist(), mode="lines",
                             line=dict(color="#cbd5e1", dash="dot"), hoverinfo="skip", showlegend=False))
    xs, ys = _data(PRESETS[0][1])
    fig.add_trace(go.Scatter(x=xs[0], y=ys[0], mode="lines", fill="toself", fillcolor="rgba(6,182,212,0.25)",
                             line=dict(color="#06b6d4", width=2), name="image of unit square"))
    fig.add_trace(go.Scatter(x=xs[1], y=ys[1], mode="lines", line=dict(color="#ef4444", width=2.5),
                             name="image of unit circle"))
    fig.add_trace(go.Scatter(x=xs[2], y=ys[2], mode="lines+markers", line=dict(color="#7c3aed", width=4),
                             name="M e₀ (column 1)"))
    fig.add_trace(go.Scatter(x=xs[3], y=ys[3], mode="lines+markers", line=dict(color="#f59e0b", width=4),
                             name="M e₁ (column 2)"))
    buttons = []
    for name, M in PRESETS:
        xs, ys = _data(M)
        buttons.append(dict(label=name, method="update",
                            args=[{"x": xs, "y": ys}, {"title.text": _title(name, M)}, [2, 3, 4, 5]]))
    fig.update_layout(template="plotly_white", title=dict(text=_title(*PRESETS[0])),
                      updatemenus=[dict(type="dropdown", buttons=buttons, active=0, showactive=True)])
    fig.update_xaxes(range=[-3.2, 3.2], dtick=1, tickangle=0, title="x", constrain="domain")
    fig.update_yaxes(range=[-2.6, 2.6], dtick=1, title="y", scaleanchor="x", constrain="domain")
    return frame(fig, height=600, narrow_plot=260)


def transform_gallery():
    """Four 2x2 matrices acting on the unit square, a unit circle and an asymmetric flag."""
    mats = [("Rotation $R$", np.array([[0, -1], [1, 0]]), "$\\det R = 1$"),
            ("Shear $S$", np.array([[1, 1], [0, 1]]), "$\\det S = 1$"),
            ("Reflection $F$", np.array([[1, 0], [0, -1]]), "$\\det F = -1$"),
            ("Collapse $C$", np.array([[1, 2], [0.5, 1]]), "$\\det C = 0$")]
    flag = np.array([[0, 0, 0.6, 0, 0], [0, 1, 0.8, 0.6, 0]], dtype=float) * 0.9 + np.array([[0.15], [0.05]])
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.4))
    for ax, (name, M, d) in zip(axes, mats):
        ax.plot(*CIRCLE, color="#cbd5e1", lw=1, ls=":")
        ax.fill(*SQUARE, color="#e2e8f0", alpha=0.6, lw=0)
        ax.plot(*flag, color="#94a3b8", lw=1.2)
        sq, ci, fl = M @ SQUARE, M @ CIRCLE, M @ flag
        ax.fill(*sq, color="#06b6d4", alpha=0.3, lw=1.5, ec="#0891b2")
        ax.plot(*ci, color="#ef4444", lw=1.6)
        ax.plot(*fl, color="#1e1b4b", lw=2)
        ax.annotate("", xy=M[:, 0], xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#7c3aed", lw=2))
        ax.annotate("", xy=M[:, 1], xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#f59e0b", lw=2))
        keeps = np.allclose(M.T @ M, np.eye(2))
        ax.set_title(f"{name}\n{d}, lengths {'kept' if keeps else 'changed'}", fontsize=10)
        ax.axhline(0, color="#94a3b8", lw=0.6)
        ax.axvline(0, color="#94a3b8", lw=0.6)
        ax.set_aspect("equal")
        ax.set_xlim(-2.4, 2.4)
        ax.set_ylim(-2.4, 2.4)
        ax.set_xticks([-2, 0, 2])
        ax.set_yticks([-2, 0, 2])
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    fig.suptitle("Grey: before. Color: after. Purple and orange arrows are the columns of the matrix; "
                 "the dark flag shows orientation.", fontsize=10)
    fig.tight_layout()
    return fig
