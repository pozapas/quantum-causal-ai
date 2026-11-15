"""Figures for L7-07 Classical shadows and observable structure.

Conventions (shared with the lesson text, its code cell and scripts/manim/l7_07.py):
- qubit 0 is the leftmost tensor factor; outcome index i has bits (b_0, ..., b_{n-1}) with b_0 most significant;
  the eigenvalue sign of bit b is 1 - 2b;
- random Pauli measurement: each qubit independently gets X, Y or Z with probability 1/3, implemented by the
  rotation U = H (X basis), H S^dagger (Y basis) or I (Z basis) followed by a computational-basis measurement;
- the test state is |psi> = cos(pi/6)|000> + sin(pi/6)|111>, with <Z_1> = 1/2, <Z_1 Z_2> = 1, <X_1 X_2 X_3> = sqrt(3)/2.
"""
from __future__ import annotations

import itertools
import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
SDG = np.diag([1, -1j])
ROT = (H, H @ SDG, I2)                  # rotate the X, Y, Z eigenbasis onto the computational basis
PAULIS = (I2, X, Y, Z)                  # word letters 0 = I, 1 = X, 2 = Y, 3 = Z

N_QUBITS = 3
THETA = math.pi / 6
PSI = np.zeros(2 ** N_QUBITS, dtype=complex)
PSI[0], PSI[-1] = math.cos(THETA), math.sin(THETA)
WORDS = {1: (3, 0, 0), 2: (3, 3, 0), 3: (1, 1, 1)}          # Z_1, Z_1 Z_2, X_1 X_2 X_3
NAMES = {1: "Z<sub>1</sub>", 2: "Z<sub>1</sub>Z<sub>2</sub>", 3: "X<sub>1</sub>X<sub>2</sub>X<sub>3</sub>"}
COLORS = {1: "#3b82f6", 2: "#f59e0b", 3: "#ef4444"}
REPS, NMAX, SEED = 400, 4000, 707
NS = [10, 20, 50, 100, 200, 500, 1000, 2000, 4000]
HIST_NS = [10, 30, 100, 300, 1000, 4000]


def kron(*ops):
    out = np.array([[1.0 + 0j]])
    for o in ops:
        out = np.kron(out, o)
    return out


def pauli(word):
    return kron(*[PAULIS[c] for c in word])


def expectation(word, psi=PSI):
    return float(np.real(psi.conj() @ pauli(word) @ psi))


def setting_probs(psi=PSI, n=N_QUBITS):
    """Outcome probabilities for every one of the 3^n basis settings, shape (3^n, 2^n)."""
    sets = list(itertools.product(range(3), repeat=n))
    return sets, np.array([np.abs(kron(*[ROT[b] for b in s]) @ psi) ** 2 for s in sets])


def simulate(reps=REPS, shots=NMAX, seed=SEED, psi=PSI, n=N_QUBITS):
    """Random-Pauli shadow data: setting index and outcome index for reps x shots snapshots."""
    sets, probs = setting_probs(psi, n)
    rng = np.random.default_rng(seed)
    s_idx = rng.integers(3 ** n, size=(reps, shots))
    o_idx = np.empty_like(s_idx)
    for s in range(3 ** n):
        m = s_idx == s
        o_idx[m] = rng.choice(2 ** n, size=int(m.sum()), p=probs[s] / probs[s].sum())
    return np.array(sets), s_idx, o_idx


def single_shot(word, sets, s_idx, o_idx, n=N_QUBITS):
    """Estimator value prod_{j in supp} 3 b_j [basis_j = P_j] for every snapshot."""
    bits = (o_idx[..., None] >> np.arange(n - 1, -1, -1)) & 1
    st = sets[s_idx]
    val = np.ones(s_idx.shape)
    for j, c in enumerate(word):
        if c:
            val = val * 3 * (1 - 2 * bits[..., j]) * (st[..., j] == c - 1)
    return val


def rmse_table():
    """RMSE of the plain mean over REPS repetitions at each N in NS, and the exact prediction."""
    sets, s_idx, o_idx = simulate()
    out = {}
    for k, w in WORDS.items():
        t = expectation(w)
        v = single_shot(w, sets, s_idx, o_idx)
        cs = np.cumsum(v, axis=1)
        est = {N: cs[:, N - 1] / N for N in sorted(set(NS) | set(HIST_NS))}
        rm = [math.sqrt(np.mean((est[N] - t) ** 2)) for N in NS]
        th = [math.sqrt((3 ** k - t ** 2) / N) for N in NS]
        out[k] = dict(truth=t, rmse=rm, theory=th, est=est)
    return out


