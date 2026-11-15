"""Figures for L7-02 Variational circuits and parameter-shift gradients."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai import science as s
from qcai.viz import frame

TH = math.pi / 6


def _var_sum(h):
    """(1 - f(th+h)^2) + (1 - f(th-h)^2) for f = cos: N times 4 Var of the two-point difference numerator."""
    return (1 - math.cos(TH + h) ** 2) + (1 - math.cos(TH - h) ** 2)


def _rmse_fd(h, n):
    bias = -math.sin(TH) * (math.sin(h) / h - 1)
    return math.sqrt(bias ** 2 + _var_sum(h) / (4 * h * h * n))


def _rmse_shift(h, n):
    return math.sqrt(_var_sum(h) / (4 * math.sin(h) ** 2 * n))


def estimator_explorer():
    """Slider over the step h: the two sampled points on f = cos, and the RMSE of both estimators at N = 1000."""
    n = 1000
    hs = [0.02, 0.05, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0, 1.2, 1.4, round(math.pi / 2, 4)]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.14,
                        subplot_titles=("Where the two circuits are run", "Error of the gradient estimate"))
    t = np.linspace(-math.pi / 2, 3 * math.pi / 2, 161)
    fig.add_trace(go.Scatter(x=t.round(4).tolist(), y=np.cos(t).round(4).tolist(), mode="lines",
                             line=dict(color="#7c3aed", width=3), name="f(θ) = cos θ"), 1, 1)

    def pts(h):
        xs = [TH - h, TH + h]
        return [round(v, 4) for v in xs], [round(math.cos(v), 4) for v in xs]

    x0, y0 = pts(hs[2])
    fig.add_trace(go.Scatter(x=x0, y=y0, mode="lines+markers", marker=dict(size=11, color="#f59e0b"),
                             line=dict(color="#f59e0b", width=2), name="points θ ± h"), 1, 1)
    fig.add_trace(go.Scatter(x=[TH], y=[math.cos(TH)], mode="markers", marker=dict(size=10, color="#ef4444"),
                             showlegend=False, hovertemplate="θ = π/6<extra></extra>"), 1, 1)
    grid = np.geomspace(0.01, math.pi / 2, 120)
    fig.add_trace(go.Scatter(x=grid.round(4).tolist(), y=[round(_rmse_fd(h, n), 5) for h in grid], mode="lines",
                             line=dict(color="#f59e0b", width=3), name="finite difference"), 1, 2)
    fig.add_trace(go.Scatter(x=grid.round(4).tolist(), y=[round(_rmse_shift(h, n), 5) for h in grid], mode="lines",
                             line=dict(color="#7c3aed", width=3), name="shift rule, step h"), 1, 2)
    fig.add_trace(go.Scatter(x=[hs[2], hs[2]], y=[round(_rmse_fd(hs[2], n), 5), round(_rmse_shift(hs[2], n), 5)],
                             mode="markers", marker=dict(size=12, color=["#f59e0b", "#7c3aed"], line=dict(color="#1e1b4b", width=1)),
                             showlegend=False, hovertemplate="h = %{x}<br>RMSE %{y:.4f}<extra></extra>"), 1, 2)
    steps = []
    for h in hs:
        px, py = pts(h)
        steps.append(dict(method="restyle", label=f"{h:g}",
                          args=[{"x": [px, [h, h]], "y": [py, [round(_rmse_fd(h, n), 5), round(_rmse_shift(h, n), 5)]]}, [1, 5]]))
    fig.update_xaxes(title="θ (radians)", range=[-1.7, 4.9], row=1, col=1)
    fig.update_yaxes(title="f(θ)", range=[-1.15, 1.15], row=1, col=1)
    fig.update_xaxes(title="step h (log scale)", type="log", range=[-2.05, 0.25], tickvals=[0.01, 0.03, 0.1, 0.3, 1], ticktext=["0.01", "0.03", "0.1", "0.3", "1"], row=1, col=2)
    fig.update_yaxes(title="RMSE at N = 1000 shots", type="log", range=[-1.9, 0.5], tickvals=[0.02, 0.05, 0.1, 0.2, 0.5, 1, 2], ticktext=["0.02", "0.05", "0.1", "0.2", "0.5", "1", "2"], row=1, col=2)
    fig.update_layout(template="plotly_white", title="Finite difference against the shift rule at θ = π/6",
                      sliders=[dict(active=2, steps=steps, currentvalue=dict(prefix="step h = "))])
    return frame(fig, height=560, stack=True)


# ------------------------------------------------------------------ loss surface
THETA_STAR = np.array([1.1, 0.7])
XS = np.linspace(-math.pi, math.pi, 15)
YS = np.array([s.vqc_expectation(THETA_STAR, x) for x in XS])


def _loss(t):
    return float(np.mean([(s.vqc_expectation(t, x) - y) ** 2 for x, y in zip(XS, YS)]))


def _grad(t):
    return sum(2 * (s.vqc_expectation(t, x) - y) * s.vqc_gradient(t, x) for x, y in zip(XS, YS)) / len(XS)


def loss_surface():
    """3-D loss surface L(theta0, theta1) with the descent path; slider reveals the path step by step."""
    g = np.linspace(-math.pi, math.pi, 31)
    Z = np.array([[_loss((a, b)) for a in g] for b in g])
    t = np.array([0.3, -2.2])
    path = [t.copy()]
    for _ in range(80):
        t = t - 0.4 * _grad(t)
        path.append(t.copy())
    path = np.array(path)
    L = np.array([_loss(p) for p in path])
    fig = go.Figure()
    fig.add_trace(go.Surface(x=g.round(3), y=g.round(3), z=Z.round(4), colorscale="Viridis", opacity=0.75, showscale=False,
                             name="loss", hovertemplate="θ0 %{x:.2f}<br>θ1 %{y:.2f}<br>loss %{z:.3f}<extra></extra>"))
    k0 = 1
    fig.add_trace(go.Scatter3d(x=path[:k0, 0].round(4), y=path[:k0, 1].round(4), z=(L[:k0] + 0.02).round(4),
                               mode="lines+markers", line=dict(color="#ef4444", width=6), marker=dict(size=3, color="#ef4444"),
                               name="descent path"))
    shows = [1, 3, 6, 10, 15, 20, 30, 45, 60, 81]
    steps = [dict(method="restyle", label=str(k - 1),
                  args=[{"x": [path[:k, 0].round(4).tolist()], "y": [path[:k, 1].round(4).tolist()],
                         "z": [(L[:k] + 0.02).round(4).tolist()]}, [1]]) for k in shows]
    fig.update_layout(template="plotly_white", title="Loss over (θ0, θ1) and gradient descent",
                      scene=dict(aspectmode="cube", xaxis_title="θ0", yaxis_title="θ1", zaxis_title="loss",
                                 camera=dict(eye=dict(x=1.5, y=-1.5, z=1.1))),
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="steps taken: "))])
    return frame(fig, height=560, xticks_lines=0, axes=False, narrow_plot=360)


def rmse_vs_shots():
    """RMSE against shots per setting: shift rule, fixed-step difference, and a difference with the best step."""
    ns = np.array([30, 100, 300, 1000, 3000, 10000, 30000])
    gen = np.random.default_rng(11)
    reps = 3000
    sim_ps, sim_fd = [], []
    for n in ns:
        def fhat(t):
            return 2 * gen.binomial(n, (1 + math.cos(t)) / 2, size=reps) / n - 1
        ps = 0.5 * (fhat(TH + math.pi / 2) - fhat(TH - math.pi / 2))
        fd = (fhat(TH + 0.1) - fhat(TH - 0.1)) / 0.2
        sim_ps.append(math.sqrt(np.mean((ps + 0.5) ** 2)))
        sim_fd.append(math.sqrt(np.mean((fd + 0.5) ** 2)))
    nn = np.geomspace(20, 50000, 100)
    hgrid = np.geomspace(0.01, 1.5, 600)
    best = [min(_rmse_fd(h, n) for h in hgrid) for n in nn]
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.loglog(nn, [_rmse_shift(math.pi / 2, n) for n in nn], color="#7c3aed", lw=2, label="shift rule (theory)")
    ax.loglog(ns, sim_ps, "o", color="#7c3aed", ms=6, label="shift rule (3000 simulated repeats)")
    ax.loglog(nn, [_rmse_fd(0.1, n) for n in nn], color="#f59e0b", lw=2, label="difference, h = 0.1 (theory)")
    ax.loglog(ns, sim_fd, "s", color="#f59e0b", ms=6, label="difference, h = 0.1 (simulated)")
    ax.loglog(nn, best, "--", color="#475569", lw=2, label="difference, best h for each N")
    ax.set_xlabel("shots per circuit setting, N")
    ax.set_ylabel("RMSE of the estimate of $f'(\\pi/6)$")
    ax.set_title("Unbiased large shift: RMSE $\\propto N^{-1/2}$; tuned difference: $\\propto N^{-1/3}$", fontsize=10)
    ax.grid(True, which="both", color="#e2e8f0", lw=0.6)
    ax.legend(fontsize=8, frameon=False, loc="lower left")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    return fig
