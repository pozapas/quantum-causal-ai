"""Figures for L5-09 Entropy and quantum tomography.

Conventions: Pauli tomography of one qubit with N shots in each of the X, Y and Z bases (3N shots in all);
the linear-inversion estimate of each Bloch component is r_i = (n_plus - n_minus) / N.
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

from qcai.viz import frame

R_TRUE = np.array([0.5, 0.3, 0.7])          # |r| = 0.911, the state used in the lesson and the animation
SHOTS = [10, 30, 100, 300, 1000, 3000, 10000]


def estimates(r, shots, reps, seed):
    """`reps` independent linear-inversion estimates, each from `shots` shots per Pauli basis."""
    rng = np.random.default_rng(seed)
    plus = rng.binomial(shots, (1 + np.asarray(r)) / 2, size=(reps, 3))
    return 2 * plus / shots - 1


def tomography_cloud():
    """3-D Bloch ball with 200 repeated tomography estimates for a chosen number of shots per basis."""
    reps = 200
    u, v = np.meshgrid(np.linspace(0, 2 * math.pi, 25), np.linspace(0, math.pi, 13))
    fig = go.Figure()
    fig.add_trace(go.Surface(x=np.cos(u) * np.sin(v), y=np.sin(u) * np.sin(v), z=np.cos(v), opacity=0.12,
                             showscale=False, colorscale=[[0, "#a78bfa"], [1, "#a78bfa"]], hoverinfo="skip",
                             showlegend=False))
    fig.add_trace(go.Scatter3d(x=[0, R_TRUE[0]], y=[0, R_TRUE[1]], z=[0, R_TRUE[2]], mode="lines+markers",
                               line=dict(color="#7c3aed", width=6), marker=dict(size=[2, 6], color="#7c3aed"),
                               name="true Bloch vector"))
    data = []
    for k, n in enumerate(SHOTS):
        e = estimates(R_TRUE, n, reps, seed=100 + k)
        out = np.linalg.norm(e, axis=1) > 1
        rms = math.sqrt(np.mean(np.sum((e - R_TRUE) ** 2, axis=1)))
        data.append((e[~out].round(4), e[out].round(4), out.mean(), rms, n))
    ins, outs, frac, rms, n0 = data[0]
    fig.add_trace(go.Scatter3d(x=ins[:, 0], y=ins[:, 1], z=ins[:, 2], mode="markers",
                               marker=dict(size=3, color="#06b6d4", opacity=0.8), name="estimate inside ball"))
    fig.add_trace(go.Scatter3d(x=outs[:, 0], y=outs[:, 1], z=outs[:, 2], mode="markers",
                               marker=dict(size=3, color="#ef4444", opacity=0.9), name="estimate outside ball"))

    def title(frac, rms, n):
        return (f"200 tomography runs, N = {n} per basis<br>"
                f"outside ball: {100 * frac:.0f}%, rms error {rms:.3f}")

    first = title(frac, rms, n0)

    steps = []
    for ins, outs, frac, rms, n in data:
        steps.append(dict(method="update", label=f"{n}",
                          args=[{"x": [ins[:, 0].tolist(), outs[:, 0].tolist()],
                                 "y": [ins[:, 1].tolist(), outs[:, 1].tolist()],
                                 "z": [ins[:, 2].tolist(), outs[:, 2].tolist()]},
                                {"title.text": title(frac, rms, n)}, [2, 3]]))
    ax = dict(range=[-1.25, 1.25], showbackground=False, gridcolor="#e2e8f0", zerolinecolor="#94a3b8", tickvals=[-1, 0, 1])
    fig.update_layout(template="plotly_white", title=dict(text=first),
                      scene=dict(aspectmode="cube", xaxis=dict(title="x", **ax), yaxis=dict(title="y", **ax),
                                 zaxis=dict(title="z", **ax), camera=dict(eye=dict(x=1.5, y=1.2, z=0.8))),
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="shots per basis N = "))])
    return frame(fig, height=600, xticks_lines=0, axes=False, narrow_plot=360)


def tomography_costs():
    """Left: rms error of the estimate against shots (Monte Carlo and the 1/sqrt(N) law).
    Right: real parameters 4^n - 1 and local Pauli settings 3^n against the number of qubits n."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 3.7))
    ns = np.array(SHOTS)
    mc = []
    for k, n in enumerate(ns):
        e = estimates(R_TRUE, int(n), 4000, seed=7 + k)
        mc.append(math.sqrt(np.mean(np.sum((e - R_TRUE) ** 2, axis=1))))
    theory = np.sqrt((3 - R_TRUE @ R_TRUE) / ns)
    a.loglog(ns, theory, color="#7c3aed", lw=2, label=r"$\sqrt{(3 - |\vec r|^2)/N}$")
    a.loglog(ns, mc, "o", color="#f59e0b", ms=6, label="Monte Carlo, 4000 runs")
    a.set_yticks([0.02, 0.05, 0.1, 0.2, 0.5])
    a.set_yticklabels(["0.02", "0.05", "0.1", "0.2", "0.5"])
    a.minorticks_off()
    a.set_xlabel("shots per basis $N$")
    a.set_ylabel(r"rms error $|\hat r - \vec r|$")
    a.set_title("Ten times the accuracy costs\na hundred times the shots", fontsize=10)
    a.legend(frameon=False, fontsize=9, loc="lower left")
    q = np.arange(1, 9)
    b.semilogy(q, 4.0 ** q - 1, "o-", color="#3b82f6", label="real parameters $4^n - 1$")
    b.semilogy(q, 3.0 ** q, "s-", color="#06b6d4", label="Pauli settings $3^n$")
    b.semilogy(q, 2.0 ** q, "^--", color="#94a3b8", label="outcomes per setting $2^n$")
    b.set_xlabel("number of qubits $n$")
    b.set_title("Full tomography grows exponentially", fontsize=10)
    b.legend(frameon=False, fontsize=9, loc="upper left")
    for ax in (a, b):
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
