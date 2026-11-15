"""Figures and exact computations for L4-08 Causal discovery and its limits.

Shared by the lesson text, the Manim scenes and the figures:
  * d-separation oracle and a small PC algorithm (skeleton search, collider orientation, Meek rules 1-3)
  * the five-node example V -> W, V -> X, W -> Y, X -> Y, Y -> Z used for the PC animation
  * the faithfulness example X -> Y -> Z plus X -> Z, linear Gaussian, unit noise variances
"""
from __future__ import annotations

import itertools
import math

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import plotly.graph_objects as go
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from plotly.subplots import make_subplots
from scipy import stats

from qcai.viz import frame

# ----------------------------------------------------------------------------------------------
# d-separation and the PC algorithm
# ----------------------------------------------------------------------------------------------
def dsep_oracle(dag: nx.DiGraph):
    """Return indep(a, b, S): True when a and b are d-separated by S in dag."""
    def indep(a, b, S):
        return nx.is_d_separator(dag, {a}, {b}, set(S))
    return indep


def pc(nodes, indep):
    """PC algorithm with a conditional-independence test `indep(a, b, S)`.

    Returns a dict with the removal log [(a, b, S)], separating sets, the oriented colliders, the Meek
    orientations [(rule, a, b)], and the final pattern as (directed edges, undirected edges).
    """
    adj = {v: set(nodes) - {v} for v in nodes}
    sep, log = {}, []
    level = 0
    while any(len(adj[a]) - 1 >= level for a in nodes):
        for a in nodes:
            for b in sorted(adj[a]):
                if b not in adj[a]:
                    continue
                others = sorted(adj[a] - {b})
                if len(others) < level:
                    continue
                for S in itertools.combinations(others, level):
                    if indep(a, b, S):
                        adj[a].discard(b)
                        adj[b].discard(a)
                        sep[frozenset((a, b))] = set(S)
                        log.append((a, b, tuple(S)))
                        break
        level += 1
    directed, undirected = set(), {frozenset((a, b)) for a in nodes for b in adj[a]}
    colliders = []
    for y in nodes:                                   # unshielded x - y - z with y not in sepset(x, z)
        for x, z in itertools.combinations(sorted(adj[y]), 2):
            if z in adj[x]:
                continue
            if y not in sep.get(frozenset((x, z)), set()):
                colliders.append((x, y, z))
                for s in (x, z):
                    undirected.discard(frozenset((s, y)))
                    directed.add((s, y))
    meek = []
    changed = True

    def is_adj(p, q):
        return q in adj[p]

    while changed:
        changed = False
        for e in sorted(undirected, key=sorted):
            for (p, q) in (tuple(sorted(e)), tuple(sorted(e))[::-1]):
                # rule 1: r -> p - q, r and q not adjacent  =>  p -> q
                r1 = any((r, p) in directed and not is_adj(r, q) for r in nodes if r not in (p, q))
                # rule 2: p -> r -> q and p - q  =>  p -> q
                r2 = any((p, r) in directed and (r, q) in directed for r in nodes)
                # rule 3: p - r -> q, p - s -> q, r and s not adjacent, p - q  =>  p -> q
                rs = [r for r in nodes if frozenset((p, r)) in undirected and (r, q) in directed]
                r3 = any(not is_adj(r, s) for r, s in itertools.combinations(rs, 2))
                rule = 1 if r1 else 2 if r2 else 3 if r3 else 0
                if rule:
                    undirected.discard(e)
                    directed.add((p, q))
                    meek.append((rule, p, q))
                    changed = True
                    break
            if changed:
                break
    return {"log": log, "sep": sep, "colliders": colliders, "meek": meek,
            "directed": sorted(directed), "undirected": sorted(tuple(sorted(e)) for e in undirected)}


def skeleton_and_v(dag: nx.DiGraph):
    """Skeleton and unshielded colliders of a DAG (the Verma-Pearl invariants)."""
    skel = frozenset(frozenset(e) for e in dag.edges)
    v = frozenset((frozenset((a, c)), b) for b in dag for a, c in itertools.combinations(sorted(dag.predecessors(b)), 2)
                  if not dag.has_edge(a, c) and not dag.has_edge(c, a))
    return skel, v


