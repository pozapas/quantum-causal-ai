"""Figures for L4-03 Confounders, mediators, and colliders.

Combined linear SCM (independent standard normal noises):
    Z := N_Z,  X := Z + N_X,  M := 1.5 X + N_M,  Y := X + 2 M + 2 Z + N_Y,  C := X + Y + N_C.
The total effect of X on Y is 1 + 1.5 * 2 = 4 and the direct effect is 1.
"""
from __future__ import annotations

import itertools
import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

from qcai.viz import frame

NAMES = ["Z", "X", "M", "Y", "C"]
IDX = {v: k for k, v in enumerate(NAMES)}
COEF = {("Z", "X"): 1.0, ("X", "M"): 1.5, ("X", "Y"): 1.0, ("M", "Y"): 2.0, ("Z", "Y"): 2.0, ("X", "C"): 1.0, ("Y", "C"): 1.0}
TOTAL, DIRECT = 1.0 + 1.5 * 2.0, 1.0


def covariance() -> np.ndarray:
    B = np.zeros((5, 5))
    for (a, b), w in COEF.items():
        B[IDX[b], IDX[a]] = w
    A = np.linalg.inv(np.eye(5) - B)
    return A @ A.T


SIGMA = covariance()


def ols_x(adjust) -> float:
    """Population regression coefficient of X when Y is regressed on X and the adjustment set."""
    reg = [IDX["X"]] + [IDX[v] for v in adjust]
    beta = np.linalg.solve(SIGMA[np.ix_(reg, reg)], SIGMA[reg, IDX["Y"]])
    return float(beta[0])


SETS = [(), ("Z",), ("Z", "M"), ("Z", "C"), ("M",), ("C",), ("Z", "M", "C")]
EST = {s: ols_x(s) for s in SETS}
assert abs(EST[()] - 5) < 1e-12 and abs(EST[("Z",)] - TOTAL) < 1e-12 and abs(EST[("Z", "M")] - DIRECT) < 1e-12
assert abs(EST[("Z", "C")] + 1 / 6) < 1e-12 and abs(EST[("Z", "M", "C")]) < 1e-12


# selection on a sum: A, B iid N(0, 1), keep S = A + B > t
def selected_corr(t: float) -> float:
    """corr(A, B | A + B > t) = (v - 2) / (v + 2) with v = Var(S | S > t), S ~ N(0, 2)."""
    s = math.sqrt(2.0)
    v = stats.truncnorm.var((t / s), np.inf, loc=0, scale=s)
    return float((v - 2) / (v + 2))


RHO0 = selected_corr(0.0)
assert abs(RHO0 + 1 / (math.pi - 1)) < 1e-10          # closed form at t = 0: -1/(pi - 1) = -0.467

POS = {"Z": (1.0, 2.0), "X": (0.0, 1.0), "Y": (2.0, 1.0), "M": (1.0, 0.25), "C": (1.0, -0.6)}
ROLE = {"Z": "confounder", "M": "mediator", "C": "collider"}


