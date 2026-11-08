"""Fixed numerical checks. The first block mirrors ../tests/science.test.js exactly."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qcai import science as s  # noqa: E402

near = lambda a, b, tol=1e-10: abs(a - b) < tol  # noqa: E731


# ---- ported tests (same fixed values as the reviewed JS suite) -------------

def test_probability_rejects_invalid():
    for p in (-1, 2, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            s.probability(p)


def test_bayes_frequency_table():
    assert near(s.bayes(0.01, 0.9, 0.05)["posterior"], 90 / 585)
    assert s.bayes(0, 1, 0)["posterior"] is None
    assert near(s.bayes(1, 0.2, 0.7)["posterior"], 1)


def test_scm_confounding_vs_intervention():
    q = s.causal()
    for k, v in dict(treated=.7, untreated=.2, observed=.5, do1=.55, do0=.35, ate=.2).items():
        assert near(q[k], v), k
    assert near(s.causal(low=.5, high=.5)["observed"], .2)
    assert near(s.causal(effect=0)["observed"], .3)


def test_qubit_endpoints_and_bloch_norm():
    assert near(s.qubit(0)["p0"], 1)
    assert near(s.qubit(math.pi)["p1"], 1)
    t = 0.0
    while t <= 6:
        q = s.qubit(t, t / 3)
        assert near(q["p0"] + q["p1"], 1)
        assert near(q["x"] ** 2 + q["y"] ** 2 + q["z"] ** 2, 1)
        t += 0.2


def test_interference():
    assert near(s.interference(0)["p0"], 1)
    assert near(s.interference(math.pi)["p0"], 0)
    assert near(s.interference(1.9, 0)["p0"], .5)


def test_bell_distribution_no_signalling():
    for a in (0, .3, math.pi / 2):
        for b in (0, .9, math.pi / 4):
            p = s.bell_distribution(a, b)
            assert near(sum(p), 1) and near(p[0] + p[1], .5) and near(p[0] + p[2], .5)
            assert all(x >= 0 for x in p)
    assert s.bell_distribution(0, 0) == [.5, 0, 0, .5]
    assert near(s.bell(), 2 * math.sqrt(2))
    assert near(s.bell(0), 0)
    assert near(s.bell(1 / math.sqrt(2)), 2)


def test_depolarization():
    assert near(s.depolarize(.7, .8, 0)["purity"], 1)
    assert near(s.depolarize(.7, .8, 1)["purity"], .5)
    assert near(s.depolarize(.7, .8, 1)["p0"], .5)


def test_parameter_shift():
    for t in (0, .2, .7, 1.4, math.pi):
        assert near(s.parameter_shift(t), -math.sin(t))
        h = 1e-5
        assert abs(s.parameter_shift(t) - (s.expectation(t + h) - s.expectation(t - h)) / (2 * h)) < 1e-8


def test_entropy():
    assert near(s.entropy(0), 0) and near(s.entropy(1), 0) and near(s.entropy(.5), 1)
    assert near(s.entropy(.2), s.entropy(.8))


def test_seeded_trials():
    assert s.trials(.3, 100) == s.trials(.3, 100)
    assert s.trials(0, 20)["hits"] == 0
    assert s.trials(1, 20)["hits"] == 20
    with pytest.raises(ValueError):
        s.trials(.2, 0)


def test_rng_matches_js_lcg():
    # First values of the JS LCG with seed 42, computed by hand from
    # state' = (1664525*state + 1013904223) mod 2^32.
    r = s.rng(42)
    st = 42
    for _ in range(5):
        st = (1664525 * st + 1013904223) % 2 ** 32
        assert r() == st / 2 ** 32


# ---- linear-algebra extensions (checked against closed forms) ------------

def test_closed_forms_agree_with_matrices():
    for t, ph in [(0.3, 0.1), (1.2, 2.0), (2.9, -1.0)]:
        rho = s.dm(s.ket(t, ph))
        q = s.qubit(t, ph)
        assert np.allclose(s.bloch(rho), [q["x"], q["y"], q["z"]])
        for p in (0, .3, 1):
            out = s.apply_kraus(rho, s.depolarizing_kraus(p))
            d = s.depolarize(t, ph, p)
            assert np.allclose(s.bloch(out), [d["x"], d["y"], d["z"]])
            assert near(s.purity(out), d["purity"])


def test_interference_matches_circuit():
    for phi in np.linspace(0, 2 * math.pi, 9):
        psi = s.H @ np.diag([1, np.exp(1j * phi)]) @ s.H @ s.KET0
        assert near(abs(psi[0]) ** 2, s.interference(phi)["p0"])


def test_channels_cptp_and_choi_psd():
    for kr in (s.depolarizing_kraus(.4), s.amplitude_damping_kraus(.3), s.dephasing_kraus(.6)):
        assert s.is_cptp(kr)
        J = s.choi(kr)
        assert np.min(np.linalg.eigvalsh(J)) > -1e-10
        # trace-preservation <=> Tr_out J = I
        assert np.allclose(s.partial_trace(J, keep=0), np.eye(2))


def test_bell_states_and_werner():
    phi = s.dm(s.bell_state())
    assert near(s.concurrence(phi), 1)
    assert near(s.von_neumann_entropy(s.partial_trace(phi, 0)), 1)
    q = math.pi / 4
    assert near(s.chsh_value(phi, 0, math.pi / 2, q, -q), 2 * math.sqrt(2))
    assert near(s.horodecki_max_chsh(phi), 2 * math.sqrt(2))
    for v in (0, .5, 1 / math.sqrt(2), .9):
        w = s.werner(v)
        assert s.is_density_matrix(w)
        assert near(s.horodecki_max_chsh(w), 2 * math.sqrt(2) * v)
        assert near(s.concurrence(w), max(0, (3 * v - 1) / 2))
    assert near(s.concurrence(s.werner(1 / 3)), 0)


def test_quantum_switch_trace_and_known_result():
    rho = s.dm(s.KET0)
    out = s.quantum_switch(rho, s.depolarizing_kraus(1), s.depolarizing_kraus(1))
    assert s.is_density_matrix(out)
    # Two completely depolarizing channels in a switch: the control is no longer
    # maximally mixed / |+>: <X_control> = 1/4 for a qubit target (d=2 gives 1/d^2).
    xc = float(np.real(np.trace(out @ s.kron(s.X, s.I2))))
    assert near(xc, 0.25)
    # In a definite order the composition is still completely depolarizing.
    seq = s.apply_kraus(s.apply_kraus(rho, s.depolarizing_kraus(1)), s.depolarizing_kraus(1))
    assert np.allclose(seq, np.eye(2) / 2)


def test_classical_shadow_is_unbiased():
    rho = s.dm(s.ket(1.0))
    r = s.classical_shadow_z(rho, 20000, seed=3)
    assert abs(r.estimates[-1] - r.truth) < 0.05


def test_vqc_parameter_shift_matches_finite_difference():
    for params, x in [([.1, .4], .3), ([1.0, -2.0], 1.7)]:
        g = s.vqc_gradient(params, x)
        h = 1e-6
        for k in range(2):
            p1 = list(params); p1[k] += h
            p2 = list(params); p2[k] -= h
            fd = (s.vqc_expectation(p1, x) - s.vqc_expectation(p2, x)) / (2 * h)
            assert abs(g[k] - fd) < 1e-7
