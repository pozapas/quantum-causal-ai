"""Figures for L6-01 Quantum common causes.

CHSH convention: S = E(a0,b0) + E(a0,b1) + E(a1,b0) - E(a1,b1); observables cos(t) Z + sin(t) X.
On v|Phi+><Phi+| + (1 - v) I/4, E(s, t) = v cos(s - t).
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai import science as s
from qcai.viz import frame

SQ2 = math.sqrt(2)


def s_value(phi, v=1.0):
    """S for Alice at 0 and pi/2, Bob at +phi and -phi, on the Werner state of visibility v."""
    return v * (2 * math.cos(phi) + 2 * math.sin(phi))


def chsh_explorer():
    """Measurement directions in the x-z plane and S(phi) for four visibilities (slider over phi)."""
    for v in (1.0, 0.8):
        for ph in (0.0, 0.5, math.pi / 4):
            assert abs(s.chsh_value(s.werner(v), 0, math.pi / 2, ph, -ph) - s_value(ph, v)) < 1e-12
    degs = list(range(0, 91, 5))
    fig = make_subplots(rows=1, cols=2, column_widths=[0.42, 0.58], horizontal_spacing=0.14,
                        subplot_titles=("Alice violet, Bob orange", "CHSH value S(φ)"))
    t = np.linspace(0, 2 * math.pi, 121)
    fig.add_trace(go.Scatter(x=np.cos(t).round(4).tolist(), y=np.sin(t).round(4).tolist(), mode="lines",
                             line=dict(color="#cbd5e1", dash="dot"), hoverinfo="skip", showlegend=False), 1, 1)
    fig.add_trace(go.Scatter(x=[0, 0, None, 0, 1], y=[0, 1, None, 0, 0], mode="lines+markers",
                             line=dict(color="#7c3aed", width=4), name="Alice: Z, X", showlegend=False), 1, 1)

    def bob(d):
        f = math.radians(d)
        return [math.sin(f), 0, None, 0, -math.sin(f)], [math.cos(f), 0, None, 0, math.cos(f)]

    bx, by = bob(degs[0])
    fig.add_trace(go.Scatter(x=[0, bx[0], None, 0, bx[4]], y=[0, by[0], None, 0, by[4]], mode="lines+markers",
                             line=dict(color="#f59e0b", width=4), name="Bob: ±φ from Z", showlegend=False), 1, 1)
    ph = np.radians(np.arange(0, 90.5, 0.5))
    for v, col, dash in ((1.0, "#ef4444", "solid"), (0.85, "#3b82f6", "solid"), (1 / SQ2, "#06b6d4", "dash")):
        nm = "v = 1 (|Φ+⟩)" if v == 1.0 else ("v = 1/√2" if v < 0.71 else f"v = {v:g}")
        fig.add_trace(go.Scatter(x=np.degrees(ph).round(2).tolist(), y=[round(s_value(p, v), 4) for p in ph], mode="lines",
                                 line=dict(color=col, dash=dash), name=nm), 1, 2)
    fig.add_trace(go.Scatter(x=[0, 90], y=[2, 2], mode="lines", line=dict(color="#475569", dash="dot"),
                             name="classical bound 2"), 1, 2)
    fig.add_trace(go.Scatter(x=[degs[0]], y=[s_value(0)], mode="markers", marker=dict(size=12, color="#ef4444"),
                             showlegend=False, hovertemplate="φ = %{x}°<br>S = %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for d in degs:
        bx, by = bob(d)
        steps.append(dict(method="restyle", label=f"{d}°",
                          args=[{"x": [[round(u, 4) if u is not None else None for u in bx], [d]],
                                 "y": [[round(u, 4) if u is not None else None for u in by], [round(s_value(math.radians(d)), 4)]]},
                                [2, 7]]))
    fig.update_xaxes(range=[-1.25, 1.25], title="x", constrain="domain", zeroline=False, row=1, col=1)
    fig.update_yaxes(range=[-0.3, 1.25], title="z", scaleanchor="x", constrain="domain", zeroline=False, row=1, col=1)
    fig.update_xaxes(title="Bob's angle φ (degrees)", range=[0, 90], dtick=15, tickangle=0, row=1, col=2)
    fig.update_yaxes(title="S", range=[1.0, 3.0], row=1, col=2)
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="Bob's angle φ = "))])
    return frame(fig, height=540, stack=True)


def correlation_curves():
    """E(theta) for the quantum singlet-type model and for a classical hidden-direction model."""
    th = np.linspace(0, math.pi, 400)
    eq_ = np.cos(th)
    ec = 1 - 2 * th / math.pi
    sq = 3 * math.cos(math.pi / 4) - math.cos(3 * math.pi / 4)
    sc = 3 * (1 - 2 * 0.25) - (1 - 2 * 0.75)
    assert abs(sq - 2 * SQ2) < 1e-12 and abs(sc - 2) < 1e-12
    fig, ax = plt.subplots(figsize=(7.6, 3.9))
    ax.plot(np.degrees(th), eq_, color="#ef4444", lw=2.2, label=r"quantum, $|\Phi^+\rangle$: $E = \cos\theta$")
    ax.plot(np.degrees(th), ec, color="#3b82f6", lw=2.2, label=r"classical hidden direction: $E = 1 - 2\theta/\pi$")
    for d in (45, 135):
        r = math.radians(d)
        ax.plot([d, d], [math.cos(r), 1 - 2 * r / math.pi], color="#94a3b8", lw=1, ls=":")
        ax.scatter([d, d], [math.cos(r), 1 - 2 * r / math.pi], color=["#ef4444", "#3b82f6"], zorder=3, s=22)
    ax.annotate(r"$\theta = 45^\circ$: $0.707$ vs $0.5$", xy=(45, 0.707), xytext=(60, 0.9), fontsize=9,
                arrowprops=dict(arrowstyle="-", color="#94a3b8"))
    ax.annotate(r"$\theta = 135^\circ$: $-0.707$ vs $-0.5$", xy=(135, -0.707), xytext=(95, -0.95), fontsize=9,
                arrowprops=dict(arrowstyle="-", color="#94a3b8"))
    ax.axhline(0, color="#cbd5e1", lw=0.8)
    ax.set_xlabel(r"angle between the two measurement directions $\theta$ (degrees)")
    ax.set_ylabel(r"correlation $E$")
    ax.set_xticks([0, 45, 90, 135, 180])
    ax.set_xlim(0, 180)
    ax.set_ylim(-1.1, 1.1)
    ax.legend(loc="lower left", fontsize=9, frameon=False)
    ax.set_title(r"CHSH angles: three of $45^\circ$, one of $135^\circ$. Quantum $S = 2\sqrt{2}$, this classical model $S = 2$",
                 fontsize=10)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    return fig
