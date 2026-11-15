"""L6-09 Quantum counterfactual questions: four scenes.

ClassicalThreeSteps  Pearl's abduction, action, prediction on Y = X xor U, then a second model Y = U' with the
                     same interventional law and the opposite counterfactual answer.
DilationFamily       the completely dephasing channel written as a two-branch mixture of phase rotations
                     R_z(alpha), R_z(alpha + pi); Bayesian abduction on the factual record; the counterfactual
                     value kappa(alpha) = 1 - sin^2(alpha)/2 sweeps from 1 to 1/2 while the channel never changes;
                     then the bound kappa >= 1/2.
EnsembleChoice       one fixed dilation (controlled-Z, background I/2); the background's ensemble decomposition
                     along polar angle theta gives kappa(theta) = 1 - sin^2(theta)/2.
PureRewind           the pure CNOT dilation: holding the background fixed gives 1/2; the retrodictive "rewind"
                     rule produces the background |->, outside the support of the prior |0>, and gives 1.
Every number on screen is computed here; facts() lists strings that also appear in the lesson text.
"""
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, ORIGIN, PI, RIGHT, UP, UR, DR, Arrow, Axes, Circle, Create, Cross, DashedLine, Dot, FadeIn,
                   FadeOut, Indicate, Line, Rectangle, Scene, SurroundingRectangle, TracedPath, Transform,
                   TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

# ----------------------------------------------------------------------------------------------
# numbers (shared with the lesson text)
# ----------------------------------------------------------------------------------------------
PLUS = np.array([1, 1]) / math.sqrt(2)
MINUS = np.array([1, -1]) / math.sqrt(2)


def rz(a):
    return np.diag([np.exp(-1j * a / 2), np.exp(1j * a / 2)])


def kappa_alpha(a):
    """Bayes-abduction counterfactual for the two-branch dilation R_z(a), R_z(a + pi), prior 1/2 each."""
    phis = (a, a + math.pi)
    s = np.array([abs(MINUS @ rz(f) @ PLUS) ** 2 for f in phis])          # P(factual - | branch)
    post = s / s.sum()
    cf = np.array([abs(PLUS @ rz(f) @ MINUS) ** 2 for f in phis])        # P(+ | branch, input |->)
    return float(post @ cf)


def kappa_theta(t):
    """Ensemble choice for (CZ, I/2): members with Z weights sin^2(t/2), cos^2(t/2)."""
    z = np.array([math.sin(t / 2) ** 2, math.cos(t / 2) ** 2])
    q = np.array([0.5, 0.5])
    return float(np.sum(q * z * z) / np.sum(q * z))


for _a in np.linspace(0, math.pi / 2, 7):
    assert abs(kappa_alpha(_a) - (1 - 0.5 * math.sin(_a) ** 2)) < 1e-12
    assert abs(kappa_theta(_a) - (1 - 0.5 * math.sin(_a) ** 2)) < 1e-12
K_PI6 = kappa_alpha(math.pi / 6)
assert abs(K_PI6 - 0.875) < 1e-12 and abs(kappa_theta(math.pi / 3) - 0.625) < 1e-12

# pure CNOT dilation, rewind rule
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)
_post = np.kron(np.outer(MINUS, MINUS), np.eye(2)) @ CNOT @ np.kron(PLUS, [1, 0])
P_FACT = float(np.vdot(_post, _post).real)
_rew = CNOT.conj().T @ (_post / math.sqrt(P_FACT))
assert abs(P_FACT - 0.5) < 1e-12 and np.allclose(_rew, np.kron(PLUS, MINUS))


def facts(L):
    """Strings the animations put on screen; each also appears in the lesson text."""
    return ["Y = X \\oplus U", "1 - \\tfrac{1}{2}\\sin^2\\alpha", "0.875", "0.625",
            "\\kappa = 2\\sum_k q_k z_k^2", "|+\\rangle|-\\rangle"]


def node(name, pos, color=INK, r=0.42):
    c = Circle(radius=r, color=color, stroke_width=4).move_to(pos)
    t = eq(name, size=36, color=color).move_to(pos)
    return VGroup(c, t)


