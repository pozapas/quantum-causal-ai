"""Small, exact teaching models used by the lab notebooks.

Ported from the reviewed JavaScript engine (../src/science.js) with the same
formulas, then extended with linear-algebra tools for density matrices,
channels, Choi states and the quantum switch.  Angles are in radians.
Nothing here runs on quantum hardware; every function is a classical
simulation of a textbook equation.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import numpy as np

# ---------------------------------------------------------------------------
# Probability, Bayes, simple structural causal model
# ---------------------------------------------------------------------------


def probability(x: float) -> float:
    """Return ``x`` if it is a finite probability in [0, 1]; otherwise raise."""
    if not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0 or x > 1:
        raise ValueError("Probability must be from 0 to 1.")
    return float(x)


def bayes(prior: float, sensitivity: float, false_positive: float) -> dict:
    """Posterior P(condition | positive test) by Bayes' rule."""
    for v in (prior, sensitivity, false_positive):
        probability(v)
    positive = prior * sensitivity + (1 - prior) * false_positive
    return {"positive": positive,
            "posterior": None if positive == 0 else prior * sensitivity / positive}


def causal(prevalence=0.5, low=0.2, high=0.8, base=0.1, effect=0.2, confound=0.5) -> dict:
    """Binary SCM  Z -> X -> Y <- Z.

    Z ~ Bernoulli(prevalence); P(X=1|Z) = high if Z else low;
    P(Y=1|X,Z) = base + effect*X + confound*Z.  Returns the observational
    contrast and the interventional quantities P(Y=1|do(X=x)).
    """
    for v in (prevalence, low, high, base, base + effect, base + confound,
              base + effect + confound):
        probability(v)
    px = xy = notxy = 0.0
    for z in (0, 1):
        pz = prevalence if z else 1 - prevalence
        tx = high if z else low
        px += pz * tx
        xy += pz * tx * (base + effect + confound * z)
        notxy += pz * (1 - tx) * (base + confound * z)
    treated = None if px == 0 else xy / px
    untreated = None if px == 1 else notxy / (1 - px)
    observed = None if treated is None or untreated is None else treated - untreated
    return {"treated": treated, "untreated": untreated, "observed": observed,
            "do1": base + effect + confound * prevalence,
            "do0": base + confound * prevalence, "ate": effect}


def entropy(p: float) -> float:
    """Binary Shannon entropy in bits."""
    probability(p)
    return 0.0 if p in (0, 1) else -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def rng(seed: int = 42) -> Callable[[], float]:
    """Linear congruential generator identical to the JS engine (repeatable)."""
    state = seed & 0xFFFFFFFF

    def nxt() -> float:
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return state / 4294967296

    return nxt


def trials(p: float, n: int, seed: int = 42) -> dict:
    """Seeded Bernoulli trials with the running frequency."""
    probability(p)
    if not isinstance(n, int) or n < 1 or n > 10000:
        raise ValueError("Use 1 to 10000 trials.")
    rand = rng(seed)
    hits, trace = 0, []
    for i in range(1, n + 1):
        hits += 1 if rand() < p else 0
        trace.append(hits / i)
    return {"hits": hits, "n": n, "frequency": hits / n, "trace": trace}


# ---------------------------------------------------------------------------
# Qubits, interference, Bell correlations, noise, gradients (closed forms)
# ---------------------------------------------------------------------------


def qubit(theta: float, phi: float = 0.0) -> dict:
    """Outcome probabilities and Bloch vector of cos(t/2)|0> + e^{i phi} sin(t/2)|1>."""
    if not (math.isfinite(theta) and math.isfinite(phi)):
        raise ValueError("Use finite angles.")
    return {"p0": math.cos(theta / 2) ** 2, "p1": math.sin(theta / 2) ** 2,
            "x": math.sin(theta) * math.cos(phi), "y": math.sin(theta) * math.sin(phi),
            "z": math.cos(theta)}


def interference(phi: float, visibility: float = 1.0) -> dict:
    """Balanced Mach-Zehnder (H, phase phi, H) with fringe visibility."""
    probability(visibility)
    return {"p0": (1 + visibility * math.cos(phi)) / 2,
            "p1": (1 - visibility * math.cos(phi)) / 2}


def correlation(a: float, b: float, visibility: float = 1.0) -> float:
    """E(a,b) for |Phi+> mixed with white noise, measured in the XZ plane."""
    probability(visibility)
    return visibility * math.cos(a - b)


def bell(visibility: float = 1.0) -> float:
    """CHSH value S at the optimal angles (2*sqrt(2)*visibility)."""
    c = lambda a, b: correlation(a, b, visibility)  # noqa: E731
    q = math.pi / 4
    return c(0, q) + c(0, -q) + c(math.pi / 2, q) - c(math.pi / 2, -q)


def bell_distribution(a: float, b: float, visibility: float = 1.0) -> list[float]:
    """Joint outcome probabilities [p(++), p(+-), p(-+), p(--)]."""
    e = correlation(a, b, visibility)
    return [(1 + e) / 4, (1 - e) / 4, (1 - e) / 4, (1 + e) / 4]


