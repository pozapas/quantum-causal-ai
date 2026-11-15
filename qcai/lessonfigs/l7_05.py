"""Figures and shared numbers for L7-05 Identifiability before quantum causal learning.

Classical pair: both models give P(X=1) = 0.5, P(Y=1|X=1) = 0.8, P(Y=1|X=0) = 0.2.
  M1 (confounded, no effect): U ~ Bern(1/2), X := U xor N_X (N_X ~ Bern(0.1)), Y := U xor N_Y (N_Y ~ Bern(0.125)).
  M2 (direct effect):        X ~ Bern(1/2),  Y := X xor N_Y (N_Y ~ Bern(0.2)).
Quantum triple: same-basis Pauli correlations c = (<XX>, <YY>, <ZZ>) of a common-cause state, or
t_i = (1/2) Tr[sigma_i E(sigma_i)] for a direct cause A -> B with A maximally mixed, measured
projectively in the sigma_i basis, and its eigenstate passed through the channel E.
"""
from __future__ import annotations

import itertools

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from qcai.viz import frame

# ------------------------------------------------------------------------------------------------
# classical structural models (exact enumeration)
# ------------------------------------------------------------------------------------------------
PX1 = 0.5
PY1_X1 = 0.8
PY1_X0 = 0.2
A_NX, Q_NY1 = 0.1, 0.125     # M1 noise levels
Q_NY2 = 0.2                  # M2 noise level


def _bern(p, v):
    return p if v == 1 else 1 - p


def joint_m1(do_x=None):
    """P(X, Y) under M1, optionally under do(X = do_x)."""
    P = np.zeros((2, 2))
    for u, nx, ny in itertools.product((0, 1), repeat=3):
        w = 0.5 * _bern(A_NX, nx) * _bern(Q_NY1, ny)
        x = (u ^ nx) if do_x is None else do_x
        y = u ^ ny
        P[x, y] += w
    return P


def joint_m2(do_x=None):
    P = np.zeros((2, 2))
    for x0, ny in itertools.product((0, 1), repeat=2):
        w = _bern(PX1, x0) * _bern(Q_NY2, ny)
        x = x0 if do_x is None else do_x
        P[x, x ^ ny] += w
    return P


def do_y1(model, x):
    P = (joint_m1 if model == 1 else joint_m2)(do_x=x)
    return float(P[x, 1])


ATE_M1 = do_y1(1, 1) - do_y1(1, 0)     # 0
ATE_M2 = do_y1(2, 1) - do_y1(2, 0)     # 0.6
assert np.allclose(joint_m1(), joint_m2()) and np.allclose(joint_m1(), [[0.4, 0.1], [0.1, 0.4]])
assert abs(ATE_M1) < 1e-12 and abs(ATE_M2 - 0.6) < 1e-12 and abs(do_y1(1, 1) - 0.5) < 1e-12


def ate_bounds(gamma: float):
    """Sharp ATE bounds when |P(Y_x=1 | X=1-x) - P(Y_x=1 | X=x)| <= gamma (gamma = 1: no assumption)."""
    px0 = 1 - PX1
    e1 = (PX1 * PY1_X1 + px0 * max(0.0, PY1_X1 - gamma), PX1 * PY1_X1 + px0 * min(1.0, PY1_X1 + gamma))
    e0 = (px0 * PY1_X0 + PX1 * max(0.0, PY1_X0 - gamma), px0 * PY1_X0 + PX1 * min(1.0, PY1_X0 + gamma))
    return e1[0] - e0[1], e1[1] - e0[0]


MANSKI = ate_bounds(1.0)           # (-0.2, 0.8)
assert np.allclose(MANSKI, (-0.2, 0.8)) and np.allclose(ate_bounds(0.0), (0.6, 0.6))
assert np.allclose(ate_bounds(0.6), (0.0, 0.8))
GAMMA_M1 = 0.6                     # confounding strength in M1: P(Y=1|U...) difference seen through X
assert abs((joint_m1()[0, 1] / joint_m1()[0].sum()) - 0.2) < 1e-12


# ------------------------------------------------------------------------------------------------
# quantum: same-basis correlation triples
# ------------------------------------------------------------------------------------------------
I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.diag([1.0 + 0j, -1.0])
PAULIS = (SX, SY, SZ)


def state_triple(rho):
    return np.array([np.real(np.trace(rho @ np.kron(s, s))) for s in PAULIS])


