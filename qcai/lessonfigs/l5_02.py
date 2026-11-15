"""Figures for L5-02 Gates and circuit order."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

from qcai import science
from qcai.viz import frame

S_GATE = np.diag([1, 1j])
T_GATE = np.diag([1, np.exp(1j * math.pi / 4)])
GATES = {"X": science.X, "Y": science.Y, "Z": science.Z, "H": science.H, "S": S_GATE, "T": T_GATE}
# Bloch rotation (axis, angle) of each gate; every gate equals a phase times exp(-i angle/2 n.sigma)
AXES = {"X": ((1, 0, 0), math.pi), "Y": ((0, 1, 0), math.pi), "Z": ((0, 0, 1), math.pi),
        "H": ((1 / math.sqrt(2), 0, 1 / math.sqrt(2)), math.pi), "S": ((0, 0, 1), math.pi / 2),
        "T": ((0, 0, 1), math.pi / 4)}
CIRCUITS = [("H", ["H"]), ("H, then S", ["H", "S"]), ("S, then H", ["S", "H"]), ("H, S, S, H", ["H", "S", "S", "H"]),
            ("H, T, H", ["H", "T", "H"]), ("X, then H", ["X", "H"]), ("H, then X", ["H", "X"])]
STEP_COLORS = ["#7c3aed", "#06b6d4", "#f59e0b", "#3b82f6"]


def rotate(r, n, a):
    """Rodrigues: rotate vector r by angle a about unit axis n (right-hand rule)."""
    r, n = np.asarray(r, float), np.asarray(n, float)
    return r * math.cos(a) + np.cross(n, r) * math.sin(a) + n * np.dot(n, r) * (1 - math.cos(a))


def path(gates, samples=40):
    """Bloch trajectory of |0> under the circuit (true rotation arcs) and the final state vector."""
    r = np.array([0.0, 0.0, 1.0])
    psi = science.KET0.copy()
    arcs = []
    for g in gates:
        n, a = AXES[g]
        arcs.append(np.array([rotate(r, n, a * s) for s in np.linspace(0, 1, samples)]))
        r = arcs[-1][-1]
        psi = GATES[g] @ psi
        assert np.allclose(r, science.bloch(science.dm(psi)), atol=1e-9)   # arc endpoint = Bloch vector of U|0>
    return arcs, psi, r


def _sphere():
    u, v = np.meshgrid(np.linspace(0, 2 * math.pi, 25), np.linspace(0, math.pi, 13))
    out = [go.Surface(x=(np.cos(u) * np.sin(v)).round(3), y=(np.sin(u) * np.sin(v)).round(3), z=np.cos(v).round(3),
                      opacity=0.13, showscale=False, colorscale=[[0, "#a78bfa"], [1, "#a78bfa"]], hoverinfo="skip")]
    t = np.linspace(0, 2 * math.pi, 73)
    for xs, ys, zs in ((np.cos(t), np.sin(t), 0 * t), (np.sin(t), 0 * t, np.cos(t))):
        out.append(go.Scatter3d(x=xs.round(3), y=ys.round(3), z=zs.round(3), mode="lines",
                                line=dict(color="#cbd5e1", width=2), hoverinfo="skip", showlegend=False))
    for a in ((1.2, 0, 0), (0, 1.2, 0), (0, 0, 1.2)):
        out.append(go.Scatter3d(x=[-a[0], a[0]], y=[-a[1], a[1]], z=[-a[2], a[2]], mode="lines",
                                line=dict(color="#94a3b8", width=2), hoverinfo="skip", showlegend=False))
    out.append(go.Scatter3d(x=[0, 0, 1.3, -1.3, 0, 0], y=[0, 0, 0, 0, 1.3, -1.3], z=[1.25, -1.25, 0, 0, 0, 0], mode="text",
                            text=["|0⟩", "|1⟩", "|+⟩", "|−⟩", "|+i⟩", "|−i⟩"], textfont=dict(size=13, color="#1e1b4b"),
                            hoverinfo="skip", showlegend=False))
    return out


def _fmt(psi):
    """Short text for a state, with the global phase removed so the first nonzero amplitude is real."""
    k = 0 if abs(psi[0]) > 1e-9 else 1
    v = psi * np.exp(-1j * np.angle(psi[k]))

    def c(z):
        if abs(z.imag) < 1e-9:
            return f"{z.real:.3f}"
        if abs(z.real) < 1e-9:
            return f"{z.imag:.3f}i"
        return f"({z.real:.3f}{z.imag:+.3f}i)"
    return f"{c(v[0])}|0⟩ + {c(v[1])}|1⟩".replace("+ -", "− ").replace("+ (-", "+ (−")


def circuit_explorer():
    """Bloch sphere with a dropdown of short circuits applied to |0>; each gate's rotation arc is drawn."""
    fig = go.Figure(_sphere())
    n0 = len(fig.data)
    maxg = max(len(g) for _, g in CIRCUITS)

    def traces(gates):
        arcs, psi, r = path(gates)
        out = []
        for i in range(maxg):
            if i < len(arcs):
                a = arcs[i]
                out.append(dict(x=a[:, 0].round(4).tolist(), y=a[:, 1].round(4).tolist(), z=a[:, 2].round(4).tolist()))
            else:
                out.append(dict(x=[None], y=[None], z=[None]))
        out.append(dict(x=[0, r[0]], y=[0, r[1]], z=[0, r[2]]))
        return out, f"{_fmt(psi)}, P(0) = {abs(psi[0]) ** 2:.3f}"

    first, label0 = traces(CIRCUITS[0][1])
    for i in range(maxg):
        fig.add_trace(go.Scatter3d(**first[i], mode="lines", line=dict(color=STEP_COLORS[i], width=6),
                                   name=f"gate {i + 1} arc", showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter3d(**first[maxg], mode="lines+markers", line=dict(color="#1e1b4b", width=6),
                               marker=dict(size=[0, 5], color="#1e1b4b"), showlegend=False, hoverinfo="skip"))
    idx = list(range(n0, n0 + maxg + 1))
    buttons = []
    for name, gates in CIRCUITS:
        tr, lab = traces(gates)
        buttons.append(dict(method="update", label=name,
                            args=[{"x": [t["x"] for t in tr], "y": [t["y"] for t in tr], "z": [t["z"] for t in tr]},
                                  {"title.text": f"Start at |0⟩, apply {name}.<br>Result: {lab}"}, idx]))
    ax = dict(visible=False, range=[-1.4, 1.4])
    fig.update_layout(template="plotly_white", title=f"Start at |0⟩, apply H.<br>Result: {label0}",
                      scene=dict(aspectmode="cube", xaxis=ax, yaxis=ax, zaxis=ax, camera=dict(eye=dict(x=1.35, y=0.75, z=0.55))),
                      updatemenus=[dict(type="dropdown", buttons=buttons, active=0, showactive=True)])
    return frame(fig, height=600, xticks_lines=0, axes=False, narrow_plot=380)


def commutator_map():
    """Heat map of the Frobenius norm of AB - BA for the six standard gates."""
    names = list(GATES)
    M = np.array([[np.linalg.norm(GATES[a] @ GATES[b] - GATES[b] @ GATES[a]) for b in names] for a in names])
    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    im = ax.imshow(M, cmap="Purples", vmin=0, vmax=3)
    for i in range(len(names)):
        for j in range(len(names)):
            v = M[i, j]
            ax.text(j, i, "0" if v < 1e-9 else f"{v:.2f}", ha="center", va="center", fontsize=10,
                    color="white" if v > 1.8 else "#1e1b4b")
    ax.set_xticks(range(len(names)), names)
    ax.set_yticks(range(len(names)), names)
    ax.set_xlabel("second matrix B")
    ax.set_ylabel("first matrix A")
    ax.set_title(r"$\|AB - BA\|_F$: zero means the order does not matter", fontsize=11)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    return fig
