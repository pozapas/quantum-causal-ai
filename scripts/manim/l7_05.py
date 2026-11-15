"""L7-05 Identifiability before quantum causal learning: four scenes.

SameDataDifferentEffects  M1 (hidden common cause U, no effect) and M2 (X -> Y) produce the same table
                          P(X, Y) = (0.4, 0.1; 0.1, 0.4); graph surgery for do(X = 1) gives 0.5 versus 0.8.
BoundsFromConsistency     term-by-term derivation of the no-assumption bounds ATE in [-0.2, 0.8], then a
                          sweep of the confounding bound gamma that shrinks the set to the point 0.6.
BasesReveal               Z-basis correlations cannot separate an identity channel from two common causes;
                          X and Y correlations can, because c_xx + c_yy + c_zz <= 1 for every state.
CorrelationTetrahedra     ThreeDScene: the tetrahedron of common-cause states, the dual tetrahedron of
                          direct-cause channels, and their octahedral overlap where direction is not identified.
Numbers come from qcai/lessonfigs/l7_05.py and are checked against the lesson text by facts().
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np
from manim import (DEGREES, DOWN, LEFT, ORIGIN, PI, RIGHT, UP, Arrow, Circle, Create, DashedLine, DashedVMobject,
                   Dot, Dot3D, FadeIn, FadeOut, Line, Line3D, Polyhedron, Rectangle, Scene, Square, ThreeDScene,
                   TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label
from qcai.lessonfigs import l7_05 as M

JOINT = M.joint_m1()
assert np.allclose(JOINT, M.joint_m2())
DO1 = (M.do_y1(1, 1), M.do_y1(2, 1))          # 0.5, 0.8
DO0 = (M.do_y1(1, 0), M.do_y1(2, 0))          # 0.5, 0.2
assert np.allclose(DO1, (0.5, 0.8)) and np.allclose(DO0, (0.5, 0.2))
LO, HI = M.MANSKI                              # -0.2, 0.8
E1 = (0.4, 0.9)
E0 = (0.1, 0.6)
assert abs(E1[0] - E0[1] - LO) < 1e-12 and abs(E1[1] - E0[0] - HI) < 1e-12
TRIPLES = {"identity channel": M.T_IDENTITY, "classical common cause": M.T_CLASSICAL, "Phi+": M.T_PHI}


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["[-0.2, 0.8]", r"\gamma = 0.6", "0.4, 0.1, 0.1, 0.4", r"c_{xx} + c_{yy} + c_{zz} \le 1",
            r"|c_1| + |c_2| + |c_3| \le 1"]


def node(tex, pos, color=INK, dashed=False):
    c = Circle(radius=0.36, color=color, stroke_width=4).move_to(pos)
    if dashed:
        c = DashedVMobject(c, num_dashes=14)
    return VGroup(c, eq(tex, size=34, color=color).move_to(pos))


def edge(a, b, color=INK):
    return Arrow(a.get_center(), b.get_center(), buff=0.42, color=color, stroke_width=5, max_tip_length_to_length_ratio=0.18)


def bar_chart(values, labels, center, width=2.6, height=1.6, color=VIOLET, vmax=1.0, fmt="{:.1f}"):
    """Simple bars on a baseline; values in [0, vmax]."""
    n = len(values)
    grp = VGroup()
    base = Line(center + LEFT * width / 2, center + RIGHT * width / 2, color=MUTED, stroke_width=2)
    grp.add(base)
    w = width / n
    for k, (v, lab) in enumerate(zip(values, labels)):
        x = center[0] - width / 2 + w * (k + 0.5)
        h = max(v / vmax * height, 0.02)
        r = Rectangle(width=w * 0.62, height=h, fill_color=color, fill_opacity=0.7, stroke_color=INK, stroke_width=1)
        r.move_to([x, center[1] + h / 2, 0])
        grp.add(r)
        grp.add(label(fmt.format(v), 22, INK).next_to(r, UP, buff=0.06))
        grp.add(eq(lab, size=28, color=MUTED).move_to([x, center[1] - 0.28, 0]))
    return grp


# ---- scene 1 ----------------------------------------------------------------------------------
class SameDataDifferentEffects(Scene):
    def construct(self):
        title = label("Two causal models, one distribution", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        lc, rc = LEFT * 3.5, RIGHT * 3.5
        U1 = node("U", lc + UP * 2.1, MUTED, dashed=True)
        X1 = node("X", lc + LEFT * 1.3 + UP * 1.0)
        Y1 = node("Y", lc + RIGHT * 1.3 + UP * 1.0)
        ux, uy = edge(U1, X1, MUTED), edge(U1, Y1, MUTED)
        X2 = node("X", rc + LEFT * 1.3 + UP * 1.0)
        Y2 = node("Y", rc + RIGHT * 1.3 + UP * 1.0)
        xy = edge(X2, Y2)
        n1 = label("M1: hidden common cause", 24, INK).next_to(lc + UP * 1.0, DOWN, buff=0.55)
        n2 = label("M2: X causes Y", 24, INK).next_to(rc + UP * 1.0, DOWN, buff=0.55)
        self.play(FadeIn(U1), FadeIn(X1), FadeIn(Y1), Create(ux), Create(uy), FadeIn(n1))
        self.play(FadeIn(X2), FadeIn(Y2), Create(xy), FadeIn(n2))
        vals = [JOINT[0, 0], JOINT[0, 1], JOINT[1, 0], JOINT[1, 1]]
        labs = ["00", "01", "10", "11"]
        b1 = bar_chart(vals, labs, lc + DOWN * 2.6, height=1.8, color=CYAN)
        b2 = bar_chart(vals, labs, rc + DOWN * 2.6, height=1.8, color=CYAN)
        cap = eq(r"P(X, Y) = (0.4, 0.1, 0.1, 0.4)", size=30).move_to(DOWN * 0.45)
        self.play(FadeIn(b1), FadeIn(b2), Write(cap))
        same = label("identical: no amount of observational data separates them", 24, RED).move_to(DOWN * 3.65)
        self.play(FadeIn(same))
        self.wait(1.2)

        # graph surgery: do(X = 1)
        self.play(FadeOut(same), FadeOut(b1), FadeOut(b2), FadeOut(cap))
        dox = eq(r"\mathrm{do}(X = 1)", size=34, color=VIOLET).move_to(DOWN * 0.45)
        self.play(Write(dox))
        cut = ux.copy().set_color(RED)
        self.play(cut.animate.set_stroke(width=8), run_time=0.5)
        self.play(FadeOut(cut), FadeOut(ux), run_time=0.8)
        sq1 = Square(side_length=0.72, color=VIOLET, stroke_width=5).move_to(X1)
        sq2 = Square(side_length=0.72, color=VIOLET, stroke_width=5).move_to(X2)
        self.play(Create(sq1), Create(sq2))
        r1 = bar_chart([DO1[0]], [r"P(Y{=}1 \mid \mathrm{do}(X{=}1))"], lc + DOWN * 2.6, width=1.4, height=1.8, color=VIOLET, fmt="{:.1f}")
        r2 = bar_chart([DO1[1]], [r"P(Y{=}1 \mid \mathrm{do}(X{=}1))"], rc + DOWN * 2.6, width=1.4, height=1.8, color=VIOLET, fmt="{:.1f}")
        self.play(FadeIn(r1), FadeIn(r2))
        a1 = eq(r"\text{ATE} = 0.5 - 0.5 = 0", size=30, color=RED).next_to(r1, RIGHT, buff=0.3).shift(UP * 0.9)
        a2 = eq(r"\text{ATE} = 0.8 - 0.2 = 0.6", size=30, color=RED).next_to(r2, LEFT, buff=0.3).shift(DOWN * 0.3)
        self.play(Write(a1), Write(a2))
        msg = label("same P(X, Y), different P(Y | do(X)): the effect is not identified", 24, INK).move_to(DOWN * 3.65)
        self.play(FadeIn(msg))
        self.wait(2)
        _ = (DashedLine, Dot, ORIGIN)


# ---- scene 2 ----------------------------------------------------------------------------------
class BoundsFromConsistency(Scene):
    def construct(self):
        title = label("What the data do pin down: an interval", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        s1 = eq(r"P(Y_1{=}1)", r"=", r"P(Y_1{=}1, X{=}1)", r"+", r"P(Y_1{=}1, X{=}0)", size=34)
        s2 = eq(r"P(Y_1{=}1)", r"=", r"P(Y{=}1, X{=}1)", r"+", r"P(Y_1{=}1, X{=}0)", size=34)
        s3 = eq(r"P(Y_1{=}1)", r"\in", r"[\,0.4,\ 0.4 + 0.5\,]", r"=", r"[0.4, 0.9]", size=34)
        for m in (s1, s2, s3):
            m.move_to(UP * 2.1)
        why = label("consistency: if X = 1 then Y_1 = Y", 22, MUTED).next_to(s1, DOWN, buff=0.2)
        self.play(Write(s1))
        self.play(FadeIn(why))
        self.play(TransformMatchingTex(s1, s2), run_time=1.4)
        why2 = label("the unseen term lies between 0 and P(X = 0) = 0.5", 22, MUTED).next_to(s1, DOWN, buff=0.2)
        self.play(FadeOut(why), FadeIn(why2))
        self.play(TransformMatchingTex(s2, s3), run_time=1.4)
        s4 = eq(r"P(Y_0{=}1) \in [0.1, 0.6]", size=34).next_to(s3, DOWN, buff=0.75)
        self.play(FadeOut(why2), Write(s4))
        s5 = eq(r"\text{ATE} \in [0.4 - 0.6,\ 0.9 - 0.1] = [-0.2, 0.8]", size=34, color=VIOLET).next_to(s4, DOWN, buff=0.3)
        self.play(Write(s5))

        x0, x1 = -0.4, 1.0
        y = -2.0

        def X(v):
            return np.array([-5.0 + (v - x0) / (x1 - x0) * 10.0, y, 0])

        axis = Line(X(x0), X(x1), color=MUTED, stroke_width=2)
        ticks = VGroup(*[VGroup(Line(X(v) + UP * 0.08, X(v) + DOWN * 0.08, color=MUTED),
                                label(f"{v:g}", 22, MUTED).next_to(X(v), DOWN, buff=0.15)) for v in (-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0)])
        self.play(Create(axis), FadeIn(ticks))
        g = ValueTracker(1.0)
        bar = always_redraw(lambda: Line(X(M.ate_bounds(g.get_value())[0]), X(M.ate_bounds(g.get_value())[1]) + RIGHT * 1e-3,
                                         color=VIOLET, stroke_width=14))
        self.add(bar)
        m1 = VGroup(Dot(X(M.ATE_M1) + UP * 0.45, color=RED, radius=0.09), label("M1", 22, RED).next_to(X(M.ATE_M1) + UP * 0.45, UP, buff=0.08))
        m2 = VGroup(Dot(X(M.ATE_M2) + UP * 0.45, color=CYAN, radius=0.09), label("M2", 22, CYAN).next_to(X(M.ATE_M2) + UP * 0.45, UP, buff=0.08))
        self.play(FadeIn(m1), FadeIn(m2))
        self.wait(0.8)
        self.play(FadeOut(s3), FadeOut(s4), FadeOut(s5))
        assume = eq(r"\text{assume } |P(Y_x{=}1 \mid X{=}1{-}x) - P(Y_x{=}1 \mid X{=}x)| \le \gamma", size=32).move_to(UP * 2.1)
        self.play(Write(assume))
        rd = always_redraw(lambda: eq(rf"\gamma = {g.get_value():.2f}:\ \ \text{{ATE}} \in [{M.ate_bounds(g.get_value())[0]:.2f},\ {M.ate_bounds(g.get_value())[1]:.2f}]",
                                      size=32, color=VIOLET).move_to(UP * 1.0))
        self.add(rd)
        self.play(g.animate.set_value(0.6), run_time=3, rate_func=linear)
        self.wait(0.3)
        enter = label("M1 sits on the edge here: explaining the effect away needs confounding of 0.6", 22, RED).move_to(UP * 0.2)
        mark = eq(r"\gamma = 0.6", size=30, color=RED).next_to(enter, DOWN, buff=0.15)
        self.play(FadeIn(enter), FadeIn(mark))
        self.wait(1)
        self.play(FadeOut(enter), FadeOut(mark))
        self.play(g.animate.set_value(0.0), run_time=3, rate_func=linear)
        end = label("gamma = 0 (no confounding) identifies 0.6; a randomized experiment would test it", 22, INK).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(end))
        self.wait(2)


# ---- scene 3 ----------------------------------------------------------------------------------
class BasesReveal(Scene):
    def construct(self):
        title = label("Quantum data can see the direction", 32, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        cols = [(-4.4, "A → B: identity channel", M.T_IDENTITY, AMBER),
                (0.0, "common cause: classical", M.T_CLASSICAL, BLUE),
                (4.4, "common cause: |Φ+⟩", M.T_PHI, BLUE)]
        base_y, scale = -0.6, 1.25
        heads = VGroup()
        for x, name, _, col in cols:
            heads.add(label(name, 24, col).move_to([x, 2.55, 0]))
            heads.add(Line([x - 1.6, base_y, 0], [x + 1.6, base_y, 0], color=MUTED, stroke_width=2))
        self.play(FadeIn(heads))
        order = [(2, "zz", r"c_{zz}"), (0, "xx", r"c_{xx}"), (1, "yy", r"c_{yy}")]
        offs = {2: -1.0, 0: 0.0, 1: 1.0}
        for idx, _, tx in order:
            grp = VGroup()
            for x, _, t, col in cols:
                v = float(t[idx])
                h = max(abs(v) * scale, 0.03)
                r = Rectangle(width=0.6, height=h, fill_color=col, fill_opacity=0.75, stroke_color=INK, stroke_width=1)
                r.move_to([x + offs[idx], base_y + np.sign(v) * h / 2 if v != 0 else base_y, 0])
                grp.add(r)
                grp.add(label(f"{v:+.0f}" if v != 0 else "0", 22, INK).next_to(r, UP if v >= 0 else DOWN, buff=0.06))
                grp.add(eq(tx, size=32, color=MUTED).move_to([x + offs[idx], base_y - 1.75, 0]))
            self.play(FadeIn(grp), run_time=1.0)
            if idx == 2:
                z = label("measuring Z on both sides: all three look the same", 24, RED).move_to(DOWN * 3.0)
                self.play(FadeIn(z))
                self.wait(1.0)
                self.play(FadeOut(z))
        sums = VGroup(*[eq(rf"\Sigma = {int(round(t.sum()))}", size=30, color=col).move_to([x, -3.15, 0]) for x, _, t, col in cols])
        self.play(Write(sums))
        bound = eq(r"c_{xx} + c_{yy} + c_{zz} \le 1", r"\ \text{for every state, since it equals } 2\operatorname{Tr}(\rho F) - 1",
                   size=30).move_to(DOWN * 3.7)
        self.play(Write(bound))
        self.wait(2)


# ---- scene 4 ----------------------------------------------------------------------------------
class CorrelationTetrahedra(ThreeDScene):
    def construct(self):
        s = 1.8
        self.set_camera_orientation(phi=68 * DEGREES, theta=-40 * DEGREES, zoom=0.9)
        title = label("Where the data identify the causal direction", 30, INK, "BOLD").to_edge(UP, buff=0.25)
        self.add_fixed_in_frame_mobjects(title)
        self.remove(title)
        corners = [np.array(c) for c in np.array(np.meshgrid([-1, 1], [-1, 1], [-1, 1])).T.reshape(-1, 3)]
        cube = VGroup()
        for a in corners:
            for b in corners:
                if np.sum(np.abs(a - b)) == 2 and tuple(a) < tuple(b):
                    cube.add(Line3D(s * a, s * b, color=GRID, thickness=0.006))
        self.play(FadeIn(title), Create(cube), run_time=1.5)
        faces = [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]]
        st = Polyhedron([list(s * v) for v in M.STATE_VERTS], faces,
                        faces_config={"fill_color": BLUE, "fill_opacity": 0.22, "stroke_color": BLUE, "stroke_width": 2})
        ch = Polyhedron([list(s * v) for v in M.CHAN_VERTS], faces,
                        faces_config={"fill_color": AMBER, "fill_opacity": 0.22, "stroke_color": AMBER, "stroke_width": 2})
        for p in (st, ch):
            p.graph.set_opacity(0)          # hide the vertex dots
        k1 = label("blue: correlations of any common-cause state", 22, BLUE)
        k2 = label("amber: any direct-cause channel A → B", 22, AMBER)
        k3 = eq(r"\text{overlap: } |c_1| + |c_2| + |c_3| \le 1", size=30, color=VIOLET)
        keys = VGroup(k1, k2, k3).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(DOWN + LEFT, buff=0.3)
        self.add_fixed_in_frame_mobjects(keys)
        self.remove(keys)
        self.play(Create(st), FadeIn(k1), run_time=1.8)
        self.play(Create(ch), FadeIn(k2), run_time=1.8)
        octa_faces = [[0, 2, 4], [0, 3, 4], [1, 2, 4], [1, 3, 4], [0, 2, 5], [0, 3, 5], [1, 2, 5], [1, 3, 5]]
        oc = Polyhedron([list(s * v) for v in M.OCTA_VERTS], octa_faces,
                        faces_config={"fill_color": VIOLET, "fill_opacity": 0.45, "stroke_color": VIOLET, "stroke_width": 2})
        oc.graph.set_opacity(0)
        self.play(FadeIn(oc), FadeIn(k3), run_time=1.5)
        pts = [(M.T_IDENTITY, AMBER, "identity (1, 1, 1)"), (M.T_PHI, BLUE, "Φ+ (1, -1, 1)"), (M.T_CLASSICAL, VIOLET, "classical (0, 0, 1)")]
        tags = VGroup()
        for i, (t, col, name) in enumerate(pts):
            d = Dot3D(s * np.array(t, dtype=float), color=col, radius=0.1)
            self.play(FadeIn(d), run_time=0.5)
            tag = label(name, 22, col)
            tags.add(tag)
        tags.arrange(DOWN, aligned_edge=RIGHT, buff=0.12).to_corner(UP + RIGHT, buff=0.3).shift(DOWN * 0.6)
        self.add_fixed_in_frame_mobjects(tags)
        self.remove(tags)
        self.play(FadeIn(tags))
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        self.wait(0.5)
        _ = (linear, PI, RIGHT, LEFT, UP, CYAN, MUTED, RED)