def shadow_error_explorer():
    """Left: RMSE against snapshots (log-log) for weight 1, 2, 3 Paulis; right: error histograms at a chosen N."""
    tab = rmse_table()
    fig = make_subplots(rows=1, cols=2, column_widths=[0.55, 0.45], horizontal_spacing=0.14,
                        subplot_titles=("RMSE against snapshots N", "Spread of 400 estimates"))
    for k in (1, 2, 3):
        fig.add_trace(go.Scatter(x=NS, y=[round(v, 5) for v in tab[k]["rmse"]], mode="markers",
                                 marker=dict(color=COLORS[k], size=8), name=f"weight {k}: {NAMES[k]}",
                                 legendgroup=f"w{k}",
                                 hovertemplate="N = %{x}<br>RMSE %{y:.4f}<extra></extra>"), 1, 1)
        fig.add_trace(go.Scatter(x=NS, y=[round(v, 5) for v in tab[k]["theory"]], mode="lines",
                                 line=dict(color=COLORS[k], dash="dot"), legendgroup=f"w{k}", showlegend=False,
                                 hovertemplate="theory %{y:.4f}<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", line=dict(color="#475569", dash="dot"),
                             name="theory √((3<sup>k</sup> − ⟨P⟩²)/N)"), 1, 1)
    edges = np.linspace(-4, 4, 41)
    centers = ((edges[:-1] + edges[1:]) / 2).round(3).tolist()

    def hist(k, N):
        e = np.clip(tab[k]["est"][N] - tab[k]["truth"], -3.999, 3.999)
        return (np.histogram(e, bins=edges)[0] / REPS).round(4).tolist()

    for k in (1, 3):
        fig.add_trace(go.Bar(x=centers, y=hist(k, HIST_NS[0]), marker_color=COLORS[k], opacity=0.6, showlegend=False,
                             legendgroup=f"w{k}", hovertemplate="error %{x}<br>fraction %{y}<extra></extra>"), 1, 2)
    steps = []
    for N in HIST_NS:
        h1, h3 = hist(1, N), hist(3, N)
        top = round(1.15 * max(h1 + h3), 3)
        steps.append(dict(method="update", label=str(N),
                          args=[{"y": [h1, h3]}, {"yaxis2.range": [0, top]}, [7, 8]]))
    fig.update_xaxes(type="log", title="snapshots N", row=1, col=1)
    fig.update_yaxes(type="log", title="RMSE", row=1, col=1)
    fig.update_xaxes(title="estimate − true value", range=[-4, 4], dtick=2, row=1, col=2)
    fig.update_yaxes(title="fraction of runs", range=[0, round(1.15 * max(hist(1, HIST_NS[0]) + hist(3, HIST_NS[0])), 3)], row=1, col=2)
    fig.update_layout(template="plotly_white", barmode="overlay",
                      title=dict(text="Random-Pauli shadows on 3 qubits<br>state cos(π/6)|000⟩ + sin(π/6)|111⟩<br>"
                                      "400 seeded repetitions per point"),
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="histogram at N = "))])
    return frame(fig, height=600, stack=True)


def budget(k, M, eps, delta):
    """Theorem 1 of Huang, Kueng and Preskill for weight-k Pauli strings: K, N and N K."""
    K = math.ceil(2 * math.log(2 * M / delta))
    N = math.ceil(34 * 3 ** k / eps ** 2)
    return K, N, K * N


def separate(M, eps, delta):
    """Measure each Pauli in its own basis; Hoeffding plus a union bound: M ceil((2/eps^2) ln(2M/delta))."""
    return M * math.ceil(2 / eps ** 2 * math.log(2 * M / delta))


def shadow_budget():
    """Left: single-snapshot second moment against weight.  Right: Theorem 1 budgets against the number of observables."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.8, 3.9))
    ks = np.arange(1, 11)
    a.semilogy(ks, 3.0 ** ks, "o-", color="#ef4444", label=r"Pauli string: $3^k$ (exact)")
    a.semilogy(ks, 4.0 ** ks, "s--", color="#7c3aed", label=r"$k$-local, $\|O\|_\infty = 1$: $4^k$ (bound)")
    a.semilogy(ks, np.ones_like(ks), ":", color="#475569", label="measure that one Pauli directly: 1")
    a.set_xlabel("weight (locality) $k$")
    a.set_ylabel("variance scale")
    a.set_title("Cost of one observable, random Pauli shadows", fontsize=10)
    a.legend(fontsize=8, frameon=False, loc="upper left")
    Ms = np.unique(np.logspace(0, 6, 60).astype(int))
    eps, delta = 0.1, 0.01
    for k, c in ((1, "#3b82f6"), (2, "#f59e0b"), (3, "#ef4444")):
        b.loglog(Ms, [budget(k, M, eps, delta)[2] for M in Ms], color=c, label=f"Theorem 1, weight {k}")
    b.loglog(Ms, [separate(M, eps, delta) for M in Ms], color="#475569", ls="--", label="each Pauli separately")
    b.set_xlabel("number of observables $M$")
    b.set_ylabel("snapshots or shots (bound)")
    b.set_title(r"Worst-case budgets, $\epsilon = 0.1$, $\delta = 0.01$", fontsize=10)
    b.legend(fontsize=8, frameon=False, loc="upper left")
    for ax in (a, b):
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
