"""Figures for L7-08 Reproducible quantum causal benchmarks, and the small benchmark harness the lesson uses.

Conventions (shared with the lesson text, its code cell and scripts/manim/l7_08.py):
- linear Gaussian structural causal model X = X B + E, rows are samples, B[i, j] != 0 means an edge i -> j,
  E has independent N(0, 1) entries;
- held-out interventions do(X_j = c_j) with c_j two observational standard deviations of X_j;
- intervention do(X_j = c): delete the incoming edges of j and set X_j = c; with zero-mean noise the
  interventional mean is the row vector c e_j (I - B_j)^(-1), where B_j is B with column j set to zero;
- structural Hamming distance (SHD): the number of unordered pairs {i, j} whose edge state (none, i -> j,
  j -> i) differs between two graphs, so a reversed edge counts 1;
- interventional error: for each j, the mean over i != j of (predicted - true)^2 / Var(X_i) for
  E[X_i | do(X_j = 2)], averaged over j (dividing by the observational variance makes it unit-free).
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

D, N_TRAIN, P_EDGE, C_DO, TAU = 6, 500, 0.5, 2.0, 3.0


def make_task(seed, d=D, n=N_TRAIN, p=P_EDGE, permute=True, rescale=False):
    """A seeded ground-truth task: random DAG, train and test samples, and held-out interventions."""
    rng = np.random.default_rng(seed)
    B = np.triu(rng.uniform(0.5, 2.0, (d, d)) * rng.choice([-1, 1], (d, d)) * (rng.random((d, d)) < p), k=1)
    perm = rng.permutation(d) if permute else np.arange(d)
    B = B[np.ix_(perm, perm)]                       # relabel nodes so that index order is not causal order
    s = 10 ** rng.uniform(-1, 1, d)                # always drawn, so both variants share the same noise
    s = s if rescale else np.ones(d)
    B = B * s[None, :] / s[:, None]                 # change of units X_i -> s_i X_i keeps the graph
    A = np.linalg.inv(np.eye(d) - B)

    def sample(m):
        return (rng.normal(size=(m, d)) * s) @ A

    var = np.diag(A.T @ np.diag(s ** 2) @ A)        # exact observational variances
    return dict(B=B, train=sample(n), test=sample(n), var=var,
                do_mean=np.array([do_mean(B, j, C_DO * math.sqrt(var[j])) for j in range(d)]))


def do_mean(W, j, c):
    """E[X | do(X_j = c)] for the linear SCM with weights W and zero-mean noise."""
    Wj = W.copy()
    Wj[:, j] = 0
    return c * np.linalg.inv(np.eye(len(W)) - Wj)[j]


def fit_order(X, order, tau=TAU):
    """Regress each variable on the variables before it in `order` (OLS) and keep coefficients with |t| >= tau.

    The t statistic (coefficient over its standard error) does not change with the units of the variables."""
    n, d = X.shape
    W = np.zeros((d, d))
    for k in range(1, d):
        i, pa = order[k], list(order[:k])
        A = X[:, pa]
        w, *_ = np.linalg.lstsq(A, X[:, i], rcond=None)
        s2 = np.sum((X[:, i] - A @ w) ** 2) / (n - len(pa))
        se = np.sqrt(s2 * np.diag(np.linalg.inv(A.T @ A)))
        W[pa, i] = np.where(np.abs(w / se) >= tau, w, 0.0)
    return W


def shd(W1, W2):
    """Structural Hamming distance between the supports of two weighted adjacency matrices (reversal = 1)."""
    a, b = W1 != 0, W2 != 0
    d = len(a)
    return int(sum((a[i, j], a[j, i]) != (b[i, j], b[j, i]) for i in range(d) for j in range(i + 1, d)))


def obs_error(X, Xt, W=None):
    """Held-out prediction error: predict each X_i from all other variables (W None) or from its parents in W."""
    errs = []
    for i in range(X.shape[1]):
        cols = [j for j in range(X.shape[1]) if j != i] if W is None else list(np.flatnonzero(W[:, i]))
        if cols:
            w = np.linalg.lstsq(X[:, cols], X[:, i], rcond=None)[0]
            pred = Xt[:, cols] @ w
        else:
            pred = np.zeros(len(Xt))
        errs.append(np.mean((Xt[:, i] - pred) ** 2) / np.var(Xt[:, i]))
    return float(np.mean(errs))


def int_error(task, W=None, X=None):
    """Interventional error of a weighted DAG W, or (W None) of conditioning E[X | X_j = c] estimated from X."""
    d = len(task["B"])
    S = np.cov(X, rowvar=False) if W is None else None
    out = []
    for j in range(d):
        c = C_DO * math.sqrt(task["var"][j])        # intervene at two standard deviations of X_j
        pred = c * S[j] / S[j, j] if W is None else do_mean(W, j, c)
        keep = [i for i in range(d) if i != j]
        out.append(np.mean((pred[keep] - task["do_mean"][j][keep]) ** 2 / task["var"][keep]))
    return float(np.mean(out))


def true_order(B):
    """A topological order of the DAG with weights B."""
    d, order, left = len(B), [], set(range(len(B)))
    while left:
        src = [i for i in sorted(left) if not any(B[j, i] != 0 for j in left)]
        order.append(src[0])
        left.remove(src[0])
    return np.array(order)


LEARNERS = ["predict from all others", "empty graph", "column order", "variance sort", "random order", "true order"]
ORDERED = LEARNERS[2:]
GRID = [2.0, 3.0, 4.0, 6.0, 8.0, 12.0]


def orders_for(name, task, seed):
    """The variable order an order-based learner uses."""
    X = task["train"]
    return {"column order": np.arange(D), "variance sort": np.argsort(X.var(axis=0)),
            "random order": np.random.default_rng(10_000 + seed).permutation(D),
            "true order": true_order(task["B"])}[name]


def run_benchmark(seeds, taus=None, permute=True, rescale=False, full=True):
    """Rows (learner, seed, SHD, held-out prediction error, interventional error); taus maps learner -> threshold.

    full=False computes SHD only (enough for tuning thresholds)."""
    taus = taus or {}
    rows = []
    for seed in seeds:
        t = make_task(seed, permute=permute, rescale=rescale)
        X, Xt = t["train"], t["test"]
        if full:
            rows.append(("predict from all others", seed, np.nan, obs_error(X, Xt), int_error(t, X=X)))
            W0 = np.zeros((D, D))
            rows.append(("empty graph", seed, shd(W0, t["B"]), obs_error(X, Xt, W0), int_error(t, W0)))
        for name in ORDERED:
            W = fit_order(X, orders_for(name, t, seed), taus.get(name, TAU))
            rows.append((name, seed, shd(W, t["B"])) + ((obs_error(X, Xt, W), int_error(t, W)) if full else (np.nan, np.nan)))
    return rows


def tune(seeds, grid=GRID, **task_options):
    """Per-learner threshold with the smallest mean SHD on the given (validation) seeds."""
    res = {tau: run_benchmark(seeds, {L: tau for L in ORDERED}, full=False, **task_options) for tau in grid}
    return {L: min(grid, key=lambda tau: summarize(res[tau], L, 2)[0]) for L in ORDERED}


def summarize(rows, learner, col):
    """Mean and sample standard deviation of one column for one learner."""
    v = np.array([r[col] for r in rows if r[0] == learner], dtype=float)
    return float(np.mean(v)), (float(np.std(v, ddof=1)) if len(v) > 1 else 0.0)


VAL_SEEDS = list(range(0, 20))
TEST_SEEDS = list(range(100, 120))
COLORS = {"predict from all others": "#06b6d4", "empty graph": "#1e1b4b", "column order": "#94a3b8", "variance sort": "#f59e0b",
          "random order": "#ef4444", "true order": "#7c3aed"}
SHORT = {"predict from all others": "predict<br>from all", "empty graph": "empty<br>graph", "column order": "column<br>order",
         "variance sort": "variance<br>sort", "random order": "random<br>order", "true order": "true<br>order"}
TEXTPOS = {"predict from all others": "top right", "empty graph": "top center", "column order": "top right",
           "variance sort": "bottom center", "random order": "bottom center", "true order": "top center"}
LABEL = {"predict from all others": "predict", "empty graph": "empty", "column order": "column",
         "variance sort": "variance sort", "random order": "random", "true order": "true order"}


def benchmark_explorer():
    """Left: prediction error against interventional error per learner; right: SHD.  Slider: number of seeds."""
    rows = run_benchmark(TEST_SEEDS, tune(VAL_SEEDS))
    counts = [1, 2, 5, 10, 20]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.16,
                        subplot_titles=("Prediction against intervention", "Structure recovery (SHD)"))

    def stats(m):
        """Means and standard errors over the first m test seeds."""
        sub = [r for r in rows if r[1] in TEST_SEEDS[:m]]
        out = {}
        for L in LEARNERS:
            vals = []
            for col in (3, 4, 2):
                if col == 2 and L == "predict from all others":
                    vals += [0.0, 0.0]
                    continue
                mu, sd = summarize(sub, L, col)
                vals += [mu, sd / math.sqrt(m)]
            out[L] = vals
        return out

    def logbar(mu, se, color):
        """Error bar on a log axis: the lower arm never reaches zero."""
        return dict(type="data", symmetric=False, array=[round(se, 4)], arrayminus=[round(min(se, 0.8 * mu), 4)],
                    color=color)

    bl = [L for L in LEARNERS if L != "predict from all others"]

    def restyle(st):
        xs = [[round(st[L][0], 4)] for L in LEARNERS] + [[SHORT[L] for L in bl]]
        ys = [[round(st[L][2], 4)] for L in LEARNERS] + [[round(st[L][4], 3) for L in bl]]
        ex = [logbar(st[L][0], st[L][1], COLORS[L]) for L in LEARNERS] + [None]
        ey = [logbar(st[L][2], st[L][3], COLORS[L]) for L in LEARNERS] + \
             [dict(type="data", array=[round(st[L][5], 3) for L in bl], color="#475569")]
        return {"x": xs, "y": ys, "error_x": ex, "error_y": ey}

    def step_args(st):
        """Slider step with dotted keys, so only the data arrays change."""
        b = restyle(st)
        return {"x": b["x"], "y": b["y"],
                "error_x.array": [e["array"] if e else [] for e in b["error_x"]],
                "error_x.arrayminus": [e["arrayminus"] if e else [] for e in b["error_x"]],
                "error_y.array": [e["array"] for e in b["error_y"]],
                "error_y.arrayminus": [e.get("arrayminus", e["array"]) for e in b["error_y"]]}

    first = restyle(stats(counts[-1]))
    for k, L in enumerate(LEARNERS):
        fig.add_trace(go.Scatter(x=first["x"][k], y=first["y"][k], mode="markers+text", text=[LABEL[L]],
                                 textposition=TEXTPOS[L], textfont=dict(size=11, color=COLORS[L]),
                                 error_x=first["error_x"][k], error_y=first["error_y"][k],
                                 marker=dict(size=11, color=COLORS[L]), showlegend=False,
                                 hovertemplate=f"{L}<br>prediction error %{{x:.3f}}<br>interventional error %{{y:.3f}}<extra></extra>"), 1, 1)
    fig.add_trace(go.Bar(x=first["x"][-1], y=first["y"][-1], error_y=first["error_y"][-1],
                         marker_color=[COLORS[L] for L in bl], showlegend=False,
                         hovertemplate="%{x}<br>mean SHD %{y:.2f}<extra></extra>"), 1, 2)
    steps = [dict(method="restyle", label=str(m), args=[step_args(stats(m))]) for m in counts]
    fig.update_xaxes(title="held-out prediction error", type="log", range=[math.log10(0.08), math.log10(1.8)],
                     tickvals=[0.1, 0.2, 0.5, 1], ticktext=["0.1", "0.2", "0.5", "1"], tickangle=0, row=1, col=1)
    fig.update_yaxes(title="interventional error", type="log", range=[-3.8, 0.8], tickvals=[0.001, 0.01, 0.1, 1],
                     ticktext=["0.001", "0.01", "0.1", "1"], row=1, col=1)
    fig.update_xaxes(tickangle=0, tickfont=dict(size=10), row=1, col=2)
    fig.update_yaxes(title="mean SHD (lower is better)", range=[0, 13], row=1, col=2)
    fig.update_layout(template="plotly_white",
                      title=dict(text="Five learners and a predictor, 6-variable SCMs<br>mean ± standard error over seeds"),
                      sliders=[dict(active=len(counts) - 1, steps=steps, currentvalue=dict(prefix="seeds used = "))])
    return frame(fig, height=600, stack=True, xticks_lines=2)


def varsortability(seeds, rescale=False):
    """Fraction of true edges i -> j with Var(X_i) < Var(X_j) in the training data, pooled over seeds."""
    hits = []
    for seed in seeds:
        t = make_task(seed, rescale=rescale)
        v = t["train"].var(axis=0)
        hits += [v[i] < v[j] for i, j in np.argwhere(t["B"] != 0)]
    return float(np.mean(hits))


def variance_figure():
    """Marginal variance against causal position: raw units (left) and randomly rescaled units (right)."""
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.7), sharey=True)
    for ax, rescale, ttl, c in ((axes[0], False, "equal noise scales, raw units", "#f59e0b"),
                                (axes[1], True, "same graphs, random units", "#7c3aed")):
        frac = varsortability(TEST_SEEDS, rescale)
        for seed in TEST_SEEDS:
            t = make_task(seed, rescale=rescale)
            v = t["train"].var(axis=0)[true_order(t["B"])]
            ax.plot(range(1, D + 1), v, color="#94a3b8", lw=0.8, alpha=0.7)
            ax.scatter(range(1, D + 1), v, color=c, s=8, zorder=3)
        ax.set_yscale("log")
        ax.set_xlabel("position in the true causal order")
        ax.set_title(f"{ttl}\nedges pointing to higher variance: {100 * frac:.0f}%", fontsize=10)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
    axes[0].set_ylabel("marginal variance (log scale)")
    fig.suptitle("Sorting by variance can recover causal order in synthetic data, for the wrong reason", fontsize=10)
    fig.tight_layout()
    return fig


FRESH_SEEDS = list(range(200, 220))


def null_model_shd(tasks, k, tau):
    """Mean SHD of 'null model' k: a fixed random variable order (seed 500 + k), whatever the task."""
    order = np.random.default_rng(500 + k).permutation(D)
    return float(np.mean([shd(fit_order(t["train"], order, tau), t["B"]) for t in tasks]))


def selection_demo(n_models=30):
    """Pick the best of n_models null models on the test seeds, then score all of them on fresh seeds."""
    tau = tune(VAL_SEEDS)["random order"]
    test_tasks = [make_task(s) for s in TEST_SEEDS]
    fresh_tasks = [make_task(s) for s in FRESH_SEEDS]
    test = [null_model_shd(test_tasks, k, tau) for k in range(n_models)]
    fresh = [null_model_shd(fresh_tasks, k, tau) for k in range(n_models)]
    best = int(np.argmin(test))
    return dict(best=best, test_best=test[best], test_mean=float(np.mean(test)),
                fresh_best=fresh[best], fresh_mean=float(np.mean(fresh)))
