"""Figures and the single source of numbers for L7-10 Open problems and critical synthesis.

Two computations carry the lesson:
  * the claim audit: two-qubit Pauli correlation triples of common causes fill the tetrahedron T_cc and those
    of direct causes the dual tetrahedron T_dc (L7-05); their overlap is the octahedron |c1|+|c2|+|c3| <= 1,
    which holds exactly half of each tetrahedron's volume;
  * the cut inflation of the triangle network for the noisy perfectly correlated distribution
    P_v = v * (000 or 111 with probability 1/2 each) + (1 - v) * uniform, which is feasible iff v <= 1/2.
"""
from __future__ import annotations

import itertools
import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.optimize import linprog

from qcai.viz import frame

T_CC = np.array([[-1, -1, -1], [-1, 1, 1], [1, -1, 1], [1, 1, -1]], dtype=float)   # common-cause vertices
T_CE = -T_CC                                                                         # direct-cause vertices
AUDIT_SEED = 314
AUDIT_POINTS = 4000
SHOTS = (25, 100, 400, 1600)


# ----------------------------------------------------------------------------- claim audit
def in_octahedron(c: np.ndarray) -> np.ndarray:
    return np.abs(c).sum(axis=-1) <= 1


def in_tetra(c: np.ndarray, verts: np.ndarray) -> np.ndarray:
    """Membership in T_cc (facets 1 - c1 - c2 - c3 >= 0, 1 - c1 + c2 + c3 >= 0, 1 + c1 - c2 + c3 >= 0,
    1 + c1 + c2 - c3 >= 0) or in T_dc = -T_cc (the same facets evaluated at -c)."""
    c = c if np.allclose(verts, T_CC) else -c
    x, y, zz = c[..., 0], c[..., 1], c[..., 2]
    f = np.stack([1 - x - y - zz, 1 - x + y + zz, 1 + x - y + zz, 1 + x + y - zz], axis=-1)
    return (f >= -1e-12).all(axis=-1)


def uniform_in(verts: np.ndarray, m: int, rng) -> np.ndarray:
    """Uniform points in a tetrahedron: Dirichlet(1, 1, 1, 1) weights on its vertices."""
    w = rng.dirichlet(np.ones(4), size=m)
    return w @ verts


def classify(c_hat: np.ndarray) -> np.ndarray:
    """+1 'common cause' (in T_cc, outside the octahedron), -1 'direct cause', 0 'undetermined'."""
    cc = in_tetra(c_hat, T_CC) & ~in_octahedron(c_hat)
    ce = in_tetra(c_hat, T_CE) & ~in_octahedron(c_hat)
    return np.where(cc, 1, np.where(ce, -1, 0))


def audit(shots=SHOTS, m: int = AUDIT_POINTS, seed: int = AUDIT_SEED) -> dict:
    """Uniform common-cause triples; N shots per Pauli basis; fractions correct / undetermined / wrong."""
    rng = np.random.default_rng(seed)
    c = uniform_in(T_CC, m, rng)
    exact = classify(c)
    out = {"exact_correct": float((exact == 1).mean()), "exact_wrong": float((exact == -1).mean()), "rows": []}
    for n in shots:
        k = rng.binomial(n, (1 + c) / 2)                 # outcomes with ab = +1 in each basis
        lab = classify(2 * k / n - 1)
        out["rows"].append((n, float((lab == 1).mean()), float((lab == 0).mean()), float((lab == -1).mean())))
    return out


# ----------------------------------------------------------------------------- cut inflation of the triangle
def noisy_ghz(v: float) -> np.ndarray:
    """P(a, b, c) for the mixture of the perfectly correlated distribution and the uniform one."""
    P = np.full((2, 2, 2), (1 - v) / 8)
    P[0, 0, 0] += v / 2
    P[1, 1, 1] += v / 2
    return P


def cut_inflation_slack(v: float) -> float:
    """Smallest t >= 0 such that some Q(A2, B1, C1) matches Q(A2,B1) = P(A,B), Q(B1,C1) = P(B,C) and
    Q(A2,C1) = P(A)P(C) entry by entry up to t (a linear program; t = 0 means the cut inflation is feasible)."""
    P = noisy_ghz(v)
    PAB, PBC = P.sum(axis=2), P.sum(axis=0)
    PA, PC = P.sum(axis=(1, 2)), P.sum(axis=(0, 1))
    idx = list(itertools.product((0, 1), repeat=3))           # variables q_abc, then t
    rows, rhs = [], []
    def add(mask, target):
        row = [1.0 if mask(*k) else 0.0 for k in idx]
        rows.append(row + [-1.0]); rhs.append(target)           # sum - t <= target
        rows.append([-x for x in row] + [-1.0]); rhs.append(-target)   # -sum - t <= -target
    for a, b in itertools.product((0, 1), repeat=2):
        add(lambda x, y, z, a=a, b=b: x == a and y == b, PAB[a, b])
        add(lambda x, y, z, a=a, b=b: y == a and z == b, PBC[a, b])
        add(lambda x, y, z, a=a, b=b: x == a and z == b, PA[a] * PC[b])
    A_eq = [[1.0] * 8 + [0.0]]
    res = linprog(c=[0.0] * 8 + [1.0], A_ub=rows, b_ub=rhs, A_eq=A_eq, b_eq=[1.0], bounds=[(0, None)] * 9, method="highs")
    return float(res.x[-1])