def link(a, b, color=MUTED):
    return Arrow(a[0].get_center(), b[0].get_center(), buff=0.45, color=color, stroke_width=5,
                 max_tip_length_to_length_ratio=0.18)


def bars(vals, names, origin, color, width=0.55, height=1.6):
    g = VGroup()
    for k, (v, n) in enumerate(zip(vals, names)):
        x = origin + RIGHT * k * (width + 0.75)
        r = Rectangle(width=width, height=max(v * height, 0.02), color=color, fill_opacity=0.75, stroke_width=0)
        r.move_to(x + UP * max(v * height, 0.02) / 2)
        g.add(VGroup(r, eq(n, size=30).next_to(x, DOWN, buff=0.15),
                     eq(f"{v:g}", size=28, color=MUTED).next_to(r, UP, buff=0.08)))
    return g


class ClassicalThreeSteps(Scene):
    def construct(self):
        title = label("A classical counterfactual: abduction, action, prediction", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        ux = node("U_X", LEFT * 5.6 + UP * 1.4, MUTED)
        x = node("X", LEFT * 5.6 + DOWN * 0.6, BLUE)
        u = node("U", LEFT * 2.6 + UP * 1.4, MUTED)
        y = node("Y", LEFT * 2.6 + DOWN * 0.6, VIOLET)
        e_ux, e_xy, e_uy = link(ux, x), link(x, y), link(u, y)
        self.play(*[FadeIn(m) for m in (ux, x, u, y)], Create(e_ux), Create(e_xy), Create(e_uy))
        model = VGroup(eq(r"Y = X \oplus U", size=40), eq(r"U \sim \mathrm{Bern}(\tfrac{1}{2})", size=34, color=MUTED))
        model.arrange(DOWN, aligned_edge=LEFT).move_to(RIGHT * 2.6 + UP * 2.0)
        self.play(Write(model))

        step = label("1. Evidence", 28, AMBER, "BOLD").move_to(RIGHT * 1.4 + UP * 0.6).align_to(model, LEFT)
        ev = eq(r"X = 1,\ Y = 1", size=38, color=AMBER).next_to(step, RIGHT, buff=0.4)
        self.play(FadeIn(step), Write(ev), Indicate(x), Indicate(y))

        step2 = label("2. Abduction", 28, AMBER, "BOLD").move_to(step).align_to(step, LEFT)
        ab = eq("U", "=", r"X \oplus Y", size=38).next_to(step2, RIGHT, buff=0.4)
        ab2 = eq("U", "=", r"1 \oplus 1", "= 0", size=38).next_to(step2, RIGHT, buff=0.4)
        self.play(Transform(step, step2), FadeOut(ev), Write(ab))
        self.play(TransformMatchingTex(ab, ab2))
        prior = bars([0.5, 0.5], ["U=0", "U=1"], RIGHT * 1.6 + DOWN * 2.6, CYAN)
        post = bars([1, 0], ["U=0", "U=1"], RIGHT * 1.6 + DOWN * 2.6, CYAN)
        cap = label("P(U | evidence)", 24, MUTED).next_to(prior, RIGHT, buff=0.5).shift(UP * 0.4)
        self.play(FadeIn(prior), FadeIn(cap))
        self.play(Transform(prior, post), run_time=1.4)

        step3 = label("3. Action", 28, AMBER, "BOLD").move_to(step).align_to(step, LEFT)
        act = eq(r"\mathrm{do}(X = 0)", size=38).next_to(step3, RIGHT, buff=0.4)
        self.play(Transform(step, step3), FadeOut(ab2), Write(act))
        cut = Cross(e_ux, stroke_color=RED, stroke_width=6, scale_factor=0.35)
        x0 = node("0", x.get_center(), RED)
        self.play(Create(cut), Transform(x, x0))

        step4 = label("4. Prediction", 28, AMBER, "BOLD").move_to(step).align_to(step, LEFT)
        pr = eq(r"Y_{X=0} = 0 \oplus 0 = 0", size=38, color=VIOLET).next_to(step4, RIGHT, buff=0.4)
        self.play(Transform(step, step4), FadeOut(act), Write(pr))
        self.wait(1.0)

        # a second model with the same interventional law
        self.play(FadeOut(VGroup(prior, cap, pr, step, cut)), Transform(x, node("X", x.get_center(), BLUE)))
        model2 = VGroup(eq(r"Y = U'", size=40, color=RED), eq(r"U' \sim \mathrm{Bern}(\tfrac{1}{2})", size=34, color=MUTED))
        model2.arrange(DOWN, aligned_edge=LEFT).move_to(model).align_to(model, LEFT)
        self.play(FadeOut(e_xy), Transform(model, model2))
        same = eq(r"P(Y = 1 \mid \mathrm{do}(X = x)) = \tfrac{1}{2}\ \text{in both models}", size=34).move_to(RIGHT * 2.4 + UP * 0.5)
        self.play(Write(same))
        ans = VGroup(eq(r"\text{Model 1: } P(Y_{X=0} = 1 \mid X{=}1, Y{=}1) = 0", size=32, color=VIOLET),
                     eq(r"\text{Model 2: } P(Y_{X=0} = 1 \mid X{=}1, Y{=}1) = 1", size=32, color=RED))
        ans.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(RIGHT * 2.4 + DOWN * 1.0)
        self.play(Write(ans[0]))
        self.play(Write(ans[1]))
        note = label("Same interventions, opposite counterfactuals: the model must be given.", 26, MUTED)
        note.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note))
        self.wait(2.0)


