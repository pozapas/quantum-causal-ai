"""Figures for L3-02 Vectors and inner products."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

V = np.array([3.0, 4.0])
ARG_V = math.degrees(math.atan2(4, 3))


def projection_explorer():
    """Shadow of v = (3, 4) on the line of a unit vector u at angle alpha, and <u, v> against alpha."""
    angles = list(range(0, 361, 15))
    xs = np.linspace(0, 360, 181)
    fig = make_subplots(rows=1, cols=2, column_widths=[0.46, 0.54], horizontal_spacing=0.14,
                        subplot_titles=("Shadow of v on the line of u", "Signed shadow length ⟨u, v⟩"))

    def parts(d):
        a = math.radians(d)
        u = np.array([math.cos(a), math.sin(a)])
        s = float(u @ V)
        foot = s * u
        return u, s, foot

    t = np.linspace(0, 2 * math.pi, 121)
    fig.add_trace(go.Scatter(x=np.cos(t).round(4).tolist(), y=np.sin(t).round(4).tolist(), mode="lines",
                             line=dict(color="#cbd5e1", dash="dot"), hoverinfo="skip", showlegend=False), 1, 1)
    fig.add_trace(go.Scatter(x=[0, 3], y=[0, 4], mode="lines+markers", line=dict(color="#7c3aed", width=4),
                             name="v = (3, 4)"), 1, 1)

    u, s, foot = parts(angles[0])

    def geo(d):
        u, s, foot = parts(d)
        line = ([round(-5.5 * u[0], 4), round(5.5 * u[0], 4)], [round(-5.5 * u[1], 4), round(5.5 * u[1], 4)])
        perp = ([3, round(foot[0], 4)], [4, round(foot[1], 4)])
        shadow = ([0, round(foot[0], 4)], [0, round(foot[1], 4)])
        uu = ([0, round(u[0], 4)], [0, round(u[1], 4)])
        return line, perp, shadow, uu, s

    line, perp, shadow, uu, s = geo(angles[0])
    fig.add_trace(go.Scatter(x=line[0], y=line[1], mode="lines", line=dict(color="#94a3b8", dash="dash"),
                             hoverinfo="skip", showlegend=False), 1, 1)                              # 2
    fig.add_trace(go.Scatter(x=perp[0], y=perp[1], mode="lines", line=dict(color="#475569", dash="dot"),
                             hoverinfo="skip", showlegend=False), 1, 1)                              # 3
    fig.add_trace(go.Scatter(x=shadow[0], y=shadow[1], mode="lines", line=dict(color="#06b6d4", width=8),
                             name="shadow"), 1, 1)                                                   # 4
    fig.add_trace(go.Scatter(x=uu[0], y=uu[1], mode="lines+markers", line=dict(color="#f59e0b", width=4),
                             name="unit vector u"), 1, 1)                                            # 5
    fig.add_trace(go.Scatter(x=xs.round(2).tolist(), y=(5 * np.cos(np.radians(xs - ARG_V))).round(4).tolist(),
                             mode="lines", line=dict(color="#7c3aed"), name="5 cos(α − 53.13°)"), 1, 2)  # 6
    for yb in (5, -5):
        fig.add_trace(go.Scatter(x=[0, 360], y=[yb, yb], mode="lines", line=dict(color="#ef4444", dash="dot"),
                                 hoverinfo="skip", showlegend=False), 1, 2)
    fig.add_trace(go.Scatter(x=[angles[0]], y=[round(s, 4)], mode="markers", marker=dict(size=12, color="#06b6d4"),
                             showlegend=False, hovertemplate="α = %{x}°<br>⟨u, v⟩ = %{y:.3f}<extra></extra>"), 1, 2)  # 9
    steps = []
    for d in angles:
        line, perp, shadow, uu, s = geo(d)
        steps.append(dict(method="restyle", label=f"{d}°",
                          args=[{"x": [line[0], perp[0], shadow[0], uu[0], [d]],
                                 "y": [line[1], perp[1], shadow[1], uu[1], [round(s, 4)]]}, [2, 3, 4, 5, 9]]))
    fig.update_xaxes(range=[-5.6, 5.6], title="x", constrain="domain", dtick=2, tickangle=0, row=1, col=1)
    fig.update_yaxes(range=[-5.6, 5.6], title="y", scaleanchor="x", constrain="domain", dtick=2, row=1, col=1)
    fig.update_xaxes(title="angle α of u (degrees)", range=[0, 360], dtick=90, row=1, col=2)
    fig.update_yaxes(title="⟨u, v⟩", range=[-5.6, 5.6], dtick=5, row=1, col=2)
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="angle of u: α = "))])
    return frame(fig, height=540, stack=True)


def parseval_two_bases():
    """The arrow v = (3, 4) in the standard basis and in the turned orthonormal basis u1, u2."""
    u1, u2 = np.array([0.8, 0.6]), np.array([-0.6, 0.8])
    c1, c2 = float(u1 @ V), float(u2 @ V)
    assert abs(c1 - 4.8) < 1e-12 and abs(c2 - 1.4) < 1e-12
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.4))
    for ax, basis, coeffs, names, ttl in (
            (axes[0], (np.array([1.0, 0]), np.array([0, 1.0])), (3.0, 4.0), ("$e_0$", "$e_1$"),
             "Standard basis: $v = 3e_0 + 4e_1$"),
            (axes[1], (u1, u2), (c1, c2), ("$u_1$", "$u_2$"), "Turned basis: $v = 4.8u_1 + 1.4u_2$")):
        b1, b2 = basis
        p1 = coeffs[0] * b1
        ax.add_patch(plt.Polygon([[0, 0], p1, V, coeffs[1] * b2], closed=True, color="#f5f3ff", zorder=0))
        ax.plot([0, p1[0]], [0, p1[1]], color="#06b6d4", lw=5, solid_capstyle="butt", zorder=2)
        ax.plot([p1[0], V[0]], [p1[1], V[1]], color="#ef4444", lw=4, zorder=2)
        ax.annotate("", xy=V, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#7c3aed", lw=2.4), zorder=3)
        for k, (b, nm) in enumerate(zip(basis, names)):
            ax.annotate("", xy=b, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color="#f59e0b", lw=2.2), zorder=4)
            side = np.array([b[1], -b[0]]) if k == 0 else np.array([-b[1], b[0]])
            ax.text(*(0.5 * b + 0.33 * side), nm, fontsize=12, color="#b45309", ha="center", va="center")
        mid1 = 0.55 * p1
        off = np.array([b1[1], -b1[0]]) * 0.35
        ax.text(*(mid1 + off), f"{coeffs[0]:g}", color="#0e7490", fontsize=12, ha="center", va="center")
        mid2 = p1 + 0.5 * (V - p1)
        off2 = b1 * 0.38
        ax.text(*(mid2 + off2), f"{coeffs[1]:g}", color="#b91c1c", fontsize=12, ha="center", va="center")
        ax.text(V[0] + 0.1, V[1] + 0.12, "$v$", fontsize=13, color="#7c3aed")
        ax.set_title(ttl + f"\n${coeffs[0]:g}^2 + {coeffs[1]:g}^2 = {coeffs[0]**2 + coeffs[1]**2:g}$", fontsize=11)
        ax.axhline(0, color="#94a3b8", lw=0.7)
        ax.axvline(0, color="#94a3b8", lw=0.7)
        ax.set_aspect("equal")
        ax.set_xlim(-1.4, 5.0)
        ax.set_ylim(-0.6, 4.8)
        ax.grid(color="#e2e8f0", lw=0.6)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    fig.tight_layout()
    return fig