def construction(v: float) -> np.ndarray:
    """An explicit Q(A2, B1, C1) for v <= 1/2: A2, C1 fair and independent; B1 copies A2 when A2 = C1, else a
    fair coin picks A2 or C1; then B1 is flipped with probability r = 1/2 - v."""
    r = 0.5 - v
    Q = np.zeros((2, 2, 2))
    for a, cc in itertools.product((0, 1), repeat=2):
        pb = {a: 1.0} if a == cc else {a: 0.5, cc: 0.5}
        for b, w in pb.items():
            Q[a, b, cc] += 0.25 * w * (1 - r)
            Q[a, 1 - b, cc] += 0.25 * w * r
    return Q


def threshold(tol: float = 1e-6) -> float:
    lo, hi = 0.0, 1.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if cut_inflation_slack(mid) <= 1e-9:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ----------------------------------------------------------------------------- figures
def inflation_explorer():
    """Slider over v: the disagreement budget of the cut inflation, and the LP slack against v."""
    vs = [round(0.05 * i, 2) for i in range(21)]
    slack = [cut_inflation_slack(v) for v in vs]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.45, 0.55], horizontal_spacing=0.16,
                        subplot_titles=("Disagreement budget", "Smallest violation (LP)"))
    cats = ["P(A₂≠B₁)<br>+ P(B₁≠C₁)", "P(A₂≠C₁)<br>required"]

    def bars(v):
        return [round(1 - v, 4), 0.5]

    fig.add_trace(go.Bar(x=cats, y=bars(vs[0]), marker_color=["#7c3aed", "#f59e0b"], showlegend=False,
                         text=[f"{b:.2f}" for b in bars(vs[0])], textposition="outside",
                         hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=vs, y=[round(s, 5) for s in slack], mode="lines+markers", name="LP slack t",
                             line=dict(color="#ef4444", width=3), hovertemplate="v = %{x:.2f}: t = %{y:.4f}<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=[0.5, 0.5], y=[0, max(slack) * 1.1], mode="lines", name="v = 1/2",
                             line=dict(color="#94a3b8", dash="dash"), hoverinfo="skip"), 1, 2)
    fig.add_trace(go.Scatter(x=[vs[0]], y=[slack[0]], mode="markers", marker=dict(size=13, color="#1e1b4b"),
                             showlegend=False, hoverinfo="skip"), 1, 2)
    steps = []
    for v, s in zip(vs, slack):
        b = bars(v)
        verdict = "incompatible with the triangle" if s > 1e-9 else "this test is silent"
        steps.append(dict(method="update", label=f"{v:.2f}",
                          args=[{"y": [b, [round(t, 5) for t in slack], [0, max(slack) * 1.1], [round(s, 5)]],
                                 "x": [cats, vs, [0.5, 0.5], [v]],
                                 "text": [[f"{x:.2f}" for x in b], None, None, None]},
                                {"title.text": f"Cut inflation of the triangle, v = {v:.2f}<br>Verdict: {verdict}"}]))
    fig.update_yaxes(range=[0, 1.15], title="probability", row=1, col=1)
    fig.update_xaxes(tickangle=0, row=1, col=1)
    fig.update_xaxes(title="correlation weight v", range=[-0.02, 1.02], dtick=0.25, row=1, col=2)
    fig.update_yaxes(title="slack t", range=[0, max(slack) * 1.15], row=1, col=2)
    fig.update_layout(template="plotly_white", title="Cut inflation of the triangle, v = 0.00<br>Verdict: this test is silent",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="v = "))])
    return frame(fig, height=560, stack=True, xticks_lines=2)


def audit_figure():
    """Finite-shot audit of 'perfect accuracy': outcome fractions against shots per basis."""
    a = audit()
    ns = [r[0] for r in a["rows"]]
    corr = [r[1] for r in a["rows"]]
    und = [r[2] for r in a["rows"]]
    wrong = [r[3] for r in a["rows"]]
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    x = np.arange(len(ns))
    ax.bar(x, corr, color="#7c3aed", width=0.6, label="identified correctly")
    ax.bar(x, und, bottom=corr, color="#cbd5e1", width=0.6, label="undetermined")
    ax.bar(x, wrong, bottom=np.add(corr, und), color="#ef4444", width=0.6, label="wrong structure")
    for i in range(len(ns)):
        ax.text(i, corr[i] / 2, f"{corr[i]:.3f}", ha="center", va="center", color="white", fontsize=9)
        ax.text(i, 1.02, f"wrong {wrong[i]:.3f}", ha="center", va="bottom", fontsize=9, color="#b91c1c")
    ax.axhline(0.5, color="#1e1b4b", lw=0.9, ls="--")
    ax.text(len(ns) - 0.55, 0.52, "exact-data limit 1/2", fontsize=9, color="#1e1b4b", ha="right")
    ax.set_xticks(x, [f"N = {n}" for n in ns])
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("fraction of common-cause models")
    ax.set_title(f"Pauli-correlation test on {AUDIT_POINTS} uniformly drawn common causes, N shots per basis", fontsize=10.5)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False, fontsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
