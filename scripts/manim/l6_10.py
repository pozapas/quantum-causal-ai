"""L6-10 Design a quantum causal experiment: four scenes.

DesignPipeline  the two hypotheses as graphs (common source versus direct channel), then the design pipeline from
                question to decision rule, each stage filled with the concrete choice made in the lesson.
WitnessSpectra  XX + YY + ZZ = 2 SWAP - I and its partial transpose 2|Omega><Omega| - I give the ranges
                [-3, 1] (common cause) and [-1, 3] (cause-effect) of S = c_x + c_y + c_z; a mixture point
                S = 3v(2p - 1) slides along the number line through the three verdict regions.
ShotsSharpen    exact sampling distributions of the estimate under the boundary null (S = 1) and the planned
                alternative (S = 1.35) for N = 30, 100, 300, 579 shots per setting, with the Hoeffding threshold.
PowerCurve      exact power against N with the Hoeffding guarantee, and the planned N = 579.
Every number on screen is computed here; facts() lists strings that also appear in the lesson text.
"""
import math
import pathlib
import sys

import numpy as np
from scipy.stats import binom

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, PI, RIGHT, UP, Arrow, Axes, Circle, Create, DashedLine, Dot, FadeIn, FadeOut, Line,
                   NumberLine, Rectangle, RoundedRectangle, Scene, SurroundingRectangle, TracedPath, Transform,
                   TransformMatchingTex, ValueTracker, VGroup, VMobject, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

# ----------------------------------------------------------------------------------------------
# design numbers (shared with the lesson text)
# ----------------------------------------------------------------------------------------------
ALPHA, BETA = 0.025, 0.10           # per one-sided test, and planned type II error
V, P_ALT = 0.9, 0.75                 # visibility and mixing weight of the planned alternative
S_ALT = 3 * V * (2 * P_ALT - 1)      # 1.35
DELTA = S_ALT - 1                    # 0.35
N_REQ = math.ceil(6 * (math.sqrt(math.log(1 / ALPHA)) + math.sqrt(math.log(1 / BETA))) ** 2 / DELTA ** 2)
assert abs(S_ALT - 1.35) < 1e-12 and N_REQ == 579


def t_n(n):
    return math.sqrt(6 * math.log(1 / ALPHA) / n)


def power(S, n):
    """Exact P(S_hat > 1 + t_N) when c = (S/3)(1, 1, 1): S_hat = (2K - 3N)/N with K ~ Bin(3N, (1 + S/3)/2)."""
    thr = n * (4 + t_n(n)) / 2
    return float(binom.sf(math.floor(thr), 3 * n, (1 + S / 3) / 2))


def hoeffding_lb(S, n):
    gap = S - 1 - t_n(n)
    return 1 - math.exp(-n * gap ** 2 / 6) if gap > 0 else 0.0


T579 = t_n(N_REQ)
POW579 = power(S_ALT, N_REQ)
assert abs(T579 - 0.1955) < 1e-4 and POW579 > 0.99 and hoeffding_lb(S_ALT, N_REQ) >= 0.9


def facts(L):
    """Strings the animations put on screen; each also appears in the lesson text."""
    return ["XX + YY + ZZ = 2\\,\\mathrm{SWAP} - I", "S = 3v(2p - 1)", "579", f"{T579:.3f}", "1.35", f"{POW579:.3f}"]


def graph_cc(center):
    lam = VGroup(Circle(radius=0.38, color=AMBER, stroke_width=4), eq(r"\Lambda", size=34, color=AMBER)).move_to(center + UP * 0.9)
    a = VGroup(Circle(radius=0.38, color=BLUE, stroke_width=4), eq("A", size=34, color=BLUE)).move_to(center + DOWN * 0.6 + LEFT * 1.0)
    b = VGroup(Circle(radius=0.38, color=VIOLET, stroke_width=4), eq("B", size=34, color=VIOLET)).move_to(center + DOWN * 0.6 + RIGHT * 1.0)
    return VGroup(lam, a, b, Arrow(lam.get_center(), a.get_center(), buff=0.42, color=MUTED, stroke_width=5),
                  Arrow(lam.get_center(), b.get_center(), buff=0.42, color=MUTED, stroke_width=5))