def equator(center, R):
    circ = Circle(radius=R, color=MUTED, stroke_width=3).move_to(center)
    ax = VGroup(DashedLine(center + LEFT * (R + 0.3), center + RIGHT * (R + 0.3), color=GRID),
                DashedLine(center + DOWN * (R + 0.3), center + UP * (R + 0.3), color=GRID))
    return VGroup(ax, circ)


class DilationFamily(Scene):
    def construct(self):
        title = label("One channel, a family of dilations", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        C, R = LEFT * 4.1 + DOWN * 0.4, 2.0
        eqt = equator(C, R)
        lp = eq(r"|+\rangle", size=32, color=BLUE).next_to(C + RIGHT * R, RIGHT, buff=0.12)
        lm = eq(r"|-\rangle", size=32, color=MUTED).next_to(C + LEFT * R, LEFT, buff=0.12)
        cap = label("equator of the Bloch sphere", 22, MUTED).next_to(eqt, DOWN, buff=0.15)
        self.play(Create(eqt), FadeIn(lp), FadeIn(lm), FadeIn(cap))
        rule = VGroup(eq(r"V_\lambda = R_z(\alpha + \lambda\pi),\ \ \lambda \in \{0, 1\}", size=32),
                      eq(r"\tfrac{1}{2}\textstyle\sum_\lambda V_\lambda \rho V_\lambda^\dagger = \Delta(\rho)\ \text{for every } \alpha",
                         size=30, color=MUTED))
        rule.arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(RIGHT * 2.7 + UP * 2.35)
        self.play(Write(rule))
        query = VGroup(eq(r"\text{fact: input } |+\rangle,\ \text{X outcome } -", size=28, color=AMBER),
                       eq(r"\text{query: had the input been } |-\rangle,\ P(+)?", size=28, color=AMBER))
        query.arrange(DOWN, aligned_edge=LEFT, buff=0.1).next_to(rule, DOWN, buff=0.2).align_to(rule, LEFT)
        self.play(FadeIn(query))

        a = ValueTracker(0.0)

        def branch_dots():
            al = a.get_value()
            w0, w1 = math.sin(al / 2) ** 2, math.cos(al / 2) ** 2          # posterior weights
            g = VGroup()
            for phi, w, col in ((al, w0, VIOLET), (al + PI, w1, RED)):
                p = C + R * np.array([math.cos(phi), math.sin(phi), 0])
                g.add(Line(C, p, color=col, stroke_width=3), Dot(p, radius=0.06 + 0.22 * w, color=col, fill_opacity=0.85))
            return g

        dots = always_redraw(branch_dots)
        self.play(FadeIn(dots))
        ax = Axes(x_range=[0, PI / 2, PI / 8], y_range=[0.4, 1.0, 0.1], x_length=5.6, y_length=2.6,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 2.9 + DOWN * 1.65)
        ylab = eq(r"\kappa(\alpha)", size=30).next_to(ax, UP, buff=0.12).align_to(ax, LEFT)
        xlab = eq(r"\alpha", size=30).next_to(ax.x_axis, RIGHT, buff=0.1)
        ticks = VGroup(eq("0", size=24).next_to(ax.c2p(0, 0.4), DOWN, buff=0.12),
                       eq(r"\tfrac{\pi}{2}", size=24).next_to(ax.c2p(PI / 2, 0.4), DOWN, buff=0.12),
                       eq("1", size=24).next_to(ax.c2p(0, 1.0), LEFT, buff=0.12),
                       eq(r"\tfrac{1}{2}", size=24).next_to(ax.c2p(0, 0.5), LEFT, buff=0.12))
        flat = DashedLine(ax.c2p(0, 0.5), ax.c2p(PI / 2, 0.5), color=CYAN, stroke_width=4)
        flab = label("intervention: 1/2", 22, CYAN).next_to(ax.c2p(PI / 8, 0.5), UP, buff=0.12)
        formula = eq(r"= 1 - \tfrac{1}{2}\sin^2\alpha", size=30, color=VIOLET).next_to(ylab, RIGHT, buff=0.12)
        self.play(Create(ax), Write(ylab), Write(xlab), FadeIn(ticks), Create(flat), FadeIn(flab), Write(formula))
        tr_dot = always_redraw(lambda: Dot(ax.c2p(a.get_value(), kappa_alpha(a.get_value())), color=VIOLET, radius=0.07))
        trace = TracedPath(tr_dot.get_center, stroke_color=VIOLET, stroke_width=4)
        self.add(trace, tr_dot)
        self.play(a.animate.set_value(PI / 6), run_time=3, rate_func=linear)
        mark = eq(rf"\alpha = \tfrac{{\pi}}{{6}}:\ \kappa = {K_PI6:.3f}", size=28, color=VIOLET)
        mark.next_to(ax.c2p(PI / 6, K_PI6), UR, buff=0.12)
        self.play(FadeIn(mark))
        self.wait(0.6)
        self.play(FadeOut(mark))
        self.play(a.animate.set_value(PI / 2), run_time=5, rate_func=linear)
        self.wait(0.8)

        # the bound
        self.play(FadeOut(VGroup(rule, query)))
        b1 = eq(r"\kappa = ", r"{\sum_k q_k z_k^2", r"\over", r"\sum_k q_k z_k}", size=34)
        b2 = eq(r"\kappa = 2\sum_k q_k z_k^2", r"\ \ge\ 2\Big(\sum_k q_k z_k\Big)^2 = \tfrac{1}{2}", size=34)
        b1.move_to(RIGHT * 2.7 + UP * 2.2)
        b2.move_to(RIGHT * 2.7 + UP * 2.2)
        why = eq(r"\textstyle\sum_k q_k z_k = \tfrac{1}{2}\ \text{(complete dephasing)}", size=28, color=MUTED)
        why.next_to(b1, DOWN, buff=0.3)
        self.play(Write(b1))
        self.play(FadeIn(why))
        self.play(TransformMatchingTex(b1, b2), run_time=1.6)
        self.play(Create(SurroundingRectangle(b2, color=AMBER, buff=0.15)))
        self.wait(2.0)
        _ = (ORIGIN, Transform, Rectangle)


class EnsembleChoice(Scene):
    def construct(self):
        title = label("Same unitary, same background state, different ensembles", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        C, R = LEFT * 4.1 + DOWN * 0.5, 2.0
        disk = Circle(radius=R, color=MUTED, stroke_width=3).move_to(C)
        axes = VGroup(DashedLine(C + DOWN * (R + 0.3), C + UP * (R + 0.3), color=GRID),
                      DashedLine(C + LEFT * (R + 0.3), C + RIGHT * (R + 0.3), color=GRID))
        z0 = eq(r"|0\rangle", size=30, color=MUTED).next_to(C + UP * R, UR, buff=0.08)
        z1 = eq(r"|1\rangle", size=30, color=MUTED).next_to(C + DOWN * R, DR, buff=0.08)
        cen = Dot(C, color=INK, radius=0.07)
        clab = eq(r"\text{center: } \sigma = I/2", size=28).move_to(C + UP * (R + 0.35) + LEFT * 1.4)
        self.play(Create(axes), Create(disk), FadeIn(z0), FadeIn(z1), FadeIn(cen), FadeIn(clab))
        setup = VGroup(eq(r"U = \mathrm{CZ},\ \ \text{background } \sigma = I/2", size=32),
                       eq(r"\mathcal{E}_k(\rho) = (1 - z_k)\rho + z_k Z\rho Z", size=32),
                       eq(r"z_0 = \sin^2\tfrac{\theta}{2},\ \ z_1 = \cos^2\tfrac{\theta}{2}", size=30, color=MUTED))
        setup.arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(RIGHT * 2.7 + UP * 2.0)
        self.play(Write(setup[0]))
        self.play(Write(setup[1]), Write(setup[2]))

        th = ValueTracker(0.0)

        def diam():
            t = th.get_value()
            d = np.array([math.sin(t), math.cos(t), 0])
            w0, w1 = math.sin(t / 2) ** 2, math.cos(t / 2) ** 2                  # posterior weights
            return VGroup(Line(C - R * d, C + R * d, color=VIOLET, stroke_width=4),
                          Dot(C + R * d, radius=0.06 + 0.22 * w0, color=VIOLET, fill_opacity=0.85),
                          Dot(C - R * d, radius=0.06 + 0.22 * w1, color=RED, fill_opacity=0.85))

        dg = always_redraw(diam)
        self.play(FadeIn(dg))
        ax = Axes(x_range=[0, PI / 2, PI / 8], y_range=[0.4, 1.0, 0.1], x_length=5.6, y_length=2.4,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 2.9 + DOWN * 1.9)
        ylab = eq(r"\kappa(\theta) = 1 - \tfrac{1}{2}\sin^2\theta", size=30, color=VIOLET).next_to(ax, UP, buff=0.12).align_to(ax, LEFT)
        xlab = eq(r"\theta", size=30).next_to(ax.x_axis, RIGHT, buff=0.1)
        flat = DashedLine(ax.c2p(0, 0.5), ax.c2p(PI / 2, 0.5), color=CYAN, stroke_width=4)
        ticks = VGroup(eq("1", size=24).next_to(ax.c2p(0, 1.0), LEFT, buff=0.12),
                       eq(r"\tfrac{1}{2}", size=24).next_to(ax.c2p(0, 0.5), LEFT, buff=0.12),
                       eq(r"\tfrac{\pi}{2}", size=24).next_to(ax.c2p(PI / 2, 0.4), DOWN, buff=0.12))
        self.play(Create(ax), Write(ylab), Write(xlab), Create(flat), FadeIn(ticks))
        d = always_redraw(lambda: Dot(ax.c2p(th.get_value(), kappa_theta(th.get_value())), color=VIOLET, radius=0.07))
        trace = TracedPath(d.get_center, stroke_color=VIOLET, stroke_width=4)
        self.add(trace, d)
        self.play(th.animate.set_value(PI / 3), run_time=4, rate_func=linear)
        m = eq(rf"\theta = \tfrac{{\pi}}{{3}}:\ \kappa = {kappa_theta(PI / 3):.3f}", size=28, color=VIOLET)
        m.next_to(ax.c2p(PI / 3, kappa_theta(PI / 3)), UR, buff=0.1)
        self.play(FadeIn(m))
        self.wait(0.5)
        self.play(FadeOut(m), th.animate.set_value(PI / 2), run_time=2.5, rate_func=linear)
        self.wait(0.5)

        # classical contrast
        self.play(FadeOut(setup))
        simplex = VGroup(Line(RIGHT * 1.0 + UP * 2.1, RIGHT * 4.2 + UP * 2.1, color=BLUE, stroke_width=5),
                         Dot(RIGHT * 1.0 + UP * 2.1, color=BLUE), Dot(RIGHT * 4.2 + UP * 2.1, color=BLUE),
                         Dot(RIGHT * 2.6 + UP * 2.1, color=INK, radius=0.08))
        stext = label("classical bit: one way to split (1/2, 1/2) into point masses", 24, BLUE)
        stext.next_to(simplex, DOWN, buff=0.2).shift(RIGHT * 0.4)
        qtext = label("qubit: every diameter splits I/2 into pure states", 24, VIOLET).next_to(stext, DOWN, buff=0.15).align_to(stext, LEFT)
        self.play(Create(simplex), FadeIn(stext))
        self.play(FadeIn(qtext))
        self.wait(2.0)


class PureRewind(Scene):
    def construct(self):
        title = label("A pure background: hold it fixed, or rewind it?", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        setup = eq(r"U = \mathrm{CNOT}_{S \to E},\ \ \text{background } |0\rangle_E", size=34).move_to(UP * 2.4)
        self.play(Write(setup))
        l1 = eq(r"\mathrm{CNOT}\,|+\rangle|0\rangle", r"=", r"\tfrac{1}{\sqrt{2}}(|00\rangle + |11\rangle)", size=36)
        l2 = eq(r"(|-\rangle\langle-| \otimes I)", r"\tfrac{1}{\sqrt{2}}(|00\rangle + |11\rangle)", r"=", r"\tfrac{1}{\sqrt{2}}\,|-\rangle|-\rangle", size=36)
        l3 = eq(r"\mathrm{CNOT}^\dagger", r"|-\rangle|-\rangle", r"=", r"|+\rangle|-\rangle", size=36)
        for m in (l1, l2, l3):
            m.move_to(UP * 1.3 + LEFT * 1.6)
        self.play(Write(l1))
        self.wait(0.5)
        self.play(TransformMatchingTex(l1, l2), run_time=1.6)
        pf = label(f"factual outcome - has probability {P_FACT:g}", 24, MUTED).next_to(l2, DOWN, buff=0.2)
        self.play(FadeIn(pf))
        self.wait(0.6)
        self.play(FadeOut(pf), TransformMatchingTex(l2, l3), run_time=1.6)
        rw = label("rewound to the input time", 24, MUTED).next_to(l3, DOWN, buff=0.2)
        self.play(FadeIn(rw))

        # Bloch disk: prior |0>, posterior |->
        C, R = RIGHT * 4.6 + UP * 0.2, 1.4
        disk = Circle(radius=R, color=MUTED, stroke_width=3).move_to(C)
        pr = Arrow(C, C + UP * R, buff=0, color=CYAN, stroke_width=6)
        po = Arrow(C, C + LEFT * R, buff=0, color=RED, stroke_width=6)
        prl = eq(r"\text{prior } |0\rangle", size=28, color=CYAN).next_to(C + UP * R, UP, buff=0.08)
        pol = eq(r"\text{rewound } |-\rangle", size=28, color=RED).next_to(C + LEFT * R, LEFT, buff=0.12)
        self.play(Create(disk), Create(pr), FadeIn(prl))
        self.play(Create(po), FadeIn(pol))
        supp = label("outside the prior's support", 24, RED).next_to(disk, DOWN, buff=0.5)
        self.play(FadeIn(supp))

        res = VGroup(eq(r"\text{hold } |0\rangle_E \text{ fixed:}\ \ \kappa = \tfrac{1}{2}", size=34, color=CYAN),
                     eq(r"\text{rewind to } |-\rangle_E:\ \ \kappa = 1", size=34, color=RED))
        res.arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(LEFT * 2.6 + DOWN * 1.7)
        self.play(Write(res[0]))
        self.play(Write(res[1]))
        note = label("Both rules use the same channel and the same dilation.", 26, MUTED).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note))
        self.wait(2.0)
