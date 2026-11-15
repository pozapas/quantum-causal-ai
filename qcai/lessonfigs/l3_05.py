"""Figures for L3-05 Eigenvectors and observables."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

A = np.array([[2.0, 1.0], [1.0, 2.0]])


def _turn(theta_deg):
    """Signed angle (degrees) from v = (cos t, sin t) to Av, and the stretch |Av|."""
    v = np.array([math.cos(math.radians(theta_deg)), math.sin(math.radians(theta_deg))])
    w = A @ v
    ang = math.degrees(math.atan2(v[0] * w[1] - v[1] * w[0], v @ w))
    return v, w, ang, float(np.linalg.norm(w))


def eigen_hunt():
    """Turn a unit vector v around the circle; watch Av, and the angle between v and Av."""
    thetas = list(range(0, 181, 15))
    t = np.linspace(0, 2 * math.pi, 181)
    circ = np.stack([np.cos(t), np.sin(t)])
    ell = A @ circ
    fig = make_subplots(rows=1, cols=2, column_widths=[0.48, 0.52], horizontal_spacing=0.14,
                        subplot_titles=("v (blue) and Av (red)", "Angle from v to Av"))
    fig.add_trace(go.Scatter(x=circ[0].round(4).tolist(), y=circ[1].round(4).tolist(), mode="lines",
                             line=dict(color="#94a3b8", dash="dot"), hoverinfo="skip", showlegend=False), 1, 1)
    fig.add_trace(go.Scatter(x=ell[0].round(4).tolist(), y=ell[1].round(4).tolist(), mode="lines",
                             line=dict(color="#1e1b4b", width=1.5), name="image of the circle"), 1, 1)
    for (dx, dy), c, nm in (((1, 1), "#7c3aed", "eigenline λ = 3"), ((1, -1), "#06b6d4", "eigenline λ = 1")):
        fig.add_trace(go.Scatter(x=[-3.2 * dx, 3.2 * dx], y=[-3.2 * dy, 3.2 * dy], mode="lines",
                                 line=dict(color=c, dash="dash", width=2), name=nm, hoverinfo="skip"), 1, 1)
    v, w, ang, st = _turn(thetas[0])
    fig.add_trace(go.Scatter(x=[0, round(v[0], 4)], y=[0, round(v[1], 4)], mode="lines+markers",
                             line=dict(color="#3b82f6", width=4), showlegend=False, hoverinfo="skip"), 1, 1)
    fig.add_trace(go.Scatter(x=[0, round(w[0], 4)], y=[0, round(w[1], 4)], mode="lines+markers",
                             line=dict(color="#ef4444", width=4), showlegend=False,
                             hovertemplate="Av = (%{x:.3f}, %{y:.3f})<extra></extra>"), 1, 1)
    xs = np.arange(0, 180.5, 1.0)
    angs = [_turn(x)[2] for x in xs]
    fig.add_trace(go.Scatter(x=xs.tolist(), y=np.round(angs, 3).tolist(), mode="lines", line=dict(color="#ef4444"),
                             showlegend=False, hovertemplate="θ = %{x}°<br>turn %{y:.1f}°<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=[thetas[0]], y=[round(ang, 3)], mode="markers", marker=dict(size=12, color="#ef4444"),
                             showlegend=False, hovertemplate="θ = %{x}°<br>turn %{y:.1f}°<extra></extra>"), 1, 2)
    steps = []
    for d in thetas:
        v, w, ang, st = _turn(d)
        steps.append(dict(method="restyle", label=f"{d}°",
                          args=[{"x": [[0, round(v[0], 4)], [0, round(w[0], 4)], [d]],
                                 "y": [[0, round(v[1], 4)], [0, round(w[1], 4)], [round(ang, 3)]]}, [4, 5, 7]]))
    fig.update_xaxes(range=[-3.3, 3.3], title="x", constrain="domain", dtick=1, row=1, col=1)
    fig.update_yaxes(range=[-3.3, 3.3], title="y", scaleanchor="x", constrain="domain", dtick=1, row=1, col=1)
    fig.update_xaxes(title="direction θ of v (degrees)", range=[0, 180], dtick=45, row=1, col=2)
    fig.update_yaxes(title="turn (degrees)", range=[-36, 36], dtick=10, zeroline=True, row=1, col=2)
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="direction θ = "))])
    return frame(fig, height=560, stack=True)


def three_maps():
    """The unit circle under a symmetric matrix, a non-symmetric one, and a rotation."""
    mats = [(np.array([[2.0, 1.0], [1.0, 2.0]]), "symmetric: rows (2, 1), (1, 2)",
             "eigenvectors at right angles"),
            (np.array([[3.0, 1.0], [0.0, 2.0]]), "not symmetric: rows (3, 1), (0, 2)",
             "eigenvectors not at right angles"),
            (np.array([[0.0, -1.0], [1.0, 0.0]]), "quarter turn: rows (0, -1), (1, 0)",
             "no real eigenvector")]
    t = np.linspace(0, 2 * math.pi, 300)
    circ = np.stack([np.cos(t), np.sin(t)])
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.9))
    for ax, (M, ttl, sub) in zip(axes, mats):
        img = M @ circ
        ax.plot(circ[0], circ[1], color="#cbd5e1", lw=1.2)
        ax.plot(img[0], img[1], color="#1e1b4b", lw=1.6)
        vals, vecs = np.linalg.eig(M)
        cols = ["#7c3aed", "#06b6d4"]
        if np.all(np.abs(vals.imag) < 1e-12):
            for k in range(2):
                d = vecs[:, k].real
                d = d / np.linalg.norm(d)
                ax.plot([-3.4 * d[0], 3.4 * d[0]], [-3.4 * d[1], 3.4 * d[1]], ls="--", color=cols[k], lw=1.3)
                ax.annotate("", xy=(vals[k].real * d[0], vals[k].real * d[1]), xytext=(0, 0),
                            arrowprops=dict(arrowstyle="-|>", color=cols[k], lw=2))
                tx, ty = vals[k].real * d[0], vals[k].real * d[1]
                ax.text(min(tx, 2.7), ty + 0.4, f"λ = {vals[k].real:g}", color=cols[k], fontsize=9, ha="center",
                        bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))
        else:
            v = np.array([1.0, 0.3])
            w = M @ v
            ax.annotate("", xy=tuple(v), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#3b82f6", lw=2))
            ax.annotate("", xy=tuple(w), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#ef4444", lw=2))
            ax.text(1.1, 0.0, "v", color="#3b82f6", fontsize=10)
            ax.text(-0.75, 1.15, "Mv", color="#ef4444", fontsize=10)
        ax.set_title(ttl, fontsize=10)
        ax.set_xlabel(sub, fontsize=9, color="#475569")
        ax.axhline(0, color="#94a3b8", lw=0.6)
        ax.axvline(0, color="#94a3b8", lw=0.6)
        ax.set_aspect("equal")
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-3.6, 3.6)
        ax.set_xticks([-3, 0, 3])
        ax.set_yticks([-3, 0, 3])
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.suptitle("Gray: the unit circle.  Dark: its image.  Dashed: eigenlines, arrows: eigenvalue times unit eigenvector",
                 fontsize=10)
    fig.tight_layout()
    return fig
