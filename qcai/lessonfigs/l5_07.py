"""Figures for L5-07 Measurements and instruments."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

PRIORS = [("|+⟩ (x = 1, z = 0)", math.pi / 2), ("tilted up (θ = 45°)", math.pi / 4), ("tilted down (θ = 120°)", 2 * math.pi / 3)]
EPS = [round(0.1 * k, 1) for k in range(11)]
COL = {"prior": "#7c3aed", "plus": "#3b82f6", "minus": "#f59e0b", "avg": "#ef4444", "grid": "#cbd5e1"}


def weak_update(theta: float, eps: float) -> dict:
    """Lueders instrument of E_pm = (I pm eps Z)/2 on the pure state with Bloch vector (sin t, 0, cos t)."""
    x, z = math.sin(theta), math.cos(theta)
    c = math.sqrt(max(1 - eps ** 2, 0.0))
    pp, pm = (1 + eps * z) / 2, (1 - eps * z) / 2
    plus = (c * x / (1 + eps * z), (z + eps) / (1 + eps * z))
    minus = (c * x / (1 - eps * z), (z - eps) / (1 - eps * z))
    avg = (c * x, z)
    return {"p_plus": pp, "p_minus": pm, "plus": plus, "minus": minus, "avg": avg, "coherence": c}


def weak_measurement():
    """Bloch-disk explorer: prior state (menu), strength eps (slider), conditioned and average states, probabilities."""
    fig = make_subplots(rows=1, cols=2, column_widths=[0.55, 0.45], horizontal_spacing=0.16,
                        subplot_titles=("Bloch disk (x, z)", "Outcome chances and coherence"))
    t = np.linspace(0, 2 * math.pi, 121)
    fig.add_trace(go.Scatter(x=np.sin(t).round(4).tolist(), y=np.cos(t).round(4).tolist(), mode="lines",
                             line=dict(color=COL["grid"]), hoverinfo="skip", showlegend=False), 1, 1)
    per = 6
    for g, (name, th) in enumerate(PRIORS):
        u = weak_update(th, EPS[0])
        vis = g == 0
        sl = g == 0
        fig.add_trace(go.Scatter(x=[round(math.sin(th), 4)], y=[round(math.cos(th), 4)], mode="markers",
                                 marker=dict(size=13, color=COL["prior"], symbol="diamond"), name="state before",
                                 legendgroup="prior", showlegend=sl, visible=vis), 1, 1)
        fig.add_trace(go.Scatter(x=[u["plus"][0], u["minus"][0]], y=[u["plus"][1], u["minus"][1]], mode="lines",
                                 line=dict(color="#94a3b8", dash="dot"), hoverinfo="skip", showlegend=False, visible=vis), 1, 1)
        fig.add_trace(go.Scatter(x=[u["plus"][0]], y=[u["plus"][1]], mode="markers", marker=dict(size=12, color=COL["plus"]),
                                 name="after outcome +", legendgroup="plus", showlegend=sl, visible=vis), 1, 1)
        fig.add_trace(go.Scatter(x=[u["minus"][0]], y=[u["minus"][1]], mode="markers", marker=dict(size=12, color=COL["minus"]),
                                 name="after outcome −", legendgroup="minus", showlegend=sl, visible=vis), 1, 1)
        fig.add_trace(go.Scatter(x=[u["avg"][0]], y=[u["avg"][1]], mode="markers", marker=dict(size=11, color=COL["avg"]),
                                 name="average (no record)", legendgroup="avg", showlegend=sl, visible=vis), 1, 1)
        fig.add_trace(go.Bar(x=["p(+)", "p(−)", "coherence<br>√(1−ε²)"], y=[u["p_plus"], u["p_minus"], u["coherence"]],
                             marker_color=[COL["plus"], COL["minus"], COL["avg"]], showlegend=False, visible=vis,
                             hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 2)
    idx = [1 + g * per + k for g in range(len(PRIORS)) for k in (1, 2, 3, 4, 5)]
    steps = []
    for e in EPS:
        xs, ys = [], []
        for _, th in PRIORS:
            u = weak_update(th, e)
            r = lambda v: round(v, 4)  # noqa: E731
            xs += [[r(u["plus"][0]), r(u["minus"][0])], [r(u["plus"][0])], [r(u["minus"][0])], [r(u["avg"][0])],
                   ["p(+)", "p(−)", "coherence<br>√(1−ε²)"]]
            ys += [[r(u["plus"][1]), r(u["minus"][1])], [r(u["plus"][1])], [r(u["minus"][1])], [r(u["avg"][1])],
                   [r(u["p_plus"]), r(u["p_minus"]), r(u["coherence"])]]
        steps.append(dict(method="restyle", label=f"{e:.1f}", args=[{"x": xs, "y": ys}, idx]))
    ntr = 1 + per * len(PRIORS)
    buttons = []
    for g, (name, _) in enumerate(PRIORS):
        vis = [True] + [gg == g for gg in range(len(PRIORS)) for _ in range(per)]
        buttons.append(dict(method="restyle", label=name, args=[{"visible": vis}, list(range(ntr))]))
    fig.update_xaxes(range=[-1.15, 1.15], title="x", constrain="domain", dtick=0.5, row=1, col=1)
    fig.update_yaxes(range=[-1.15, 1.15], title="z", scaleanchor="x", constrain="domain", dtick=0.5, row=1, col=1)
    fig.update_xaxes(tickangle=0, row=1, col=2)
    fig.update_yaxes(range=[0, 1.05], title="value", row=1, col=2)
    fig.update_layout(template="plotly_white",
                      updatemenus=[dict(buttons=buttons, active=0, x=0, xanchor="left", type="dropdown")],
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="strength ε = "))])
    return frame(fig, height=600, stack=True, xticks_lines=2)


def effects_as_arrows():
    """Qubit effects E = a (I + m . sigma) drawn as weighted arrows a m in the Bloch x-z disk; they balance at 0."""
    sets = [
        ("Projective Z", [(0.5, (0, 1), "$E_0 = |0\\rangle\\langle 0|$"), (0.5, (0, -1), "$E_1 = |1\\rangle\\langle 1|$")]),
        ("Trine (three outcomes)", [(1 / 3, (math.sin(2 * math.pi * k / 3), math.cos(2 * math.pi * k / 3)), f"$E_{k}$")
                                    for k in range(3)]),
        ("Weak Z, $\\varepsilon = 0.3$", [(0.5, (0, 0.3), "$E_+$"), (0.5, (0, -0.3), "$E_-$")]),
    ]
    cols = ["#7c3aed", "#06b6d4", "#f59e0b"]
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.6))
    t = np.linspace(0, 2 * math.pi, 300)
    for ax, (name, effs) in zip(axes, sets):
        ax.plot(np.sin(t), np.cos(t), color="#cbd5e1", lw=1)
        ax.axhline(0, color="#e2e8f0", lw=0.8)
        ax.axvline(0, color="#e2e8f0", lw=0.8)
        tot = np.zeros(2)
        for k, (a, m, lab) in enumerate(effs):
            m = np.array(m, dtype=float)
            ax.annotate("", xy=tuple(m), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=cols[k], lw=2.2))
            off = 0.2 * m / max(np.linalg.norm(m), 1e-9)
            ha = "left" if m[0] > 0.1 else ("right" if m[0] < -0.1 else "center")
            ax.text(m[0] + off[0] + (0.08 if ha == "center" else 0), m[1] + off[1], f"{lab}\n$a = {a:.2f}$".replace("0.33", "1/3").replace("0.50", "1/2"),
                    fontsize=9, color=cols[k], ha=ha if ha != "center" else "left", va="center")
            tot += a * m
        assert np.allclose(tot, 0) and abs(sum(a for a, _, _ in effs) - 1) < 1e-12
        ax.plot([0], [0], "o", color="#1e1b4b", ms=4)
        ax.set_title(name, fontsize=10)
        ax.set_aspect("equal")
        ax.set_xlim(-1.6, 1.6)
        ax.set_ylim(-1.45, 1.45)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.text(1.5, -1.35, "x", fontsize=9, color="#475569", ha="right")
        ax.text(-0.08, 1.3, "z", fontsize=9, color="#475569", ha="right")
    fig.suptitle("Each effect $E = a(I + m\\cdot\\sigma)$ is an arrow $m$ with weight $a$; completeness means "
                 "$\\sum a = 1$ and $\\sum a\\,m = 0$", fontsize=10)
    fig.tight_layout()
    return fig
