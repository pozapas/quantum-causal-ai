"""Figures for L6-03 Quantum DAGs and Markov assumptions.

The DAG is Fig. 5 of Barrett, Lorenz and Oreshkov: A1 -> A2, A1 -> A3, A2 -> A4, A3 -> A4, A1 -> A5, A4 -> A5.
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import plotly.graph_objects as go

from qcai.viz import frame

EDGES = [("A1", "A2"), ("A1", "A3"), ("A2", "A4"), ("A3", "A4"), ("A1", "A5"), ("A4", "A5")]
POS = {"A1": (0.0, 0.0), "A2": (1.0, 0.9), "A3": (1.0, -0.9), "A4": (2.0, 0.0), "A5": (3.0, 0.9)}
QUERIES = [("A2", "A3", ("A1",)), ("A2", "A3", ()), ("A2", "A3", ("A1", "A4")), ("A2", "A3", ("A1", "A5")),
           ("A1", "A4", ("A2", "A3")), ("A2", "A5", ("A1", "A4")), ("A3", "A5", ("A4",))]


def _descendants(n):
    out, stack = set(), [n]
    while stack:
        u = stack.pop()
        for a, b in EDGES:
            if a == u and b not in out:
                out.add(b)
                stack.append(b)
    return out


def _paths(x, y):
    nbr = {}
    for a, b in EDGES:
        nbr.setdefault(a, []).append(b)
        nbr.setdefault(b, []).append(a)
    res = []

    def walk(path):
        if path[-1] == y:
            res.append(list(path))
            return
        for v in nbr[path[-1]]:
            if v not in path:
                walk(path + [v])
    walk([x])
    return res


def active_paths(x, y, z):
    """Paths from x to y that are open given the conditioning set z (d-separation rules)."""
    z = set(z)
    out = []
    for p in _paths(x, y):
        ok = True
        for i in range(1, len(p) - 1):
            a, m, b = p[i - 1], p[i], p[i + 1]
            collider = (a, m) in EDGES and (b, m) in EDGES
            if collider:
                if not (m in z or (_descendants(m) & z)):
                    ok = False
            elif m in z:
                ok = False
        if ok:
            out.append(p)
    return out


def dsep_explorer():
    """Pick a d-separation query on the five-node DAG; open paths are drawn in red."""
    G = nx.DiGraph(EDGES)
    dsep = getattr(nx, "is_d_separator", None) or getattr(nx, "d_separated")
    fig = go.Figure()
    for a, b in EDGES:
        (x0, y0), (x1, y1) = POS[a], POS[b]
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", line=dict(color="#94a3b8", width=3),
                                 hoverinfo="skip", showlegend=False))
    n_base = len(EDGES)
    titles = []
    for k, (x, y, z) in enumerate(QUERIES):
        act = active_paths(x, y, z)
        sep = not act
        assert sep == dsep(G, {x}, {y}, set(z))
        xs, ys = [], []
        for p in act:
            for u, v in zip(p, p[1:]):
                xs += [POS[u][0], POS[v][0], None]
                ys += [POS[u][1], POS[v][1], None]
        fig.add_trace(go.Scatter(x=xs or [None], y=ys or [None], mode="lines", line=dict(color="#ef4444", width=7),
                                 opacity=0.75, hoverinfo="skip", showlegend=False, visible=(k == 0)))
        cols = ["#7c3aed" if n in (x, y) else ("#f59e0b" if n in z else "#e0f2fe") for n in POS]
        fig.add_trace(go.Scatter(x=[POS[n][0] for n in POS], y=[POS[n][1] for n in POS], mode="markers+text",
                                 marker=dict(size=40, color=cols, line=dict(color="#1e1b4b", width=2)),
                                 text=[n for n in POS], textfont=dict(size=15, color="#1e1b4b"), hoverinfo="skip",
                                 showlegend=False, visible=(k == 0)))
        zs = "{" + ", ".join(z) + "}" if z else "∅"
        verdict = "d-separated: every path blocked" if sep else f"not d-separated: {len(act)} open path" + ("s" if len(act) > 1 else "")
        titles.append(f"{x} and {y} given {zs}<br>{verdict}")
    buttons = []
    for k, (x, y, z) in enumerate(QUERIES):
        vis = [True] * n_base + [False] * (2 * len(QUERIES))
        vis[n_base + 2 * k] = vis[n_base + 2 * k + 1] = True
        zs = ",".join(z) if z else "∅"
        buttons.append(dict(method="update", label=f"{x}, {y} | {zs}", args=[{"visible": vis}, {"title.text": titles[k]}]))
    ann = []
    for a, b in EDGES:
        (x0, y0), (x1, y1) = POS[a], POS[b]
        d = math.hypot(x1 - x0, y1 - y0)
        f = 1 - 0.17 / d
        ann.append(dict(x=x0 + f * (x1 - x0), y=y0 + f * (y1 - y0), ax=x0 + 0.6 * (x1 - x0), ay=y0 + 0.6 * (y1 - y0),
                        xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1.4,
                        arrowwidth=2, arrowcolor="#475569", text=""))
    fig.update_layout(template="plotly_white", title=dict(text=titles[0]), annotations=ann,
                      updatemenus=[dict(type="dropdown", buttons=buttons, active=0, showactive=True)])
    fig.update_xaxes(visible=False, range=[-0.4, 3.4])
    fig.update_yaxes(visible=False, range=[-1.3, 1.3], scaleanchor="x")
    return frame(fig, height=480, axes=False)


def markov_spaces():
    """Which spaces each factor of the quantum Markov condition acts on, for the five-node DAG."""
    rows = [("ρ(A1)", ["A1 in"]), ("ρ(A2 | A1)", ["A2 in", "A1 out"]), ("ρ(A3 | A1)", ["A3 in", "A1 out"]),
            ("ρ(A4 | A2 A3)", ["A4 in", "A2 out", "A3 out"]), ("ρ(A5 | A1 A4)", ["A5 in", "A1 out", "A4 out"])]
    cols = [f"A{i} {s}" for i in range(1, 6) for s in ("in", "out")]
    M = np.array([[1 if c in r[1] else 0 for c in cols] for r in rows])
    fig, ax = plt.subplots(figsize=(9.2, 3.2))
    ax.imshow(M, cmap="Purples", vmin=0, vmax=1.6, aspect="auto")
    for i in range(len(rows)):
        for j in range(len(cols)):
            if M[i, j]:
                ax.text(j, i, "in" if cols[j].endswith("in") else "out", ha="center", va="center", fontsize=8, color="white")
    shared = [j for j, c in enumerate(cols) if M[:, j].sum() > 1]
    for j in shared:
        ax.add_patch(plt.Rectangle((j - 0.5, -0.5), 1, len(rows), fill=False, ec="#ef4444", lw=2))
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([c.replace(" ", "\n") for c in cols], fontsize=8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=9)
    ax.set_title("Spaces touched by each factor; red columns are shared, so those factors must commute", fontsize=10)
    fig.tight_layout()
    return fig