def depolarize(theta: float, phi: float, p: float) -> dict:
    """Depolarizing channel rho -> (1-p) rho + p I/2 on a pure Bloch state."""
    probability(p)
    q = qubit(theta, phi)
    v = 1 - p
    return {"x": v * q["x"], "y": v * q["y"], "z": v * q["z"],
            "p0": (1 + v * q["z"]) / 2, "purity": (1 + v * v) / 2}


def expectation(theta: float) -> float:
    """<Z> after RY(theta)|0>."""
    return math.cos(theta)


def parameter_shift(theta: float) -> float:
    """Parameter-shift gradient of ``expectation`` (exact for Pauli rotations)."""
    return (expectation(theta + math.pi / 2) - expectation(theta - math.pi / 2)) / 2


# ---------------------------------------------------------------------------
# Linear algebra for density matrices and channels
# ---------------------------------------------------------------------------

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
KET0 = np.array([1, 0], dtype=complex)
KET1 = np.array([0, 1], dtype=complex)


def ket(theta: float, phi: float = 0.0) -> np.ndarray:
    """Pure qubit state vector on the Bloch sphere."""
    return np.array([math.cos(theta / 2), np.exp(1j * phi) * math.sin(theta / 2)])


def dm(psi: np.ndarray) -> np.ndarray:
    """Density matrix |psi><psi|."""
    psi = np.asarray(psi, dtype=complex).reshape(-1)
    return np.outer(psi, psi.conj())


def bloch(rho: np.ndarray) -> np.ndarray:
    """Bloch vector (x, y, z) of a single-qubit density matrix."""
    return np.real([np.trace(rho @ P) for P in (X, Y, Z)])


def purity(rho: np.ndarray) -> float:
    return float(np.real(np.trace(rho @ rho)))


def von_neumann_entropy(rho: np.ndarray) -> float:
    """S(rho) = -Tr rho log2 rho (bits)."""
    w = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    w = w[w > 1e-12]
    return float(-np.sum(w * np.log2(w)))


def is_density_matrix(rho: np.ndarray, tol: float = 1e-9) -> bool:
    rho = np.asarray(rho)
    herm = np.allclose(rho, rho.conj().T, atol=tol)
    tr = abs(np.trace(rho) - 1) < tol
    psd = np.min(np.linalg.eigvalsh((rho + rho.conj().T) / 2)) > -tol
    return bool(herm and tr and psd)


def rx(t: float) -> np.ndarray:
    return math.cos(t / 2) * I2 - 1j * math.sin(t / 2) * X


def ry(t: float) -> np.ndarray:
    return math.cos(t / 2) * I2 - 1j * math.sin(t / 2) * Y


def rz(t: float) -> np.ndarray:
    return math.cos(t / 2) * I2 - 1j * math.sin(t / 2) * Z


def kron(*ops: np.ndarray) -> np.ndarray:
    out = np.array([[1]], dtype=complex)
    for op in ops:
        out = np.kron(out, op)
    return out


def partial_trace(rho: np.ndarray, keep: int, dims: Sequence[int] = (2, 2)) -> np.ndarray:
    """Trace out every subsystem except index ``keep`` of a bipartite state."""
    d0, d1 = dims
    r = rho.reshape(d0, d1, d0, d1)
    return np.einsum("ijkj->ik", r) if keep == 0 else np.einsum("ijil->jl", r)


def bell_state(name: str = "phi+") -> np.ndarray:
    s = 1 / math.sqrt(2)
    table = {"phi+": [s, 0, 0, s], "phi-": [s, 0, 0, -s],
             "psi+": [0, s, s, 0], "psi-": [0, s, -s, 0]}
    return np.array(table[name], dtype=complex)


def werner(visibility: float) -> np.ndarray:
    """v |Phi+><Phi+| + (1-v) I/4."""
    probability(visibility)
    return visibility * dm(bell_state()) + (1 - visibility) * np.eye(4) / 4


def concurrence(rho: np.ndarray) -> float:
    """Wootters concurrence of a two-qubit state."""
    yy = kron(Y, Y)
    rt = yy @ rho.conj() @ yy
    ev = np.sqrt(np.clip(np.real(np.linalg.eigvals(rho @ rt)), 0, None))
    ev = np.sort(ev)[::-1]
    return float(max(0.0, ev[0] - ev[1] - ev[2] - ev[3]))


def chsh_value(rho: np.ndarray, a0: float, a1: float, b0: float, b1: float) -> float:
    """CHSH S for a two-qubit state with measurements cos(t)Z + sin(t)X."""
    def obs(t):
        return math.cos(t) * Z + math.sin(t) * X

    def e(a, b):
        return float(np.real(np.trace(rho @ kron(obs(a), obs(b)))))

    return e(a0, b0) + e(a0, b1) + e(a1, b0) - e(a1, b1)