def channel_triple(kraus):
    return np.array([0.5 * np.real(np.trace(s @ sum(K @ s @ K.conj().T for K in kraus))) for s in PAULIS])


PHI_PLUS = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
RHO_PHI = np.outer(PHI_PLUS, PHI_PLUS.conj())
RHO_CLASSICAL = np.diag([0.5, 0, 0, 0.5]).astype(complex)
T_IDENTITY = channel_triple([I2])                    # (1, 1, 1)
T_PHI = state_triple(RHO_PHI)                        # (1, -1, 1)
T_CLASSICAL = state_triple(RHO_CLASSICAL)            # (0, 0, 1)
assert np.allclose(T_IDENTITY, [1, 1, 1]) and np.allclose(T_PHI, [1, -1, 1]) and np.allclose(T_CLASSICAL, [0, 0, 1])

STATE_VERTS = np.array([[-1, -1, -1], [-1, 1, 1], [1, -1, 1], [1, 1, -1]])
CHAN_VERTS = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]])
OCTA_VERTS = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]])


def in_state_set(c, tol=1e-9):
    c1, c2, c3 = c
    return min(1 - c1 - c2 - c3, 1 - c1 + c2 + c3, 1 + c1 - c2 + c3, 1 + c1 + c2 - c3) >= -tol


def in_channel_set(t, tol=1e-9):
    t1, t2, t3 = t
    return min(1 + t1 + t2 + t3, 1 + t1 - t2 - t3, 1 - t1 + t2 - t3, 1 - t1 - t2 + t3) >= -tol


def classify(c):
    s, k = in_state_set(c), in_channel_set(c)
    if s and k:
        return "both explanations fit: not identified"
    if s:
        return "only a common cause fits"
    if k:
        return "only a direct cause fits"
    return "neither model class fits"


# ------------------------------------------------------------------------------------------------
# interactive 1: identified set against the strength of an assumption
# ------------------------------------------------------------------------------------------------
def sensitivity_bounds():
    gammas = [round(0.05 * k, 2) for k in range(21)]
    gs = np.linspace(0, 1, 101)
    lo = [ate_bounds(g)[0] for g in gs]
    hi = [ate_bounds(g)[1] for g in gs]
    fig = make_subplots(rows=1, cols=2, column_widths=[0.45, 0.55], horizontal_spacing=0.14,
                        subplot_titles=("Identified set for the ATE", "Bounds against γ"))
    b0 = ate_bounds(gammas[0])
    fig.add_trace(go.Scatter(x=[b0[0], b0[1]], y=[0, 0], mode="lines+markers", line=dict(color="#7c3aed", width=10),
                             marker=dict(size=12, color="#7c3aed"), name="identified set",
                             hovertemplate="ATE bound %{x:.2f}<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=[ATE_M1], y=[0.35], mode="markers+text", text=["M1"], textposition="top center",
                             marker=dict(size=13, color="#ef4444", symbol="diamond"), name="M1: ATE 0",
                             hovertemplate="M1 (confounded): ATE 0<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=[ATE_M2], y=[0.35], mode="markers+text", text=["M2"], textposition="top center",
                             marker=dict(size=13, color="#06b6d4", symbol="diamond"), name="M2: ATE 0.6",
                             hovertemplate="M2 (direct): ATE 0.6<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=gs.tolist(), y=lo, mode="lines", line=dict(color="#7c3aed"), showlegend=False,
                             hovertemplate="γ = %{x:.2f}<br>lower %{y:.2f}<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=gs.tolist(), y=hi, mode="lines", line=dict(color="#7c3aed"), fill="tonexty",
                             fillcolor="rgba(124,58,237,0.15)", showlegend=False,
                             hovertemplate="γ = %{x:.2f}<br>upper %{y:.2f}<extra></extra>"), 1, 2)
    fig.add_trace(go.Scatter(x=[gammas[0], gammas[0]], y=[-0.3, 0.9], mode="lines", line=dict(color="#f59e0b", dash="dash"),
                             showlegend=False, hoverinfo="skip"), 1, 2)
    steps = []
    for g in gammas:
        b = ate_bounds(g)
        steps.append(dict(method="restyle", label=f"{g:.2f}",
                          args=[{"x": [[round(b[0], 4), round(b[1], 4)], [g, g]]}, [0, 5]]))
    fig.update_xaxes(range=[-0.35, 0.95], title="average treatment effect", dtick=0.2, tickangle=0, row=1, col=1)
    fig.update_yaxes(range=[-0.5, 0.8], showticklabels=False, showgrid=False, zeroline=False, row=1, col=1)
    fig.update_xaxes(range=[0, 1], title="confounding bound γ", dtick=0.2, tickangle=0, row=1, col=2)
    fig.update_yaxes(range=[-0.3, 0.9], title="ATE", dtick=0.2, row=1, col=2)
    fig.update_layout(template="plotly_white",
                      sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="γ = "))])
    return frame(fig, height=520, stack=True)


