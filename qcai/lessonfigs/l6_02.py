"""Figures for L6-02 Channels in the Choi representation.

Convention: J = sum_ij |i><j| (x) E(|i><j|) on H_in (x) H_out (input first, unnormalized, Tr J = d_in).
"""
from __future__ import annotations

import itertools
import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

from qcai.viz import frame

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = (I2, X, Y, Z)


def choi(E, d=2):
    """J = sum_ij |i><j| (x) E(|i><j|), input factor first."""
    J = np.zeros((d * d, d * d), dtype=complex)
    for i in range(d):
        for j in range(d):
            Eij = np.zeros((d, d), dtype=complex)
            Eij[i, j] = 1
            J += np.kron(Eij, E(Eij))
    return J


def pauli_weights(lx, ly, lz):
    """Weights p_I, p_X, p_Y, p_Z of the Pauli-diagonal map with Bloch scalings (lx, ly, lz)."""
    return np.array([1 + lx + ly + lz, 1 + lx - ly - lz, 1 - lx + ly - lz, 1 - lx - ly + lz]) / 4


def pauli_map(lam):
    w = pauli_weights(*lam)
    return lambda R: sum(wk * P @ R @ P for wk, P in zip(w, PAULI))


CHANNELS = [
    ("identity", (1, 1, 1)),
    ("dephasing, p = 0.5", (0.5, 0.5, 1)),
    ("bit flip, 30%", (1, 0.4, 0.4)),
    ("depolarizing, p = 0.5", (0.5, 0.5, 0.5)),
    ("completely depolarizing", (0, 0, 0)),
    ("depolarizing, p = 4/3", (-1 / 3, -1 / 3, -1 / 3)),
    ("transpose", (1, -1, 1)),
    ("universal NOT", (-1, -1, -1)),
]


def pauli_tetrahedron():
    """Pauli-diagonal qubit maps as points (lx, ly, lz): CP ones fill a tetrahedron inside the cube of positive maps."""
    V = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], dtype=float)
    faces = list(itertools.combinations(range(4), 3))
    fig = go.Figure()
    fig.add_trace(go.Mesh3d(x=V[:, 0], y=V[:, 1], z=V[:, 2], i=[f[0] for f in faces], j=[f[1] for f in faces],
                            k=[f[2] for f in faces], color="#7c3aed", opacity=0.15, name="CP maps (tetrahedron)",
                            showlegend=True, hoverinfo="skip"))
    xs, ys, zs = [], [], []
    for a, b in itertools.combinations(range(4), 2):
        xs += [V[a, 0], V[b, 0], None]
        ys += [V[a, 1], V[b, 1], None]
        zs += [V[a, 2], V[b, 2], None]
    fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line=dict(color="#7c3aed", width=4), showlegend=False,
                               hoverinfo="skip"))
    C = np.array(list(itertools.product([-1, 1], repeat=3)), dtype=float)
    cx, cy, cz = [], [], []
    for a, b in itertools.combinations(range(8), 2):
        if np.sum(np.abs(C[a] - C[b])) == 2:
            cx += [C[a, 0], C[b, 0], None]
            cy += [C[a, 1], C[b, 1], None]
            cz += [C[a, 2], C[b, 2], None]
    fig.add_trace(go.Scatter3d(x=cx, y=cy, z=cz, mode="lines", line=dict(color="#94a3b8", width=2, dash="dash"),
                               name="positive maps (cube)", hoverinfo="skip"))
    lam = np.array([c[1] for c in CHANNELS], dtype=float)
    fig.add_trace(go.Scatter3d(x=lam[:, 0], y=lam[:, 1], z=lam[:, 2], mode="markers",
                               marker=dict(size=4, color="#475569"), name="named maps",
                               text=[c[0] for c in CHANNELS], hovertemplate="%{text}<br>λ = (%{x:.2f}, %{y:.2f}, %{z:.2f})<extra></extra>"))

    def info(name, lmb):
        ev = 2 * pauli_weights(*lmb)
        J = choi(pauli_map(lmb))
        assert np.allclose(np.sort(np.linalg.eigvalsh(J)), np.sort(ev))
        cp = bool(ev.min() > -1e-12)
        evs = ", ".join(f"{v:.2f}".replace("-0.00", "0.00") for v in ev)
        verdict = "CP: a physical channel" if cp else "not CP: no physical channel"
        return (f"{name}: λ = ({lmb[0]:.2f}, {lmb[1]:.2f}, {lmb[2]:.2f})<br>eigenvalues of J: {evs}<br>{verdict}",
                "#06b6d4" if cp else "#ef4444")

    t0, c0 = info(*CHANNELS[0])
    fig.add_trace(go.Scatter3d(x=[lam[0, 0]], y=[lam[0, 1]], z=[lam[0, 2]], mode="markers",
                               marker=dict(size=9, color=c0, line=dict(color="#1e1b4b", width=1)), name="selected map",
                               hoverinfo="skip"))
    steps = []
    for name, lmb in CHANNELS:
        t, col = info(name, lmb)
        steps.append(dict(method="update", label=name.split(",")[0],
                          args=[{"x": [[lmb[0]]], "y": [[lmb[1]]], "z": [[lmb[2]]], "marker.color": [col]},
                                {"title.text": t}, [4]]))
    ax = dict(range=[-1.15, 1.15], tickvals=[-1, 0, 1], backgroundcolor="white", gridcolor="#e2e8f0")
    fig.update_layout(template="plotly_white", title=dict(text=t0),
                      scene=dict(aspectmode="cube", xaxis=dict(title="λx", **ax), yaxis=dict(title="λy", **ax),
                                 zaxis=dict(title="λz", **ax), camera=dict(eye=dict(x=1.5, y=1.3, z=0.9))),
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="map: "))])
    return frame(fig, height=620, xticks_lines=0, axes=False, narrow_plot=360)


