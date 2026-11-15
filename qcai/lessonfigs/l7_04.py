"""Figures and shared numbers for L7-04 Barren plateaus and trainability.

The circuit family (used by the lesson text, the code block, the animations and these figures):
n qubits start in |0...0>, get one layer of R_Y(pi/4), then L layers.  Each layer applies to every
qubit a Pauli rotation exp(-i theta P / 2) with P drawn uniformly from {X, Y, Z} and theta uniform in
[0, 2 pi), followed by a ladder of controlled-Z gates on neighboring qubits.  The differentiated gate
is the rotation on qubit 0 in the last layer, and it is always an R_Y.  The gradient is computed
exactly with the parameter-shift rule (no shot noise).  Two observables: the local Z_0 and the global
projector |0...0><0...0|.

If the part of the circuit before the differentiated gate is a unitary 2-design, the gradient has mean
zero and variance exactly 1 / (2^n + 1) for Z_0 and 1 / (2 * 2^n * (2^n + 1)) for the projector
(proved in the lesson).  TABLE below holds Monte Carlo estimates from `simulate`.
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

# ------------------------------------------------------------------------------------------------
# exact simulator
# ------------------------------------------------------------------------------------------------
_PAULI = {
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}
_AX = ("X", "Y", "Z")


def rot(p: str, t: float) -> np.ndarray:
    """exp(-i t P / 2) for a Pauli P."""
    return math.cos(t / 2) * np.eye(2) - 1j * math.sin(t / 2) * _PAULI[p]


def _apply(psi: np.ndarray, U: np.ndarray, q: int, n: int) -> np.ndarray:
    psi = psi.reshape([2] * n)
    psi = np.moveaxis(np.tensordot(U, psi, axes=([1], [q])), 0, q)
    return psi.reshape(-1)


def cz_ladder(n: int) -> np.ndarray:
    """Diagonal of the CZ ladder on qubits (0,1), (1,2), ..., qubit 0 is the most significant bit."""
    idx = np.arange(2 ** n)
    d = np.ones(2 ** n)
    for q in range(n - 1):
        b1 = (idx >> (n - 1 - q)) & 1
        b2 = (idx >> (n - 2 - q)) & 1
        d = d * np.where(b1 & b2, -1.0, 1.0)
    return d


def gradient_sample(n: int, L: int, g: np.random.Generator, czd: np.ndarray) -> tuple[float, float]:
    """One random circuit: exact parameter-shift gradients for (local Z_0, global projector)."""
    psi = np.zeros(2 ** n, dtype=complex)
    psi[0] = 1.0
    r0 = rot("Y", math.pi / 4)
    for q in range(n):
        psi = _apply(psi, r0, q, n)
    for _ in range(L - 1):
        for q in range(n):
            psi = _apply(psi, rot(_AX[g.integers(3)], g.uniform(0, 2 * math.pi)), q, n)
        psi = czd * psi
    # last layer: qubit 0 is R_Y(theta), the others random
    t0 = g.uniform(0, 2 * math.pi)
    others = [(_AX[g.integers(3)], g.uniform(0, 2 * math.pi)) for _ in range(1, n)]
    zsign = 1.0 - 2.0 * ((np.arange(2 ** n) >> (n - 1)) & 1)   # eigenvalues of Z_0
    vals = []
    for s in (+1, -1):
        phi = _apply(psi, rot("Y", t0 + s * math.pi / 2), 0, n)
        for q, (p, t) in enumerate(others, start=1):
            phi = _apply(phi, rot(p, t), q, n)
        phi = czd * phi
        pr = np.abs(phi) ** 2
        vals.append((float(zsign @ pr), float(pr[0])))
    return 0.5 * (vals[0][0] - vals[1][0]), 0.5 * (vals[0][1] - vals[1][1])


def simulate(n: int, L: int, samples: int, seed: int) -> np.ndarray:
    """Array of shape (samples, 2): exact gradients (local, global) over random circuits."""
    g = np.random.default_rng(seed)
    czd = cz_ladder(n)
    return np.array([gradient_sample(n, L, g, czd) for _ in range(samples)])


# ------------------------------------------------------------------------------------------------
# theory
# ------------------------------------------------------------------------------------------------
def var_local_2design(n: int) -> float:
    return 1.0 / (2 ** n + 1)


def var_global_2design(n: int) -> float:
    return 1.0 / (2 * 2 ** n * (2 ** n + 1))


def var_product_global(n: int) -> float:
    """Depth-one product ansatz, cost 1 - prod cos^2(theta_j / 2): Var of d/dtheta_1."""
    return (1 / 8) * (3 / 8) ** (n - 1)


def var_product_local(n: int) -> float:
    """Depth-one product ansatz, cost 1 - (1/n) sum cos^2(theta_j / 2): Var of d/dtheta_1."""
    return 1 / (8 * n ** 2)


def shots_to_resolve(var: float) -> int:
    """Shots per shifted circuit so that the worst-case shot-noise s.d. 1/sqrt(2N) equals sqrt(var)."""
    return math.ceil(1 / (2 * var))


# Monte Carlo estimates produced by `simulate(n, L, 400, seed=1000 * n + L)` (sample variance, ddof=1).
# The relative standard error of a sample variance from 400 draws is roughly 7 to 15 percent here.
QUBITS = [2, 3, 4, 5, 6, 7, 8, 9, 10]
DEPTHS = [1, 2, 4, 8, 16, 32, 64, 128, 256]
SAMPLES = 400
# (n, L): (Var local, Var global), Monte Carlo over 400 circuits, seed 1000 * n + L
TABLE = {
    (2, 1): (5.2620e-01, 6.4296e-02), (2, 2): (2.7238e-01, 4.3379e-02), (2, 4): (2.2051e-01, 2.5818e-02), (2, 8): (2.0892e-01, 2.3796e-02), (2, 16): (1.8986e-01, 2.3501e-02), (2, 32): (1.8792e-01, 2.3357e-02), (2, 64): (1.9866e-01, 2.3512e-02), (2, 128): (2.1779e-01, 2.3415e-02), (2, 256): (2.1008e-01, 2.8585e-02),
    (3, 1): (5.0671e-01, 2.7806e-02), (3, 2): (2.9595e-01, 1.5609e-02), (3, 4): (2.1161e-01, 9.3335e-03), (3, 8): (1.4727e-01, 7.6577e-03), (3, 16): (1.3260e-01, 6.8435e-03), (3, 32): (1.1695e-01, 7.3779e-03), (3, 64): (1.1680e-01, 6.9460e-03), (3, 128): (1.0669e-01, 7.1214e-03), (3, 256): (1.1211e-01, 6.4367e-03),
    (4, 1): (4.9582e-01, 1.3893e-02), (4, 2): (3.2030e-01, 5.6398e-03), (4, 4): (2.3005e-01, 3.3997e-03), (4, 8): (1.4630e-01, 2.9779e-03), (4, 16): (8.5598e-02, 2.1045e-03), (4, 32): (6.0989e-02, 2.2072e-03), (4, 64): (6.0770e-02, 1.7254e-03), (4, 128): (6.3866e-02, 1.6441e-03), (4, 256): (6.0045e-02, 1.5717e-03),
    (5, 1): (4.8682e-01, 7.0480e-03), (5, 2): (2.9166e-01, 2.1622e-03), (5, 4): (2.2010e-01, 8.5775e-04), (5, 8): (1.5075e-01, 4.8644e-04), (5, 16): (7.9886e-02, 5.0955e-04), (5, 32): (4.4613e-02, 4.5969e-04), (5, 64): (3.3047e-02, 4.5514e-04), (5, 128): (3.1104e-02, 4.3173e-04), (5, 256): (2.9386e-02, 4.5149e-04),
    (6, 1): (4.9627e-01, 3.2295e-03), (6, 2): (3.0814e-01, 9.2968e-04), (6, 4): (2.2657e-01, 2.7301e-04), (6, 8): (1.4643e-01, 2.0260e-04), (6, 16): (8.6288e-02, 1.5287e-04), (6, 32): (3.0562e-02, 1.0909e-04), (6, 64): (1.4840e-02, 1.0716e-04), (6, 128): (1.6622e-02, 1.5154e-04), (6, 256): (1.3717e-02, 1.2075e-04),
    (7, 1): (4.8708e-01, 1.2454e-03), (7, 2): (2.8715e-01, 2.7976e-04), (7, 4): (2.1766e-01, 1.3061e-04), (7, 8): (1.3870e-01, 7.5275e-05), (7, 16): (8.0805e-02, 3.9856e-05), (7, 32): (2.5906e-02, 2.7696e-05), (7, 64): (8.7085e-03, 2.8452e-05), (7, 128): (6.7698e-03, 3.0476e-05), (7, 256): (6.8109e-03, 3.1701e-05),
    (8, 1): (4.9376e-01, 3.4445e-04), (8, 2): (3.1639e-01, 5.9232e-05), (8, 4): (2.1608e-01, 2.6350e-05), (8, 8): (1.4083e-01, 1.2568e-05), (8, 16): (8.5146e-02, 1.1033e-05), (8, 32): (2.4409e-02, 8.9162e-06), (8, 64): (6.4284e-03, 8.3965e-06), (8, 128): (4.1159e-03, 7.7600e-06), (8, 256): (3.7840e-03, 7.9426e-06),
    (9, 1): (5.0696e-01, 2.4934e-04), (9, 2): (3.3123e-01, 2.4755e-05), (9, 4): (1.9766e-01, 5.4430e-06), (9, 8): (1.3375e-01, 3.9141e-06), (9, 16): (8.6146e-02, 3.5729e-06), (9, 32): (2.6011e-02, 2.7734e-06), (9, 64): (4.3422e-03, 1.7770e-06), (9, 128): (2.0864e-03, 1.9379e-06), (9, 256): (2.0698e-03, 1.8279e-06),
    (10, 1): (4.8154e-01, 1.4390e-04), (10, 2): (2.9943e-01, 9.2520e-06), (10, 4): (2.2744e-01, 9.5923e-06), (10, 8): (1.5090e-01, 8.2084e-07), (10, 16): (7.1890e-02, 9.4567e-07), (10, 32): (2.7138e-02, 6.2787e-07), (10, 64): (3.6282e-03, 4.7041e-07), (10, 128): (1.1417e-03, 4.3462e-07), (10, 256): (1.1021e-03, 4.4187e-07),
}


# Numbers quoted in the lesson (n = 8)
N_DEMO = 8
SD_LOCAL_8 = math.sqrt(var_local_2design(8))      # 0.0624
SD_GLOBAL_8 = math.sqrt(var_global_2design(8))    # 0.00276
assert abs(SD_LOCAL_8 - 0.0624) < 5e-5 and abs(SD_GLOBAL_8 - 0.00276) < 5e-6
assert shots_to_resolve(var_local_2design(8)) == 129
assert shots_to_resolve(var_global_2design(8)) == 65792


# ------------------------------------------------------------------------------------------------
# interactive: gradient variance against qubit number, one curve per depth (slider)
# ------------------------------------------------------------------------------------------------
def variance_explorer():
    """Monte Carlo gradient variance vs n for depth L (slider), with the exact 2-design predictions."""
    ns = QUBITS
    fig = go.Figure()
    L0 = DEPTHS[0]
    fig.add_trace(go.Scatter(x=ns, y=[TABLE[(n, L0)][0] for n in ns], mode="markers+lines", name="local Z<sub>0</sub>, simulated",
                             marker=dict(size=9, color="#7c3aed"), line=dict(color="#7c3aed", width=1.5),
                             hovertemplate="n = %{x}<br>Var = %{y:.2e}<extra></extra>"))
    fig.add_trace(go.Scatter(x=ns, y=[TABLE[(n, L0)][1] for n in ns], mode="markers+lines", name="global, simulated",
                             marker=dict(size=9, color="#f59e0b", symbol="square"), line=dict(color="#f59e0b", width=1.5),
                             hovertemplate="n = %{x}<br>Var = %{y:.2e}<extra></extra>"))
    fig.add_trace(go.Scatter(x=ns, y=[var_local_2design(n) for n in ns], mode="lines", name="local, 2-design: 1/(2<sup>n</sup>+1)",
                             line=dict(color="#7c3aed", dash="dash"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=ns, y=[var_global_2design(n) for n in ns], mode="lines", name="global, 2-design",
                             line=dict(color="#f59e0b", dash="dash"), hoverinfo="skip"))
    steps = []
    for L in DEPTHS:
        steps.append(dict(method="restyle", label=str(L),
                          args=[{"y": [[TABLE[(n, L)][0] for n in ns], [TABLE[(n, L)][1] for n in ns]]}, [0, 1]]))
    fig.update_xaxes(title="qubits n", dtick=1, range=[1.6, 10.4], tickangle=0)
    fig.update_yaxes(title="Var of the gradient", type="log", range=[-7, 0.2], exponentformat="power")
    fig.update_layout(template="plotly_white",
                      title="Exact gradients of 400 random circuits per point:<br>depth L sets how close they get to a 2-design",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="layers L = "))])
    return frame(fig, height=540, narrow_plot=330)


# ------------------------------------------------------------------------------------------------
# static figure: local Pauli noise makes the gradient decay with depth (density-matrix simulation)
# ------------------------------------------------------------------------------------------------
def _apply_dm(rho: np.ndarray, U: np.ndarray, q: int, n: int) -> np.ndarray:
    t = rho.reshape([2] * (2 * n))
    t = np.moveaxis(np.tensordot(U, t, axes=([1], [q])), 0, q)
    t = np.moveaxis(np.tensordot(U.conj(), t, axes=([1], [n + q])), 0, n + q)
    return t.reshape(2 ** n, 2 ** n)


def _noise(rho: np.ndarray, qn: float, n: int) -> np.ndarray:
    """Local depolarizing noise N(sigma) = qn * sigma on every qubit (Paulis shrink by qn)."""
    for j in range(n):
        t = rho.reshape([2] * (2 * n))
        red = np.trace(t, axis1=j, axis2=n + j)                       # trace out qubit j
        red = np.expand_dims(np.expand_dims(red, j), n + j)
        eye = np.eye(2).reshape([2 if k in (j, n + j) else 1 for k in range(2 * n)])
        rho = (qn * t + (1 - qn) * red * eye / 2).reshape(2 ** n, 2 ** n)
    return rho


def noisy_gradients(n: int, L: int, qn: float, samples: int, seed: int) -> np.ndarray:
    """Exact parameter-shift gradients of <Z_0> (last-layer R_Y on qubit 0) with noise after every layer."""
    g = np.random.default_rng(seed)
    czd = cz_ladder(n)
    CZ = np.outer(czd, czd)
    z0 = 1.0 - 2.0 * ((np.arange(2 ** n) >> (n - 1)) & 1)
    out = []
    for _ in range(samples):
        rho = np.zeros((2 ** n, 2 ** n), dtype=complex)
        rho[0, 0] = 1
        for q in range(n):
            rho = _apply_dm(rho, rot("Y", math.pi / 4), q, n)
        for _ in range(L - 1):
            for q in range(n):
                rho = _apply_dm(rho, rot(_AX[g.integers(3)], g.uniform(0, 2 * math.pi)), q, n)
            rho = _noise(CZ * rho, qn, n)
        t0 = g.uniform(0, 2 * math.pi)
        others = [(_AX[g.integers(3)], g.uniform(0, 2 * math.pi)) for _ in range(1, n)]
        v = []
        for s in (+1, -1):
            r = _apply_dm(rho, rot("Y", t0 + s * math.pi / 2), 0, n)
            for q, (p, t) in enumerate(others, start=1):
                r = _apply_dm(r, rot(p, t), q, n)
            r = _noise(CZ * r, qn, n)
            v.append(float(np.real(z0 @ np.diag(r))))
        out.append(0.5 * (v[0] - v[1]))
    return np.array(out)


NOISE_QS = (1.0, 0.98, 0.95, 0.9)
NOISE_LS = (1, 2, 4, 8, 12, 16, 24, 32, 40)
# RMS gradient sqrt(mean(g^2)) from noisy_gradients(4, L, q, 40, seed=500 + L), precomputed (about 20 s).
NOISE_RMS = {
    1.0: [7.3806e-01, 5.5975e-01, 4.6813e-01, 3.7111e-01, 3.1844e-01, 3.6163e-01, 2.7486e-01, 2.2695e-01, 2.1972e-01],
    0.98: [7.2330e-01, 5.3758e-01, 4.2581e-01, 2.9619e-01, 2.1823e-01, 2.0616e-01, 1.1431e-01, 5.5001e-02, 3.2122e-02],
    0.95: [7.0116e-01, 5.0517e-01, 3.6840e-01, 2.1128e-01, 1.2635e-01, 9.3200e-02, 3.5311e-02, 9.0500e-03, 3.0998e-03],
    0.9: [6.6425e-01, 4.5340e-01, 2.8713e-01, 1.1995e-01, 5.2591e-02, 2.6839e-02, 5.7274e-03, 7.3434e-04, 1.3078e-04],
}


def noisy_gradient_decay():
    """RMS gradient of <Z_0> against depth for n = 4 under local depolarizing noise of strength q."""
    n = 4
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    colors = ("#475569", "#3b82f6", "#7c3aed", "#ef4444")
    for qn, c in zip(NOISE_QS, colors):
        rms = NOISE_RMS[qn]
        ax.semilogy(NOISE_LS, rms, "o-", color=c, lw=1.6, ms=5, label=("noiseless" if qn == 1 else f"q = {qn}"))
    ax.axhline(math.sqrt(var_local_2design(n)), color="#475569", ls=":", lw=1)
    ax.text(40.5, math.sqrt(var_local_2design(n)) * 1.15, "2-design level", ha="right", fontsize=9, color="#475569")
    ax.set_xlabel("layers L (noise after every layer)")
    ax.set_ylabel(r"RMS of $\partial_\theta\langle Z_0\rangle$")
    ax.set_title("n = 4 qubits, 40 random circuits per point, exact density-matrix simulation", fontsize=10)
    ax.set_xlim(0, 41)
    ax.legend(loc="lower left", fontsize=9, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
