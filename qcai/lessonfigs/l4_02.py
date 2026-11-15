"""Figures for L4-02 DAGs and d-separation.

The running graph has six nodes and six arrows: A -> C <- B -> E, C -> D -> F <- E.
d_separated() decides d-separation with the moralization criterion and is cross-checked against
networkx's own test in the lesson's code block.
"""
from __future__ import annotations

import itertools

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import plotly.graph_objects as go

from qcai.viz import frame

NODES = ["A", "B", "C", "D", "E", "F"]
EDGES = [("A", "C"), ("B", "C"), ("C", "D"), ("B", "E"), ("D", "F"), ("E", "F")]
POS = {"A": (0.0, 2.0), "B": (2.4, 2.0), "C": (1.2, 1.0), "E": (3.6, 1.0), "D": (1.2, -0.2), "F": (2.4, -1.2)}
PATHS_AE = [["A", "C", "B", "E"], ["A", "C", "D", "F", "E"]]


def graph() -> nx.DiGraph:
    g = nx.DiGraph()
    g.add_nodes_from(NODES)
    g.add_edges_from(EDGES)
    return g


def d_separated(g: nx.DiGraph, xs, ys, zs) -> bool:
    """True if xs and ys are d-separated by zs in g (moralize the ancestral graph, delete zs, test reachability)."""
    xs, ys, zs = set(xs), set(ys), set(zs)
    keep = set().union(*(nx.ancestors(g, v) | {v} for v in xs | ys | zs))
    h = g.subgraph(keep)
    m = nx.Graph(h.to_undirected())
    for v in h:
        ps = list(h.predecessors(v))
        m.add_edges_from(itertools.combinations(ps, 2))
    m.remove_nodes_from(zs)
    reach = set().union(*(nx.node_connected_component(m, x) for x in xs))
    return not (reach & ys)


def path_open(g: nx.DiGraph, path, zs) -> tuple[bool, str | None]:
    """Is this path open given zs?  Returns (open, first blocking node)."""
    zs = set(zs)
    for i in range(1, len(path) - 1):
        a, v, b = path[i - 1], path[i], path[i + 1]
        collider = g.has_edge(a, v) and g.has_edge(b, v)
        if collider:
            if not ({v} | nx.descendants(g, v)) & zs:
                return False, v
        elif v in zs:
            return False, v
    return True, None


G = graph()
assert d_separated(G, {"A"}, {"E"}, set())
assert not d_separated(G, {"A"}, {"E"}, {"D"})
assert d_separated(G, {"A"}, {"E"}, {"B", "D"})
assert not d_separated(G, {"A"}, {"E"}, {"F"})
assert [path_open(G, p, {"D"})[0] for p in PATHS_AE] == [True, False]

CHOICES = [(), ("C",), ("D",), ("F",), ("B",), ("B", "D"), ("B", "C")]


def dsep_explorer():
    """Pick a conditioning set; open paths between A and E light up and the title gives the verdict."""
    g = G
    fig = go.Figure()
    # open-path highlight traces (one per path), drawn under the arrows
    for _ in PATHS_AE:
        fig.add_trace(go.Scatter(x=[], y=[], mode="lines", line=dict(color="#f59e0b", width=14), opacity=0.55,
                                 hoverinfo="skip", showlegend=False))
    for a, b in EDGES:
        (x0, y0), (x1, y1) = POS[a], POS[b]
        fig.add_annotation(x=x0 + 0.78 * (x1 - x0), y=y0 + 0.78 * (y1 - y0), ax=x0 + 0.22 * (x1 - x0), ay=y0 + 0.22 * (y1 - y0),
                           xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2, arrowsize=1.4,
                           arrowwidth=2.2, arrowcolor="#475569", text="")
    xs = [POS[v][0] for v in NODES]
    ys = [POS[v][1] for v in NODES]

    def colors(zs):
        return ["#cbd5e1" if v in zs else ("#ede9fe" if v in ("A", "E") else "#ffffff") for v in NODES]

    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers+text", text=NODES, textfont=dict(size=18, color="#1e1b4b"),
                             marker=dict(size=40, color=colors(()), line=dict(color="#1e1b4b", width=2)),
                             hovertemplate="%{text}<extra></extra>", showlegend=False))

    def state(zs):
        hx, hy, notes = [], [], []
        for p in PATHS_AE:
            ok, where = path_open(g, p, zs)
            hx.append([POS[v][0] for v in p] if ok else [])
            hy.append([POS[v][1] for v in p] if ok else [])
            notes.append(f"{'-'.join(p)} {'open' if ok else 'blocked at ' + where}")
        sep = d_separated(g, {"A"}, {"E"}, set(zs))
        zt = "{" + ", ".join(zs) + "}" if zs else "∅"
        verdict = "d-separated" if sep else "d-connected"
        title = f"Given Z = {zt}: A and E are {verdict}<br>{notes[0]}<br>{notes[1]}"
        return hx, hy, title

    hx, hy, title = state(())
    for k in range(len(PATHS_AE)):
        fig.data[k].x, fig.data[k].y = hx[k], hy[k]
    buttons = []
    for zs in CHOICES:
        hx, hy, t = state(zs)
        lab = ",".join(zs) if zs else "∅"
        buttons.append(dict(method="update", label=lab,
                            args=[{"x": hx + [xs], "y": hy + [ys], "marker.color": ["#f59e0b", "#f59e0b", colors(zs)]},
                                  {"title.text": t}]))
    fig.update_layout(template="plotly_white", title=dict(text=title),
                      updatemenus=[dict(type="buttons", direction="right", buttons=buttons, showactive=True,
                                        x=0, xanchor="left", pad=dict(t=0, r=4))],
                      xaxis=dict(visible=False, range=[-0.5, 4.1]), yaxis=dict(visible=False, range=[-1.7, 2.5]))
    return frame(fig, height=520, axes=False, narrow_plot=330)


def junction_scatter():
    """Chain, fork and collider: correlation of X and Y overall and inside a thin slice of M."""
    g = np.random.default_rng(11)
    n = 4000
    e = lambda: g.normal(size=n)  # noqa: E731
    x1 = e(); m1 = x1 + e(); y1 = m1 + e()                 # chain  X -> M -> Y
    m2 = e(); x2 = m2 + e(); y2 = m2 + e()                 # fork   X <- M -> Y
    x3 = e(); y3 = e(); m3 = x3 + y3 + e()                 # collider X -> M <- Y
    data = [("chain  $X \\to M \\to Y$", x1, m1, y1), ("fork  $X \\leftarrow M \\to Y$", x2, m2, y2),
            ("collider  $X \\to M \\leftarrow Y$", x3, m3, y3)]
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.7))
    for ax, (name, x, m, y) in zip(axes, data):
        s = np.abs(m - np.median(m)) < 0.25
        ax.scatter(x, y, s=4, color="#cbd5e1", lw=0)
        ax.scatter(x[s], y[s], s=7, color="#7c3aed", lw=0)
        r_all = np.corrcoef(x, y)[0, 1]
        r_all = 0.0 if abs(r_all) < 0.005 else r_all
        r_in = np.corrcoef(x[s], y[s])[0, 1]
        ax.set_title(f"{name}\nall: r = {r_all:.2f}    slice of $M$: r = {r_in:.2f}", fontsize=10)
        ax.set_xlabel("$X$")
        ax.set_xlim(-4.5, 4.5)
        ax.set_ylim(-5.5, 5.5)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0].set_ylabel("$Y$")
    fig.suptitle("Grey: all samples.  Purple: samples with $M$ in a thin slice (conditioning on $M$).", fontsize=10)
    fig.tight_layout()
    return fig