# ------------------------------------------------------------------------------------------------
# interactive 2: the two tetrahedra of correlation triples
# ------------------------------------------------------------------------------------------------
def _tetra_mesh(V, color, name):
    i, j, k = [0, 0, 0, 1], [1, 1, 2, 2], [2, 3, 3, 3]
    return go.Mesh3d(x=V[:, 0], y=V[:, 1], z=V[:, 2], i=i, j=j, k=k, color=color, opacity=0.18, name=name,
                     showlegend=True, hoverinfo="skip", flatshading=True)


def _edges(V, color):
    xs, ys, zs = [], [], []
    for a, b in itertools.combinations(range(len(V)), 2):
        if len(V) == 6 and np.allclose(V[a], -V[b]):
            continue           # octahedron: skip the three long diagonals
        xs += [V[a][0], V[b][0], None]
        ys += [V[a][1], V[b][1], None]
        zs += [V[a][2], V[b][2], None]
    return go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line=dict(color=color, width=3), showlegend=False, hoverinfo="skip")


def correlation_tetrahedra():
    fig = go.Figure()
    fig.add_trace(_tetra_mesh(STATE_VERTS, "#3b82f6", "common-cause states"))
    fig.add_trace(_tetra_mesh(CHAN_VERTS, "#f59e0b", "direct-cause channels"))
    fig.add_trace(_edges(STATE_VERTS, "#3b82f6"))
    fig.add_trace(_edges(CHAN_VERTS, "#f59e0b"))
    fig.add_trace(_edges(OCTA_VERTS, "#7c3aed"))
    named = [(T_PHI, "Φ<sup>+</sup>"), (T_IDENTITY, "identity"), (T_CLASSICAL, "classical"),
             (np.array([-1, -1, -1]), "singlet")]
    fig.add_trace(go.Scatter3d(x=[p[0] for p, _ in named], y=[p[1] for p, _ in named], z=[p[2] for p, _ in named],
                               mode="markers+text", text=[n for _, n in named],
                               textposition=["middle left", "middle left", "top center", "bottom right"],
                               marker=dict(size=4, color="#1e1b4b"), showlegend=False,
                               hovertemplate="%{text}<br>(%{x}, %{y}, %{z})<extra></extra>"))
    ss = [round(-1 + 0.2 * k, 1) for k in range(11)]
    fig.add_trace(go.Scatter3d(x=[ss[5]], y=[ss[5]], z=[ss[5]], mode="markers", marker=dict(size=8, color="#ef4444"),
                               name="observed (s, s, s)", hovertemplate="(%{x}, %{y}, %{z})<extra></extra>"))
    steps = []
    for s in ss:
        steps.append(dict(method="update", label=f"{s:.1f}",
                          args=[{"x": [[s]], "y": [[s]], "z": [[s]]}, {"title.text": f"Observed triple ({s:.1f}, {s:.1f}, {s:.1f}):<br>{classify((s, s, s))}"}, [6]]))
    fig.update_layout(template="plotly_white",
                      title=f"Observed triple ({ss[5]:.1f}, {ss[5]:.1f}, {ss[5]:.1f}):<br>{classify((ss[5],) * 3)}",
                      scene=dict(aspectmode="cube", xaxis=dict(title="XX", range=[-1.1, 1.1]),
                                 yaxis=dict(title="YY", range=[-1.1, 1.1]), zaxis=dict(title="ZZ", range=[-1.1, 1.1]),
                                 camera=dict(eye=dict(x=1.8, y=-1.7, z=1.0))),
                      sliders=[dict(active=5, steps=steps, currentvalue=dict(prefix="s = "))])
    return frame(fig, height=600, xticks_lines=0, axes=False, narrow_plot=360)