def cpdag(dag: nx.DiGraph):
    """The pattern of dag's Markov equivalence class, computed by PC with a d-separation oracle."""
    out = pc(sorted(dag.nodes), dsep_oracle(dag))
    return out["directed"], out["undirected"]


# five-node example for the PC animation
PC_NODES = ["V", "W", "X", "Y", "Z"]
PC_EDGES = [("V", "W"), ("V", "X"), ("W", "Y"), ("X", "Y"), ("Y", "Z")]
PC_DAG = nx.DiGraph(PC_EDGES)
PC_RUN = pc(PC_NODES, dsep_oracle(PC_DAG))
assert PC_RUN["colliders"] == [("W", "Y", "X")]
assert PC_RUN["directed"] == [("W", "Y"), ("X", "Y"), ("Y", "Z")]
assert PC_RUN["undirected"] == [("V", "W"), ("V", "X")]
assert PC_RUN["meek"] == [(1, "Y", "Z")]
assert PC_RUN["log"] == [("V", "Z", ("Y",)), ("W", "X", ("V",)), ("W", "Z", ("Y",)), ("X", "Z", ("Y",)),
                         ("V", "Y", ("W", "X"))]

# ----------------------------------------------------------------------------------------------
# Faithfulness: X -> Y -> Z and X -> Z with weights a, b, c and unit-variance Gaussian noise
# ----------------------------------------------------------------------------------------------
A_W, B_W = 0.8, 1.0
C_CANCEL = -A_W * B_W                      # c = -ab makes Cov(X, Z) = 0


def cov_xyz(c, a=A_W, b=B_W):
    """Covariance of (X, Y, Z) for X = N_X, Y = aX + N_Y, Z = cX + bY + N_Z."""
    Bm = np.array([[0, 0, 0], [a, 0, 0], [c, b, 0]], float)
    Ainv = np.linalg.inv(np.eye(3) - Bm)
    return Ainv @ Ainv.T


def corr_xz(c):
    S = cov_xyz(c)
    return S[0, 2] / math.sqrt(S[0, 0] * S[2, 2])


def pcorr_xz_y(c):
    P = np.linalg.inv(cov_xyz(c))
    return -P[0, 2] / math.sqrt(P[0, 0] * P[2, 2])


assert abs(corr_xz(C_CANCEL)) < 1e-12
assert abs(cov_xyz(0.3)[0, 2] - (0.3 + A_W * B_W)) < 1e-12        # Cov(X, Z) = c + ab
assert abs(corr_xz(0.0) - 0.8 / math.sqrt(0.64 + 2)) < 1e-12

N_DEMO = 200
THRESH = stats.norm.ppf(0.975) / math.sqrt(N_DEMO - 3)            # smallest |r| a 5% test reliably flags (roughly)


def pc_threshold(c, thresh=THRESH):
    """PC on (X, Y, Z) when the test calls |population partial correlation| < thresh independent."""
    S = cov_xyz(c)

    def indep(a, b, cond):
        idx = [a, b] + list(cond)
        P = np.linalg.inv(S[np.ix_(idx, idx)])
        r = -P[0, 1] / math.sqrt(P[0, 0] * P[1, 1])
        return abs(r) < thresh
    return pc([0, 1, 2], indep)


_cancel = pc_threshold(C_CANCEL)
assert _cancel["directed"] == [(0, 1), (2, 1)] and _cancel["undirected"] == []      # X -> Y <- Z, wrong


# ----------------------------------------------------------------------------------------------
# Static figure: the four orientations of a two-edge skeleton
# ----------------------------------------------------------------------------------------------
def _draw_graph(ax, edges, pos, color, undirected=()):
    for n, (x, y) in pos.items():
        ax.add_patch(plt.Circle((x, y), 0.17, fill=True, fc="white", ec=color, lw=2, zorder=3))
        ax.text(x, y, n, ha="center", va="center", fontsize=12, color=color, zorder=4)
    for a, b in edges:
        ax.add_patch(FancyArrowPatch(pos[a], pos[b], arrowstyle="-|>", mutation_scale=16, lw=2, color=color,
                                     shrinkA=12, shrinkB=12, zorder=2))
    for a, b in undirected:
        ax.add_patch(FancyArrowPatch(pos[a], pos[b], arrowstyle="-", lw=2, color=color, shrinkA=12, shrinkB=12, zorder=2))