def choi_gallery():
    """Choi matrices of four qubit maps, with their eigenvalues."""
    g = 0.36
    sq = math.sqrt(1 - g)

    def ad(R):
        K0 = np.array([[1, 0], [0, sq]])
        K1 = np.array([[0, math.sqrt(g)], [0, 0]])
        return K0 @ R @ K0.conj().T + K1 @ R @ K1.conj().T

    maps = [("identity", lambda R: R), ("depolarizing, p = 1/2", lambda R: 0.5 * R + 0.5 * np.trace(R) * I2 / 2),
            ("amplitude damping, γ = 0.36", ad), ("transpose (not CP)", lambda R: R.T)]
    fig, axes = plt.subplots(1, 4, figsize=(11.6, 3.5))
    ticks = ["00", "01", "10", "11"]
    for ax, (name, E) in zip(axes, maps):
        J = choi(E)
        assert np.allclose(J.imag, 0)
        ev = np.sort(np.linalg.eigvalsh(J))[::-1]
        ax.imshow(J.real, cmap="PuOr", vmin=-1.2, vmax=1.2)
        for r in range(4):
            for c in range(4):
                v = J.real[r, c]
                ax.text(c, r, f"{v:g}" if abs(v) > 1e-12 else "0", ha="center", va="center", fontsize=9,
                        color="white" if abs(v) > 0.6 else "#1e1b4b")
        ax.axhline(1.5, color="#475569", lw=0.8)
        ax.axvline(1.5, color="#475569", lw=0.8)
        ax.set_xticks(range(4))
        ax.set_yticks(range(4))
        ax.set_xticklabels(ticks, fontsize=8)
        ax.set_yticklabels(ticks, fontsize=8)
        evs = ", ".join(f"{v:.2f}".replace("-0.00", "0.00") for v in ev)
        ax.set_title(f"{name}\neigenvalues {evs}", fontsize=9)
    fig.suptitle("Choi matrices $J$ (rows and columns labeled $|i_{in}\\, o_{out}\\rangle$); lines mark the $2\\times 2$ blocks "
                 "E(|i⟩⟨j|)", fontsize=10)
    fig.tight_layout()
    return fig
