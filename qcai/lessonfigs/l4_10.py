"""Figures for L4-10 Causal machine learning, transport, and fairness."""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

TAU = (1.0, 3.0)          # stratum effects tau(z), z = 0, 1
P_SRC = 0.5               # P(Z = 1) in the source
B_C, B_S, VAR_NS = 0.2, 0.8, 0.25


def mse_spurious(e):
    """Test MSE of the all-features predictor 0.2 X_c + 0.8 X_s when X_s := e Y + N_s."""
    return (1 - B_C - B_S * e) ** 2 + (1 - B_S * e) ** 2 + B_S ** 2 * VAR_NS


def transport_explorer():
    """Slider over the target share of stratum z = 1: composition bars and the transported ATE."""
    ps = [round(0.1 * k, 1) for k in range(11)]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.45, 0.55], horizontal_spacing=0.14,
                        subplot_titles=("Who is in each population", "Average effect in the target"))
    cats = ["z = 0<br>(effect 1)", "z = 1<br>(effect 3)"]
    fig.add_trace(go.Bar(x=cats, y=[1 - P_SRC, P_SRC], name="source mix", marker_color="#94a3b8",
                         hovertemplate="%{x}<br>share %{y:.2f}<extra>source</extra>"), 1, 1)
    p0 = 0.2
    fig.add_trace(go.Bar(x=cats, y=[1 - p0, p0], name="target mix", marker_color="#7c3aed",
                         hovertemplate="%{x}<br>share %{y:.2f}<extra>target</extra>"), 1, 1)
    grid = np.linspace(0, 1, 101)
    fig.add_trace(go.Scatter(x=grid.round(2).tolist(), y=(TAU[0] + (TAU[1] - TAU[0]) * grid).round(3).tolist(),
                             mode="lines", line=dict(color="#7c3aed"), name="transported ATE"), 1, 2)
    fig.add_trace(go.Scatter(x=[0, 1], y=[2, 2], mode="lines", line=dict(color="#94a3b8", dash="dash"),
                             name="source ATE = 2"), 1, 2)
    fig.add_trace(go.Scatter(x=[p0], y=[TAU[0] * (1 - p0) + TAU[1] * p0], mode="markers",
                             marker=dict(size=13, color="#7c3aed"), showlegend=False,
                             hovertemplate="target share %{x:.1f}<br>ATE %{y:.2f}<extra></extra>"), 1, 2)
    steps = []
    for p in ps:
        ate = TAU[0] * (1 - p) + TAU[1] * p
        steps.append(dict(method="restyle", label=f"{p:.1f}",
                          args=[{"y": [[round(1 - p, 2), p], [round(ate, 3)]], "x": [cats, [p]]}, [1, 4]]))
    fig.update_yaxes(range=[0, 1.05], title="share of population", row=1, col=1)
    fig.update_xaxes(tickangle=0, row=1, col=1)
    fig.update_xaxes(range=[0, 1], dtick=0.2, title="target share of z = 1", row=1, col=2)
    fig.update_yaxes(range=[0.8, 3.2], title="ATE", row=1, col=2)
    fig.update_layout(template="plotly_white", barmode="group",
                      sliders=[dict(active=ps.index(p0), steps=steps, currentvalue=dict(prefix="target share of z = 1: "))])
    return frame(fig, height=560, stack=True, xticks_lines=2)


