"""Figures and exact model numbers for L4-07 Identification before estimation.

The constants here are the single source for the lesson text, the Manim scenes and the figures.
Two structural models share one observational joint P(x, y) and disagree about P(y | do(x)):
  model A  X -> Y with no confounding:  X ~ P(x),  Y drawn from P(y | x)
  model B  no effect of X on Y:  hidden U ~ P(y),  X drawn from P(x | y = U),  Y = U
The mixture "lambda A + (1 - lambda) B" (a hidden coin picks the mechanism) keeps the same joint.
"""
from __future__ import annotations

from fractions import Fraction as F

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

# ----------------------------------------------------------------------------------------------
# The observationally equivalent pair
# ----------------------------------------------------------------------------------------------
PX1 = F(1, 2)                                 # P(X = 1)
PY1_GIVEN_X = {0: F(1, 5), 1: F(4, 5)}        # P(Y = 1 | X = x)


def joint_A():
    """Exact P(X = x, Y = y) in model A, by enumerating its mechanisms."""
    out = {}
    for x in (0, 1):
        px = PX1 if x else 1 - PX1
        for y in (0, 1):
            py = PY1_GIVEN_X[x] if y else 1 - PY1_GIVEN_X[x]
            out[(x, y)] = px * py
    return out


def py1():
    """P(Y = 1) under the shared joint."""
    j = joint_A()
    return j[(0, 1)] + j[(1, 1)]


def joint_B():
    """Exact P(X = x, Y = y) in model B: U ~ P(y), X ~ P(x | y = U), Y = U."""
    j = joint_A()
    pu1 = py1()
    out = {}
    for u in (0, 1):
        pu = pu1 if u else 1 - pu1
        for x in (0, 1):
            px_given_u = j[(x, u)] / (j[(0, u)] + j[(1, u)])
            y = u
            out[(x, y)] = out.get((x, y), F(0)) + pu * px_given_u
    for k in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        out.setdefault(k, F(0))
    return out


def do_A(x):
    """P(Y = 1 | do(X = x)) in model A: the Y mechanism is untouched, so it is P(Y = 1 | X = x)."""
    return PY1_GIVEN_X[x]


def do_B(x):
    """P(Y = 1 | do(X = x)) in model B: Y = U and U keeps its distribution, so it is P(Y = 1)."""
    return py1()


def do_mix(x, lam):
    """P(Y = 1 | do(X = x)) when a hidden coin uses model A with probability lam, model B otherwise."""
    return lam * do_A(x) + (1 - lam) * do_B(x)


def bounds(x):
    """No-assumption bounds on P(Y = 1 | do(X = x)): [P(x, Y=1), P(x, Y=1) + P(X != x)]."""
    j = joint_A()
    lo = j[(x, 1)]
    return lo, lo + (j[(1 - x, 0)] + j[(1 - x, 1)])


ACE_A = do_A(1) - do_A(0)        # 3/5
ACE_B = do_B(1) - do_B(0)        # 0
assert joint_A() == joint_B()
assert ACE_A == F(3, 5) and ACE_B == 0 and py1() == F(1, 2)
assert bounds(1) == (F(2, 5), F(9, 10)) and bounds(0) == (F(1, 10), F(3, 5))


def se_contrast(n):
    """Standard error of the observed contrast  p(Y=1|X=1) - p(Y=1|X=0)  with n records (large n)."""
    p1, p0 = float(PY1_GIVEN_X[1]), float(PY1_GIVEN_X[0])
    return float(np.sqrt(p1 * (1 - p1) / (n * float(PX1)) + p0 * (1 - p0) / (n * (1 - float(PX1)))))


assert abs(se_contrast(1) - 0.8) < 1e-12    # SE = 0.8 / sqrt(n)

# ----------------------------------------------------------------------------------------------
# The worked example: a fully observed confounded model  Z -> X -> Y,  Z -> Y
# ----------------------------------------------------------------------------------------------
PZ1 = F(2, 5)
PX1_GIVEN_Z = {0: F(1, 5), 1: F(7, 10)}


def py1_given_xz(x, z):
    return F(1, 10) + F(1, 2) * x + F(3, 10) * z


def we_do(x):
    """Truncated factorization: P(Y=1 | do(X=x)) = sum_z P(z) P(Y=1 | x, z)."""
    return sum((PZ1 if z else 1 - PZ1) * py1_given_xz(x, z) for z in (0, 1))


def we_obs(x):
    """Observed P(Y=1 | X=x) = sum_z P(z | x) P(Y=1 | x, z)."""
    num = den = F(0)
    for z in (0, 1):
        pz = PZ1 if z else 1 - PZ1
        pxz = PX1_GIVEN_Z[z] if x else 1 - PX1_GIVEN_Z[z]
        num += pz * pxz * py1_given_xz(x, z)
        den += pz * pxz
    return num / den


assert we_do(1) == F(18, 25) and we_do(0) == F(11, 50)          # 0.72 and 0.22
assert we_obs(1) == F(81, 100) and we_obs(0) == F(4, 25)        # 0.81 and 0.16
assert we_do(1) - we_do(0) == F(1, 2) and we_obs(1) - we_obs(0) == F(13, 20)


def f2(q) -> str:
    """Format an exact fraction as a short decimal string for the text and the scenes."""
    s = f"{float(q):.2f}".rstrip("0").rstrip(".")
    return s if s not in ("-0",) else "0"


