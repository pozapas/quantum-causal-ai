"""Figures for L3-01 Complex numbers and phase."""
from __future__ import annotations

import cmath
import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame


def phase_sum():
    """Two unit arrows, 1 and e^{i phi}, their sum, and |1 + e^{i phi}|^2 against phi (slider)."""
    phis = list(range(0, 361, 15))
    xs = np.linspace(0, 360, 181)
    fig = make_subplots(rows=1, cols=2, column_widths=[0.45, 0.55], horizontal_spacing=0.14,
                        subplot_titles=("Arrows in the complex plane", "Squared length of the sum"))
    t = np.linspace(0, 2 * math.pi, 121)
    fig.add_trace(go.Scatter(x=(1 + np.cos(t)).round(4).tolist(), y=np.sin(t).round(4).tolist(), mode="lines",
                             line=dict(color="#cbd5e1", dash="dot"), hoverinfo="skip", showlegend=False), 1, 1)

    def arrows(d):
        e = cmath.exp(1j * math.radians(d))
        s = 1 + e
        return [[0, 1], [0, 0]], [[1, s.real], [0, e.imag]], [[0, s.real], [0, s.imag]], abs(s) ** 2

    (a1x, a1y), (a2x, a2y), (sx, sy), p0 = arrows(phis[0])
    fig.add_trace(go.Scatter(x=a1x, y=a1y, mode="lines+markers", line=dict(color="#3b82f6", width=4), name="1"), 1, 1)
    fig.add_trace(go.Scatter(x=a2x, y=a2y, mode="lines+markers", line=dict(color="#f59e0b", width=4), name="e<sup>iφ</sup>"), 1, 1)
    fig.add_trace(go.Scatter(x=sx, y=sy, mode="lines+markers", line=dict(color="#ef4444", width=3, dash="dash"),
                             name="sum 1 + e<sup>iφ</sup>"), 1, 1)
    fig.add_trace(go.Scatter(x=xs.round(2).tolist(), y=(2 + 2 * np.cos(np.radians(xs))).round(4).tolist(), mode="lines",
                             line=dict(color="#ef4444"), name="2 + 2 cos φ"), 1, 2)
    fig.add_trace(go.Scatter(x=[phis[0]], y=[p0], mode="markers", marker=dict(size=12, color="#ef4444"), showlegend=False,
                             hovertemplate="φ = %{x}°<br>squared length %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for d in phis:
        (_, _), (bx, by), (cx, cy), p = arrows(d)
        steps.append(dict(method="restyle", label=f"{d}°",
                          args=[{"x": [[round(v, 4) for v in bx], [round(v, 4) for v in cx], [d]],
                                 "y": [[round(v, 4) for v in by], [round(v, 4) for v in cy], [round(p, 4)]]}, [2, 3, 5]]))
    fig.update_xaxes(range=[-0.3, 2.3], title="real part", constrain="domain", row=1, col=1)
    fig.update_yaxes(range=[-1.3, 1.3], title="imaginary part", scaleanchor="x", constrain="domain", row=1, col=1)
    fig.update_xaxes(title="relative phase φ (degrees)", range=[0, 360], dtick=90, row=1, col=2)
    fig.update_yaxes(title="|1 + e<sup>iφ</sup>|²", range=[-0.1, 4.2], row=1, col=2)
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="relative phase φ = "))])
    return frame(fig, height=520, stack=True)


def roots_of_unity():
    """Multiplying by w = e^{2 pi i / n} walks around the unit circle: the n-th roots of unity."""
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.4))
    t = np.linspace(0, 2 * math.pi, 300)
    for ax, n in zip(axes, (3, 5, 8)):
        w = np.exp(2j * np.pi * np.arange(n + 1) / n)
        ax.plot(np.cos(t), np.sin(t), color="#cbd5e1", lw=1)
        ax.plot(w.real, w.imag, color="#7c3aed", lw=1.6)
        ax.scatter(w.real[:-1], w.imag[:-1], color="#7c3aed", zorder=3, s=28)
        ax.annotate("", xy=(w[1].real, w[1].imag), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color="#f59e0b", lw=2))
        ax.text(0.03, -0.18, "1", fontsize=9, color="#475569")
        ax.set_title(f"n = {n}: angle step 360°/{n} = {360 / n:g}°", fontsize=10)
        ax.axhline(0, color="#94a3b8", lw=0.6)
        ax.axvline(0, color="#94a3b8", lw=0.6)
        ax.set_aspect("equal")
        ax.set_xlim(-1.35, 1.35)
        ax.set_ylim(-1.35, 1.35)
        ax.set_xticks([-1, 0, 1])
        ax.set_yticks([-1, 0, 1])
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.suptitle("The solutions of $z^n = 1$ sit evenly on the unit circle; the orange arrow is $w = e^{2\\pi i/n}$",
                 fontsize=10)
    fig.tight_layout()
    return fig