def equivalence_classes():
    """Chain, reverse chain and fork share one class; the collider is alone. Bottom row: the patterns."""
    pos = {"X": (0, 0), "Y": (0.75, 0.0), "Z": (1.5, 0)}
    graphs = [("chain", [("X", "Y"), ("Y", "Z")]), ("reverse chain", [("Z", "Y"), ("Y", "X")]),
              ("fork", [("Y", "X"), ("Y", "Z")]), ("collider", [("X", "Y"), ("Z", "Y")])]
    for name, e in graphs:                            # verify the claim drawn in the figure
        d = nx.DiGraph(e)
        ind_m = nx.is_d_separator(d, {"X"}, {"Z"}, set())
        ind_c = nx.is_d_separator(d, {"X"}, {"Z"}, {"Y"})
        assert (ind_m, ind_c) == ((True, False) if name == "collider" else (False, True))
    fig, axes = plt.subplots(2, 4, figsize=(9.6, 3.9), gridspec_kw={"height_ratios": [1, 0.9]})
    cols = ["#7c3aed", "#7c3aed", "#7c3aed", "#ef4444"]
    for ax, (name, e), col in zip(axes[0], graphs, cols):
        _draw_graph(ax, e, pos, col)
        ax.set_title(name, fontsize=10, color=col)
    for ax in axes.ravel():
        ax.set_xlim(-0.3, 1.8)
        ax.set_ylim(-0.7, 0.35)
        ax.set_aspect("equal")
        ax.axis("off")
    d1, u1 = cpdag(nx.DiGraph(graphs[0][1]))
    d2, u2 = cpdag(nx.DiGraph(graphs[3][1]))
    assert d1 == [] and u1 == [("X", "Y"), ("Y", "Z")] and d2 == [("X", "Y"), ("Z", "Y")]
    _draw_graph(axes[1][1], d1, pos, "#7c3aed", u1)
    _draw_graph(axes[1][3], d2, pos, "#ef4444", u2)
    axes[1][1].set_title("pattern: X - Y - Z", fontsize=10, color="#7c3aed")
    axes[1][3].set_title("pattern: X → Y ← Z", fontsize=10, color="#ef4444")
    axes[1][0].text(0.75, -0.1, "implies: X, Z dependent\nand  $X \\perp\\!\\!\\!\\perp Z \\mid Y$", ha="center", va="center",
                    fontsize=10, color="#7c3aed")
    axes[1][2].text(0.75, -0.1, "three DAGs,\none pattern", ha="center", va="center", fontsize=10, color="#7c3aed")
    axes[1][3].text(0.75, -0.45, "implies: $X \\perp\\!\\!\\!\\perp Z$, and\nX, Z dependent given Y", ha="center", va="center",
                    fontsize=10, color="#ef4444")
    box = FancyBboxPatch((0.012, 0.03), 0.715, 0.86, boxstyle="round,pad=0.005", transform=fig.transFigure,
                         fc="none", ec="#a78bfa", lw=1.2, ls="--")
    fig.patches.append(box)
    fig.suptitle("Same skeleton X - Y - Z: three orientations are Markov equivalent, the collider is not", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    return fig


# ----------------------------------------------------------------------------------------------
# Interactive: faithfulness and its near violations
# ----------------------------------------------------------------------------------------------
def faithfulness_explorer():
    """Slider over the direct weight c; left: correlations, right: what PC concludes at n = 200."""
    cs = [round(-1.6 + 0.1 * i, 1) for i in range(20)]          # -1.6 ... 0.3
    grid = np.linspace(-1.6, 0.3, 191)
    fig = make_subplots(rows=1, cols=2, column_widths=[0.58, 0.42], horizontal_spacing=0.12,
                        subplot_titles=("Correlations as c varies", "What PC outputs (n = 200)"))
    fig.add_trace(go.Scatter(x=[-1.6, 0.3, 0.3, -1.6], y=[-THRESH, -THRESH, THRESH, THRESH], fill="toself", mode="lines",
                             fillcolor="rgba(148,163,184,0.25)", line=dict(width=0), name="too weak to detect",
                             hoverinfo="skip"), 1, 1)
    fig.add_trace(go.Scatter(x=grid.round(3).tolist(), y=[round(corr_xz(c), 4) for c in grid], mode="lines",
                             line=dict(color="#7c3aed", width=3), name="corr(X, Z)"), 1, 1)
    fig.add_trace(go.Scatter(x=grid.round(3).tolist(), y=[round(pcorr_xz_y(c), 4) for c in grid], mode="lines",
                             line=dict(color="#06b6d4", width=3, dash="dash"), name="partial corr(X, Z | Y)"), 1, 1)
    c0 = cs[-1]
    fig.add_trace(go.Scatter(x=[c0, c0], y=[round(corr_xz(c0), 4), round(pcorr_xz_y(c0), 4)], mode="markers",
                             marker=dict(size=11, color=["#7c3aed", "#06b6d4"]), showlegend=False,
                             hovertemplate="c = %{x}<br>%{y:.3f}<extra></extra>"), 1, 1)
    pos = {0: (0.0, 0.0), 1: (0.5, 0.8), 2: (1.0, 0.0)}
    names = {0: "X", 1: "Y", 2: "Z"}
    pairs = [(0, 1), (1, 2), (0, 2)]

    def edge_xy(p, q, directed_pq):
        (x0, y0), (x1, y1) = pos[p], pos[q]
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        s = 0.11
        return [round(x0 + ux * s, 4), round(x1 - ux * s, 4)], [round(y0 + uy * s, 4), round(y1 - uy * s, 4)]

    def edges_for(c):
        out = pc_threshold(c)
        xs, ys, sizes = [], [], []
        for p, q in pairs:
            if (p, q) in out["directed"]:
                x, y = edge_xy(p, q, True)
                xs.append(x), ys.append(y), sizes.append([0, 16])
            elif (q, p) in out["directed"]:
                x, y = edge_xy(q, p, True)
                xs.append(x), ys.append(y), sizes.append([0, 16])
            elif (min(p, q), max(p, q)) in out["undirected"]:
                x, y = edge_xy(p, q, False)
                xs.append(x), ys.append(y), sizes.append([0, 0])
            else:
                xs.append([None, None]), ys.append([None, None]), sizes.append([0, 0])
        return xs, ys, sizes
    xs, ys, sizes = edges_for(c0)
    for k in range(3):
        fig.add_trace(go.Scatter(x=xs[k], y=ys[k], mode="lines+markers", line=dict(color="#1e1b4b", width=3),
                                 marker=dict(symbol="arrow", angleref="previous", size=sizes[k], color="#1e1b4b"),
                                 showlegend=False, hoverinfo="skip"), 1, 2)
    fig.add_trace(go.Scatter(x=[pos[i][0] for i in range(3)], y=[pos[i][1] for i in range(3)], mode="markers+text",
                             text=[names[i] for i in range(3)], textfont=dict(size=16, color="#1e1b4b"),
                             marker=dict(size=34, color="white", line=dict(color="#7c3aed", width=2)),
                             showlegend=False, hoverinfo="skip"), 1, 2)
    steps = []
    for c in cs:
        xs, ys, sizes = edges_for(c)
        steps.append(dict(method="restyle", label=f"{c:.1f}",
                          args=[{"x": [[c, c]] + xs, "y": [[round(corr_xz(c), 4), round(pcorr_xz_y(c), 4)]] + ys,
                                 "marker.size": [11] + sizes}, [3, 4, 5, 6]]))
    fig.update_xaxes(title="direct weight c",range=[-1.65, 0.35], dtick=0.4,
                     row=1, col=1)
    fig.update_yaxes(title="correlation", range=[-0.85, 0.85], dtick=0.4, row=1, col=1)
    fig.update_xaxes(range=[-0.25, 1.25], visible=False, row=1, col=2)
    fig.update_yaxes(range=[-0.3, 1.1], visible=False, row=1, col=2)
    fig.update_layout(template="plotly_white", title="True graph: X → Y → Z and X → Z (a = 0.8, b = 1).<br>"
                      "At c = -0.8 the paths cancel and corr(X, Z) = 0.",
                      sliders=[dict(active=len(cs) - 1, steps=steps, currentvalue=dict(prefix="direct weight c = "))])
    return frame(fig, height=560, stack=True)