def horodecki_max_chsh(rho: np.ndarray) -> float:
    """Maximal CHSH value of a two-qubit state (Horodecki criterion)."""
    paulis = (X, Y, Z)
    T = np.array([[np.real(np.trace(rho @ kron(a, b))) for b in paulis] for a in paulis])
    w = np.sort(np.linalg.eigvalsh(T.T @ T))[::-1]
    return float(2 * math.sqrt(w[0] + w[1]))


# --- channels -------------------------------------------------------------


def apply_kraus(rho: np.ndarray, kraus: Iterable[np.ndarray]) -> np.ndarray:
    return sum(K @ rho @ K.conj().T for K in kraus)


def depolarizing_kraus(p: float) -> list[np.ndarray]:
    """Kraus operators of rho -> (1-p) rho + p I/2."""
    probability(p)
    return [math.sqrt(1 - 3 * p / 4) * I2, math.sqrt(p / 4) * X,
            math.sqrt(p / 4) * Y, math.sqrt(p / 4) * Z]


def amplitude_damping_kraus(gamma: float) -> list[np.ndarray]:
    probability(gamma)
    return [np.array([[1, 0], [0, math.sqrt(1 - gamma)]], dtype=complex),
            np.array([[0, math.sqrt(gamma)], [0, 0]], dtype=complex)]


def dephasing_kraus(p: float) -> list[np.ndarray]:
    probability(p)
    return [math.sqrt(1 - p / 2) * I2, math.sqrt(p / 2) * Z]


def is_cptp(kraus: Iterable[np.ndarray], tol: float = 1e-9) -> bool:
    kraus = list(kraus)
    d = kraus[0].shape[1]
    return bool(np.allclose(sum(K.conj().T @ K for K in kraus), np.eye(d), atol=tol))


def choi(kraus: Iterable[np.ndarray]) -> np.ndarray:
    """Choi matrix J = sum_ij |i><j| (x) E(|i><j|) (unnormalized)."""
    kraus = list(kraus)
    d = kraus[0].shape[1]
    J = np.zeros((d * d, d * d), dtype=complex)
    for i in range(d):
        for j in range(d):
            Eij = np.zeros((d, d), dtype=complex)
            Eij[i, j] = 1
            J += np.kron(Eij, apply_kraus(Eij, kraus))
    return J


# --- quantum switch ---------------------------------------------------------


def quantum_switch(rho: np.ndarray, kraus_a: Sequence[np.ndarray],
                   kraus_b: Sequence[np.ndarray], control: np.ndarray | None = None) -> np.ndarray:
    """Output (control (x) target) of the quantum switch of channels A and B.

    Kraus form from Chiribella, D'Ariano, Perinotti, Valiron (arXiv:0912.0195):
    W_ij = |0><0| (x) B_j A_i + |1><1| (x) A_i B_j.  Default control is |+>.
    """
    if control is None:
        control = dm(np.array([1, 1]) / math.sqrt(2))
    P0, P1 = dm(KET0), dm(KET1)
    state = np.kron(control, rho)
    out = np.zeros_like(state)
    for A in kraus_a:
        for B in kraus_b:
            W = np.kron(P0, B @ A) + np.kron(P1, A @ B)
            out += W @ state @ W.conj().T
    return out


# --- classical shadows (single qubit, random Pauli measurements) -------------


@dataclass
class ShadowResult:
    estimates: np.ndarray
    truth: float


def classical_shadow_z(rho: np.ndarray, shots: int, seed: int = 7) -> ShadowResult:
    """Estimate <Z> from random-Pauli classical shadows (Huang, Kueng, Preskill 2020).

    For each shot a basis X, Y or Z is chosen uniformly and the outcome b=+/-1
    is sampled.  The single-shot estimator of <Z> is 3*b if the basis was Z,
    else 0.  Returns the running mean.
    """
    g = np.random.default_rng(seed)
    paulis = (X, Y, Z)
    est = np.empty(shots)
    for k in range(shots):
        idx = g.integers(3)
        P = paulis[idx]
        p_plus = float(np.real(np.trace(rho @ (I2 + P) / 2)))
        b = 1 if g.random() < p_plus else -1
        est[k] = 3 * b if idx == 2 else 0.0
    running = np.cumsum(est) / np.arange(1, shots + 1)
    return ShadowResult(running, float(np.real(np.trace(rho @ Z))))


# --- variational circuit helpers -------------------------------------------


def vqc_expectation(params: Sequence[float], x: float) -> float:
    """<Z> of RY(p1) RZ(x) RY(p0) |0> : a one-qubit data re-uploading model."""
    psi = ry(params[1]) @ rz(x) @ ry(params[0]) @ KET0
    return float(np.real(psi.conj() @ Z @ psi))


def vqc_gradient(params: Sequence[float], x: float) -> np.ndarray:
    """Exact parameter-shift gradient of ``vqc_expectation``."""
    g = np.zeros(len(params))
    for k in range(len(params)):
        plus = list(params); plus[k] += math.pi / 2
        minus = list(params); minus[k] -= math.pi / 2
        g[k] = (vqc_expectation(plus, x) - vqc_expectation(minus, x)) / 2
    return g
