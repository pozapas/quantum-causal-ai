"""Figures for L5-10 Noise, encoding, and error correction.

Conventions: qubits are ordered q1 q2 q3 (then ancillas a1 a2) from left to right in kets and in the
Kronecker product; a bit flip is X, a phase flip is Z; flips hit each qubit independently with probability p.
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

# Gate list of the bit-flip code on five wires (0, 1, 2 data; 3, 4 ancillas).  The figure is drawn from it and
# syndrome_table() simulates it, so the drawing and the table cannot disagree.
ENCODE = [("cx", 0, 1), ("cx", 0, 2)]
SYNDROME = [("cx", 0, 3), ("cx", 1, 3), ("cx", 1, 4), ("cx", 2, 4)]


def _apply(state, gate, n=5):
    psi = state.reshape([2] * n).copy()
    if gate[0] == "cx":
        c, t = gate[1], gate[2]
        idx = [slice(None)] * n
        idx[c] = 1
        sub = psi[tuple(idx)]
        tt = t - (1 if t > c else 0)
        psi[tuple(idx)] = np.flip(sub, axis=tt)
    elif gate[0] in ("x", "z", "h"):
        q = gate[1]
        m = {"x": np.array([[0, 1], [1, 0]]), "z": np.array([[1, 0], [0, -1]]),
             "h": np.array([[1, 1], [1, -1]]) / math.sqrt(2)}[gate[0]]
        psi = np.moveaxis(np.tensordot(m, psi, axes=([1], [q])), 0, q)
    return psi.reshape(-1)


def syndrome_table(alpha=0.6, beta=0.8j):
    """Simulate encode, one X error (or none), syndrome extraction; return {error: (s1, s2)}.

    The ancilla outcomes are deterministic and the same for every alpha, beta."""
    out = {}
    for err in (None, 0, 1, 2):
        psi = np.zeros(32, dtype=complex)
        psi[0], psi[16] = alpha, beta                      # (alpha|0> + beta|1>) |0000>
        for g in ENCODE + ([("x", err)] if err is not None else []) + SYNDROME:
            psi = _apply(psi, g)
        p = np.abs(psi.reshape(8, 4)) ** 2
        anc = p.sum(axis=0)
        k = int(np.argmax(anc))
        assert abs(anc[k] - 1) < 1e-12                     # the syndrome is certain
        out["none" if err is None else f"X{err + 1}"] = (k >> 1, k & 1)
    return out


def logical_rate(p):
    return 3 * p ** 2 - 2 * p ** 3


def code_explorer():
    """Left: logical error rate 3p^2 - 2p^3 against p with Monte Carlo points. Right: chance of 0, 1, 2, 3 flips."""
    rng = np.random.default_rng(2024)
    grid = np.round(np.arange(0.0, 0.61, 0.05), 2)
    trials = 4000
    mc = [(rng.random((trials, 3)) < p).sum(axis=1).__ge__(2).mean() for p in grid]
    ps = np.linspace(0, 0.6, 121)
    fig = make_subplots(rows=1, cols=2, column_widths=[0.56, 0.44], horizontal_spacing=0.14,
                        subplot_titles=("Logical against physical error", "Number of flipped qubits"))
    fig.add_trace(go.Scatter(x=ps.round(4).tolist(), y=ps.round(4).tolist(), mode="lines",
                             line=dict(color="#94a3b8", dash="dash"), name="no code: p"), 1, 1)
    fig.add_trace(go.Scatter(x=ps.round(4).tolist(), y=logical_rate(ps).round(5).tolist(), mode="lines",
                             line=dict(color="#7c3aed", width=3), name="code: 3p² − 2p³"), 1, 1)
    fig.add_trace(go.Scatter(x=grid.tolist(), y=[round(float(m), 4) for m in mc], mode="markers",
                             marker=dict(color="#f59e0b", size=8), name="Monte Carlo"), 1, 1)

    def bars(p):
        return [round((1 - p) ** 3, 4), round(3 * p * (1 - p) ** 2, 4), round(3 * p ** 2 * (1 - p), 4), round(p ** 3, 4)]

    p0 = 0.1
    fig.add_trace(go.Scatter(x=[p0], y=[round(logical_rate(p0), 5)], mode="markers", showlegend=False,
                             marker=dict(color="#ef4444", size=13, line=dict(color="white", width=1)),
                             hovertemplate="p = %{x}<br>logical %{y:.4f}<extra></extra>"), 1, 1)
    fig.add_trace(go.Bar(x=["0", "1", "2", "3"], y=bars(p0), marker_color=["#06b6d4", "#06b6d4", "#ef4444", "#ef4444"],
                         showlegend=False, hovertemplate="%{x} flips: %{y:.4f}<extra></extra>"), 1, 2)
    steps = []
    for p in grid:
        steps.append(dict(method="restyle", label=f"{p:.2f}",
                          args=[{"x": [[float(p)], ["0", "1", "2", "3"]],
                                 "y": [[round(logical_rate(p), 5)], bars(p)]}, [3, 4]]))
    fig.update_xaxes(title="physical flip probability p", range=[0, 0.6], dtick=0.1, row=1, col=1)
    fig.update_yaxes(title="probability of logical error", range=[0, 0.6], row=1, col=1)
    fig.update_xaxes(title="flips (red: decoder fails)", row=1, col=2)
    fig.update_yaxes(title="probability", range=[0, 1], row=1, col=2)
    fig.update_layout(template="plotly_white", bargap=0.3,
                      sliders=[dict(active=2, steps=steps, currentvalue=dict(prefix="flip probability p = "))])
    return frame(fig, height=540, stack=True)


def _draw(ax, gates, wires, labels, title, boxes=()):
    n = len(labels)
    xmax = len(gates) + 1.4
    for w in range(n):
        ax.plot([0.2, xmax], [-w, -w], color="#475569", lw=1.2, zorder=1)
        ax.text(0.05, -w, labels[w], ha="right", va="center", fontsize=11)
    for (x0, x1, lab, color) in boxes:
        ax.add_patch(plt.Rectangle((x0, -n + 0.45), x1 - x0, n - 0.1, fc=color, ec="none", alpha=0.25, zorder=0))
        ax.text((x0 + x1) / 2, 0.75, lab, ha="center", va="bottom", fontsize=9.5, color="#475569")
    for i, g in enumerate(gates):
        x = i + 1
        if g[0] == "cx":
            c, t = -g[1], -g[2]
            ax.plot([x, x], [c, t], color="#1e1b4b", lw=1.5, zorder=2)
            ax.plot(x, c, "o", color="#1e1b4b", ms=6, zorder=3)
            ax.add_patch(plt.Circle((x, t), 0.2, fc="white", ec="#1e1b4b", lw=1.5, zorder=3))
            ax.plot([x - 0.2, x + 0.2], [t, t], color="#1e1b4b", lw=1.5, zorder=4)
            ax.plot([x, x], [t - 0.2, t + 0.2], color="#1e1b4b", lw=1.5, zorder=4)
        elif g[0] in ("x", "h", "err", "zerr"):
            q = -g[1]
            fc = {"x": "#cffafe", "h": "#dbeafe", "err": "#fee2e2", "zerr": "#fee2e2"}[g[0]]
            txt = {"x": "X", "h": "H", "err": "X", "zerr": "Z"}[g[0]]
            ec = "#ef4444" if g[0] in ("err", "zerr") else "#1e1b4b"
            ax.add_patch(plt.Rectangle((x - 0.26, q - 0.26), 0.52, 0.52, fc=fc, ec=ec, lw=1.4, zorder=3))
            ax.text(x, q, txt, ha="center", va="center", fontsize=11, zorder=4, color=ec)
        elif g[0] == "m":
            q = -g[1]
            ax.add_patch(plt.Rectangle((x - 0.3, q - 0.26), 0.6, 0.52, fc="#f1f5f9", ec="#1e1b4b", lw=1.4, zorder=3))
            ax.text(x, q, "M", ha="center", va="center", fontsize=10, zorder=4)
    ax.set_xlim(-0.9, xmax + 0.1)
    ax.set_ylim(-n + 0.3, 1.35)
    ax.set_title(title, fontsize=11)
    ax.set_aspect("equal")
    ax.axis("off")


def code_circuits():
    """Bit-flip code (encode, an X error, syndrome extraction) and the Hadamard-conjugated phase-flip encoder."""
    table = syndrome_table()
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.4, 3.9), gridspec_kw=dict(width_ratios=[1.55, 1]))
    gates = ENCODE + [("err", 1)] + SYNDROME + [("m", 3), ("m", 4)]
    labs = [r"$\alpha|0\rangle+\beta|1\rangle$", r"$|0\rangle$", r"$|0\rangle$", r"$a_1{:}\ |0\rangle$", r"$a_2{:}\ |0\rangle$"]
    _draw(a, gates, 5, labs, "Bit-flip code: encode, error on qubit 2, measure parities",
          boxes=[(0.6, 2.4, "encode", "#ddd6fe"), (2.6, 3.4, "noise", "#fecaca"), (3.6, 7.4, "syndrome", "#a5f3fc")])
    rows = "   ".join(f"{k}: {v[0]}{v[1]}" for k, v in table.items())
    a.text(4.5, -5.0, "simulated syndromes  " + rows, ha="center", va="center", fontsize=9.5, color="#475569")
    gates2 = ENCODE + [("h", 0), ("h", 1), ("h", 2)]
    _draw(b, gates2, 3, [r"$\alpha|0\rangle+\beta|1\rangle$", r"$|0\rangle$", r"$|0\rangle$"],
          "Phase-flip code: same encoder, then H",
          boxes=[(0.6, 2.4, "encode", "#ddd6fe"), (2.6, 5.4, "change basis", "#bfdbfe")])
    b.text(3.0, -2.95, r"$\alpha|{+}{+}{+}\rangle+\beta|{-}{-}{-}\rangle$", ha="center", fontsize=11)
    fig.tight_layout()
    return fig