def adjustment_explorer():
    """Pick an adjustment set; the population regression coefficient of X is compared with the total effect 4."""
    fig = make_subplots(rows=1, cols=2, column_widths=[0.48, 0.52], horizontal_spacing=0.12,
                        subplot_titles=("Graph (grey = adjusted for)", "Coefficient of X in the regression"))
    for (a, b) in COEF:
        (x0, y0), (x1, y1) = POS[a], POS[b]
        fig.add_annotation(x=x0 + 0.75 * (x1 - x0), y=y0 + 0.75 * (y1 - y0), ax=x0 + 0.25 * (x1 - x0), ay=y0 + 0.25 * (y1 - y0),
                           xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1.3,
                           arrowwidth=2, arrowcolor="#475569", text="")
    xs = [POS[v][0] for v in NAMES]
    ys = [POS[v][1] for v in NAMES]

    def colors(s):
        return ["#cbd5e1" if v in s else ("#ede9fe" if v in ("X", "Y") else "#ffffff") for v in NAMES]

    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers+text", text=NAMES, textfont=dict(size=16, color="#1e1b4b"),
                             marker=dict(size=34, color=colors(()), line=dict(color="#1e1b4b", width=2)),
                             customdata=[ROLE.get(v, "treatment" if v == "X" else "outcome") for v in NAMES],
                             hovertemplate="%{text}: %{customdata}<extra></extra>", showlegend=False), 1, 1)
    labels = ["none", "Z", "Z,M", "Z,C", "M", "C", "Z,M,C"]
    vals = [round(EST[s], 4) for s in SETS]
    fig.add_trace(go.Bar(x=labels, y=vals, marker_color=["#cbd5e1"] * len(SETS), name="estimate",
                         text=[f"{v:.2f}" for v in vals], textposition="outside", cliponaxis=False,
                         hovertemplate="adjust for %{x}: %{y:.3f}<extra></extra>", showlegend=False), 1, 2)
    fig.add_trace(go.Scatter(x=[labels[0], labels[-1]], y=[TOTAL, TOTAL], mode="lines", name="total effect 4",
                             line=dict(color="#f59e0b", width=3, dash="dash")), 1, 2)
    fig.add_trace(go.Scatter(x=[labels[0], labels[-1]], y=[DIRECT, DIRECT], mode="lines", name="direct effect 1",
                             line=dict(color="#7c3aed", width=2, dash="dot")), 1, 2)

    def bar_colors(k):
        return ["#3b82f6" if j == k else "#cbd5e1" for j in range(len(SETS))]

    def title(k):
        s = SETS[k]
        txt = "nothing" if not s else "{" + ", ".join(s) + "}"
        good = "estimates the total effect" if abs(EST[s] - TOTAL) < 1e-9 else (
            "estimates the direct effect only" if abs(EST[s] - DIRECT) < 1e-9 else "is biased for both effects")
        return f"Adjust for {txt}: coefficient {EST[s]:.2f}<br>{good}"

    buttons = [dict(method="update", label=labels[k],
                    args=[{"marker.color": [colors(SETS[k]), bar_colors(k)]}, {"title.text": title(k)}, [0, 1]])
               for k in (0, 1, 2, 3, 6)]
    fig.data[0].marker.color = colors(SETS[1])
    fig.data[1].marker.color = bar_colors(1)
    fig.update_xaxes(visible=False, range=[-0.4, 2.4], row=1, col=1)
    fig.update_yaxes(visible=False, range=[-1.0, 2.4], row=1, col=1)
    fig.update_yaxes(title="coefficient of X", range=[-1, 6], row=1, col=2)
    fig.update_xaxes(tickangle=0, row=1, col=2)
    fig.update_layout(template="plotly_white", title=dict(text=title(1)),
                      updatemenus=[dict(type="buttons", direction="right", buttons=buttons, active=1, showactive=True,
                                        x=0, xanchor="left", pad=dict(t=0, r=4))])
    return frame(fig, height=560, stack=True)


def berkson_figure():
    """Selection on a sum: A and B independent; keeping A + B > 0 makes them negatively correlated."""
    g = np.random.default_rng(5)
    a, b = g.normal(size=(2, 3000))
    keep = a + b > 0
    ts = np.linspace(-3, 2, 101)
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9))
    ax = axes[0]
    ax.scatter(a[~keep], b[~keep], s=5, color="#cbd5e1", lw=0)
    ax.scatter(a[keep], b[keep], s=5, color="#ef4444", lw=0)
    xx = np.linspace(-4, 4, 2)
    ax.plot(xx, -xx, color="#1e1b4b", lw=1.5)
    r = np.corrcoef(a[keep], b[keep])[0, 1]
    ax.set_title(f"Keep $A + B > 0$ (red): sample r = {r:.2f}\npopulation value $-1/(\\pi - 1) = {RHO0:.3f}$", fontsize=10)
    ax.set_xlabel("$A$")
    ax.set_ylabel("$B$")
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.set_aspect("equal")
    ax = axes[1]
    ax.plot(ts, [selected_corr(t) for t in ts], color="#ef4444", lw=2.2)
    ax.axhline(0, color="#94a3b8", lw=0.8)
    ax.scatter([0], [RHO0], color="#1e1b4b", zorder=3, s=25)
    ax.set_xlabel("selection threshold $t$")
    ax.set_ylabel("corr$(A, B \\mid A + B > t)$")
    ax.set_title("A stricter threshold gives a stronger\nnegative correlation", fontsize=10)
    ax.set_ylim(-1, 0.1)
    for a_ in axes:
        for sp in ("top", "right"):
            a_.spines[sp].set_visible(False)
    fig.tight_layout()
    return fig


_ = itertools
