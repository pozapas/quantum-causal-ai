"""L4-07 Identification before estimation: three 3Blue1Brown-style scenes.

TwoModelsOneJoint   model A (X causes Y) and model B (a hidden U drives both, no effect of X) build
                    identical bars for P(x, y); graph surgery do(X = x) then splits their bars.
MoreDataSharpens    histograms of the observed contrast from n = 25 to n = 6400 records: the spread
                    shrinks like 0.8/sqrt(n), but the centre stays at 0.6, the right answer only for model A.
DoCalculusBackdoor  the backdoor formula derived by do-calculus, each rule licensed by a cut graph,
                    then checked against the truncated factorization with the worked-example numbers.
Every number is computed from qcai.lessonfigs.l4_07, the module the lesson text and figures use.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, Cross, DashedLine, DashedVMobject, FadeIn,
                   FadeOut, Indicate, Line, Rectangle, ReplacementTransform, Scene, Square, SurroundingRectangle,
                   Transform, TransformMatchingTex, VGroup, Write)

from qcai_style import AMBER, BLUE, CYAN, INK, MUTED, RED, VIOLET, eq, label
from qcai.lessonfigs import l4_07 as M

# ---- numbers shared with the lesson text -------------------------------------------------------
JOINT = {k: float(v) for k, v in M.joint_A().items()}
assert M.joint_A() == M.joint_B()
DA = [float(M.do_A(0)), float(M.do_A(1))]          # 0.2, 0.8
DB = [float(M.do_B(0)), float(M.do_B(1))]          # 0.5, 0.5
ACE_A_TEX = f"{M.f2(M.do_A(1))} - {M.f2(M.do_A(0))} = {M.f2(M.ACE_A)}"      # 0.8 - 0.2 = 0.6
ACE_B_TEX = f"{M.f2(M.do_B(1))} - {M.f2(M.do_B(0))} = {M.f2(M.ACE_B)}"      # 0.5 - 0.5 = 0
assert ACE_A_TEX == "0.8 - 0.2 = 0.6" and ACE_B_TEX == "0.5 - 0.5 = 0"

P10, P11 = M.py1_given_xz(1, 0), M.py1_given_xz(1, 1)                       # 0.6, 0.9
PZ0, PZ1 = 1 - M.PZ1, M.PZ1                                                 # 0.6, 0.4
assert P10 * PZ0 + P11 * PZ1 == M.we_do(1)
WE_TEX = rf"{M.f2(P10)} \cdot {M.f2(PZ0)} + {M.f2(P11)} \cdot {M.f2(PZ1)} = {M.f2(M.we_do(1))}"
assert WE_TEX == r"0.6 \cdot 0.6 + 0.9 \cdot 0.4 = 0.72"
SE_TEX = r"0.8/\sqrt{n}"


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return [ACE_A_TEX, ACE_B_TEX, SE_TEX, WE_TEX, r"G_{\overline{X}}", r"G_{\underline{X}}"]


# ---- small drawing helpers -----------------------------------------------------------------------
def node(name, pos, color=INK, hidden=False, r=0.36):
    c = Circle(radius=r, color=color, stroke_width=4).move_to(pos)
    if hidden:
        c = DashedVMobject(c, num_dashes=14)
    t = eq(name, size=36, color=color).move_to(pos)
    return VGroup(c, t)


def edge(a, b, color=INK):
    return Arrow(a.get_center(), b.get_center(), buff=0.42, color=color, stroke_width=5,
                 max_tip_length_to_length_ratio=0.18)


def bars(ax, xs, hs, color, width=0.32, shift=0.0):
    g = VGroup()
    for x, h in zip(xs, hs):
        p0, p1 = ax.c2p(x + shift - width / 2, 0), ax.c2p(x + shift + width / 2, h)
        r = Rectangle(width=p1[0] - p0[0], height=max(p1[1] - p0[1], 1e-3), color=color, fill_color=color,
                      fill_opacity=0.85, stroke_width=1)
        r.move_to([(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0])
        g.add(r)
    return g


class TwoModelsOneJoint(Scene):
    def construct(self):
        title = label("Two causal models, one observational distribution", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=1.2)

        # model A: X -> Y
        la = label("Model A: X causes Y", 24, VIOLET).move_to([-4.8, 2.65, 0])
        xa, ya = node("X", [-5.8, 1.75, 0], VIOLET), node("Y", [-3.8, 1.75, 0], VIOLET)
        ea = edge(xa, ya, VIOLET)
        ma = eq(r"Y \sim P(y \mid x)", size=30, color=VIOLET).move_to([-4.8, 0.95, 0])
        # model B: X <- U -> Y, no arrow from X to Y
        lb = label("Model B: hidden U, no effect", 24, CYAN).move_to([-4.8, 0.05, 0])
        ub = node("U", [-4.8, -0.75, 0], CYAN, hidden=True)
        xb, yb = node("X", [-5.8, -1.95, 0], CYAN), node("Y", [-3.8, -1.95, 0], CYAN)
        eux, euy = edge(ub, xb, CYAN), edge(ub, yb, CYAN)
        mb = eq(r"Y = U", size=30, color=CYAN).move_to([-4.8, -2.85, 0])
        self.play(FadeIn(la), FadeIn(xa), FadeIn(ya), Create(ea), Write(ma))
        self.play(FadeIn(lb), FadeIn(ub), FadeIn(xb), FadeIn(yb), Create(eux), Create(euy), Write(mb))

        # observational joint
        ax1 = Axes(x_range=[0, 4.6, 1], y_range=[0, 0.5, 0.1], x_length=7.0, y_length=3.6,
                   axis_config={"color": MUTED, "include_tip": False}, y_axis_config={"include_numbers": True,
                   "font_size": 24, "decimal_number_config": {"num_decimal_places": 1, "color": MUTED}},
                   x_axis_config={"include_ticks": False}).move_to([2.7, 0.45, 0])
        head1 = eq(r"P(x, y)", size=34).next_to(ax1, UP, buff=0.15)
        keys = [(0, 0), (0, 1), (1, 0), (1, 1)]
        cats = VGroup(*[eq(f"({x},{y})", size=28, color=MUTED).next_to(ax1.c2p(i + 1, 0), DOWN, buff=0.2)
                        for i, (x, y) in enumerate(keys)])
        xl = label("(x, y)", 24, MUTED).next_to(cats, RIGHT, buff=0.3)
        self.play(Create(ax1), Write(head1), FadeIn(cats), FadeIn(xl))
        hs = [JOINT[k] for k in keys]
        ba = bars(ax1, range(1, 5), hs, VIOLET, shift=-0.18)
        bb = bars(ax1, range(1, 5), hs, CYAN, shift=0.18)
        vals = VGroup(*[eq(M.f2(M.joint_A()[k]), size=26, color=INK).next_to(ax1.c2p(i + 1, JOINT[k]), UP, buff=0.12)
                        for i, k in enumerate(keys)])
        self.play(Indicate(VGroup(xa, ya, ea), color=VIOLET), *[Create(r) for r in ba], run_time=1.6)
        self.play(Indicate(VGroup(ub, xb, yb), color=CYAN), *[Create(r) for r in bb], run_time=1.6)
        self.play(FadeIn(vals))
        same = label("identical bars for every (x, y)", 26, INK).move_to([2.7, -2.45, 0])
        self.play(Write(same))
        self.wait(1.2)

        # intervene: cut arrows into X, set X = x
        self.play(FadeOut(VGroup(ba, bb, vals, same)))
        cut = DashedLine(ub.get_center(), xb.get_center(), color=RED).set_opacity(0.6)
        sqa = Square(0.7, color=VIOLET, stroke_width=4).move_to(xa)
        sqb = Square(0.7, color=CYAN, stroke_width=4).move_to(xb)
        xa_set = eq("x", size=36, color=RED).move_to(xa)
        xb_set = eq("x", size=36, color=RED).move_to(xb)
        self.play(ReplacementTransform(eux, cut), run_time=1.0)
        self.play(FadeOut(cut), ReplacementTransform(xa[0], sqa), ReplacementTransform(xb[0], sqb),
                  ReplacementTransform(xa[1], xa_set), ReplacementTransform(xb[1], xb_set))
        surgery = eq(r"\mathrm{do}(X{=}x)\text{: cut arrows into } X", size=28, color=RED).move_to([-4.6, -3.45, 0])
        self.play(FadeIn(surgery))

        ax2 = Axes(x_range=[0, 2.8, 1], y_range=[0, 1, 0.2], x_length=7.0, y_length=3.6,
                   axis_config={"color": MUTED, "include_tip": False}, y_axis_config={"include_numbers": True,
                   "font_size": 24, "decimal_number_config": {"num_decimal_places": 1, "color": MUTED}},
                   x_axis_config={"include_ticks": False}).move_to([2.7, 0.45, 0])
        head2 = eq(r"P(Y{=}1 \mid \mathrm{do}(X{=}x))", size=34).next_to(ax2, UP, buff=0.15)
        cats2 = VGroup(*[eq(f"x = {i}", size=28, color=MUTED).next_to(ax2.c2p(i + 1, 0), DOWN, buff=0.2) for i in (0, 1)])
        self.play(ReplacementTransform(ax1, ax2), ReplacementTransform(head1, head2), FadeOut(xl),
                  ReplacementTransform(cats, cats2))
        da = bars(ax2, (1, 2), DA, VIOLET, width=0.22, shift=-0.14)
        db = bars(ax2, (1, 2), DB, CYAN, width=0.22, shift=0.14)
        va = VGroup(*[eq(M.f2(M.do_A(i)), size=26, color=VIOLET).next_to(da[i], UP, buff=0.1) for i in (0, 1)])
        vb = VGroup(*[eq(M.f2(M.do_B(i)), size=26, color=CYAN).next_to(db[i], UP, buff=0.1) for i in (0, 1)])
        self.play(*[Create(r) for r in da], FadeIn(va), run_time=1.4)
        self.play(*[Create(r) for r in db], FadeIn(vb), run_time=1.4)
        ace_a = eq(r"\text{A: }" + ACE_A_TEX, size=32, color=VIOLET).move_to([1.0, -2.35, 0])
        ace_b = eq(r"\text{B: }" + ACE_B_TEX, size=32, color=CYAN).move_to([4.5, -2.35, 0])
        self.play(Write(ace_a), Write(ace_b))
        msg = label("Same P(x, y), different effects: more data cannot decide", 24, INK).move_to([2.75, -3.3, 0])
        self.play(FadeIn(msg))
        self.wait(2.5)


class MoreDataSharpens(Scene):
    def construct(self):
        title = label("More data sharpens the estimate, not the question", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=1.2)
        ns = [25, 100, 400, 1600, 6400]
        reps, w = 800, 0.02
        edges = np.round(np.arange(-0.3, 1.1 + 1e-9, w), 6)
        rng = np.random.default_rng(11)
        p1, p0, px = float(M.PY1_GIVEN_X[1]), float(M.PY1_GIVEN_X[0]), float(M.PX1)
        hists, sds = [], []
        for n in ns:
            n1 = rng.binomial(n, px, reps)
            n1 = np.clip(n1, 1, n - 1)
            est = rng.binomial(n1, p1) / n1 - rng.binomial(n - n1, p0) / (n - n1)
            h, _ = np.histogram(est, bins=edges)
            hists.append(h / reps)
            sds.append(est.std())
        for n, s in zip(ns, sds):                  # simulation agrees with SE = 0.8 / sqrt(n)
            assert abs(s / M.se_contrast(n) - 1) < 0.15, (n, s)
        assert max(h.max() for h in hists) < 0.5

        ax = Axes(x_range=[-0.3, 1.1, 0.1], y_range=[0, 0.6, 0.1], x_length=11.0, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False},
                  y_axis_config={"include_ticks": False}).move_to([0, -0.75, 0])
        ax.y_axis.set_opacity(0)
        ticks = VGroup(*[eq(f"{v:g}", size=26, color=MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.18)
                         for v in (-0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0)])
        xlab = label("estimated contrast  p(Y=1 | X=1) - p(Y=1 | X=0)", 24, MUTED).next_to(ax, DOWN, buff=0.55)
        ylab = label("share of 800 studies", 22, MUTED).rotate(np.pi / 2).next_to(ax, LEFT, buff=0.15)
        self.play(Create(ax), FadeIn(ticks), FadeIn(xlab), FadeIn(ylab))
        tb = DashedLine(ax.c2p(0, 0), ax.c2p(0, 0.56), color=CYAN, stroke_width=4)
        ta = DashedLine(ax.c2p(0.6, 0), ax.c2p(0.6, 0.56), color=VIOLET, stroke_width=4)
        lbB = label("model B effect: 0", 24, CYAN).next_to(tb, UP, buff=0.1)
        lbA = label("model A effect: 0.6", 24, VIOLET).next_to(ta, UP, buff=0.1)
        self.play(Create(tb), Create(ta), FadeIn(lbB), FadeIn(lbA))

        def hist_mob(h):
            g = VGroup()
            for i, f in enumerate(h):
                if f <= 0:
                    continue
                p0_, p1_ = ax.c2p(edges[i], 0), ax.c2p(edges[i + 1], f)
                g.add(Rectangle(width=p1_[0] - p0_[0], height=p1_[1] - p0_[1], fill_color=AMBER, fill_opacity=0.8,
                                stroke_color=INK, stroke_width=0.5).move_to([(p0_[0] + p1_[0]) / 2, (p0_[1] + p1_[1]) / 2, 0]))
            return g

        def readout(n):
            return eq(rf"n = {n},\quad \mathrm{{SE}} = " + SE_TEX + rf" = {M.se_contrast(n):.3f}", size=32,
                      color=INK).move_to([0, 2.55, 0])

        h = hist_mob(hists[0])
        r = readout(ns[0])
        self.play(FadeIn(h), Write(r), run_time=1.4)
        self.wait(1.0)
        for k in range(1, len(ns)):
            self.play(Transform(h, hist_mob(hists[k])), Transform(r, readout(ns[k])), run_time=1.8)
            self.wait(0.9)
        self.play(FadeOut(r))
        split = eq(r"\hat\tau_n - \tau_B", "=", r"\underbrace{(\hat\tau_n - 0.6)}_{\text{estimation: } \to 0}", "+",
                   r"\underbrace{(0.6 - 0)}_{\text{identification: stays}}", size=40).move_to([0, 2.3, 0])
        self.play(Write(split), run_time=2.0)
        self.wait(2.5)


class DoCalculusBackdoor(Scene):
    def construct(self):
        title = label("Graph surgery licenses each step of the derivation", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=1.2)
        z = node("Z", [-5.0, 1.7, 0], INK)
        x = node("X", [-6.2, -0.1, 0], INK)
        y = node("Y", [-3.8, -0.1, 0], INK)
        ezx, ezy, exy = edge(z, x), edge(z, y), edge(x, y)
        gname = eq("G", size=34, color=MUTED).move_to([-5.0, -1.1, 0])
        self.play(FadeIn(VGroup(z, x, y)), Create(ezx), Create(ezy), Create(exy), FadeIn(gname))

        parts0 = [r"P(y \mid \mathrm{do}(x))", "=", r"\sum_z", r"P(y \mid \mathrm{do}(x), z)", r"P(z \mid \mathrm{do}(x))"]
        parts1 = parts0[:4] + [r"P(z)"]
        parts2 = parts0[:3] + [r"P(y \mid x, z)", r"P(z)"]
        d0 = eq(*parts0, size=34).move_to([2.2, 2.1, 0])
        why0 = label("condition on Z inside the do(x) model", 24, MUTED).move_to([2.2, 1.35, 0])
        self.play(Write(d0), FadeIn(why0), run_time=1.8)
        self.wait(0.6)

        # Rule 3 on P(z | do(x)): cut the arrows into X
        d0[4].set_color(AMBER)
        cut1 = DashedLine(z.get_center(), x.get_center(), color=RED).set_opacity(0.5)
        g1 = eq(r"G_{\overline{X}}", size=34, color=RED).move_to(gname)
        self.play(ReplacementTransform(ezx, cut1), ReplacementTransform(gname, g1))
        test1 = eq(r"(Z \perp\!\!\!\perp X)_{G_{\overline{X}}}", size=32, color=RED).move_to([2.2, 0.55, 0])
        why1 = label("only path Z -> Y <- X is blocked at the collider Y", 24, MUTED).move_to([2.2, -0.05, 0])
        self.play(Write(test1), FadeIn(why1), Indicate(y, color=RED))
        d1 = eq(*parts1, size=34).move_to(d0)
        d1[4].set_color(AMBER)
        r3 = label("Rule 3: delete do(x) from P(z | do(x))", 24, AMBER).move_to([2.2, -0.65, 0])
        self.play(TransformMatchingTex(d0, d1), FadeIn(r3), run_time=1.6)
        self.wait(1.0)
        ezx2 = edge(z, x)
        gname2 = eq("G", size=34, color=MUTED).move_to(g1)
        self.play(FadeOut(VGroup(test1, why1, r3)), ReplacementTransform(cut1, ezx2), ReplacementTransform(g1, gname2))
        d1[4].set_color(INK)

        # Rule 2 on P(y | do(x), z): cut the arrows out of X
        d1[3].set_color(BLUE)
        cut2 = DashedLine(x.get_center(), y.get_center(), color=RED).set_opacity(0.5)
        g2 = eq(r"G_{\underline{X}}", size=34, color=RED).move_to(gname2)
        self.play(ReplacementTransform(exy, cut2), ReplacementTransform(gname2, g2))
        test2 = eq(r"(Y \perp\!\!\!\perp X \mid Z)_{G_{\underline{X}}}", size=32, color=RED).move_to([2.2, 0.55, 0])
        why2 = label("only path X <- Z -> Y is blocked by conditioning on Z", 24, MUTED).move_to([2.2, -0.05, 0])
        self.play(Write(test2), FadeIn(why2), Indicate(z, color=RED))
        d2 = eq(*parts2, size=34).move_to(d1)
        d2[3].set_color(BLUE)
        r2 = label("Rule 2: replace the action do(x) by the observation x", 24, BLUE).move_to([2.2, -0.65, 0])
        self.play(TransformMatchingTex(d1, d2), FadeIn(r2), run_time=1.6)
        self.wait(1.0)
        exy2 = edge(x, y)
        gname3 = eq("G", size=34, color=MUTED).move_to(g2)
        self.play(FadeOut(VGroup(test2, why2, r2, why0)), ReplacementTransform(cut2, exy2), ReplacementTransform(g2, gname3))
        d2[3].set_color(INK)
        box = SurroundingRectangle(d2, color=VIOLET, buff=0.12)
        self.play(Create(box))

        # numbers from the worked example
        num = eq(r"P(Y{=}1 \mid \mathrm{do}(X{=}1)) = " + WE_TEX, size=32, color=VIOLET).move_to([2.2, 0.75, 0])
        self.play(Write(num), run_time=1.6)

        # same answer from the truncated factorization: delete the factor of the intervened variable
        tf = eq(r"P(z)", r"P(x \mid z)", r"P(y \mid x, z)", size=36).move_to([2.2, -0.75, 0])
        tfl = label("observational factorization", 24, MUTED).next_to(tf, DOWN, buff=0.2)
        self.play(Write(tf), FadeIn(tfl))
        cross = Cross(tf[1], stroke_color=RED, stroke_width=5)
        self.play(Create(cross))
        tf2 = eq(r"\sum_z", r"P(z)", r"P(y \mid x, z)", size=36).move_to(tf)
        tfl2 = label("truncated: drop the factor of X, sum over z", 24, RED).next_to(tf2, DOWN, buff=0.2)
        self.play(FadeOut(cross), TransformMatchingTex(tf, tf2), ReplacementTransform(tfl, tfl2), run_time=1.4)
        agree = label("the same backdoor formula, reached two ways", 26, INK).move_to([2.2, -2.75, 0])
        self.play(FadeIn(agree))
        self.wait(2.5)
        _ = (Line, CYAN)