# ----------------------------------------------------------------------------------------------
# Interactive: a family of models with one joint and a sliding causal answer
# ----------------------------------------------------------------------------------------------
def equivalent_models():
    """Slider over the causal share lambda; the observational bars never move, do(X=x) bars do."""
    lams = [i / 10 for i in range(11)]
    j = joint_A()
    cats = ["X=0<br>Y=0", "X=0<br>Y=1", "X=1<br>Y=0", "X=1<br>Y=1"]
    obs = [float(j[k]) for k in [(0, 0), (0, 1), (1, 0), (1, 1)]]
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.14,
                        subplot_titles=("Observational P(X, Y)", "P(Y=1 | do(X=x))"))
    fig.add_trace(go.Bar(x=cats, y=obs, marker_color="#7c3aed", name="observational joint",
                         hovertemplate="%{x}: %{y:.2f}<extra></extra>"), 1, 1)
    xs = ["do(X=0)", "do(X=1)"]

    def dvals(lam):
        return [round(float(do_mix(0, F(lam).limit_denominator(10))), 4),
                round(float(do_mix(1, F(lam).limit_denominator(10))), 4)]
    lo = [float(bounds(0)[0]), float(bounds(1)[0])]
    hi = [float(bounds(0)[1]), float(bounds(1)[1])]
    fig.add_trace(go.Scatter(x=xs, y=[(a + b) / 2 for a, b in zip(lo, hi)], mode="markers",
                             marker=dict(size=1, color="#94a3b8"),
                             error_y=dict(type="data", array=[(b - a) / 2 for a, b in zip(lo, hi)], color="#94a3b8",
                                          thickness=10, width=0),
                             name="no-assumption bounds", hoverinfo="skip"), 1, 2)
    fig.add_trace(go.Bar(x=xs, y=dvals(1.0), marker_color="#06b6d4", width=0.45, name="model with share λ",
                         hovertemplate="%{x}: %{y:.2f}<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=xs, y=[float(PY1_GIVEN_X[0]), float(PY1_GIVEN_X[1])], mode="markers",
                             marker=dict(symbol="diamond", size=12, color="#f59e0b"), name="seen P(Y=1 | X=x)",
                             hovertemplate="%{x}: seen %{y:.2f}<extra></extra>"), 1, 2)
    steps = []
    for lam in lams:
        steps.append(dict(method="restyle", label=f"{lam:.1f}", args=[{"y": [dvals(lam)]}, [2]]))
    fig.update_yaxes(range=[0, 1], dtick=0.2, title="probability", row=1, col=1)
    fig.update_yaxes(range=[0, 1], dtick=0.2, row=1, col=2)
    fig.update_xaxes(tickangle=0)
    fig.update_layout(template="plotly_white", barmode="overlay",
                      title="One joint, many causal answers:<br>effect P(Y=1|do(1)) - P(Y=1|do(0)) = 0.6 λ",
                      sliders=[dict(active=10, steps=steps, currentvalue=dict(prefix="causal share λ = "))])
    return frame(fig, height=540, stack=True, xticks_lines=2)


# ----------------------------------------------------------------------------------------------
# Static figure: estimation error shrinks, identification error does not
# ----------------------------------------------------------------------------------------------
def simulate_we(n, reps, rng):
    """Naive and backdoor plug-in estimates of the effect in the worked-example model."""
    z = rng.random((reps, n)) < float(PZ1)
    x = rng.random((reps, n)) < np.where(z, float(PX1_GIVEN_Z[1]), float(PX1_GIVEN_Z[0]))
    py = 0.1 + 0.5 * x + 0.3 * z
    y = rng.random((reps, n)) < py

    def mean_where(mask):
        c = mask.sum(1)
        return (y & mask).sum(1) / np.maximum(c, 1)
    naive = mean_where(x) - mean_where(~x)
    pz = z.mean(1)
    adj = sum((pz if zz else 1 - pz) * (mean_where(x & (z == zz)) - mean_where(~x & (z == zz))) for zz in (0, 1))
    return naive, adj


def error_vs_n():
    """Root-mean-square error of two estimators against the true effect 0.5, as the sample grows."""
    rng = np.random.default_rng(7)
    ns = [50, 100, 200, 400, 800, 1600, 3200, 6400]
    truth = float(we_do(1) - we_do(0))
    r_naive, r_adj = [], []
    for n in ns:
        a, b = simulate_we(n, 300, rng)
        r_naive.append(float(np.sqrt(np.mean((a - truth) ** 2))))
        r_adj.append(float(np.sqrt(np.mean((b - truth) ** 2))))
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.loglog(ns, r_naive, "o-", color="#ef4444", lw=2, label="naive contrast (not the estimand)")
    ax.loglog(ns, r_adj, "o-", color="#7c3aed", lw=2, label="backdoor plug-in (identified)")
    bias = float(we_obs(1) - we_obs(0)) - truth
    ax.axhline(bias, color="#ef4444", ls=":", lw=1.2)
    ax.text(ns[-1], bias * 0.9, f"bias floor {bias:.2f}", color="#ef4444", fontsize=9, ha="right", va="top")
    ref = [r_adj[0] * np.sqrt(ns[0] / n) for n in ns]
    ax.loglog(ns, ref, "--", color="#94a3b8", lw=1, label=r"slope $-1/2$ (error $\propto 1/\sqrt{n}$)")
    ax.set_xlabel("number of records $n$")
    ax.set_ylabel("RMS error against the true effect 0.5")
    ax.set_title("More data removes noise, not a wrong estimand", fontsize=11)
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
