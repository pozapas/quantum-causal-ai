"""Figures for L6-05 Discovery and informational access."""
from __future__ import annotations

import itertools

import numpy as np
import plotly.graph_objects as go

from qcai.viz import frame

V_CC = {"Φ+": (1, -1, 1), "Φ−": (-1, 1, 1), "Ψ+": (1, 1, -1), "Ψ−": (-1, -1, -1)}
V_CE = {"I": (1, 1, 1), "X": (1, -1, -1), "Y": (-1, 1, -1), "Z": (-1, -1, 1)}


def _mesh(verts, color, name):
    V = np.array(list(verts))
    faces = list(itertools.combinations(range(4), 3))
    return go.Mesh3d(x=V[:, 0], y=V[:, 1], z=V[:, 2], i=[f[0] for f in faces], j=[f[1] for f in faces],
                     k=[f[2] for f in faces], color=color, opacity=0.13, name=name, showlegend=True, hoverinfo="skip")


def _edges(verts, color, width=4):
    V = list(verts)
    xs, ys, zs = [], [], []
    for a, b in itertools.combinations(range(len(V)), 2):
        if len(V) == 6 and np.dot(V[a], V[b]) != 0:
            continue
        xs += [V[a][0], V[b][0], None]
        ys += [V[a][1], V[b][1], None]
        zs += [V[a][2], V[b][2], None]
    return go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line=dict(color=color, width=width), showlegend=False,
                        hoverinfo="skip")


def tetra_explorer():
    """The two tetrahedra, the octahedron, and two noisy families (-v,-v,-v) and (v,v,v) under a slider."""
    vs = [round(k / 12, 4) for k in range(13)]
    octv = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    fig = go.Figure()
    fig.add_trace(_mesh(V_CC.values(), "#3b82f6", "common cause"))
    fig.add_trace(_edges(V_CC.values(), "#3b82f6"))
    fig.add_trace(_mesh(V_CE.values(), "#ef4444", "direct cause"))
    fig.add_trace(_edges(V_CE.values(), "#ef4444"))
    fig.add_trace(_edges(octv, "#7c3aed", 3))
    labels = list(V_CC.items()) + list(V_CE.items())
    fig.add_trace(go.Scatter3d(x=[1.18 * p[0] for _, p in labels], y=[1.18 * p[1] for _, p in labels],
                               z=[1.18 * p[2] for _, p in labels], mode="text", text=[k for k, _ in labels],
                               textfont=dict(color=["#3b82f6"] * 4 + ["#ef4444"] * 4, size=13), showlegend=False,
                               hoverinfo="skip"))
    v0 = vs[-1]
    fig.add_trace(go.Scatter3d(x=[-v0], y=[-v0], z=[-v0], mode="markers", marker=dict(size=7, color="#1d4ed8"),
                               name="Werner state", hovertemplate="c = (%{x:.2f}, %{y:.2f}, %{z:.2f})<extra></extra>"))
    fig.add_trace(go.Scatter3d(x=[v0], y=[v0], z=[v0], mode="markers", marker=dict(size=7, color="#b91c1c"),
                               name="noisy identity", hovertemplate="c = (%{x:.2f}, %{y:.2f}, %{z:.2f})<extra></extra>"))
    steps = []
    for v in vs:
        verdict = "inside the octahedron: ambiguous" if 3 * v <= 1 + 1e-9 else "outside: each fits one structure"
        steps.append(dict(method="update", label=f"{v:.2f}",
                          args=[{"x": [[-v], [v]], "y": [[-v], [v]], "z": [[-v], [v]]},
                                {"title.text": f"Pauli correlations (c<sub>x</sub>, c<sub>y</sub>, c<sub>z</sub>)<br>v = {v:.2f}: {verdict}"},
                                [6, 7]]))
    ax = dict(range=[-1.3, 1.3], tickvals=[-1, 0, 1], backgroundcolor="white", gridcolor="#e2e8f0", zeroline=False)
    fig.update_layout(template="plotly_white",
                      title=f"Pauli correlations (c<sub>x</sub>, c<sub>y</sub>, c<sub>z</sub>)<br>v = {v0:.2f}: outside: each fits one structure",
                      scene=dict(aspectmode="cube", xaxis=dict(title="cx", **ax), yaxis=dict(title="cy", **ax),
                                 zaxis=dict(title="cz", **ax), camera=dict(eye=dict(x=1.6, y=-1.5, z=0.9))),
                      sliders=[dict(active=len(vs) - 1, steps=steps, currentvalue=dict(prefix="visibility v = "))])
    return frame(fig, height=620, xticks_lines=0, axes=False, narrow_plot=360)
