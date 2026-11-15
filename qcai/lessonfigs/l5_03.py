"""Figures for L5-03 Phase and interference."""
from __future__ import annotations

import cmath
import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai import science
from qcai.viz import frame

V_PARTIAL = 0.5          # visibility of the partially marked interferometer drawn for comparison


def fringe_explorer():
    """Phasors that reach detector D0, (1 + e^{i phi})/2, and the fringe P(D0) = (1 + cos phi)/2 (slider)."""
    phis = list(range(0, 361, 15))
    fig = make_subplots(rows=1, cols=2, column_widths=[0.42, 0.58], horizontal_spacing=0.14,
                        subplot_titles=("Amplitudes arriving at D0", "Detection probabilities"))
    t = np.linspace(0, 2 * math.pi, 121)
    fig.add_trace(go.Scatter(x=(0.5 + 0.5 * np.cos(t)).round(4).tolist(), y=(0.5 * np.sin(t)).round(4).tolist(), mode="lines",
                             line=dict(color="#cbd5e1", dash="dot"), hoverinfo="skip", showlegend=False), 1, 1)

    def arrows(d):
        e = cmath.exp(1j * math.radians(d)) / 2
        s = 0.5 + e
        return [[0.5 + 0 * 0, 0.5 + e.real], [0, e.imag]], [[0, s.real], [0, s.imag]], abs(s) ** 2

    fig.add_trace(go.Scatter(x=[0, 0.5], y=[0, 0], mode="lines+markers", line=dict(color="#3b82f6", width=4),
                             name="upper path, 1/2"), 1, 1)
    (bx, by), (cx, cy), p = arrows(0)
    fig.add_trace(go.Scatter(x=bx, y=by, mode="lines+markers", line=dict(color="#f59e0b", width=4),
                             name="lower path, e<sup>iφ</sup>/2"), 1, 1)
    fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines+markers", line=dict(color="#ef4444", width=3, dash="dash"),
                             showlegend=False), 1, 1)
    xs = np.linspace(0, 360, 181)
    c = np.cos(np.radians(xs))
    fig.add_trace(go.Scatter(x=xs.round(2).tolist(), y=((1 + c) / 2).round(4).tolist(), mode="lines",
                             line=dict(color="#7c3aed", width=3), name="P(D0) = (1 + cos φ)/2"), 1, 2)
    fig.add_trace(go.Scatter(x=xs.round(2).tolist(), y=((1 - c) / 2).round(4).tolist(), mode="lines",
                             line=dict(color="#06b6d4", width=2), name="P(D1) = (1 − cos φ)/2"), 1, 2)
    fig.add_trace(go.Scatter(x=xs.round(2).tolist(), y=((1 + V_PARTIAL * c) / 2).round(4).tolist(), mode="lines",
                             line=dict(color="#94a3b8", width=2, dash="dash"), name="P(D0), visibility 0.5"), 1, 2)
    fig.add_trace(go.Scatter(x=[0], y=[p], mode="markers", marker=dict(size=12, color="#ef4444"), showlegend=False,
                             hovertemplate="φ = %{x}°<br>P(D0) = %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for d in phis:
        (bx, by), (cx, cy), p = arrows(d)
        assert abs(p - science.interference(math.radians(d))["p0"]) < 1e-12
        steps.append(dict(method="restyle", label=f"{d}°",
                          args=[{"x": [[round(v, 4) for v in bx], [round(v, 4) for v in cx], [d]],
                                 "y": [[round(v, 4) for v in by], [round(v, 4) for v in cy], [round(p, 4)]]}, [2, 3, 7]]))
    fig.update_xaxes(range=[-0.15, 1.15], title="real part", constrain="domain", row=1, col=1)
    fig.update_yaxes(range=[-0.6, 0.6], title="imaginary part", scaleanchor="x", constrain="domain", row=1, col=1)
    fig.update_xaxes(title="phase φ (degrees)", range=[0, 360], dtick=90, row=1, col=2)
    fig.update_yaxes(title="probability", range=[-0.03, 1.05], row=1, col=2)
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="phase φ = "))])
    return frame(fig, height=560, stack=True)


def fringe_data():
    """Simulated detector counts (200 photons per setting) against theory, for visibility 1 and 0.6."""
    phis = np.arange(0, 361, 30)
    shots = 200
    fig, ax = plt.subplots(figsize=(8.6, 3.9))
    xs = np.linspace(0, 360, 361)
    for v, col, seed0, lab in ((1.0, "#7c3aed", 100, "unmarked paths, $V = 1$"), (0.6, "#f59e0b", 300, "partly marked, $V = 0.6$")):
        ax.plot(xs, (1 + v * np.cos(np.radians(xs))) / 2, color=col, lw=1.8, label=lab)
        est, err = [], []
        for k, d in enumerate(phis):
            p = science.interference(math.radians(d), v)["p0"]
            f = science.trials(p, shots, seed=seed0 + k)["frequency"]
            est.append(f)
            err.append(2 * math.sqrt(max(f * (1 - f), 1e-9) / shots))
        ax.errorbar(phis, est, yerr=err, fmt="o", color=col, ms=5, capsize=3, lw=1)
    ax.set_xlim(-8, 368)
    ax.set_ylim(-0.05, 1.12)
    ax.set_xticks(range(0, 361, 90))
    ax.set_xlabel(r"phase shift $\varphi$ (degrees)")
    ax.set_ylabel("fraction of photons at D0")
    ax.set_title(r"Fringes $P(D0) = (1 + V\cos\varphi)/2$: 200 simulated photons per setting, $\pm 2$ SE bars", fontsize=10.5)
    ax.legend(loc="upper center", fontsize=9, frameon=False, ncol=2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
