"""Figures for L3-06 Derivatives and gradients."""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

PX, PY = 2.0, -1.0
GRAD = np.array([4.0, -6.0])          # gradient of g(x, y) = x^2 + 3y^2 at (2, -1)


def gradient_compass():
    """Level curves of g = x^2 + 3y^2, the gradient at (2, -1), and a direction u chosen by slider."""
    angles = list(range(0, 360, 30))
    fig = make_subplots(rows=1, cols=2, column_widths=[0.52, 0.48], horizontal_spacing=0.14,
                        subplot_titles=("Level curves and directions", "Rate of change along u"))
    s = np.linspace(0, 2 * math.pi, 181)
    for k, c in enumerate((1, 4, 7, 10, 13)):
        a, b = math.sqrt(c), math.sqrt(c / 3)
        fig.add_trace(go.Scatter(x=(a * np.cos(s)).round(4).tolist(), y=(b * np.sin(s)).round(4).tolist(), mode="lines",
                                 line=dict(color="#7c3aed" if c == 7 else "#93c5fd", width=3 if c == 7 else 1.5),
                                 name="level curve g = 7" if c == 7 else "other level curves",
                                 showlegend=(c == 7 or k == 0), legendgroup="lev" if c != 7 else "seven",
                                 hovertemplate=f"g = {c}<extra></extra>"), 1, 1)
    gd = GRAD / np.linalg.norm(GRAD)
    fig.add_trace(go.Scatter(x=[PX, PX + 1.6 * gd[0]], y=[PY, PY + 1.6 * gd[1]], mode="lines+markers",
                             line=dict(color="#ef4444", width=4), marker=dict(size=[8, 1]), name="gradient direction",
                             hoverinfo="skip"), 1, 1)

    def u_of(deg):
        r = math.radians(deg)
        return math.cos(r), math.sin(r), float(GRAD @ np.array([math.cos(r), math.sin(r)]))

    ux, uy, d = u_of(angles[0])
    fig.add_trace(go.Scatter(x=[PX, round(PX + 1.2 * ux, 4)], y=[PY, round(PY + 1.2 * uy, 4)], mode="lines",
                             line=dict(color="#f59e0b", width=4), name="unit direction u", hoverinfo="skip"), 1, 1)
    xs = np.arange(0, 360.5, 2.0)
    ds = 4 * np.cos(np.radians(xs)) - 6 * np.sin(np.radians(xs))
    fig.add_trace(go.Scatter(x=xs.tolist(), y=ds.round(4).tolist(), mode="lines", line=dict(color="#f59e0b"),
                             showlegend=False, hovertemplate="angle %{x}°<br>D<sub>u</sub>g = %{y:.2f}<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=[angles[0]], y=[round(d, 4)], mode="markers", marker=dict(size=12, color="#f59e0b"),
                             showlegend=False, hovertemplate="angle %{x}°<br>D<sub>u</sub>g = %{y:.2f}<extra></extra>"), 1, 2)
    best = math.degrees(math.atan2(-6, 4)) % 360
    fig.add_trace(go.Scatter(x=[round(best, 2)], y=[round(math.sqrt(52), 4)], mode="markers",
                             marker=dict(size=10, color="#ef4444", symbol="diamond"), showlegend=False,
                             hovertemplate="maximum √52 ≈ 7.21 at %{x:.1f}°<extra></extra>"), 1, 2)
    steps = []
    for deg in angles:
        ux, uy, d = u_of(deg)
        steps.append(dict(method="restyle", label=f"{deg}°",
                          args=[{"x": [[PX, round(PX + 1.2 * ux, 4)], [deg]], "y": [[PY, round(PY + 1.2 * uy, 4)], [round(d, 4)]]},
                                [6, 8]]))
    fig.update_xaxes(range=[-4.2, 4.2], title="x", dtick=1, constrain="domain", row=1, col=1)
    fig.update_yaxes(range=[-3.2, 3.2], title="y", dtick=1, scaleanchor="x", constrain="domain", row=1, col=1)
    fig.update_xaxes(title="angle of u (degrees)", range=[0, 360], dtick=90, row=1, col=2)
    fig.update_yaxes(title="D<sub>u</sub>g = ∇g · u", range=[-8, 8], dtick=2, row=1, col=2)
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="angle of u = "))])
    return frame(fig, height=560, stack=True)


def difference_errors():
    """Error of forward and central difference quotients for sin at x = 1, against the step h (log-log)."""
    h = np.logspace(-13, 0, 200)
    x = 1.0
    exact = math.cos(x)
    fwd = np.abs((np.sin(x + h) - np.sin(x)) / h - exact)
    cen = np.abs((np.sin(x + h) - np.sin(x - h)) / (2 * h) - exact)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.loglog(h, fwd, color="#f59e0b", lw=1.8, label="forward  (f(x+h) - f(x)) / h")
    ax.loglog(h, cen, color="#7c3aed", lw=1.8, label="central  (f(x+h) - f(x-h)) / 2h")
    hh = np.logspace(-6, 0, 20)
    ax.loglog(hh, 0.5 * math.sin(x) * hh, ls="--", color="#f59e0b", lw=1, alpha=0.7)
    hc = np.logspace(-4, 0, 20)
    ax.loglog(hc, math.cos(x) / 6 * hc ** 2, ls="--", color="#7c3aed", lw=1, alpha=0.7)
    ax.text(1e-8, 6e-3, "slope 1: error ≈ (h/2)|f''|", color="#b45309", fontsize=9)
    ax.text(1e-3, 3e-10, "slope 2: error ≈ (h²/6)|f'''|", color="#6d28d9", fontsize=9)
    ax.text(1.5e-13, 3e-2, "rounding error\ngrows as h → 0", color="#475569", fontsize=9)
    ax.set_xlabel("step h")
    ax.set_ylabel("|difference quotient - cos(1)|")
    ax.set_title("Smaller h helps until floating-point rounding takes over", fontsize=11)
    ax.legend(loc="upper center", fontsize=9, frameon=False)
    ax.set_ylim(1e-12, 1)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
