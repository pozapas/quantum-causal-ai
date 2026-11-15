"""Figures for L6-08 The quantum switch.

Convention (as in qcai.science.quantum_switch): control |0> applies U_A first (U_B U_A), control |1> applies
U_B first (U_A U_B).  Experimental numbers are those reported in the arXiv versions of Procopio et al.
(arXiv:1412.4006) and Rubino et al. (arXiv:1608.01683).
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.diag([1.0, -1.0]).astype(complex)
KET0, KET1 = np.array([1, 0], dtype=complex), np.array([0, 1], dtype=complex)
PLUS = (KET0 + KET1) / math.sqrt(2)


def p_plus(UA, UB, psi, V=1.0):
    """P(+) for control |+>, with the control's coherence multiplied by V before the X-basis measurement."""
    a = UB @ UA @ psi          # branch |0>: U_A first
    b = UA @ UB @ psi          # branch |1>: U_B first
    return 0.5 * (1 + V * float(np.real(np.vdot(a, b))))


def switch_relation():
    """Slider over the angle beta between the axes of U_A = X and U_B = cos(beta) X + sin(beta) Z."""
    betas = list(range(0, 91, 5))
    fine = np.linspace(0, 90, 91)
    psi = np.array([0.6, 0.8j])
    Vs = (1.0, 0.5, 0.0)
    curves = {V: [p_plus(X, math.cos(math.radians(b)) * X + math.sin(math.radians(b)) * Z, psi, V) for b in fine] for V in Vs}
    for b, p in zip(fine, curves[1.0]):
        assert abs(p - math.cos(math.radians(b)) ** 2) < 1e-12
    assert all(abs(p - 0.5) < 1e-12 for p in curves[0.0])
    fig = make_subplots(rows=1, cols=2, column_widths=[0.42, 0.58], horizontal_spacing=0.14,
                        subplot_titles=("Rotation axes (x-z plane)", "Probability of control outcome +"))
    t = np.linspace(0, 2 * math.pi, 121)
    fig.add_trace(go.Scatter(x=np.cos(t).round(4).tolist(), y=np.sin(t).round(4).tolist(), mode="lines",
                             line=dict(color="#cbd5e1"), hoverinfo="skip", showlegend=False), 1, 1)
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 0], mode="lines+markers", line=dict(color="#3b82f6", width=5),
                             name="axis of U<sub>A</sub> = X"), 1, 1)
    b0 = betas[6]

    def baxis(b):
        r = math.radians(b)
        return [0, round(math.cos(r), 4)], [0, round(math.sin(r), 4)]
    bx, by = baxis(b0)
    fig.add_trace(go.Scatter(x=bx, y=by, mode="lines+markers", line=dict(color="#f59e0b", width=5),
                             name="axis of U<sub>B</sub>"), 1, 1)
    names = {1.0: "switch, V = 1", 0.5: "partial coherence, V = 0.5", 0.0: "mixture of orders, V = 0"}
    styles = {1.0: dict(color="#7c3aed", width=4), 0.5: dict(color="#06b6d4", width=3, dash="dash"),
              0.0: dict(color="#475569", width=3, dash="dot")}
    for V in Vs:
        fig.add_trace(go.Scatter(x=fine.round(1).tolist(), y=np.round(curves[V], 4).tolist(), mode="lines",
                                 line=styles[V], name=names[V]), 1, 2)
    fig.add_trace(go.Scatter(x=[b0], y=[round(math.cos(math.radians(b0)) ** 2, 4)], mode="markers",
                             marker=dict(size=13, color="#7c3aed"), showlegend=False,
                             hovertemplate="β = %{x}°<br>P(+) = %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for b in betas:
        bx, by = baxis(b)
        steps.append(dict(method="restyle", label=f"{b}°",
                          args=[{"x": [bx, [b]], "y": [by, [round(math.cos(math.radians(b)) ** 2, 4)]]}, [2, 6]]))
    fig.update_xaxes(range=[-1.25, 1.25], title="x", constrain="domain", row=1, col=1)
    fig.update_yaxes(range=[-1.25, 1.25], title="z", scaleanchor="x", constrain="domain", row=1, col=1)
    fig.update_xaxes(title="angle β between the axes (degrees)", range=[0, 90], dtick=15, row=1, col=2)
    fig.update_yaxes(title="P(+)", range=[-0.03, 1.05], row=1, col=2)
    fig.update_layout(template="plotly_white",
                      title="P(+) = cos²β with coherent control (V = 1),<br>1/2 for a classical mixture of orders (V = 0)",
                      sliders=[dict(active=6, steps=steps, currentvalue=dict(prefix="angle β = "))])
    return frame(fig, height=600, stack=True)


def experiments_figure():
    """Reported numbers from the two photonic experiments, with the comparison values each paper uses."""
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.7), gridspec_kw=dict(width_ratios=[1.1, 1]))
    ax = axes[0]
    vals, errs = [0.973, 0.976], [0.016, 0.015]
    ax.errorbar([0, 1], vals, yerr=errs, fmt="o", color="#7c3aed", ms=8, capsize=6, lw=2)
    ax.axhline(0.9288, color="#ef4444", ls="--", lw=1.5)
    ax.text(1.45, 0.9288 - 0.006, "fixed-order bound\n0.9288 (reported)", color="#ef4444", fontsize=8, va="top", ha="right")
    ax.axhline(1.0, color="#94a3b8", lw=0.8)
    ax.set_xticks([0, 1], ["Pauli pairs\n(16)", "random pairs\n(100)"])
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(0.88, 1.01)
    ax.set_ylabel("average success probability", fontsize=9)
    ax.set_title("Procopio et al. 2015: commute or anticommute?", fontsize=10)
    ax2 = axes[1]
    ax2.errorbar([0], [0.202], yerr=[0.029], fmt="o", color="#7c3aed", ms=8, capsize=6, lw=2, label="measured")
    ax2.plot([0], [0.2842], "D", color="#06b6d4", ms=7, label="ideal for their setup")
    ax2.axhline(0, color="#ef4444", ls="--", lw=1.5)
    ax2.text(0.42, 0.012, "causally separable: 0", color="#ef4444", fontsize=8, ha="right")
    ax2.set_xticks([0], ["quantum switch,\nAlice measures and\nreprepares, Bob unitary"])
    ax2.set_xlim(-0.5, 0.5)
    ax2.set_ylim(-0.03, 0.33)
    ax2.set_ylabel("causal nonseparability  −Tr(SW)", fontsize=9)
    ax2.set_title("Rubino et al. 2017: causal witness", fontsize=10)
    ax2.legend(loc="upper right", fontsize=8, frameon=False)
    for a in axes:
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
