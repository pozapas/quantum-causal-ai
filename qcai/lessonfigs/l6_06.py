"""Figures for L6-06 Bell inequalities and causal inequalities."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

SQ2 = math.sqrt(2)


def noise_explorer():
    """Werner visibility v: the circle of quantum points shrinks; CHSH and OCB margins cross 1 at v = 1/sqrt 2."""
    vs = [round(0.1 * k, 1) for k in range(11)]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.55, 0.45], horizontal_spacing=0.14,
                        subplot_titles=("Images in the (S<sub>1</sub>, S<sub>2</sub>) plane", "Ratio to the classical bound"))
    sq = [(2, 2), (-2, 2), (-2, -2), (2, -2), (2, 2)]
    dia = [(4, 0), (0, 4), (-4, 0), (0, -4), (4, 0)]
    t = np.linspace(0, 2 * math.pi, 181)
    fig.add_trace(go.Scatter(x=[p[0] for p in dia], y=[p[1] for p in dia], mode="lines", line=dict(color="#ef4444", width=2),
                             name="no-signaling", hoverinfo="skip"), 1, 1)
    fig.add_trace(go.Scatter(x=(2 * SQ2 * np.cos(t)).round(4).tolist(), y=(2 * SQ2 * np.sin(t)).round(4).tolist(), mode="lines",
                             line=dict(color="#7c3aed", width=2), name="quantum", hoverinfo="skip"), 1, 1)
    fig.add_trace(go.Scatter(x=[p[0] for p in sq], y=[p[1] for p in sq], mode="lines", fill="toself",
                             fillcolor="rgba(59,130,246,0.15)", line=dict(color="#3b82f6", width=2), name="local",
                             hoverinfo="skip"), 1, 1)

    def ring(v):
        ph = np.linspace(0, 2 * math.pi, 25)
        return (2 * SQ2 * v * np.cos(ph)).round(4).tolist(), (2 * SQ2 * v * np.sin(ph)).round(4).tolist()

    def bars(v):
        chsh = 2 * SQ2 * v / 2
        ocb = (0.5 + SQ2 * v / 4) / 0.75
        return [round(chsh, 4), round(ocb, 4)]

    x0, y0 = ring(vs[-1])
    fig.add_trace(go.Scatter(x=x0, y=y0, mode="markers+lines", marker=dict(size=6, color="#f59e0b"),
                             line=dict(color="#f59e0b", width=1, dash="dot"), name="Werner state",
                             hovertemplate="S<sub>1</sub> = %{x:.2f}<br>S<sub>2</sub> = %{y:.2f}<extra></extra>"), 1, 1)
    cats = ["CHSH S / 2", "OCB p / (3/4)"]
    fig.add_trace(go.Bar(x=cats, y=bars(vs[-1]), marker_color=["#7c3aed", "#06b6d4"], showlegend=False,
                         text=[f"{b:.3f}" for b in bars(vs[-1])], textposition="outside",
                         hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=cats, y=[1, 1], mode="lines", line=dict(color="#475569", dash="dash"), showlegend=False,
                             hoverinfo="skip"), 1, 2)
    steps = []
    for v in vs:
        rx, ry = ring(v)
        b = bars(v)
        steps.append(dict(method="restyle", label=f"{v:.1f}",
                          args=[{"x": [rx, cats], "y": [ry, b], "text": [None, [f"{u:.3f}" for u in b]]}, [3, 4]]))
    fig.update_xaxes(range=[-4.4, 4.4], dtick=2, title="S<sub>1</sub>", constrain="domain", row=1, col=1)
    fig.update_yaxes(range=[-4.4, 4.4], dtick=2, title="S<sub>2</sub>", scaleanchor="x", constrain="domain", row=1, col=1)
    fig.update_xaxes(tickangle=0, row=1, col=2)
    fig.update_yaxes(range=[0, 1.7], title="ratio (above 1 = violation)", row=1, col=2)
    fig.update_layout(template="plotly_white",
                      title="Noise hits both tests the same way:<br>violation exactly when v > 1/√2 ≈ 0.707",
                      sliders=[dict(active=len(vs) - 1, steps=steps, currentvalue=dict(prefix="visibility v = "))])
    return frame(fig, height=600, stack=True)


def support_functions():
    """Support functions h(phi) of the local square, quantum disk and no-signaling diamond."""
    ph = np.linspace(0, 2 * math.pi, 721)
    hl = 2 * (np.abs(np.cos(ph)) + np.abs(np.sin(ph)))
    hq = np.full_like(ph, 2 * SQ2)
    hn = 4 * np.maximum(np.abs(np.cos(ph)), np.abs(np.sin(ph)))
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    deg = np.degrees(ph)
    ax.plot(deg, hn, color="#ef4444", lw=2, label="no-signaling: $4\\max(|\\cos\\varphi|, |\\sin\\varphi|)$")
    ax.plot(deg, hq, color="#7c3aed", lw=2, label="quantum: $2\\sqrt{2}$")
    ax.plot(deg, hl, color="#3b82f6", lw=2, label="local: $2(|\\cos\\varphi| + |\\sin\\varphi|)$")
    for d in (45, 135, 225, 315):
        ax.axvline(d, color="#cbd5e1", lw=0.8, zorder=0)
    ax.set_xlim(0, 360)
    ax.set_ylim(1.5, 4.3)
    ax.set_xticks(range(0, 361, 45))
    ax.set_xlabel("direction $\\varphi$ (degrees)")
    ax.set_ylabel("$\\max\\; S_1\\cos\\varphi + S_2\\sin\\varphi$")
    ax.set_title("Largest value of $S_1\\cos\\varphi + S_2\\sin\\varphi$ over each set", fontsize=11)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3, fontsize=8.5, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
