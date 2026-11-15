"""Figures and the single source of numbers for L7-09 A research protocol from question to result.

Running example: depolarizing channel E_p(rho) = (1 - p) rho + p I/2, input |0>, Z measurement, so
P(outcome 1) = q = p/2.  Planned test: H0: p <= 0.10 against H1: p > 0.10, powered at p1 = 0.16.

Everything is seeded and vectorized so the scene file, the generator and the checker reproduce the same
numbers in well under a second.
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

from qcai.viz import frame

# ----------------------------------------------------------------------------- design constants
ALPHA = 0.05
POWER = 0.90
P0, P1 = 0.10, 0.16                   # null boundary and planned alternative for p
Q0, Q1 = P0 / 2, P1 / 2               # outcome-1 probabilities
NMAX = 1000                           # shot budget of the sequential designs
BATCH = 50                            # shots between looks (20 looks at most)
LOOKS = (1, 2, 4, 5, 10, 20)          # numbers of equally spaced looks that divide NMAX / BATCH
PS = (0.10, 0.12, 0.14, 0.16, 0.18, 0.20)
M_PATHS = 20000                       # Monte Carlo runs per true p
SEED = 2026
VILLE = 1 / ALPHA                     # likelihood-ratio threshold 20

# two-qubit mini-study
S_EFF = 0.10                          # sin^2(theta) of the partial swap: the true causal effect
C_CONF = 0.30                         # flip probability of B caused by the latent bit H
EPS_READ = 0.02                       # readout flip probability used in the robustness check
STUDY_SEED = 909


def z(u: float) -> float:
    return float(stats.norm.ppf(u))


# ----------------------------------------------------------------------------- estimator
def estimate(k: int, n: int) -> dict:
    """p_hat = 2 k / n, its plug-in standard error, and the exact Clopper-Pearson interval mapped to p."""
    qh = k / n
    lo = 0.0 if k == 0 else float(stats.beta.ppf(ALPHA / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1 - ALPHA / 2, k + 1, n - k))
    return {"p_hat": 2 * qh, "se": 2 * math.sqrt(qh * (1 - qh) / n), "ci": (2 * lo, min(1.0, 2 * hi))}


# ----------------------------------------------------------------------------- fixed-N design
def normal_n(q0=Q0, q1=Q1, alpha=ALPHA, power=POWER) -> float:
    """One-sided normal-approximation sample size for a binomial proportion."""
    return ((z(1 - alpha) * math.sqrt(q0 * (1 - q0)) + z(power) * math.sqrt(q1 * (1 - q1))) / (q1 - q0)) ** 2


def exact_test(n: int, q0=Q0, alpha=ALPHA) -> int:
    """Smallest count k* with P(K >= k* | q0) <= alpha (exact one-sided binomial test)."""
    return int(stats.binom.isf(alpha, n, q0)) + 1


def exact_power(n: int, q: float, q0=Q0, alpha=ALPHA) -> float:
    return float(stats.binom.sf(exact_test(n, q0, alpha) - 1, n, q))


def first_exact_n(target=POWER, q1=Q1, start: int = 100) -> int:
    """Smallest n with exact power >= target at q1 (power is not monotone in n: binomial discreteness)."""
    n = start
    while exact_power(n, q1) < target:
        n += 1
    return n


def fixed_design() -> dict:
    nn = normal_n()
    n_norm = math.ceil(nn)
    n = first_exact_n(start=n_norm)
    return {"n_normal": nn, "n_norm": n_norm, "power_norm": exact_power(n_norm, Q1), "size_norm": exact_power(n_norm, Q0),
            "n": n, "k_star": exact_test(n), "size": exact_power(n, Q0), "power": exact_power(n, Q1)}


# ----------------------------------------------------------------------------- optional stopping, Gaussian theory
def gauss_fpr(K: int, c: float | None = None, h: float = 0.004) -> float:
    """P(max_j Z_j > c) for K equally spaced looks at a Gaussian random walk under H0.

    W_j = xi_1 + ... + xi_j with independent standard normal xi, Z_j = W_j / sqrt(j).  The sub-density of W_j
    on the continuation region {W_i <= c sqrt(i), i <= j} is propagated by convolution with the N(0, 1)
    density on a grid of step h (recursive numerical integration); the answer is 1 minus its final mass.
    """
    from scipy.signal import fftconvolve
    c = z(1 - ALPHA) if c is None else c
    lo = -9.0 * math.sqrt(K)
    x = np.arange(lo, c * math.sqrt(K) + h, h)
    kx = np.arange(-9.0, 9.0 + h / 2, h)
    ker = stats.norm.pdf(kx) * h
    f = np.where(x <= c, stats.norm.pdf(x), 0.0)
    for j in range(2, K + 1):
        g = fftconvolve(f, ker, mode="full")[len(kx) // 2: len(kx) // 2 + len(x)]
        f = np.where(x <= c * math.sqrt(j), g, 0.0)
    return float(1 - f.sum() * h)


def gauss_fpr_mvn(K: int, c: float | None = None) -> float:
    """The same probability from the multivariate normal law (corr(Z_i, Z_j) = sqrt(i/j)); slow for K > 8."""
    c = z(1 - ALPHA) if c is None else c
    t = np.arange(1, K + 1)
    cov = np.sqrt(np.minimum.outer(t, t) / np.maximum.outer(t, t))
    return 1 - float(stats.multivariate_normal(mean=np.zeros(K), cov=cov).cdf(np.full(K, c), rng=np.random.default_rng(1)))


def gauss_bonferroni_c(K: int) -> float:
    return z(1 - ALPHA / K)


# ----------------------------------------------------------------------------- optional stopping, Bernoulli simulation
def _counts(p: float, seed: int = SEED, m: int = M_PATHS) -> np.ndarray:
    """Cumulative outcome-1 counts after each batch of BATCH shots: shape (m, NMAX // BATCH)."""
    rng = np.random.default_rng([seed, int(round(p * 1000))])
    return rng.binomial(BATCH, p / 2, size=(m, NMAX // BATCH)).cumsum(axis=1)


def _pval_table() -> np.ndarray:
    """Exact one-sided binomial p-values P(K >= k | n, q0) for every look n and count k: shape (20, NMAX+1)."""
    ns = BATCH * np.arange(1, NMAX // BATCH + 1)
    ks = np.arange(NMAX + 1)
    return stats.binom.sf(ks[None, :] - 1, ns[:, None], Q0)


def _loglr_table() -> np.ndarray:
    ns = BATCH * np.arange(1, NMAX // BATCH + 1)
    ks = np.arange(NMAX + 1)
    return ks[None, :] * math.log(Q1 / Q0) + (ns[:, None] - ks[None, :]) * math.log((1 - Q1) / (1 - Q0))


_PV = None
_LLR = None


def sequential(p: float, seed: int = SEED, m: int = M_PATHS) -> dict:
    """Rejection rate and mean shots used for each rule and number of looks K, at true p."""
    global _PV, _LLR
    if _PV is None:
        _PV, _LLR = _pval_table(), _loglr_table()
    cnt = _counts(p, seed, m)
    nb = NMAX // BATCH
    out = {"naive": [], "bonferroni": [], "ville": [], "n_naive": [], "n_bonferroni": [], "n_ville": []}
    for K in LOOKS:
        idx = np.arange(1, K + 1) * (nb // K) - 1                 # batch indices of the looks
        pv = _PV[idx[None, :], cnt[:, idx]]                         # (m, K)
        llr = _LLR[idx[None, :], cnt[:, idx]]
        rules = {"naive": pv <= ALPHA, "bonferroni": pv <= ALPHA / K, "ville": llr >= math.log(VILLE)}
        for name, rej in rules.items():
            any_ = rej.any(axis=1)
            first = np.where(any_, rej.argmax(axis=1), K - 1)
            shots = BATCH * (idx[first] + 1)
            out[name].append(float(any_.mean()))
            out["n_" + name].append(float(shots.mean()))
    return out


def mc_se(rate: float, m: int = M_PATHS) -> float:
    return math.sqrt(rate * (1 - rate) / m)


def sample_walks(n_paths: int = 40, seed: int = 11) -> np.ndarray:
    """Standardized z-statistics Z_n = (K_n - n q0) / sqrt(n q0 (1 - q0)) after every 10 shots, under H0."""
    rng = np.random.default_rng(seed)
    steps = rng.binomial(10, Q0, size=(n_paths, NMAX // 10)).cumsum(axis=1)
    n = 10 * np.arange(1, NMAX // 10 + 1)
    return (steps - n * Q0) / np.sqrt(n * Q0 * (1 - Q0))


def sample_loglr(n_paths: int = 40, seed: int = 11) -> np.ndarray:
    rng = np.random.default_rng(seed)
    steps = rng.binomial(10, Q0, size=(n_paths, NMAX // 10)).cumsum(axis=1)
    n = 10 * np.arange(1, NMAX // 10 + 1)
    return steps * math.log(Q1 / Q0) + (n - steps) * math.log((1 - Q1) / (1 - Q0))


# ----------------------------------------------------------------------------- two-qubit mini-study
def partial_swap(theta: float) -> np.ndarray:
    """exp(-i theta (XX + YY)/2) on qubits (A, B), basis |00>, |01>, |10>, |11>."""
    U = np.eye(4, dtype=complex)
    U[1, 1] = U[2, 2] = math.cos(theta)
    U[1, 2] = U[2, 1] = -1j * math.sin(theta)
    return U


def pb1(a: int, b0: int, s: float = S_EFF) -> float:
    """P(B = 1) after the partial swap acts on |a, b0>, with sin^2(theta) = s."""
    psi = np.zeros(4, dtype=complex)
    psi[2 * a + b0] = 1
    out = partial_swap(math.asin(math.sqrt(s))) @ psi
    return float(abs(out[1]) ** 2 + abs(out[3]) ** 2)


def regime_rates(s: float = S_EFF, c: float = C_CONF) -> dict:
    """P(B=1 | do(A=a)) with a randomized, and P(B=1 | A=a) when A copies the latent bit H."""
    def rate(a, h):            # B starts in |1> with probability c*h (the latent flip), else |0>
        return c * h * pb1(a, 1, s) + (1 - c * h) * pb1(a, 0, s)
    do = {a: 0.5 * rate(a, 0) + 0.5 * rate(a, 1) for a in (0, 1)}
    obs = {a: rate(a, a) for a in (0, 1)}
    return {"do0": do[0], "do1": do[1], "ace": do[1] - do[0], "obs0": obs[0], "obs1": obs[1],
            "obs_contrast": obs[1] - obs[0]}


def two_arm_n(r0: float, r1: float, alpha=ALPHA, power=POWER) -> int:
    rbar = (r0 + r1) / 2
    num = z(1 - alpha) * math.sqrt(2 * rbar * (1 - rbar)) + z(power) * math.sqrt(r0 * (1 - r0) + r1 * (1 - r1))
    return math.ceil((num / (r1 - r0)) ** 2)


def run_study(n_arm: int | None = None, seed: int = STUDY_SEED, s: float = S_EFF, c: float = C_CONF,
              eps: float = 0.0) -> dict:
    """Simulate the preregistered study: n_arm shots per arm (block randomized), plus an observational run."""
    R = regime_rates(s, c)
    if n_arm is None:
        n_arm = two_arm_n(R["do0"], R["do1"])
    rng = np.random.default_rng(seed)
    f = lambda r: eps + (1 - 2 * eps) * r          # noqa: E731  readout flips with probability eps
    y0 = rng.random(n_arm) < f(R["do0"])
    y1 = rng.random(n_arm) < f(R["do1"])
    # observational regime: A copies a fair latent bit; same total number of shots
    h = rng.random(2 * n_arm) < 0.5
    yo = rng.random(2 * n_arm) < np.where(h, f(R["obs1"]), f(R["obs0"]))
    m0, m1 = y0.mean(), y1.mean()
    ace = m1 - m0
    se = math.sqrt(m0 * (1 - m0) / n_arm + m1 * (1 - m1) / n_arm)
    pool = (y0.sum() + y1.sum()) / (2 * n_arm)
    zstat = ace / math.sqrt(pool * (1 - pool) * 2 / n_arm)
    obs = yo[h].mean() - yo[~h].mean()
    return {"n_arm": n_arm, "k0": int(y0.sum()), "k1": int(y1.sum()), "m0": m0, "m1": m1, "ace_hat": ace, "se": se,
            "ci": (ace - z(0.975) * se, ace + z(0.975) * se), "z": zstat, "reject": bool(zstat > z(1 - ALPHA)),
            "obs_hat": obs, "y0": y0, "y1": y1, "yo": yo, "h": h}


def study_type1(n_arm: int, reps: int = 20000, seed: int = 5) -> float:
    """Simulated type I error of the pooled one-sided z-test at the worst null point s = 0 (same latent c)."""
    R = regime_rates(0.0, C_CONF)
    rng = np.random.default_rng(seed)
    k0 = rng.binomial(n_arm, R["do0"], reps)
    k1 = rng.binomial(n_arm, R["do1"], reps)
    pool = (k0 + k1) / (2 * n_arm)
    zs = (k1 - k0) / n_arm / np.sqrt(pool * (1 - pool) * 2 / n_arm)
    return float((zs > z(1 - ALPHA)).mean())


def study_power(n_arm: int, reps: int = 20000, seed: int = 6) -> float:
    R = regime_rates()
    rng = np.random.default_rng(seed)
    k0 = rng.binomial(n_arm, R["do0"], reps)
    k1 = rng.binomial(n_arm, R["do1"], reps)
    pool = (k0 + k1) / (2 * n_arm)
    zs = (k1 - k0) / n_arm / np.sqrt(pool * (1 - pool) * 2 / n_arm)
    return float((zs > z(1 - ALPHA)).mean())


# ----------------------------------------------------------------------------- figures
COL = {"naive": "#ef4444", "bonferroni": "#3b82f6", "ville": "#7c3aed"}
NAME = {"naive": "peek, test at 0.05", "bonferroni": "Bonferroni 0.05/K", "ville": "likelihood ratio ≥ 20"}


def peeking_explorer():
    """Rejection rate and mean shots used against the number of looks, for three stopping rules (slider: true p)."""
    res = {p: sequential(p) for p in PS}
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.14,
                        subplot_titles=("Probability of rejecting H0", "Mean shots used"))
    x = list(LOOKS)
    first = res[PS[0]]
    for name in ("naive", "bonferroni", "ville"):
        fig.add_trace(go.Scatter(x=x, y=[round(v, 4) for v in first[name]], mode="lines+markers", name=NAME[name],
                                 line=dict(color=COL[name], width=3),
                                 hovertemplate="%{x} looks: %{y:.3f}<extra></extra>"), 1, 1)
    for name in ("naive", "bonferroni", "ville"):
        fig.add_trace(go.Scatter(x=x, y=[round(v, 1) for v in first["n_" + name]], mode="lines+markers",
                                 line=dict(color=COL[name], width=3, dash="dot"), showlegend=False,
                                 hovertemplate="%{x} looks: %{y:.0f} shots<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=[1, 20], y=[ALPHA, ALPHA], mode="lines", line=dict(color="#94a3b8", dash="dash"),
                             name="α = 0.05", hoverinfo="skip"), 1, 1)
    steps = []
    for p in PS:
        r = res[p]
        tag = "H0 true" if p <= P0 else "H1 true"
        steps.append(dict(method="restyle", label=f"{p:.2f}",
                          args=[{"y": [[round(v, 4) for v in r[n]] for n in ("naive", "bonferroni", "ville")]
                                 + [[round(v, 1) for v in r["n_" + n]] for n in ("naive", "bonferroni", "ville")]},
                                [0, 1, 2, 3, 4, 5]]))
        _ = tag
    fig.update_xaxes(title="number of looks K", type="log", tickvals=x, ticktext=[str(v) for v in x], tickangle=0)
    fig.update_yaxes(title="rejection rate (log scale)", type="log", range=[math.log10(0.003), 0.01],
                     tickvals=[0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1], ticktext=["0.005", "0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1"],
                     row=1, col=1)
    fig.update_yaxes(title="shots", range=[0, NMAX * 1.05], row=1, col=2)
    fig.update_layout(template="plotly_white",
                      title=f"Optional stopping, {M_PATHS:,} seeded runs per p<br>H0: p ≤ 0.10; looks every {NMAX}/K shots",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="true p = "))])
    return frame(fig, height=560, stack=True)


def power_curves():
    """Exact power of the fixed-N binomial test against N, for three alternatives, with the planned N marked."""
    d = fixed_design()
    ns = np.arange(100, 1001, 5)
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    for p1, col in ((0.14, "#93c5fd"), (P1, "#7c3aed"), (0.20, "#06b6d4")):
        ax.plot(ns, [exact_power(int(n), p1 / 2) for n in ns], color=col, lw=1.8, label=f"true $p = {p1:.2f}$")
    ax.plot(ns, [exact_power(int(n), Q0) for n in ns], color="#ef4444", lw=1.4, label="true $p = 0.10$ (size)")
    ax.axhline(POWER, color="#94a3b8", lw=0.8, ls="--")
    ax.axhline(ALPHA, color="#94a3b8", lw=0.8, ls="--")
    ax.axvline(d["n"], color="#f59e0b", lw=1.4)
    ax.text(d["n"] + 8, 0.42, f"planned $N = {d['n']}$", color="#b45309", fontsize=10)
    ax.text(1005, POWER, "0.90", va="center", fontsize=9, color="#475569")
    ax.text(1005, ALPHA, "0.05", va="center", fontsize=9, color="#475569")
    ax.set_xlim(100, 1000)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("number of shots $N$")
    ax.set_ylabel("probability of rejecting $H_0$")
    ax.set_title("Exact one-sided binomial test of $H_0: p \\leq 0.10$ at level 0.05", fontsize=11)
    ax.legend(loc="center left", bbox_to_anchor=(1.06, 0.5), frameon=False, fontsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