def shift_explorer():
    """Slider over the test environment e: predictions against truth, and test MSE curves."""
    es = [round(-1 + 0.25 * k, 2) for k in range(13)]
    rng = np.random.default_rng(2)
    n = 160
    xc, ny, ns = rng.normal(0, 1, n), rng.normal(0, 1, n), rng.normal(0, 0.5, n)
    y = xc + ny
    fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.14,
                        subplot_titles=("Predictions in the test environment", "Test error against e"))
    fig.add_trace(go.Scatter(x=[-6, 6], y=[-6, 6], mode="lines", line=dict(color="#cbd5e1", dash="dot"),
                             hoverinfo="skip", showlegend=False), 1, 1)
    fig.add_trace(go.Scatter(x=y.round(3).tolist(), y=xc.round(3).tolist(), mode="markers", name="causal: X<sub>c</sub>",
                             marker=dict(size=6, color="#06b6d4", opacity=0.7), hoverinfo="skip"), 1, 1)

    def spur(e):
        return (B_C * xc + B_S * (e * y + ns)).round(3).tolist()
    e0 = 1.0
    fig.add_trace(go.Scatter(x=y.round(3).tolist(), y=spur(e0), mode="markers", name="all features",
                             marker=dict(size=6, color="#f59e0b", opacity=0.7), hoverinfo="skip"), 1, 1)
    grid = np.linspace(-1, 2, 121)
    fig.add_trace(go.Scatter(x=grid.round(3).tolist(), y=[1.0] * len(grid), mode="lines", line=dict(color="#06b6d4", width=3),
                             showlegend=False, hovertemplate="causal MSE 1<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=grid.round(3).tolist(), y=[round(mse_spurious(g), 4) for g in grid], mode="lines",
                             line=dict(color="#f59e0b", width=3), showlegend=False,
                             hovertemplate="e %{x:.2f}<br>MSE %{y:.2f}<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=[e0, e0], y=[1.0, mse_spurious(e0)], mode="markers",
                             marker=dict(size=12, color=["#06b6d4", "#f59e0b"]), showlegend=False,
                             hovertemplate="MSE %{y:.2f}<extra></extra>"), 1, 2)
    steps = []
    for e in es:
        steps.append(dict(method="restyle", label=f"{e:g}",
                          args=[{"y": [spur(e), [1.0, round(mse_spurious(e), 4)]], "x": [y.round(3).tolist(), [e, e]]},
                                [2, 5]]))
    fig.update_xaxes(range=[-5, 5], title="true Y", dtick=2, row=1, col=1)
    fig.update_yaxes(range=[-5, 5], title="prediction", dtick=2, row=1, col=1)
    fig.update_xaxes(range=[-1, 2], dtick=0.5, title="environment e (training e = 1)", row=1, col=2)
    fig.update_yaxes(range=[0, 6.2], title="mean squared error", row=1, col=2)
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=es.index(e0), steps=steps, currentvalue=dict(prefix="test environment e = "))])
    return frame(fig, height=560, stack=True)


def _logistic_fit(Z, t, iters=25):
    b = np.zeros(Z.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-Z @ b))
        b += np.linalg.solve(Z.T @ (Z * (p * (1 - p))[:, None]), Z.T @ (t - p))
    return 1 / (1 + np.exp(-Z @ b))


def _ols_predict(F, y, F_new):
    return F_new @ np.linalg.lstsq(F, y, rcond=None)[0]


def doubly_robust():
    """Plug-in, IPW and AIPW estimates of an ATE of 2 when each nuisance model is right or wrong."""
    rng = np.random.default_rng(3)
    n = 20_000
    z = rng.normal(0, 1, n)
    t = (rng.random(n) < 1 / (1 + np.exp(-1.5 * z))).astype(float)
    y = 2 * t + z + 0.5 * z ** 3 + rng.normal(0, 1, n)
    one = np.ones(n)
    props = {"right": _logistic_fit(np.column_stack([one, z]), t), "wrong": np.full(n, t.mean())}
    feats = {"right": np.column_stack([one, z, z ** 3]), "wrong": one[:, None]}
    rows, est = [], {"plug-in": [], "IPW": [], "AIPW": []}
    for om in ("right", "wrong"):
        F = feats[om]
        m1 = _ols_predict(F[t == 1], y[t == 1], F)
        m0 = _ols_predict(F[t == 0], y[t == 0], F)
        for pm in ("right", "wrong"):
            e = props[pm]
            rows.append(f"outcome {om}\npropensity {pm}")
            est["plug-in"].append(np.mean(m1 - m0))
            est["IPW"].append(np.mean(t * y / e - (1 - t) * y / (1 - e)))
            est["AIPW"].append(np.mean(m1 - m0 + t * (y - m1) / e - (1 - t) * (y - m0) / (1 - e)))
    fig, ax = plt.subplots(figsize=(9.6, 3.9))
    xs = np.arange(len(rows))
    for k, (name, col) in enumerate(zip(est, ("#94a3b8", "#f59e0b", "#7c3aed"))):
        vals = est[name]
        ax.bar(xs + (k - 1) * 0.26, vals, width=0.25, color=col, label=name)
        for x0, v in zip(xs + (k - 1) * 0.26, vals):
            ax.text(x0, v + 0.06, f"{v:.2f}", ha="center", fontsize=8, color="#1e1b4b")
    ax.axhline(2, color="#1e1b4b", lw=1.2, ls="--", label="true ATE = 2")
    ax.set_xticks(xs)
    ax.set_xticklabels(rows, fontsize=9)
    ax.set_ylabel("estimated ATE")
    ax.set_ylim(0, 5.2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=9, ncol=4)
    ax.set_title("AIPW stays near 2 if either the outcome model or the propensity model is right", fontsize=10)
    fig.tight_layout()
    return fig
