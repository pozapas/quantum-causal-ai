"""Figures for L5-08 Bell correlations and the CHSH test.

Convention: polarizer angles, A(t) = cos(2t) Z + sin(2t) X, E(a, b) = v cos 2(a - b) for the Werner state
v |Phi+><Phi+| + (1 - v) I/4, and S = E(a0,b0) + E(a0,b1) + E(a1,b0) - E(a1,b1).
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

VIS = [1.0, 0.85, 0.75, 0.70]
PHIS = [7.5 * k for k in range(13)]                    # 0 to 90 degrees, includes 22.5 and 67.5
SQ2 = math.sqrt(2)


def s_value(phi_deg: float, v: float = 1.0) -> float:
    p = math.radians(phi_deg)
    a0, a1, b0, b1 = 0.0, 2 * p, p, -p
    E = lambda a, b: v * math.cos(2 * (a - b))  # noqa: E731
    return E(a0, b0) + E(a0, b1) + E(a1, b0) - E(a1, b1)


assert abs(s_value(22.5) - 2 * SQ2) < 1e-12


def _rays(phi_deg: float):
    """Polarizer directions as lines through the origin: Alice (a0, a1) and Bob (b0, b1), None-separated."""
    p = math.radians(phi_deg)
    out = []
    for group in ((0.0, 2 * p), (p, -p)):
        xs, ys = [], []
        for t in group:
            xs += [round(-math.cos(t), 4), round(math.cos(t), 4), None]
            ys += [round(-math.sin(t), 4), round(math.sin(t), 4), None]
        out.append((xs, ys))
    return out


def chsh_explorer():
    """Slider: the angle family a0 = 0, a1 = 2 phi, b0 = phi, b1 = -phi. Menu: Werner visibility v."""
    fig = make_subplots(rows=1, cols=2, column_widths=[0.4, 0.6], horizontal_spacing=0.14,
                        subplot_titles=("Polarizer settings", "CHSH value S(φ)"))
    t = np.linspace(0, 2 * math.pi, 121)
    fig.add_trace(go.Scatter(x=np.cos(t).round(4).tolist(), y=np.sin(t).round(4).tolist(), mode="lines",
                             line=dict(color="#e2e8f0"), hoverinfo="skip", showlegend=False), 1, 1)
    (ax_, ay_), (bx_, by_) = _rays(PHIS[3])
    fig.add_trace(go.Scatter(x=ax_, y=ay_, mode="lines", line=dict(color="#7c3aed", width=4), name="Alice: a₀, a₁"), 1, 1)
    fig.add_trace(go.Scatter(x=bx_, y=by_, mode="lines", line=dict(color="#06b6d4", width=4, dash="dash"),
                             name="Bob: b₀, b₁"), 1, 1)
    fine = np.linspace(0, 90, 181)
    for y0, nm, col, dash in ((2, "local bound ±2", "#3b82f6", "dash"), (2 * SQ2, "Tsirelson ±2√2", "#f59e0b", "dot")):
        for sgn, show in ((1, True), (-1, False)):
            fig.add_trace(go.Scatter(x=[0, 90], y=[sgn * y0, sgn * y0], mode="lines", line=dict(color=col, dash=dash, width=2),
                                     name=nm, legendgroup=nm, showlegend=show, hoverinfo="skip"), 1, 2)
    first = len(fig.data)
    for g, v in enumerate(VIS):
        fig.add_trace(go.Scatter(x=fine.round(2).tolist(), y=[round(s_value(f, v), 4) for f in fine], mode="lines",
                                 line=dict(color="#ef4444", width=3), name="S(φ) for chosen v", legendgroup="S",
                                 showlegend=g == 0, visible=g == 0,
                                 hovertemplate="φ = %{x}°<br>S = %{y:.3f}<extra></extra>"), 1, 2)
        s0 = s_value(PHIS[3], v)
        fig.add_trace(go.Scatter(x=[PHIS[3]], y=[round(s0, 4)], mode="markers+text", text=[f"S = {s0:.3f}"],
                                 textposition="top right", marker=dict(size=12, color="#ef4444"), showlegend=False,
                                 visible=g == 0, hoverinfo="skip"), 1, 2)
    n = len(fig.data)
    markers = [first + 2 * g + 1 for g in range(len(VIS))]
    steps = []
    for ph in PHIS:
        (ax_, ay_), (bx_, by_) = _rays(ph)
        xs, ys, txt = [ax_, bx_], [ay_, by_], [None, None]
        for v in VIS:
            s = s_value(ph, v)
            xs.append([ph])
            ys.append([round(s, 4)])
            txt.append([f"S = {s:.3f}"])
        steps.append(dict(method="restyle", label=f"{ph:g}°", args=[{"x": xs, "y": ys, "text": txt}, [1, 2] + markers]))
    buttons = []
    for g, v in enumerate(VIS):
        vis = [True] * first + [gg == g for gg in range(len(VIS)) for _ in range(2)]
        assert len(vis) == n
        lab = f"visibility v = {v:.2f}" + ("" if v * 2 * SQ2 > 2 else " (no violation)")
        buttons.append(dict(method="restyle", label=lab, args=[{"visible": vis}, list(range(n))]))
    fig.update_xaxes(range=[-1.3, 1.3], visible=False, row=1, col=1)
    fig.update_yaxes(range=[-1.3, 1.3], visible=False, scaleanchor="x", scaleratio=1, row=1, col=1)
    fig.update_xaxes(title="φ (degrees)", range=[0, 90], dtick=22.5, tickangle=0, row=1, col=2)
    fig.update_yaxes(title="S", range=[-3.3, 3.6], dtick=1, row=1, col=2)
    fig.update_layout(template="plotly_white",
                      updatemenus=[dict(buttons=buttons, active=0, x=0, xanchor="left", type="dropdown")],
                      sliders=[dict(active=3, steps=steps, currentvalue=dict(prefix="φ = "))])
    return frame(fig, height=600, stack=True)


def bounds_and_experiment():
    """Left: nested ranges of S (local, quantum, no-signaling). Right: the Hensen et al. (2015) result."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.5), gridspec_kw=dict(width_ratios=[1.35, 1]))
    rows = [("no-signaling\n(PR box)", 4, "#e2e8f0"), ("quantum\n(Tsirelson)", 2 * SQ2, "#fde68a"), ("local\n(CHSH)", 2, "#bfdbfe")]
    for k, (name, b, col) in enumerate(rows):
        ax1.barh(k, 2 * b, left=-b, height=0.6, color=col, edgecolor="#475569", lw=0.8)
        ax1.text(-4.45, k, name, ha="right", va="center", fontsize=9, color="#1e1b4b")
        ax1.text(b + 0.08, k, f"{b:.3f}".rstrip("0").rstrip("."), ha="left", va="center", fontsize=9, color="#475569")
    ax1.axvline(0, color="#94a3b8", lw=0.6)
    ax1.set_xlim(-4.5, 5.0)
    ax1.set_ylim(-0.6, 2.6)
    ax1.set_yticks([])
    ax1.set_xlabel("range of $S$ allowed")
    ax1.set_title("Each class of models allows a wider range of $S$", fontsize=10)
    for s in ("top", "right", "left"):
        ax1.spines[s].set_visible(False)

    S, err = 2.42, 0.20
    ax2.axhspan(-2, 2, color="#bfdbfe", alpha=0.5, lw=0)
    ax2.axhline(2, color="#3b82f6", ls="--", lw=1.2)
    ax2.axhline(2 * SQ2, color="#f59e0b", ls=":", lw=1.5)
    ax2.errorbar([0], [S], yerr=[err], fmt="o", color="#ef4444", capsize=6, lw=2, ms=7)
    ax2.text(0.08, S, "$S = 2.42 \\pm 0.20$\n245 trials, $p = 0.039$", va="center", fontsize=9, color="#ef4444")
    ax2.text(-0.48, 2.05, "local bound 2", fontsize=8.5, color="#3b82f6", va="bottom")
    ax2.text(-0.48, 2 * SQ2 + 0.04, "Tsirelson $2\\sqrt{2}$", fontsize=8.5, color="#b45309", va="bottom")
    ax2.set_xlim(-0.5, 0.9)
    ax2.set_ylim(1.5, 3.2)
    ax2.set_xticks([])
    ax2.set_ylabel("$S$")
    ax2.set_title("Loophole-free test, Delft 2015", fontsize=10)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
