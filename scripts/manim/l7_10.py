"""L7-10 Open problems and critical synthesis: three scenes.

ClaimAudit        a hypothetical hype claim stripped to what the lesson's computation shows (identified for 1/2
                  of the common-cause class with exact data; 0.044 wrong at 100 shots per basis), then the
                  quantifier ladder that a separation claim needs.
CutInflation      the triangle network, its cut inflation, the contradiction 1 = P(A2 = C1) = 1/2 for perfect
                  three-way correlation, and the noisy family: the cut inflation is feasible iff v <= 1/2.
OpenProblemAtlas  MovingCameraScene tour of six open-problem cards: known, open, solved when.
Numbers come from qcai/lessonfigs/l7_10.py and are checked against the lesson text by facts().
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Circle, Create, Cross, DashedLine, FadeIn, FadeOut, Line,
                   MovingCameraScene, Rectangle, RoundedRectangle, Scene, Square, Transform, TransformMatchingTex,
                   ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, INK, MUTED, RED, VIOLET, eq, label
from qcai.lessonfigs import l7_10 as M

AUD = M.audit()
ROW100 = [r for r in AUD["rows"] if r[0] == 100][0]
WRONG100 = f"{ROW100[3]:.3f}"
assert WRONG100 == "0.044" and abs(AUD["exact_correct"] - 0.5) < 0.02 and AUD["exact_wrong"] == 0.0
assert M.cut_inflation_slack(0.5) < 1e-9 and M.cut_inflation_slack(0.55) > 1e-4


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["0.044", r"P(A_2 = C_1) = 1/2", r"v \le 1/2", r"2^{\Omega(n)}", "Inflation hierarchies",
            "Certifying indefinite causal order", "Trainable yet not simulable?"]


class ClaimAudit(Scene):
    def construct(self):
        title = label("Auditing a claim: what was actually shown?", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        claim = VGroup(label("\u201cOur quantum causal learner tells cause from common cause", 26, INK),
                       label("with perfect accuracy: an exponential advantage.\u201d", 26, INK)).arrange(DOWN, buff=0.12)
        box = RoundedRectangle(width=claim.width + 0.6, height=claim.height + 0.45, corner_radius=0.15, color=MUTED,
                               stroke_width=2.5)
        cl = VGroup(box, claim).move_to(UP * 2.2)
        tag = label("a hypothetical claim", 22, MUTED).next_to(box, DOWN, buff=0.08).align_to(box, RIGHT)
        self.play(FadeIn(cl), FadeIn(tag))
        self.wait(0.8)
        rows = [("quantum causal learner", "a Pauli-correlation test on two qubits"),
                ("cause vs common cause", "only inside the two model classes of L7-05"),
                ("perfect accuracy", "exact data: identified for 1/2 of the class"),
                ("", f"100 shots per basis: {WRONG100} wrong"),
                ("exponential advantage", "no speed-up: an identifiability gap")]
        y = 0.75
        group = VGroup()
        for left, right in rows:
            r = label(right, 24, VIOLET).move_to(np.array([-0.4, y, 0]), aligned_edge=LEFT)
            items = [r]
            if left:
                lft = label(left, 24, RED).move_to(np.array([-3.6, y, 0]))
                strike = Line(lft.get_left(), lft.get_right(), color=RED, stroke_width=3)
                arr = Arrow(np.array([-1.25, y, 0]), np.array([-0.6, y, 0]), buff=0, color=MUTED, stroke_width=3,
                            max_tip_length_to_length_ratio=0.35)
                items = [lft, strike, arr, r]
                self.play(FadeIn(lft), run_time=0.5)
                self.play(Create(strike), Create(arr), FadeIn(r), run_time=0.9)
            else:
                self.play(FadeIn(r), run_time=0.7)
            group.add(*items)
            self.wait(0.7)
            y -= 0.62
        self.wait(1.5)
        self.play(FadeOut(group), FadeOut(cl), FadeOut(tag))

        head = label("What a separation claim has to prove", 28, INK, "BOLD").move_to(UP * 2.4)
        self.play(FadeIn(head))
        q1 = eq(r"\exists\, x:\ \mathrm{cost}_A(x) < \mathrm{cost}_B(x)", size=38).move_to(UP * 1.4)
        l1 = label("a simulation: one instance, one baseline", 24, MUTED).next_to(q1, DOWN, buff=0.15)
        self.play(Write(q1), FadeIn(l1))
        self.wait(1.2)
        q2 = eq(r"\forall x \in \mathcal{X}_n:\ \mathrm{cost}_A(x) \le \mathrm{poly}(n)", size=38, color=BLUE).move_to(DOWN * 0.15)
        l2 = label("an upper bound for A on every instance", 24, MUTED).next_to(q2, DOWN, buff=0.15)
        q3 = eq(r"\forall B\ \exists x \in \mathcal{X}_n:\ \mathrm{cost}_B(x) \ge 2^{\Omega(n)}", size=38, color=VIOLET).move_to(DOWN * 1.75)
        l3 = label("a lower bound against every classical B with the same access", 24, MUTED).next_to(q3, DOWN, buff=0.15)
        self.play(Write(q2), FadeIn(l2))
        self.wait(1)
        self.play(Write(q3), FadeIn(l3))
        self.wait(1)
        gap = Cross(VGroup(q1, l1), stroke_color=RED, stroke_width=4, scale_factor=0.9)
        self.play(Create(gap))
        note = label("the first line implies neither of the others", 26, RED).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note))
        self.wait(2.5)


def party(name, pos, color=INK):
    c = Circle(radius=0.34, color=color, stroke_width=4, fill_color="#ffffff", fill_opacity=1).move_to(pos)
    return VGroup(c, eq(name, size=30, color=color).move_to(pos))


def source(name, pos, color=MUTED):
    s = Square(side_length=0.42, color=color, stroke_width=3, fill_color="#ffffff", fill_opacity=1).move_to(pos)
    return VGroup(s, eq(name, size=26, color=color).move_to(pos))


def link(s, p, color=MUTED):
    return Arrow(s.get_center(), p.get_center(), buff=0.36, color=color, stroke_width=3, max_tip_length_to_length_ratio=0.2)


class CutInflation(Scene):
    def construct(self):
        title = label("Inflation: copy the sources, demand consistency", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        cA, cB, cC = np.array([-4.2, 1.9, 0]), np.array([-5.6, -0.4, 0]), np.array([-2.8, -0.4, 0])
        A, B, C = party("A", cA), party("B", cB), party("C", cC)
        g = source(r"\gamma", (cA + cB) / 2 + LEFT * 0.35)
        al = source(r"\alpha", (cB + cC) / 2 + DOWN * 0.45)
        be = source(r"\beta", (cA + cC) / 2 + RIGHT * 0.35)
        tri = VGroup(link(g, A), link(g, B), link(al, B), link(al, C), link(be, A), link(be, C), g, al, be, A, B, C)
        self.play(FadeIn(tri), run_time=1.5)
        tl = label("triangle network", 24, MUTED).move_to(np.array([-4.2, -1.45, 0]))
        tgt = eq(r"A = B = C,\ \text{each a fair bit}", size=32).move_to(np.array([-4.2, -2.1, 0]))
        self.play(FadeIn(tl), Write(tgt))
        self.wait(0.8)

        y = 1.2
        xs = {"b2": -0.4, "A2": 0.6, "g": 1.6, "B1": 2.6, "a": 3.6, "C1": 4.6, "b1": 5.6}
        A2, B1, C1 = (party(n, np.array([xs[k], y, 0])) for n, k in (("A_2", "A2"), ("B_1", "B1"), ("C_1", "C1")))
        g1 = source(r"\gamma", np.array([xs["g"], y + 0.9, 0]))
        a1 = source(r"\alpha", np.array([xs["a"], y + 0.9, 0]))
        b2 = source(r"\beta_2", np.array([xs["b2"], y + 0.9, 0]), AMBER)
        b1 = source(r"\beta_1", np.array([xs["b1"], y + 0.9, 0]), AMBER)
        inf = VGroup(link(g1, A2), link(g1, B1), link(a1, B1), link(a1, C1), link(b2, A2, AMBER), link(b1, C1, AMBER),
                     g1, a1, b1, b2, A2, B1, C1)
        il = label("cut inflation: two independent copies of beta", 24, MUTED).move_to(np.array([2.6, 0.25, 0]))
        self.play(FadeIn(inf), FadeIn(il), run_time=1.6)
        cons = VGroup(eq(r"Q(A_2, B_1) = P(A, B)", size=30), eq(r"Q(B_1, C_1) = P(B, C)", size=30),
                      eq(r"Q(A_2, C_1) = P(A)\,P(C)", size=30, color=AMBER)).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        cons.move_to(np.array([2.6, -1.0, 0]))
        self.play(Write(cons), run_time=2)
        self.wait(1)
        d1 = eq(r"A_2 = B_1,\ B_1 = C_1 \Rightarrow P(A_2 = C_1) = 1", size=32).move_to(np.array([2.3, -2.5, 0]))
        d2 = eq(r"\text{independence: } P(A_2 = C_1) = 1/2", size=32, color=AMBER).move_to(np.array([2.3, -3.2, 0]))
        self.play(Write(d1))
        self.play(Write(d2))
        x = Cross(tgt, stroke_color=RED, stroke_width=5, scale_factor=0.8)
        verdict = label("incompatible with the triangle", 26, RED).move_to(np.array([-4.2, -2.8, 0]))
        self.play(Create(x), FadeIn(verdict))
        self.wait(1.5)

        # noisy family
        self.play(FadeOut(VGroup(cons, d1, d2, x, verdict, tgt)))
        tgt2 = eq(r"P_v = v\,P_{\mathrm{GHZ}} + (1 - v)\,P_{\mathrm{unif}}", size=30).move_to(np.array([-4.2, -2.1, 0]))
        self.play(Write(tgt2))
        t1 = eq(r"P(A_2 \ne C_1) \le P(A_2 \ne B_1) + P(B_1 \ne C_1)", size=30).move_to(np.array([2.6, -0.65, 0]))
        t2 = eq(r"\tfrac12 \le \tfrac{1-v}{2} + \tfrac{1-v}{2} = 1 - v", size=30).move_to(np.array([2.6, -1.35, 0]))
        t3 = eq(r"\text{feasible only if } v \le 1/2", size=32, color=VIOLET).move_to(np.array([2.6, -2.0, 0]))
        self.play(Write(t1))
        self.play(Write(t2))
        self.play(Write(t3))
        v = ValueTracker(0.0)
        base = np.array([-1.0, -3.5, 0])
        scale = 2.2

        def bars():
            vv = v.get_value()
            h1, h2 = (1 - vv) * scale, 0.5 * scale
            r1 = Rectangle(width=0.5, height=max(h1, 0.01), color=VIOLET, fill_opacity=0.7, stroke_width=1)
            r1.move_to(base + RIGHT * 0.0 + UP * h1 / 2)
            r2 = Rectangle(width=0.5, height=h2, color=AMBER, fill_opacity=0.7, stroke_width=1).move_to(base + RIGHT * 0.8 + UP * h2 / 2)
            bad = vv > 0.5 + 1e-9
            msg = label("incompatible: certified" if bad else "this test is silent", 24, RED if bad else MUTED)
            msg.move_to(base + RIGHT * 4.2 + UP * 0.35)
            vl = label(f"v = {vv:.2f}", 24, INK).move_to(base + RIGHT * 4.2 + UP * 0.95)
            return VGroup(r1, r2, msg, vl)

        bl = VGroup(label("1 - v", 22, VIOLET).move_to(base + DOWN * 0.25), label("1/2", 22, AMBER).move_to(base + RIGHT * 0.8 + DOWN * 0.25))
        dyn = always_redraw(bars)
        self.add(dyn)
        self.play(FadeIn(bl))
        self.play(v.animate.set_value(1.0), run_time=6, rate_func=linear)
        self.play(v.animate.set_value(0.6), run_time=1.5)
        self.wait(2)
        _ = (DashedLine, Transform, TransformMatchingTex, BLUE)


CARDS = [
    ("Latent quantum causal discovery",
     ["full process matrix: Markov test and model;", "unravelling under bounded information loss"],
     ["what is identifiable when some quantum", "systems are latent and access is limited?"],
     ["equivalence classes characterized, plus a", "sound, complete, finite-sample algorithm"]),
    ("Inflation hierarchies",
     ["classical hierarchy converges; a modified", "quantum one converges (commuting operators)"],
     ["is the original quantum hierarchy complete?", "which level is needed in practice?"],
     ["a convergence proof or a counterexample,", "with explicit level bounds"]),
    ("Certifying indefinite causal order",
     ["witnesses certify nonseparability of the", "switch, assuming trusted devices"],
     ["are causal-inequality violations physical?", "certification with weaker assumptions?"],
     ["a test no causally ordered process passes,", "with every device assumption stated"]),
    ("Trainable yet not simulable?",
     ["barren plateaus for random deep circuits;", "many plateau-free models are simulable"],
     ["a model family provably trainable and not", "efficiently classically simulable?"],
     ["a proof of both for one family, or a", "general simulation theorem"]),
    ("Dequantization and the power of data",
     ["classical learners with data can rival", "quantum models; some speedups dequantized"],
     ["natural tasks on classical data with an", "end-to-end provable advantage?"],
     ["a separation against all classical algorithms", "with equal access, data loading counted"]),
    ("Quantum causal representations",
     ["latent causal variables are identifiable", "only under assumptions such as interventions"],
     ["does quantum measurement structure help", "identify them?"],
     ["an identifiability theorem that fails", "without the quantum structure"]),
]


def card(title, known, open_, done, center):
    box = RoundedRectangle(width=7.4, height=4.7, corner_radius=0.25, color=VIOLET, stroke_width=3).move_to(center)
    t = label(title, 26, INK, "BOLD").move_to(center + UP * 1.95)
    lines = VGroup()
    yy = 1.3
    for head, body, col in (("Known", known, BLUE), ("Open", open_, RED), ("Solved when", done, VIOLET)):
        h = label(head, 20, col, "BOLD").move_to(center + np.array([-3.3, yy, 0]), aligned_edge=LEFT)
        lines.add(h)
        yy -= 0.36
        for b in body:
            lines.add(label(b, 19, INK).move_to(center + np.array([-3.2, yy, 0]), aligned_edge=LEFT))
            yy -= 0.33
        yy -= 0.08
    return box, t, lines


class OpenProblemAtlas(MovingCameraScene):
    def construct(self):
        frame = self.camera.frame
        centers = [np.array([x, y, 0]) for y in (2.7, -2.7) for x in (-8.0, 0.0, 8.0)]
        built = [card(*c, center) for c, center in zip(CARDS, centers)]
        frame.set(width=25.5).move_to(np.array([0, 0.4, 0]))
        head = label("Six open problems at the quantum causal frontier", 44, INK, "BOLD").move_to(np.array([0, 5.9, 0]))
        sub = label("each card: what is known, the open question, and how one would know it is solved", 30, MUTED)
        sub.next_to(head, DOWN, buff=0.15)
        self.play(FadeIn(head), FadeIn(sub))
        self.play(*[Create(b) for b, _, _ in built], *[FadeIn(t) for _, t, _ in built], run_time=2)
        self.wait(1)
        for (b, t, lines), c in zip(built, centers):
            self.play(frame.animate.set(width=9.8).move_to(c), run_time=0.6)
            self.play(FadeIn(lines, lag_ratio=0.15), run_time=1.6)
            self.wait(2.6)
        self.play(frame.animate.set(width=25.5).move_to(np.array([0, 0.4, 0])), run_time=1.2)
        end = label("open in the cited sources as of writing; the 'solved when' tests are this lesson's criteria", 28, MUTED)
        end.move_to(np.array([0, -5.6, 0]))
        self.play(FadeIn(end))
        self.wait(2.5)
