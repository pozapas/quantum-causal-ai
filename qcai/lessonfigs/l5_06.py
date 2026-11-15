"""Figures for L5-06 Quantum channels and complete positivity.

Conventions: rho = (I + r . sigma)/2 with |0> at +z.  Channel parameters as in qcai.science:
depolarizing r -> (1 - p) r; dephasing (x, y, z) -> ((1 - p)x, (1 - p)y, z); amplitude damping
(x, y, z) -> (sqrt(1 - g) x, sqrt(1 - g) y, g + (1 - g) z).
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

from qcai.viz import frame


def _maps():
    return {
        "Depolarizing": lambda x, y, z, s: ((1 - s) * x, (1 - s) * y, (1 - s) * z),
        "Dephasing": lambda x, y, z, s: ((1 - s) * x, (1 - s) * y, z),
        "Amplitude damping": lambda x, y, z, s: (math.sqrt(1 - s) * x, math.sqrt(1 - s) * y, s + (1 - s) * z),
    }


TITLES = {"Depolarizing": "Depolarizing: r → (1 − p) r<br>every direction shrinks equally",
          "Dephasing": "Dephasing: (x, y) shrink by 1 − p, z kept<br>the ball is squashed onto the z axis",
          "Amplitude damping": "Amplitude damping: z → γ + (1 − γ) z<br>the ball shrinks toward |0⟩"}


def channel_explorer():
    """Bloch-ball explorer: choose a channel, slide its strength, watch the image of the ball."""
    maps = _maps()
    names = list(maps)
    colors = {"Depolarizing": "#7c3aed", "Dephasing": "#06b6d4", "Amplitude damping": "#f59e0b"}
    u, v = np.meshgrid(np.linspace(0, 2 * math.pi, 25), np.linspace(0, math.pi, 13))
    X0, Y0, Z0 = np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v)
    pts = np.array([[0, 0, 1], [0, 0, -1], [1, 0, 0]], dtype=float)   # |0>, |1>, |+>
    fig = go.Figure()
    t = np.linspace(0, 2 * math.pi, 73)
    for xs, ys, zs in ((np.cos(t), np.sin(t), 0 * t), (np.cos(t), 0 * t, np.sin(t)), (0 * t, np.cos(t), np.sin(t))):
        fig.add_trace(go.Scatter3d(x=xs.round(3), y=ys.round(3), z=zs.round(3), mode="lines",
                                   line=dict(color="#cbd5e1", width=2), hoverinfo="skip", showlegend=False))
    for (x, y, z), name in (((0, 0, 1.18), "|0⟩"), ((0, 0, -1.18), "|1⟩"), ((1.2, 0, 0), "|+⟩")):
        fig.add_trace(go.Scatter3d(x=[x], y=[y], z=[z], mode="text", text=[name], textfont=dict(size=14, color="#1e1b4b"),
                                   hoverinfo="skip", showlegend=False))
    n_static = len(fig.data)
    s0 = 0.5
    idx = {}
    for k, name in enumerate(names):
        f = maps[name]
        xs, ys, zs = f(X0, Y0, Z0, s0)
        idx[name] = len(fig.data)
        fig.add_trace(go.Surface(x=np.round(xs, 3), y=np.round(ys, 3), z=np.round(zs, 3), opacity=0.35, showscale=False,
                                 colorscale=[[0, colors[name]], [1, colors[name]]], hoverinfo="skip", visible=(k == 0)))
        im = np.array([f(*p, s0) for p in pts])
        fig.add_trace(go.Scatter3d(x=im[:, 0].round(4), y=im[:, 1].round(4), z=im[:, 2].round(4), mode="markers",
                                   marker=dict(size=6, color=["#3b82f6", "#ef4444", "#06b6d4"]), visible=(k == 0),
                                   text=["image of |0⟩", "image of |1⟩", "image of |+⟩"], showlegend=False,
                                   hovertemplate="%{text}<br>(%{x:.3f}, %{y:.3f}, %{z:.3f})<extra></extra>"))
    dyn = [i for name in names for i in (idx[name], idx[name] + 1)]
    steps = []
    for s in [round(0.1 * k, 1) for k in range(11)]:
        xs_l, ys_l, zs_l = [], [], []
        for name in names:
            f = maps[name]
            xs, ys, zs = f(X0, Y0, Z0, s)
            im = np.array([f(*p, s) for p in pts])
            xs_l += [np.round(xs, 3).tolist(), im[:, 0].round(4).tolist()]
            ys_l += [np.round(ys, 3).tolist(), im[:, 1].round(4).tolist()]
            zs_l += [np.round(zs, 3).tolist(), im[:, 2].round(4).tolist()]
        steps.append(dict(method="restyle", label=f"{s:.1f}", args=[{"x": xs_l, "y": ys_l, "z": zs_l}, dyn]))
    buttons = []
    for name in names:
        vis = [True] * n_static + [False] * (len(fig.data) - n_static)
        vis[idx[name]] = vis[idx[name] + 1] = True
        buttons.append(dict(label=name, method="update", args=[{"visible": vis}, {"title.text": TITLES[name]}]))
    fig.update_layout(template="plotly_white", title=dict(text=TITLES[names[0]]),
                      updatemenus=[dict(type="buttons", direction="right", buttons=buttons, showactive=True)],
                      scene=dict(aspectmode="cube", xaxis=dict(range=[-1.25, 1.25], visible=False),
                                 yaxis=dict(range=[-1.25, 1.25], visible=False),
                                 zaxis=dict(range=[-1.25, 1.25], visible=False),
                                 camera=dict(eye=dict(x=1.35, y=0.75, z=0.5))),
                      sliders=[dict(active=5, steps=steps, currentvalue=dict(prefix="strength p or γ = "))])
    return frame(fig, height=600, xticks_lines=0, axes=False, narrow_plot=360)


def cross_sections():
    """x-z cross-sections of the Bloch ball and its image under each channel at strength 0.5."""
    maps = _maps()
    s = 0.5
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.9))
    t = np.linspace(0, 2 * math.pi, 300)
    starts = [(math.sin(a), math.cos(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
    for ax, (name, f) in zip(axes, maps.items()):
        ax.plot(np.sin(t), np.cos(t), color="#cbd5e1", lw=1.2, ls="--")
        x, _, z = f(np.sin(t), 0 * t, np.cos(t), s)
        ax.plot(x, z, color="#7c3aed", lw=2.4)
        for x0, z0 in starts:
            x1, _, z1 = f(x0, 0.0, z0, s)
            ax.annotate("", xy=(x1, z1), xytext=(x0, z0), arrowprops=dict(arrowstyle="-|>", color="#f59e0b", lw=1.2))
        ax.scatter([0], [0], color="#475569", s=10, zorder=3)
        ax.set_aspect("equal")
        ax.set_xlim(-1.25, 1.25)
        ax.set_ylim(-1.25, 1.3)
        ax.set_xticks([-1, 0, 1])
        ax.set_yticks([-1, 0, 1])
        ax.set_xlabel("$x$")
        ax.set_ylabel("$z$")
        ax.text(0.04, 1.08, "$|0\\rangle$", fontsize=10)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        sym = "\\gamma" if name == "Amplitude damping" else "p"
        ax.set_title(f"{name}, ${sym} = {s}$", fontsize=10)
    fig.suptitle("Arrows: where states on the surface go.  Purple: image of the ball's x-z slice.", fontsize=10)
    fig.tight_layout()
    return fig
