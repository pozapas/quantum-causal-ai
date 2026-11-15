"""Figures for L6-07 Process matrices and validity.

Convention (stated in the lesson): subsystem order A_I A_O B_I B_O; a local CP map M with Kraus operators
K_k enters the pairing as the transpose of J = sum_ij |i><j| (x) M(|i><j|)  (the qcai.science.choi operator),
so p = Tr[W (M_A (x) M_B)] with M = J^T  (Oreshkov, Costa and Brukner 2012).
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1.0, -1.0]).astype(complex)


def kron(*ops):
    out = np.array([[1.0 + 0j]])
    for m in ops:
        out = np.kron(out, m)
    return out


def proj(v):
    v = np.asarray(v, dtype=complex)
    return np.outer(v, v.conj()) / np.vdot(v, v).real


PHI = np.array([1, 0, 0, 1], dtype=complex)          # |1>> = |00> + |11>
LINK = np.outer(PHI, PHI)                            # Choi operator of the identity channel (unnormalized)


def choi_T(kraus):
    """Transposed Choi operator (input (x) output) of a CP map: the object paired with W."""
    J = np.zeros((4, 4), dtype=complex)
    for i in range(2):
        for j in range(2):
            E = np.zeros((2, 2), dtype=complex)
            E[i, j] = 1
            J += np.kron(E, sum(K @ E @ K.conj().T for K in kraus))
    return J.T


def random_cptp(rng, n_kraus=2):
    G = rng.normal(size=(2 * n_kraus, 2)) + 1j * rng.normal(size=(2 * n_kraus, 2))
    Q, _ = np.linalg.qr(G)                          # isometry C^2 -> C^(2 n)
    return [Q[2 * k:2 * k + 2, :] for k in range(n_kraus)]


def candidates():
    """Four positive operators of trace 4 on A_I A_O B_I B_O."""
    rho0 = proj([1, 0])
    shared = kron(np.eye(1), LINK / 2)               # |Phi+><Phi+| on A_I B_I, reordered below
    # shared state on A_I B_I with identity on A_O, B_O: build in order A_I B_I A_O B_O then permute
    T = np.kron(shared, np.eye(4)).reshape([2] * 8)  # indices (AI, BI, AO, BO | AI', BI', AO', BO')
    W_state = T.transpose(0, 2, 1, 3, 4, 6, 5, 7).reshape(16, 16)
    W_chan = kron(rho0, LINK, I2)                    # rho on A_I, identity wire A_O -> B_I, B_O discarded
    W_ocb = 0.25 * (np.eye(16) + (kron(I2, Z, Z, I2) + kron(Z, I2, X, Z)) / math.sqrt(2))
    W_loop = kron(LINK, rho0, I2)                    # Alice's output wired into her own input
    return {"shared state": W_state, "channel A to B": W_chan, "OCB process": W_ocb, "loop W_loop": W_loop}


def total_probability(W, kA, kB):
    return float(np.trace(W @ np.kron(choi_T(kA), choi_T(kB))).real)


def ry(t):
    return np.array([[math.cos(t / 2), -math.sin(t / 2)], [math.sin(t / 2), math.cos(t / 2)]], dtype=complex)


def loop_mixture():
    """Slider over the mixing weight lambda of W = (1 - lambda) W_chan + lambda W_loop."""
    C = candidates()
    Wc, Wl = C["channel A to B"], C["loop W_loop"]
    thetas = np.linspace(0, 2 * math.pi, 73)
    lams = [round(v, 2) for v in np.linspace(0, 1, 11)]
    bobs = [I2.astype(complex)]
    curves, mins = {}, {}
    for lam in lams:
        W = (1 - lam) * Wc + lam * Wl
        curves[lam] = [total_probability(W, [ry(t)], bobs) for t in thetas]
        mins[lam] = float(np.linalg.eigvalsh(W).min())
        for t, v in zip(thetas, curves[lam]):        # closed form (1 - lambda) + lambda * 4 cos^2(theta/2)
            assert abs(v - ((1 - lam) + lam * 4 * math.cos(t / 2) ** 2)) < 1e-9
        assert mins[lam] > -1e-12
    deg = np.degrees(thetas).round(1).tolist()
    fig = make_subplots(rows=1, cols=2, column_widths=[0.6, 0.4], horizontal_spacing=0.14,
                        subplot_titles=("Total probability vs Alice's rotation", "Smallest eigenvalue"))
    l0 = lams[5]
    fig.add_trace(go.Scatter(x=deg, y=[1] * len(deg), mode="lines", line=dict(color="#06b6d4", dash="dash", width=3),
                             name="required: 1"), 1, 1)
    fig.add_trace(go.Scatter(x=deg, y=np.round(curves[l0], 4).tolist(), mode="lines", line=dict(color="#ef4444", width=4),
                             name="mixture W", hovertemplate="θ = %{x}°<br>total %{y:.3f}<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=lams, y=[round(mins[v], 6) for v in lams], mode="lines+markers",
                             line=dict(color="#7c3aed"), name="min eigenvalue"), 1, 2)
    fig.add_trace(go.Scatter(x=[l0], y=[round(mins[l0], 6)], mode="markers", marker=dict(size=14, color="#ef4444"),
                             showlegend=False, hovertemplate="λ = %{x}<br>min eigenvalue %{y:.3f}<extra></extra>"), 1, 2)
    steps = [dict(method="restyle", label=f"{lam:.1f}",
                  args=[{"y": [np.round(curves[lam], 4).tolist(), [round(mins[lam], 6)]],
                         "x": [deg, [lam]]}, [1, 3]]) for lam in lams]
    fig.update_xaxes(title="rotation angle θ (degrees)", range=[0, 360], dtick=90, row=1, col=1)
    fig.update_yaxes(title="sum of probabilities", range=[-0.1, 4.2], row=1, col=1)
    fig.update_xaxes(title="loop weight λ", range=[-0.05, 1.05], dtick=0.25, row=1, col=2)
    fig.update_yaxes(title="eigenvalue", range=[-0.5, 0.5], row=1, col=2)
    fig.update_layout(template="plotly_white",
                      title="W = (1 − λ) W<sub>chan</sub> + λ W<sub>loop</sub> is positive for every λ,<br>"
                            "but its probabilities sum to 1 only at λ = 0",
                      sliders=[dict(active=5, steps=steps, currentvalue=dict(prefix="loop weight λ = "))])
    return frame(fig, height=560, stack=True)


def candidates_figure():
    """Positivity and normalization of four candidate operators, tested on random local channels."""
    C = candidates()
    rng = np.random.default_rng(7)
    pairs = [(random_cptp(rng, int(rng.integers(1, 4))), random_cptp(rng, int(rng.integers(1, 4)))) for _ in range(400)]
    names = list(C)
    lo, hi = [], []
    for n in names:
        vals = [total_probability(C[n], a, b) for a, b in pairs]
        lo.append(min(vals))
        hi.append(max(vals))
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    col = ["#06b6d4", "#3b82f6", "#7c3aed", "#ef4444"]
    ypos = np.arange(len(names))[::-1]
    for y, n, c in zip(ypos, names, col):
        ev = np.round(np.linalg.eigvalsh(C[n]), 6)
        vals, counts = np.unique(ev, return_counts=True)
        axes[0].scatter(vals, [y] * len(vals), s=70, color=c, zorder=3)
        for v, k in zip(vals, counts):
            axes[0].text(v, y + 0.22, f"{v:g} (x{k})", ha="center", fontsize=8, color="#1e1b4b")
    axes[0].set_yticks(ypos, names)
    axes[0].set_xlim(-0.35, 2.4)
    axes[0].set_ylim(-0.6, len(names) - 0.3)
    axes[0].axvline(0, color="#475569", lw=0.8)
    axes[0].set_xlabel("eigenvalues of W (multiplicity)", fontsize=9)
    axes[0].set_title("Spectrum: every candidate is positive", fontsize=10)
    for y, a, b, c in zip(ypos, lo, hi, col):
        axes[1].plot([a, b], [y, y], color=c, lw=6, solid_capstyle="butt")
        axes[1].plot([a, b], [y, y], "|", color="#1e1b4b", ms=12)
        axes[1].text(b + 0.08, y, f"[{a:.2f}, {b:.2f}]", va="center", fontsize=9, color="#1e1b4b")
    axes[1].axvline(1, color="#475569", lw=1, ls="--")
    axes[1].set_yticks(ypos, [""] * len(names))
    axes[1].set_xlim(-0.2, 5.0)
    axes[1].set_ylim(-0.6, len(names) - 0.3)
    axes[1].set_xlabel("$\\mathrm{Tr}[W(M_A\\otimes M_B)]$ over 400 random channel pairs", fontsize=9)
    axes[1].set_title("Total probability: must be exactly 1", fontsize=10)
    for ax in axes:
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig
