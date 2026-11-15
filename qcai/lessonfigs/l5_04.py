"""Figures and shared helpers for L5-04 Tensor products and entanglement.

Conventions used everywhere in this lesson: |ab> = |a> (x) |b> with qubit A as the left factor, basis order
00, 01, 10, 11, and the coefficient matrix C[i, j] = <ij|psi> (row index for A, column index for B).
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

S2 = 1 / math.sqrt(2)
I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
BELL = np.array([S2, 0, 0, S2], dtype=complex)


def coeff(psi):
    """Coefficient matrix C with C[i, j] = <ij|psi> (A is the row index)."""
    return np.asarray(psi, dtype=complex).reshape(2, 2)


def schmidt(psi):
    """Schmidt coefficients, A vectors (columns of U) and B vectors (rows of Vh) of a two-qubit pure state."""
    U, s, Vh = np.linalg.svd(coeff(psi))
    return s, U, Vh


def entanglement_entropy(psi) -> float:
    """Entropy (bits) of the squared Schmidt coefficients."""
    p = schmidt(psi)[0] ** 2
    p = p[p > 1e-12]
    return float(-(p * np.log2(p)).sum())


def obs(t):
    """Measurement observable cos(t) Z + sin(t) X (outcomes +1 and -1)."""
    return math.cos(t) * Z + math.sin(t) * X


def joint_probs(rho, a, b):
    """[P(++), P(+-), P(-+), P(--)] when A measures obs(a) and B measures obs(b)."""
    out = []
    for sa in (1, -1):
        for sb in (1, -1):
            Pa = (I2 + sa * obs(a)) / 2
            Pb = (I2 + sb * obs(b)) / 2
            out.append(float(np.real(np.trace(rho @ np.kron(Pa, Pb)))))
    return out


def bell_rho():
    return np.outer(BELL, BELL.conj())


def mixture_rho():
    """The coin-flip preparation: |00> or |11> with probability 1/2 each (averaged)."""
    r = np.zeros((4, 4), dtype=complex)
    r[0, 0] = r[3, 3] = 0.5
    return r


def shots(n: int = 400, seed: int = 5):
    """Seeded simulated shots for the four experiments of the BellVsMixture animation.

    Returns a dict name -> array of outcome indices (0..3 for ++, +-, -+, -- in the chosen basis).
    """
    g = np.random.default_rng(seed)
    out = {}
    for name, rho in (("bell", bell_rho()), ("mix", mixture_rho())):
        for basis, t in (("Z", 0.0), ("X", math.pi / 2)):
            p = np.clip(joint_probs(rho, t, t), 0, None)
            out[f"{name}_{basis}"] = g.choice(4, size=n, p=p / p.sum())
    return out


# ---------------------------------------------------------------------------------------------------------
def correlation_explorer():
    """Both labs measure cos(t) Z + sin(t) X; joint outcome probabilities and the correlation E(t)."""
    angles = list(range(0, 181, 15))
    names = ["++", "+−", "−+", "−−"]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.14,
                        subplot_titles=("Joint outcome probabilities", "Correlation E = P(agree) − P(differ)"))
    rb, rm = bell_rho(), mixture_rho()
    t0 = 0.0
    fig.add_trace(go.Bar(x=names, y=joint_probs(rb, t0, t0), name="Bell state |Φ<sup>+</sup>⟩", marker_color="#7c3aed",
                         legendgroup="b", hovertemplate="%{x}: %{y:.3f}<extra>Bell</extra>"), 1, 1)
    fig.add_trace(go.Bar(x=names, y=joint_probs(rm, t0, t0), name="coin-flip mixture", marker_color="#f59e0b",
                         legendgroup="m", hovertemplate="%{x}: %{y:.3f}<extra>mixture</extra>"), 1, 1)
    ts = np.linspace(0, 180, 91)
    fig.add_trace(go.Scatter(x=ts.round(2).tolist(), y=[1.0] * len(ts), mode="lines", line=dict(color="#7c3aed", width=3),
                             legendgroup="b", showlegend=False, hoverinfo="skip"), 1, 2)
    fig.add_trace(go.Scatter(x=ts.round(2).tolist(), y=(np.cos(np.radians(ts)) ** 2).round(4).tolist(), mode="lines",
                             line=dict(color="#f59e0b", width=3), legendgroup="m", showlegend=False, hoverinfo="skip"), 1, 2)
    fig.add_trace(go.Scatter(x=[0, 0], y=[1.0, 1.0], mode="markers", marker=dict(size=12, color=["#7c3aed", "#f59e0b"]),
                             showlegend=False, hovertemplate="θ = %{x}°<br>E = %{y:.3f}<extra></extra>"), 1, 2)
    steps = []
    for d in angles:
        t = math.radians(d)
        pb = [round(v, 4) for v in joint_probs(rb, t, t)]
        pm = [round(v, 4) for v in joint_probs(rm, t, t)]
        eb, em = pb[0] - pb[1] - pb[2] + pb[3], pm[0] - pm[1] - pm[2] + pm[3]
        steps.append(dict(method="restyle", label=f"{d}°",
                          args=[{"y": [pb, pm, [round(eb, 4), round(em, 4)]], "x": [names, names, [d, d]]}, [0, 1, 4]]))
    fig.update_xaxes(title="outcome pair (A, B)", tickangle=0, row=1, col=1)
    fig.update_yaxes(title="probability", range=[0, 0.55], row=1, col=1)
    fig.update_xaxes(title="measurement angle θ (degrees)", range=[0, 180], dtick=45, tickangle=0, row=1, col=2)
    fig.update_yaxes(title="E(θ)", range=[-0.05, 1.08], row=1, col=2)
    fig.update_layout(template="plotly_white", barmode="group",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="both labs at θ = "))])
    return frame(fig, height=540, stack=True)


def coefficient_matrices():
    """Coefficient matrices of three states and the image of the unit circle under each (Schmidt picture)."""
    t = math.pi / 8
    states = [("$|+\\rangle|0\\rangle$", np.array([S2, 0, S2, 0])),
              ("$\\cos\\frac{\\pi}{8}|00\\rangle + \\sin\\frac{\\pi}{8}|11\\rangle$",
               np.array([math.cos(t), 0, 0, math.sin(t)])),
              ("$|\\Phi^+\\rangle$", BELL.real)]
    fig, axes = plt.subplots(2, 3, figsize=(9.6, 6.2), gridspec_kw=dict(height_ratios=[1, 1.15]))
    ang = np.linspace(0, 2 * math.pi, 300)
    circle = np.vstack([np.cos(ang), np.sin(ang)])
    for k, (name, psi) in enumerate(states):
        C = coeff(psi).real
        s = np.linalg.svd(C, compute_uv=False)
        E = entanglement_entropy(psi)
        ax = axes[0, k]
        ax.imshow(C, cmap="Purples", vmin=0, vmax=1)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{C[i, j]:.3f}", ha="center", va="center", fontsize=11,
                        color="white" if C[i, j] > 0.55 else "#1e1b4b")
        ax.set_xticks([0, 1], ["B: 0", "B: 1"])
        ax.set_yticks([0, 1], ["A: 0", "A: 1"])
        ax.set_title(name, fontsize=11)
        ax.tick_params(length=0)
        ax2 = axes[1, k]
        img = C @ circle
        ax2.plot(circle[0], circle[1], color="#cbd5e1", lw=1, ls="--")
        ax2.plot(img[0], img[1], color="#7c3aed", lw=2.4)
        ax2.set_aspect("equal")
        ax2.set_xlim(-1.15, 1.15)
        ax2.set_ylim(-1.15, 1.15)
        ax2.set_xticks([-1, 0, 1])
        ax2.set_yticks([-1, 0, 1])
        ax2.axhline(0, color="#94a3b8", lw=0.6)
        ax2.axvline(0, color="#94a3b8", lw=0.6)
        for sp in ("top", "right"):
            ax2.spines[sp].set_visible(False)
        ax2.set_title(f"$s_1 = {s[0]:.3f},\\ s_2 = {s[1]:.3f}$\nentropy $E = {abs(E):.3f}$ bit", fontsize=10)
    fig.suptitle("Top: coefficient matrix $C_{ij} = \\langle ij|\\psi\\rangle$.  "
                 "Bottom: $C$ maps the unit circle (dashed) to an ellipse with semi-axes $s_1, s_2$.", fontsize=10)
    fig.tight_layout()
    return fig
