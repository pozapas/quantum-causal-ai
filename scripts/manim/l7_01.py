"""L7-01 Define the learning task: three scenes.

ThreeQuestions            a decision tree that sorts a claim by its output: a prediction, an intervention
                          effect, or a quantum resource saving, and the evidence each one needs.
PredictionVsIntervention  the SCM Z -> X -> Y <- Z of science.causal(): the best predictor sees a contrast of
                          0.5, graph surgery do(X) gives 0.2; a sweep of the confounding strength c traces
                          the observed contrast 0.2 + 0.6 c against the flat effect 0.2.
SameDataDifferentEffects  two models with the same joint table P(X, Y) and the same prediction risk 0.185 but
                          effects 0.2 and 0.5: the data cannot choose between them.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DashedVMobject, DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, DashedLine, DecimalNumber, Dot, FadeIn,
                   FadeOut, Line, Rectangle, RoundedRectangle, Scene, Transform, ValueTracker, VGroup, Write,
                   always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label
from qcai import science as s

# ------------------------------------------------------------------ shared numbers
C = s.causal()                                  # defaults: prevalence .5, low .2, high .8, base .1, effect .2, confound .5
T1, T0, OBS, ATE, DO1, DO0 = C["treated"], C["untreated"], C["observed"], C["ate"], C["do1"], C["do0"]
assert abs(T1 - 0.7) < 1e-12 and abs(T0 - 0.2) < 1e-12 and abs(OBS - 0.5) < 1e-12
assert abs(DO1 - 0.55) < 1e-12 and abs(DO0 - 0.35) < 1e-12 and abs(ATE - 0.2) < 1e-12


def observed(c):
    return s.causal(confound=c)["observed"]


assert all(abs(observed(c) - (0.2 + 0.6 * c)) < 1e-12 for c in (0, 0.1, 0.25, 0.5))
JOINT = {(1, 1): 0.5 * T1, (1, 0): 0.5 * (1 - T1), (0, 1): 0.5 * T0, (0, 0): 0.5 * (1 - T0)}
assert abs(JOINT[(1, 1)] - 0.35) < 1e-12 and abs(JOINT[(0, 1)] - 0.10) < 1e-12
RISK = 0.5 * T1 * (1 - T1) + 0.5 * T0 * (1 - T0)   # E[Var(Y|X)], the Bayes risk under squared loss
assert abs(RISK - 0.185) < 1e-12


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["0.2 + 0.6c", "0.185", "E[Y \\mid do(X=1)] = 0.55", "0.35", "0.5"]


def node(name, color, pos, dashed=False):
    c = Circle(radius=0.38, color=color, stroke_width=4).move_to(pos)
    if dashed:
        c = DashedVMobject(c, num_dashes=14)
    t = eq(name, size=36, color=color).move_to(pos)
    return VGroup(c, t)


def edge(a, b, color=INK):
    return Arrow(a.get_center(), b.get_center(), buff=0.42, color=color, stroke_width=4, max_tip_length_to_length_ratio=0.18)


# ================================================================ scene 1
class ThreeQuestions(Scene):
    def construct(self):
        title = label("Sort the claim by what it outputs", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        root = VGroup(RoundedRectangle(width=7.2, height=0.8, corner_radius=0.15, color=INK),
                      label("What does the study claim to deliver?", 26, INK)).move_to(UP * 2.3)
        root[1].move_to(root[0])
        self.play(Create(root[0]), FadeIn(root[1]))
        xs = (-4.4, 0.0, 4.4)
        colors = (BLUE, VIOLET, AMBER)
        heads = ["a prediction", "an intervention effect", "a resource saving"]
        forms = [r"R(f) = E[\ell(f(X), Y)]", r"\tau = E[Y \mid do(A=1)] - E[Y \mid do(A=0)]", r"r_Q(\epsilon)\ \ \text{vs}\ \ \min r_C(\epsilon)"]
        needs = [["held-out risk with error bars", "same distribution as use", "shift is a separate claim"],
                 ["estimand stated first", "identification assumptions", "estimator and sensitivity"],
                 ["access model stated", "tuned classical baselines", "all costs: shots, gates, data"]]
        boxes = VGroup()
        for x, col, h, f, nd in zip(xs, colors, heads, forms, needs):
            box = RoundedRectangle(width=4.0, height=0.7, corner_radius=0.12, color=col).move_to([x, 1.05, 0])
            ht = label(h, 26, col, "BOLD").move_to(box)
            if ht.width > 3.8:
                ht.scale_to_fit_width(3.8)
            ln = Line(root[0].get_bottom(), box.get_top(), color=MUTED, stroke_width=2)
            if " - E[" in f:
                a_, b_ = f.split(" - E[")
                fm = VGroup(eq(a_, size=28, color=col), eq("- E[" + b_, size=28, color=col)).arrange(DOWN, buff=0.08)
                fm.next_to(box, DOWN, buff=0.2)
            else:
                fm = eq(f, size=30, color=col).next_to(box, DOWN, buff=0.3)
            if fm.width > 4.1:
                fm.scale_to_fit_width(4.1)
            ev = VGroup(*[label("• " + t, 24, INK) for t in nd]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
            ev.next_to(fm, DOWN, buff=0.3)
            evh = label("evidence needed", 24, MUTED).next_to(ev, UP, buff=0.1).align_to(ev, LEFT)
            ev.shift(DOWN * 0.2)
            evh.shift(DOWN * 0.15)
            self.play(Create(ln), Create(box), FadeIn(ht), run_time=0.9)
            self.play(Write(fm), run_time=1.0)
            self.play(FadeIn(evh), FadeIn(ev), run_time=1.0)
            boxes.add(VGroup(box, ht, ln, fm, ev, evh))
            self.wait(0.6)
        foot = label("One study can make all three claims; each needs its own evidence.", 26, RED).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(foot))
        self.wait(2.5)


# ================================================================ scene 2
class PredictionVsIntervention(Scene):
    def construct(self):
        title = label("The best predictor does not measure the effect", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        pz, px, py = LEFT * 4.6 + UP * 1.4, LEFT * 5.6 + DOWN * 0.6, LEFT * 3.6 + DOWN * 0.6
        Z, X, Y = node("Z", CYAN, pz), node("X", BLUE, px), node("Y", VIOLET, py)
        ezx, ezy, exy = edge(Z, X), edge(Z, Y), edge(X, Y)
        self.play(FadeIn(Z), FadeIn(X), FadeIn(Y), Create(ezx), Create(ezy), Create(exy))
        mech = VGroup(eq(r"P(X{=}1 \mid Z) = 0.2 + 0.6Z", size=26, color=MUTED),
                      eq(r"P(Y{=}1 \mid X, Z) = 0.1 + 0.2X + cZ", size=26, color=MUTED)
                      ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(LEFT * 4.4 + DOWN * 2.0)
        self.play(FadeIn(mech))

        ax = Axes(x_range=[0, 4, 1], y_range=[0, 0.8, 0.2], x_length=5.6, y_length=2.4,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 2.9 + DOWN * 1.7)
        self.play(Create(ax))

        def bar(i, v, col):
            r = Rectangle(width=0.8, height=max(v / 0.8 * 2.4, 0.001), stroke_width=0).set_fill(col, opacity=0.8)
            r.move_to(ax.c2p(i + 0.5, 0), aligned_edge=DOWN)
            return r

        def top(r, v, col):
            return eq(f"{v:g}", size=28, color=col).next_to(r, UP, buff=0.08)

        def under(i, s, col):
            return eq(s, size=26, color=col).next_to(ax.c2p(i + 0.5, 0), DOWN, buff=0.15)

        b1, b0 = bar(0, T1, BLUE), bar(1, T0, BLUE)
        n1, n0 = top(b1, T1, BLUE), top(b0, T0, BLUE)
        c1, c0 = under(0, "X{=}1", BLUE), under(1, "X{=}0", BLUE)
        txt1 = eq(r"E[Y \mid X=1] = 0.7,\ \ E[Y \mid X=0] = 0.2", size=28, color=BLUE)
        txt2 = eq(r"\text{observed contrast} = 0.5", size=30, color=BLUE)
        txt1.move_to(RIGHT * 2.9 + UP * 2.2)
        txt2.next_to(txt1, DOWN, buff=0.15)
        self.play(FadeIn(b1), FadeIn(b0), FadeIn(n1), FadeIn(n0), FadeIn(c1), FadeIn(c0), Write(txt1))
        self.play(Write(txt2))
        self.wait(1.0)

        # graph surgery
        self.play(ezx.animate.set_color(RED))
        self.play(FadeOut(ezx), run_time=0.8)
        doX = eq(r"do(X)", size=28, color=RED).next_to(X, DOWN, buff=0.15)
        self.play(FadeIn(doX))
        d1, d0 = bar(2, DO1, VIOLET), bar(3, DO0, VIOLET)
        m1, m0 = top(d1, DO1, VIOLET), top(d0, DO0, VIOLET)
        e1, e0 = under(2, "do(1)", VIOLET), under(3, "do(0)", VIOLET)
        txt3 = eq(r"E[Y \mid do(X=1)] = 0.55,\ \ E[Y \mid do(X=0)] = 0.35", size=28, color=VIOLET).next_to(txt2, DOWN, buff=0.25)
        txt4 = eq(r"\tau = 0.55 - 0.35 = 0.2", size=30, color=VIOLET).next_to(txt3, DOWN, buff=0.15)
        self.play(FadeIn(d1), FadeIn(d0), FadeIn(m1), FadeIn(m0), FadeIn(e1), FadeIn(e0), Write(txt3))
        self.play(Write(txt4))
        self.wait(1.8)
        b_all = VGroup(b1, b0, n1, n0, c1, c0, d1, d0, m1, m0, e1, e0, ax, txt1, txt2, txt3, txt4)

        # sweep the confounding strength
        self.play(FadeOut(b_all))
        ax2 = Axes(x_range=[0, 0.5, 0.1], y_range=[0, 0.6, 0.1], x_length=5.6, y_length=3.4,
                   axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 2.6 + DOWN * 0.3)
        xl = eq(r"c\ \text{(strength of } Z \to Y)", size=26, color=MUTED).next_to(ax2, DOWN, buff=0.2)
        ticks = VGroup(*[eq(f"{v:g}", size=24, color=MUTED).next_to(ax2.c2p(v, 0), DOWN, buff=0.1) for v in (0, 0.25, 0.5)])
        yt = VGroup(*[eq(f"{v:g}", size=24, color=MUTED).next_to(ax2.c2p(0, v), LEFT, buff=0.1) for v in (0.2, 0.5)])
        xl.next_to(ticks, DOWN, buff=0.1)
        self.play(FadeIn(ezx.set_color(INK)), FadeOut(doX), Create(ax2), FadeIn(xl), FadeIn(ticks), FadeIn(yt))
        flat = Line(ax2.c2p(0, ATE), ax2.c2p(0.5, ATE), color=VIOLET, stroke_width=4)
        fl = eq(r"\tau = 0.2", size=28, color=VIOLET).next_to(flat, DOWN, buff=0.1).align_to(flat, RIGHT)
        self.play(Create(flat), Write(fl))
        c = ValueTracker(0.0)
        dot = always_redraw(lambda: Dot(ax2.c2p(c.get_value(), observed(c.get_value())), color=BLUE, radius=0.07))
        trace = ax2.plot(lambda v: 0.2 + 0.6 * v, x_range=[0, 0.5], color=BLUE, stroke_width=4)
        lab = eq(r"\text{observed} = 0.2 + 0.6c", size=28, color=BLUE).move_to(RIGHT * 2.0 + UP * 2.0)
        val = DecimalNumber(observed(0), num_decimal_places=3, color=BLUE, font_size=34)
        val.add_updater(lambda m: m.set_value(observed(c.get_value())))
        val.next_to(lab, RIGHT, buff=0.3)
        self.play(FadeIn(dot), Write(lab), FadeIn(val))
        self.play(c.animate.set_value(0.5), Create(trace), run_time=5, rate_func=linear)
        note = label("only c = 0 (no confounding path) makes them agree", 24, MUTED).to_edge(DOWN, buff=0.25).shift(RIGHT * 2.2)
        self.play(FadeIn(note))
        self.wait(2.0)
        _ = (DashedLine, GRID, Transform, AMBER)


# ================================================================ scene 3
class SameDataDifferentEffects(Scene):
    def construct(self):
        title = label("Same data, same accuracy, different effects", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        # model A (left): Z hidden confounder
        pa = LEFT * 4.6
        ZA = node("Z", CYAN, pa + UP * 1.6, dashed=True)
        XA = node("X", BLUE, pa + LEFT * 1.0 + UP * 0.0)
        YA = node("Y", VIOLET, pa + RIGHT * 1.0 + UP * 0.0)
        ga = VGroup(ZA, XA, YA, edge(ZA, XA), edge(ZA, YA), edge(XA, YA))
        ta = label("model A: hidden Z", 24, INK).next_to(ga, DOWN, buff=0.3)
        # model B (right): no confounder
        pb = RIGHT * 4.6
        XB = node("X", BLUE, pb + LEFT * 1.0)
        YB = node("Y", VIOLET, pb + RIGHT * 1.0)
        gb = VGroup(XB, YB, edge(XB, YB))
        tb = label("model B: no confounder", 24, INK).next_to(gb, DOWN, buff=0.3).align_to(ta, DOWN)
        self.play(FadeIn(ga), FadeIn(ta), FadeIn(gb), FadeIn(tb))

        # shared observable table
        rows = [("", "Y=1", "Y=0"), ("X=1", "0.35", "0.15"), ("X=0", "0.10", "0.40")]
        cells = VGroup()
        for i, r in enumerate(rows):
            for j, v in enumerate(r):
                if v:
                    t = eq(v, size=30, color=INK if i and j else MUTED)
                    t.move_to(UP * (1.0 - 0.55 * i) + RIGHT * (-1.0 + 1.0 * j))
                    cells.add(t)
        frame = Rectangle(width=3.2, height=1.8, color=MUTED).move_to(cells)
        tt = eq(r"P(X, Y)", size=30).next_to(frame, UP, buff=0.12)
        aA = Arrow(ga.get_right() + RIGHT * 0.1, frame.get_left(), buff=0.1, color=MUTED, stroke_width=3)
        aB = Arrow(gb.get_left() + LEFT * 0.1, frame.get_right(), buff=0.1, color=MUTED, stroke_width=3)
        self.play(Create(frame), FadeIn(cells), Write(tt), Create(aA), Create(aB), run_time=1.6)
        risk = eq(r"\text{best predictor: } E[Y \mid X],\ \ \text{risk } 0.185", size=28, color=BLUE).next_to(frame, DOWN, buff=0.35)
        self.play(Write(risk))
        self.wait(1.2)

        effA = eq(r"\tau_A = 0.2", size=34, color=VIOLET).move_to(pa + DOWN * 2.4)
        effB = eq(r"\tau_B = 0.5", size=34, color=RED).move_to(pb + DOWN * 2.4)
        self.play(Write(effA), Write(effB))
        verdict = label("no estimator using P(X, Y) alone can be right in both models", 26, RED).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(verdict))
        self.wait(1.2)
        fix = label("measure Z (backdoor), randomize X, or add a justified assumption", 24, MUTED).next_to(verdict, UP, buff=0.15)
        self.play(FadeIn(fix))
        self.wait(2.5)
        _ = (DashedLine, Line, AMBER)
