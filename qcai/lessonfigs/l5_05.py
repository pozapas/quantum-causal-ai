"""Figures for L5-05 Density operators and reduced states.

Conventions: rho = (I + r . sigma)/2 with |0> at +z; A is the left tensor factor, basis order 00, 01, 10, 11.
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

from qcai.science import bloch, dm, partial_trace, purity
from qcai.viz import frame

S2 = 1 / math.sqrt(2)


def _mixture(p):
    """rho(p) = p|0><0| + (1 - p)|+><+|."""
    return p * dm(np.array([1, 0])) + (1 - p) * dm(np.array([S2, S2]))


def bloch_mixer():
    """Bloch-ball explorer: the mixture of |0> and |+> slides along a chord; the eigen-ensemble is a diameter."""
    fig = go.Figure()
    u, v = np.meshgrid(np.linspace(0, 2 * math.pi, 25), np.linspace(0, math.pi, 13))
    fig.add_trace(go.Surface(x=(np.cos(u) * np.sin(v)).round(3), y=(np.sin(u) * np.sin(v)).round(3), z=np.cos(v).round(3),
                             opacity=0.12, showscale=False, colorscale=[[0, "#c4b5fd"], [1, "#c4b5fd"]], hoverinfo="skip"))
    t = np.linspace(0, 2 * math.pi, 73)
    for xs, ys, zs in ((np.cos(t), np.sin(t), 0 * t), (np.cos(t), 0 * t, np.sin(t)), (0 * t, np.cos(t), np.sin(t))):
        fig.add_trace(go.Scatter3d(x=xs.round(3), y=ys.round(3), z=zs.round(3), mode="lines",
                                   line=dict(color="#94a3b8", width=2), hoverinfo="skip", showlegend=False))
    for (x, y, z), name in (((1.18, 0, 0), "|+⟩"), ((0, 1.18, 0), "|+i⟩"), ((0, 0, 1.15), "|0⟩"), ((0, 0, -1.15), "|1⟩")):
        fig.add_trace(go.Scatter3d(x=[x], y=[y], z=[z], mode="text", text=[name], textfont=dict(size=14, color="#1e1b4b"),
                                   hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter3d(x=[0, 1], y=[0, 0], z=[1, 0], mode="lines+markers", line=dict(color="#3b82f6", width=5),
                               marker=dict(size=5, color="#3b82f6"), name="ensemble {|0⟩, |+⟩}"))
    ps = [round(0.1 * k, 1) for k in range(11)]

    def geom(p):
        r = bloch(_mixture(p))
        n = r / np.linalg.norm(r)
        return r, n

    r0, n0 = geom(0.5)
    fig.add_trace(go.Scatter3d(x=[n0[0], -n0[0]], y=[n0[1], -n0[1]], z=[n0[2], -n0[2]], mode="lines+markers",
                               line=dict(color="#06b6d4", width=5, dash="dash"), marker=dict(size=5, color="#06b6d4"),
                               name="eigen-ensemble"))
    fig.add_trace(go.Scatter3d(x=[r0[0]], y=[r0[1]], z=[r0[2]], mode="markers", marker=dict(size=8, color="#7c3aed"),
                               name="mixture ρ(p)", hovertemplate="x %{x:.3f}<br>y %{y:.3f}<br>z %{z:.3f}<extra></extra>"))
    k_eig, k_pt = len(fig.data) - 2, len(fig.data) - 1

    def title(p):
        rho = _mixture(p)
        r = np.linalg.norm(bloch(rho))
        return (f"ρ = p|0⟩⟨0| + (1−p)|+⟩⟨+|, p = {p:.1f}<br>|r| = {r:.3f}, Tr ρ² = {purity(rho):.3f}<br>"
                f"eigen-weights {(1 + r) / 2:.3f}, {(1 - r) / 2:.3f}")

    steps = []
    for p in ps:
        r, n = geom(p)
        steps.append(dict(method="update", label=f"{p:.1f}",
                          args=[{"x": [[round(n[0], 4), round(-n[0], 4)], [round(r[0], 4)]],
                                 "y": [[0.0, 0.0], [0.0]],
                                 "z": [[round(n[2], 4), round(-n[2], 4)], [round(r[2], 4)]]},
                                {"title.text": title(p)}, [k_eig, k_pt]]))
    fig.update_layout(template="plotly_white", title=dict(text=title(0.5)),
                      scene=dict(aspectmode="cube", xaxis=dict(range=[-1.25, 1.25], visible=False),
                                 yaxis=dict(range=[-1.25, 1.25], visible=False),
                                 zaxis=dict(range=[-1.25, 1.25], visible=False),
                                 camera=dict(eye=dict(x=1.35, y=0.75, z=0.55))),
                      sliders=[dict(active=5, steps=steps, currentvalue=dict(prefix="weight of |0⟩: p = "))])
    return frame(fig, height=560, xticks_lines=0, axes=False, narrow_plot=360)


def joint_vs_reduced():
    """Three different two-qubit states with the same reduced state I/2 on each qubit."""
    bell = dm(np.array([S2, 0, 0, S2]))
    mix = np.diag([0.5, 0, 0, 0.5]).astype(complex)
    white = np.eye(4) / 4
    names = ["00", "01", "10", "11"]
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.9))
    for ax, (title, rho) in zip(axes, [("Bell state $|\\Phi^+\\rangle\\langle\\Phi^+|$", bell),
                                        ("coin flip $\\frac{1}{2}(|00\\rangle\\langle00| + |11\\rangle\\langle11|)$", mix),
                                        ("maximally mixed $I/4$", white)]):
        M = rho.real
        ax.imshow(M, cmap="Purples", vmin=0, vmax=0.6)
        for i in range(4):
            for j in range(4):
                v = M[i, j]
                ax.text(j, i, "0" if abs(v) < 1e-12 else f"{v:g}", ha="center", va="center", fontsize=10,
                        color="white" if v > 0.4 else "#1e1b4b")
        ax.axhline(1.5, color="#f59e0b", lw=1.5)
        ax.axvline(1.5, color="#f59e0b", lw=1.5)
        ax.set_xticks(range(4), names)
        ax.set_yticks(range(4), names)
        ax.tick_params(length=0)
        rA, rB = partial_trace(rho, 0).real, partial_trace(rho, 1).real
        assert np.allclose(rA, np.eye(2) / 2) and np.allclose(rB, np.eye(2) / 2)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel(f"$\\rho_A = \\rho_B = I/2$,  purity of $\\rho_{{AB}}$ = {purity(rho):g}", fontsize=10)
    fig.suptitle("Different joint states, identical reduced states (orange lines mark the 2 x 2 blocks of qubit A)",
                 fontsize=10)
    fig.tight_layout()
    return fig