def graph_ce(center):
    a = VGroup(Circle(radius=0.38, color=BLUE, stroke_width=4), eq("A", size=34, color=BLUE)).move_to(center + DOWN * 0.6 + LEFT * 1.0)
    b = VGroup(Circle(radius=0.38, color=VIOLET, stroke_width=4), eq("B", size=34, color=VIOLET)).move_to(center + DOWN * 0.6 + RIGHT * 1.0)
    ch = eq(r"\mathcal{E}", size=32, color=RED).move_to(center + DOWN * 0.15)
    return VGroup(a, b, Arrow(a.get_center(), b.get_center(), buff=0.42, color=RED, stroke_width=5), ch)


class DesignPipeline(Scene):
    def construct(self):
        title = label("From a causal question to an analysis plan", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        g1, g2 = graph_cc(LEFT * 3.2 + UP * 0.6), graph_ce(RIGHT * 3.2 + UP * 0.6)
        h1 = eq(r"H_{cc}:\ \text{shared state } \rho_{AB}", size=32, color=AMBER).next_to(g1, DOWN, buff=0.4)
        h2 = eq(r"H_{ce}:\ \text{channel } A \to B", size=32, color=RED).next_to(g2, DOWN, buff=0.4)
        q = label("Question: is the correlation between qubits A and B a common source or a direct channel?", 24, MUTED)
        q.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(q))
        self.play(FadeIn(g1), Write(h1))
        self.play(FadeIn(g2), Write(h2))
        self.wait(1.0)
        self.play(FadeOut(VGroup(g1, g2, h1, h2, q)))

        stages = [("Question", "common source or direct channel from A to B?"),
                  ("Hypotheses", "common cause: any shared state;  direct: any channel"),
                  ("Operations", "Pauli pairs XX, YY, ZZ;  A maximally mixed"),
                  ("Predictions", "common cause: S ≤ 1;  direct: S ≥ −1"),
                  ("Statistic", "S = cx + cy + cz,  each c the mean of a·b"),
                  ("Sample size", f"Hoeffding bound: N = {N_REQ} shots per setting"),
                  ("Controls", "readout, marginals, known wire, known source"),
                  ("Decision", f"falsify common cause if S > 1 + {T579:.3f}")]
        boxes = VGroup()
        for k, (name, _) in enumerate(stages):
            r, c = divmod(k, 4)
            x = -5.1 + 3.4 * (c if r == 0 else 3 - c)
            y = 1.6 if r == 0 else -0.6
            box = RoundedRectangle(width=2.7, height=0.9, corner_radius=0.15, color=VIOLET if k % 2 == 0 else CYAN,
                                   stroke_width=4).move_to([x, y, 0])
            boxes.add(VGroup(box, label(name, 26, INK, "BOLD").move_to(box)))
        arrows = VGroup()
        for k in range(len(boxes) - 1):
            a, b = boxes[k][0], boxes[k + 1][0]
            if k == 3:
                arrows.add(Arrow(a.get_bottom(), b.get_top(), buff=0.08, color=MUTED, stroke_width=4))
            elif k < 3:
                arrows.add(Arrow(a.get_right(), b.get_left(), buff=0.08, color=MUTED, stroke_width=4))
            else:
                arrows.add(Arrow(a.get_left(), b.get_right(), buff=0.08, color=MUTED, stroke_width=4))
        detail = label("", 26, INK)
        for k, (name, text) in enumerate(stages):
            new = label(text, 26, INK).move_to(DOWN * 2.3)
            anims = [FadeIn(boxes[k], shift=UP * 0.1)]
            if k > 0:
                anims.append(Create(arrows[k - 1]))
            self.play(*anims, run_time=0.8)
            self.play(Transform(detail, new) if k > 0 else FadeIn(new), run_time=0.7)
            if k == 0:
                detail = new
            self.wait(1.1)
        frame_box = SurroundingRectangle(boxes, color=AMBER, buff=0.2)
        final = label("Every number is fixed before any data are taken.", 28, AMBER, "BOLD").to_edge(DOWN, buff=0.4)
        self.play(Create(frame_box), FadeIn(final))
        self.wait(2.0)


