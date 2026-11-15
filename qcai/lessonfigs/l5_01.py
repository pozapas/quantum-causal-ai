"""Figures for L5-01 States and the Born rule."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

from qcai import science
from qcai.viz import frame

PHI_SHOWN = 60          # degrees: the azimuth of the one state drawn as an arrow on the ring


def _sphere_traces():
    """Light sphere, equator and prime meridian, axes and pole labels (static traces)."""
    u, v = np.meshgrid(np.linspace(0, 2 * math.pi, 25), np.linspace(0, math.pi, 13))
    out = [go.Surface(x=(np.cos(u) * np.sin(v)).round(3), y=(np.sin(u) * np.sin(v)).round(3), z=np.cos(v).round(3),
                      opacity=0.13, showscale=False, colorscale=[[0, "#a78bfa"], [1, "#a78bfa"]], hoverinfo="skip")]
    t = np.linspace(0, 2 * math.pi, 73)
    for xs, ys, zs in ((np.cos(t), np.sin(t), 0 * t), (np.sin(t), 0 * t, np.cos(t))):
        out.append(go.Scatter3d(x=xs.round(3), y=ys.round(3), z=zs.round(3), mode="lines",
                                line=dict(color="#cbd5e1", width=2), hoverinfo="skip", showlegend=False))
    for a, b in (((-1.2, 0, 0), (1.2, 0, 0)), ((0, -1.2, 0), (0, 1.2, 0)), ((0, 0, -1.2), (0, 0, 1.2))):
        out.append(go.Scatter3d(x=[a[0], b[0]], y=[a[1], b[1]], z=[a[2], b[2]], mode="lines",
                                line=dict(color="#94a3b8", width=2), hoverinfo="skip", showlegend=False))
    out.append(go.Scatter3d(x=[0, 0, 1.38, 0], y=[0, 0, 0, 1.36], z=[1.3, -1.3, 0, 0], mode="text",
                            text=["|0⟩", "|1⟩", "|+⟩ (x)", "y"], textfont=dict(size=14, color="#1e1b4b"),
                            hoverinfo="skip", showlegend=False))
    return out


def _state(theta_deg: float):
    th, ph = math.radians(theta_deg), math.radians(PHI_SHOWN)
    q = science.qubit(th, ph)
    ring_t = np.linspace(0, 2 * math.pi, 73)
    ring = (math.sin(th) * np.cos(ring_t), math.sin(th) * np.sin(ring_t), np.full_like(ring_t, math.cos(th)))
    return q, ring


def bloch_explorer():
    """Bloch sphere: polar angle slider; the latitude ring, one state on it, and its projection onto z."""
    thetas = list(range(0, 181, 15))
    fig = go.Figure(_sphere_traces())
    n0 = len(fig.data)
    start = thetas.index(60)            # open on the lesson's example state, theta = 60 degrees

    def dyn(theta_deg):
        q, ring = _state(theta_deg)
        x, y, z = q["x"], q["y"], q["z"]
        return [
            dict(x=ring[0].round(4).tolist(), y=ring[1].round(4).tolist(), z=ring[2].round(4).tolist()),
            dict(x=[0, x], y=[0, y], z=[0, z]),
            dict(x=[x, 0], y=[y, 0], z=[z, z]),
            dict(x=[0], y=[0], z=[z], text=[f"  P(0) = {q['p0']:.3f}"]),
        ]

    d = dyn(thetas[start])
    fig.add_trace(go.Scatter3d(**d[0], mode="lines", line=dict(color="#06b6d4", width=5), name="same P(0), any φ"))
    fig.add_trace(go.Scatter3d(**d[1], mode="lines+markers", line=dict(color="#7c3aed", width=7),
                               marker=dict(size=[0, 6], color="#7c3aed"), name=f"state with φ = {PHI_SHOWN}°"))
    fig.add_trace(go.Scatter3d(**d[2], mode="lines", line=dict(color="#f59e0b", width=4, dash="dash"),
                               name="projection onto z"))
    fig.add_trace(go.Scatter3d(**d[3], mode="markers+text", marker=dict(size=5, color="#f59e0b"),
                               textposition="middle right", textfont=dict(size=13, color="#1e1b4b"), showlegend=False))
    idx = [n0, n0 + 1, n0 + 2, n0 + 3]
    steps = []
    for t in thetas:
        dd = dyn(t)
        args = {"x": [e["x"] for e in dd], "y": [e["y"] for e in dd], "z": [e["z"] for e in dd],
                "text": [None, None, None, dd[3]["text"]]}
        steps.append(dict(method="restyle", label=f"{t}°", args=[args, idx]))
    ax = dict(visible=False, range=[-1.45, 1.45])
    fig.update_layout(template="plotly_white",
                      title="Polar angle θ sets P(0) = cos²(θ/2);<br>the azimuth φ does not change it",
                      scene=dict(aspectmode="cube", xaxis=ax, yaxis=ax, zaxis=ax,
                                 camera=dict(eye=dict(x=1.35, y=0.75, z=0.55))),
                      sliders=[dict(active=start, steps=steps, currentvalue=dict(prefix="polar angle θ = "))])
    return frame(fig, height=600, xticks_lines=0, axes=False, narrow_plot=360)


def shots_convergence():
    """Running frequency of outcome 1 for P(1) = 1/4, with the 2-sigma band 1/4 +- 2 sqrt(p(1-p)/n)."""
    p = 0.25
    n = np.arange(1, 4001)
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    band = 2 * np.sqrt(p * (1 - p) / n)
    ax.fill_between(n, p - band, p + band, color="#cffafe", label=r"$p \pm 2\sqrt{p(1-p)/n}$")
    for seed, col in ((42, "#7c3aed"), (99, "#3b82f6"), (5, "#f59e0b")):
        tr = science.trials(p, 4000, seed=seed)["trace"]
        ax.plot(n, tr, color=col, lw=1.3, label=f"seed {seed}")
    ax.axhline(p, color="#1e1b4b", lw=1, ls="--")
    ax.text(4200, p, r"$|\beta|^2 = 1/4$", va="center", fontsize=10, color="#1e1b4b")
    ax.set_xscale("log")
    ax.set_xlim(1, 4000)
    ax.set_ylim(0, 0.6)
    ax.set_xlabel("number of shots $n$ (log scale)")
    ax.set_ylabel("fraction of outcome 1")
    ax.set_title(r"Three runs of $n$ shots on $\frac{\sqrt{3}}{2}|0\rangle + \frac{1}{2}|1\rangle$", fontsize=11)
    ax.legend(loc="upper right", fontsize=9, frameon=False, ncol=2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