class WitnessSpectra(Scene):
    def construct(self):
        title = label("One statistic, two ranges", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        d1 = eq(r"S = c_x + c_y + c_z", size=38).move_to(UP * 2.3)
        self.play(Write(d1))
        a1 = eq(r"S_{cc} = \operatorname{Tr}[\rho_{AB}\,(", r"XX + YY + ZZ", r")]", size=36).move_to(UP * 1.3 + LEFT * 2.7)
        a2 = eq(r"XX + YY + ZZ", r"= 2\,\mathrm{SWAP} - I", size=36).move_to(UP * 1.3 + LEFT * 2.7)
        a3 = eq(r"\text{eigenvalues } 1, 1, 1, -3", r"\ \Rightarrow\ ", r"-3 \le S_{cc} \le 1", size=36, color=BLUE).move_to(UP * 1.3 + LEFT * 2.7)
        self.play(Write(a1))
        self.wait(0.6)
        self.play(TransformMatchingTex(a1, a2), run_time=1.3)
        self.wait(0.6)
        self.play(TransformMatchingTex(a2, a3), run_time=1.3)
        self.play(a3.animate.scale(0.8).move_to(UP * 1.35 + LEFT * 3.3))

        b1 = eq(r"S_{ce} = \operatorname{Tr}[(", r"XX - YY + ZZ", r")\,J/2]", size=36).move_to(UP * 0.25 + LEFT * 2.7)
        b2 = eq(r"XX - YY + ZZ", r"= 2|\Omega\rangle\langle\Omega| - I", size=36).move_to(UP * 0.25 + LEFT * 2.7)
        b3 = eq(r"\text{eigenvalues } 3, -1, -1, -1", r"\ \Rightarrow\ ", r"-1 \le S_{ce} \le 3", size=36, color=RED).move_to(UP * 0.25 + LEFT * 2.7)
        note = eq(r"Y^{T} = -Y:\ \text{the partial transpose of } XX + YY + ZZ", size=28, color=MUTED).next_to(b1, DOWN, buff=0.2)
        self.play(Write(b1), FadeIn(note))
        self.wait(0.6)
        self.play(TransformMatchingTex(b1, b2), run_time=1.3)
        self.wait(0.5)
        self.play(TransformMatchingTex(b2, b3), FadeOut(note), run_time=1.3)
        self.play(b3.animate.scale(0.8).move_to(UP * 0.55 + LEFT * 3.3))

        nl = NumberLine(x_range=[-3, 3, 1], length=10, color=MUTED, include_numbers=False).move_to(DOWN * 1.6)
        nums = VGroup(*[eq(str(k), size=28, color=MUTED).next_to(nl.n2p(k), DOWN, buff=0.18) for k in range(-3, 4)])
        cc = Line(nl.n2p(-3), nl.n2p(1), color=BLUE, stroke_width=12).shift(UP * 0.55)
        ce = Line(nl.n2p(-1), nl.n2p(3), color=RED, stroke_width=12).shift(UP * 0.8)
        cct = label("common cause", 24, BLUE).next_to(cc, LEFT, buff=0.15).shift(DOWN * 0.05 + RIGHT * 0.1)
        cct.next_to(nl.n2p(-3) + UP * 0.55, UP, buff=0.35).shift(RIGHT * 0.9)
        cet = label("cause-effect", 24, RED).next_to(nl.n2p(3) + UP * 0.8, UP, buff=0.15).shift(LEFT * 0.9)
        self.play(Create(nl), FadeIn(nums))
        self.play(Create(cc), FadeIn(cct))
        self.play(Create(ce), FadeIn(cet))
        band = Rectangle(width=nl.n2p(1)[0] - nl.n2p(-1)[0], height=1.2, color=GRID, fill_color=GRID, fill_opacity=0.6,
                         stroke_width=0).move_to((nl.n2p(-1) + nl.n2p(1)) / 2 + UP * 0.55)
        bt = label("inconclusive", 22, MUTED).move_to((nl.n2p(-1) + nl.n2p(1)) / 2 + UP * 1.4)
        self.play(FadeIn(band), FadeIn(bt))
        self.bring_to_back(band)

        mix = eq(r"\text{mixture: } S = 3v(2p - 1),\ v = 0.9", size=32, color=VIOLET).move_to(RIGHT * 3.4 + UP * 1.0)
        self.play(Write(mix))
        p = ValueTracker(0.0)

        def marker():
            s = 3 * V * (2 * p.get_value() - 1)
            col = BLUE if s < -1 else (RED if s > 1 else MUTED)
            return Dot(nl.n2p(s) + UP * 0.25, radius=0.13, color=col)

        def verdict():
            s = 3 * V * (2 * p.get_value() - 1)
            txt = "falsifies H_ce" if s < -1 else ("falsifies H_cc" if s > 1 else "no verdict")
            col = BLUE if s < -1 else (RED if s > 1 else MUTED)
            return label(f"p = {p.get_value():.2f}:  S = {s:+.2f},  {txt}", 26, col).move_to(RIGHT * 3.0 + UP * 0.2)

        dot, vt = always_redraw(marker), always_redraw(verdict)
        self.add(dot, vt)
        self.play(p.animate.set_value(P_ALT), run_time=5, rate_func=linear)
        self.wait(0.8)
        self.play(p.animate.set_value(1.0), run_time=1.5, rate_func=linear)
        self.wait(1.5)


def dist_curve(ax, S, n, color):
    """Exact pmf of S_hat (support (2K - 3N)/N) drawn as a density curve on the S axis."""
    k = np.arange(3 * n + 1)
    x = (2 * k - 3 * n) / n
    pm = binom.pmf(k, 3 * n, (1 + S / 3) / 2) * n / 2          # density per unit of S
    keep = (x > -0.5) & (x < 2.6)
    pts = [ax.c2p(xx, yy) for xx, yy in zip(x[keep], pm[keep])]
    m = VMobject(color=color, stroke_width=4)
    m.set_points_as_corners(pts)
    return m


class ShotsSharpen(Scene):
    def construct(self):
        title = label("More shots, sharper estimates, lower threshold", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        ax = Axes(x_range=[-0.5, 2.6, 0.5], y_range=[0, 6.5, 1], x_length=9.0, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(DOWN * 0.6 + LEFT * 1.2)
        xl = VGroup(*[eq(f"{v:g}", size=26, color=MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.15) for v in (0, 0.5, 1, 1.5, 2, 2.5)])
        xlab = eq(r"\hat S", size=32).next_to(ax.x_axis, RIGHT, buff=0.15)
        self.play(Create(ax), FadeIn(xl), Write(xlab))
        leg = VGroup(eq(r"\text{boundary null } S = 1", size=28, color=BLUE),
                     eq(r"\text{alternative } S = 1.35", size=28, color=RED),
                     eq(r"\text{threshold } 1 + t_N", size=28, color=AMBER)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        leg.move_to(RIGHT * 4.9 + UP * 2.0)
        self.play(FadeIn(leg))
        info = None
        c0 = c1 = thr = None
        for n in (30, 100, 300, N_REQ):
            n0, n1 = dist_curve(ax, 1.0, n, BLUE), dist_curve(ax, S_ALT, n, RED)
            th = DashedLine(ax.c2p(1 + t_n(n), 0), ax.c2p(1 + t_n(n), 6.4), color=AMBER, stroke_width=4)
            txt = VGroup(eq(rf"N = {n}", size=32), eq(rf"t_N = {t_n(n):.3f}", size=30, color=AMBER),
                         eq(rf"\text{{power}} = {power(S_ALT, n):.3f}", size=30, color=RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            txt.move_to(RIGHT * 4.9 + DOWN * 0.4)
            if c0 is None:
                self.play(Create(n0), Create(n1), Create(th), FadeIn(txt), run_time=1.5)
            else:
                self.play(Transform(c0, n0), Transform(c1, n1), Transform(thr, th), Transform(info, txt), run_time=1.8)
                n0, n1, th, txt = c0, c1, thr, info
            c0, c1, thr, info = n0, n1, th, txt
            self.wait(1.4)
        note = label("Hoeffding holds for every common-cause model, not only the boundary one.", 24, MUTED).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note))
        self.wait(2.0)


class PowerCurve(Scene):
    def construct(self):
        title = label("Power against the planned alternative S = 1.35", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        ax = Axes(x_range=[0, 1000, 100], y_range=[0, 1.0, 0.25], x_length=9.0, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(DOWN * 0.4 + LEFT * 1.3)
        xl = VGroup(*[eq(str(v), size=26, color=MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.15) for v in (0, 250, 500, 750, 1000)])
        yl = VGroup(*[eq(f"{v:g}", size=26, color=MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.15) for v in (0, 0.5, 0.9, 1)])
        xlab = label("shots per setting N", 24, MUTED).next_to(ax.x_axis, DOWN, buff=0.6)
        nine = DashedLine(ax.c2p(0, 0.9), ax.c2p(1000, 0.9), color=GRID, stroke_width=3)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(xlab), Create(nine))
        leg = VGroup(eq(r"\text{exact (binomial)}", size=28, color=RED),
                     eq(r"\text{Hoeffding guarantee}", size=28, color=VIOLET)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        leg.move_to(RIGHT * 5.0 + UP * 1.8)
        self.play(FadeIn(leg))
        n = ValueTracker(10)
        d_ex = always_redraw(lambda: Dot(ax.c2p(n.get_value(), power(S_ALT, int(n.get_value()))), color=RED, radius=0.06))
        d_hb = always_redraw(lambda: Dot(ax.c2p(n.get_value(), hoeffding_lb(S_ALT, int(n.get_value()))), color=VIOLET, radius=0.06))
        tr1 = TracedPath(d_ex.get_center, stroke_color=RED, stroke_width=4)
        tr2 = TracedPath(d_hb.get_center, stroke_color=VIOLET, stroke_width=4)
        self.add(tr1, tr2, d_ex, d_hb)
        self.play(n.animate.set_value(1000), run_time=8, rate_func=linear)
        vline = DashedLine(ax.c2p(N_REQ, 0), ax.c2p(N_REQ, 1.0), color=AMBER, stroke_width=4)
        vt = eq(rf"N = {N_REQ}", size=30, color=AMBER).next_to(ax.c2p(N_REQ, 1.0), UP, buff=0.1)
        self.play(Create(vline), FadeIn(vt))
        res = VGroup(eq(rf"\text{{exact power}} = {POW579:.3f}", size=30, color=RED),
                     eq(rf"\text{{guaranteed}} \ge 0.9", size=30, color=VIOLET),
                     eq(r"N \ge \frac{6\big(\sqrt{\ln(1/\alpha)} + \sqrt{\ln(1/\beta)}\big)^2}{\Delta^2}", size=30))
        res.arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(RIGHT * 4.6 + DOWN * 0.8)
        self.play(Write(res[0]))
        self.play(Write(res[1]))
        self.play(Write(res[2]))
        self.wait(2.0)
        _ = (PI, Transform, SurroundingRectangle)
