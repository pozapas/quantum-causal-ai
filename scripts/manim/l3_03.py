"""L3-03 Matrices as transformations: three 3Blue1Brown-style scenes.

GridTransformations  LinearTransformationScene: the whole grid under a quarter-turn rotation R, a shear S,
                     a reflection F and a collapse C; the unit square's signed area is the determinant
                     (1, 1, -1, 0), and C squashes the plane onto a line, so it cannot be undone.
CompositionOrder     apply S then R (the product RS) and R then S (the product SR): the basis vectors land in
                     different places, so RS != SR.
NormPreserving       a point runs around the unit circle; a rotation keeps its length 1 while the shear S
                     stretches the circle into an ellipse with lengths between 0.618 and 1.618.
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from manim import (DOWN, LEFT, RIGHT, UL, UP, UR, WHITE, Arrow, BackgroundRectangle, Circle, Create,  # noqa: E402
                   DecimalNumber, Dot, FadeIn, FadeOut, LinearTransformationScene, NumberPlane, ParametricFunction,
                   Scene, Transform, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE_LIGHT, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label  # noqa: E402

R = np.array([[0, -1], [1, 0]])
S = np.array([[1, 1], [0, 1]])
F = np.array([[1, 0], [0, -1]])
C = np.array([[1, 2], [0.5, 1]])
DETS = {k: round(float(np.linalg.det(M)), 10) for k, M in (("R", R), ("S", S), ("F", F), ("C", C))}
assert DETS == {"R": 1.0, "S": 1.0, "F": -1.0, "C": 0.0}
RS, SR = R @ S, S @ R
assert (RS == np.array([[0, -1], [1, 1]])).all() and (SR == np.array([[1, -1], [1, 0]])).all()
SV = np.linalg.svd(S, compute_uv=False)                  # singular values of the shear
GOLD = (1 + math.sqrt(5)) / 2
assert abs(SV[0] - GOLD) < 1e-12 and abs(SV[1] - 1 / GOLD) < 1e-12
ROT30 = np.array([[math.cos(math.pi / 6), -math.sin(math.pi / 6)], [math.sin(math.pi / 6), math.cos(math.pi / 6)]])
assert np.allclose(ROT30.T @ ROT30, np.eye(2))


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["\\det R = 1", "\\det S = 1", "\\det F = -1", "\\det C = 0", "RS \\ne SR", "1.618", "0.618"]


def mat(name, M):
    rows = r" \\ ".join(" & ".join(_fmt(x) for x in row) for row in M)
    return rf"{name} = \begin{{pmatrix}} {rows} \end{{pmatrix}}"


def _fmt(x):
    x = float(x)
    if abs(x - round(x)) < 1e-12:
        return str(int(round(x)))
    return {0.5: r"\tfrac12"}.get(x, f"{x:g}")


PLANE_KW = dict(
    show_coordinates=False, leave_ghost_vectors=False, show_basis_vectors=True,
    background_plane_kwargs={"background_line_style": {"stroke_color": GRID, "stroke_width": 1},
                             "axis_config": {"color": GRID}},
    foreground_plane_kwargs={"x_range": [-10, 10], "y_range": [-7, 7], "faded_line_ratio": 1,
                             "background_line_style": {"stroke_color": BLUE_LIGHT, "stroke_width": 1.3},
                             "axis_config": {"color": MUTED}},
    i_hat_color=VIOLET, j_hat_color=AMBER)


def card(*lines, corner=UL):
    g = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_corner(corner, buff=0.3)
    return VGroup(BackgroundRectangle(g, color=WHITE, fill_opacity=0.92, buff=0.15), g)


def swap(scene, old, new, run_time=0.8):
    """Replace a card.  Cards sit above the moving grid by z_index (fading foreground mobjects breaks
    LinearTransformationScene in Manim 0.22)."""
    scene.play(FadeOut(old), FadeIn(new.set_z_index(10)), run_time=run_time)
    return new


def pt(x, y):
    """Screen point of plane coordinates (x, y); the plane's own c2p moves with the grid."""
    return np.array([float(x), float(y), 0.0])


def top(*mobs):
    return [m.set_z_index(10) for m in mobs]


class GridScene(LinearTransformationScene):
    """LinearTransformationScene with the course plane.  Manim 0.22's Scene.play overwrites the attribute
    `moving_mobjects`, which LinearTransformationScene also uses for its own list; clear it before each
    transformation so that earlier animations are not dragged along."""

    def __init__(self, **kw):
        super().__init__(**PLANE_KW, **kw)

    def apply_function(self, function, added_anims=[], **kwargs):  # noqa: B006
        self.moving_mobjects = []
        super().apply_function(function, added_anims=added_anims, **kwargs)


class GridTransformations(GridScene):

    def construct(self):
        self.add_unit_square(color=CYAN, opacity=0.35)
        info = card(label("Columns = where the basis vectors land", 28, INK, "BOLD"),
                    eq(r"M e_0 = \text{column } 1, \quad M e_1 = \text{column } 2", size=34))
        self.add(*top(info))
        self.wait(1.5)
        steps = [("R", R, "quarter turn", "area kept"), ("S", S, "shear", "area kept, shape changes"),
                 ("F", F, "reflection", "area kept, orientation flips"),
                 ("C", C, "collapse onto a line", "area 0: no way back")]
        for name, M, what, area in steps:
            new = card(label(what, 28, INK, "BOLD"), eq(mat(name, M), size=36),
                       eq(rf"\det {name} = {int(DETS[name])}", size=36, color=RED), label(area, 26, MUTED))
            info = swap(self, info, new)
            self.apply_matrix(M, run_time=1.4)
            self.wait(1.2)
            if name != "C":
                self.apply_inverse(M, run_time=0.7)
                self.wait(0.3)
        ker = Arrow(pt(0, 0), pt(2, -1), buff=0, color=RED, stroke_width=6)
        kl = eq(r"C\,(2, -1) = (0, 0)", size=34, color=RED).next_to(ker.get_end(), DOWN, buff=0.15)
        kb = BackgroundRectangle(kl, color=WHITE, fill_opacity=0.92, buff=0.08)
        top(ker, kb, kl)
        self.play(Create(ker), FadeIn(kb), Write(kl))
        self.wait(2)


class CompositionOrder(GridScene):

    def construct(self):
        self.add_unit_square(color=CYAN, opacity=0.35)
        info = card(label("Order matters: RS means S first, then R", 28, INK, "BOLD"),
                    eq(mat("R", R) + r",\quad " + mat("S", S), size=34))
        self.add(*top(info))
        self.wait(1.5)
        new = card(label("RS: shear first, then turn", 28, INK, "BOLD"), eq(mat("RS", RS), size=36))
        info = swap(self, info, new)
        self.apply_matrix(S, run_time=1.3)
        self.apply_matrix(R, run_time=1.3)
        mark1 = VGroup(Dot(pt(*RS[:, 0]), color=VIOLET, radius=0.09), Dot(pt(*RS[:, 1]), color=AMBER, radius=0.09))
        top(mark1)
        self.play(FadeIn(mark1))
        self.wait(1.2)
        self.apply_inverse(RS, run_time=1.2)
        new = card(label("SR: turn first, then shear", 28, INK, "BOLD"), eq(mat("SR", SR), size=36))
        info = swap(self, info, new)
        self.apply_matrix(R, run_time=1.3)
        self.apply_matrix(S, run_time=1.3)
        self.wait(0.6)
        res = card(eq(mat("RS", RS), size=34), eq(mat("SR", SR), size=34),
                   eq(r"RS \ne SR", size=40, color=RED), label("dots: where RS sent the basis", 24, MUTED), corner=UR)
        top(res)
        self.play(FadeIn(res))
        self.wait(2.5)


class NormPreserving(Scene):
    def construct(self):
        title = label("Which matrices keep every length?", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        unit = 1.25
        planes = []
        for x in (-3.4, 3.4):
            p = NumberPlane(x_range=[-2, 2, 1], y_range=[-2, 2, 1], x_length=4 * unit, y_length=4 * unit,
                            background_line_style={"stroke_color": GRID, "stroke_width": 1},
                            axis_config={"color": MUTED}).move_to(RIGHT * x + DOWN * 0.55)
            planes.append(p)
        pl, pr = planes
        heads = VGroup(eq(r"R_{30}: \text{ rotation by } 30^\circ", size=34, color=VIOLET).next_to(pl, UP, buff=0.15),
                       eq(mat("S", S), size=34, color=AMBER).next_to(pr, UP, buff=0.1))
        self.play(Create(pl), Create(pr), Write(heads))
        circles = VGroup(*[Circle(radius=unit, color=MUTED, stroke_width=2).move_to(p.c2p(0, 0)) for p in planes])
        self.play(Create(circles))
        ell_l = ParametricFunction(lambda t: pl.c2p(*(ROT30 @ np.array([math.cos(t), math.sin(t)]))), t_range=[0, 2 * math.pi],
                                   color=VIOLET, stroke_width=4)
        ell_r = ParametricFunction(lambda t: pr.c2p(*(S @ np.array([math.cos(t), math.sin(t)]))), t_range=[0, 2 * math.pi],
                                   color=AMBER, stroke_width=4)
        self.play(Create(ell_l), Create(ell_r), run_time=1.6)
        t = ValueTracker(0.0)

        def x_of():
            a = t.get_value()
            return np.array([math.cos(a), math.sin(a)])

        inl = always_redraw(lambda: Arrow(pl.c2p(0, 0), pl.c2p(*x_of()), buff=0, color=MUTED, stroke_width=3,
                                          max_tip_length_to_length_ratio=0.15))
        inr = always_redraw(lambda: Arrow(pr.c2p(0, 0), pr.c2p(*x_of()), buff=0, color=MUTED, stroke_width=3,
                                          max_tip_length_to_length_ratio=0.15))
        outl = always_redraw(lambda: Arrow(pl.c2p(0, 0), pl.c2p(*(ROT30 @ x_of())), buff=0, color=VIOLET, stroke_width=6,
                                           max_tip_length_to_length_ratio=0.15))
        outr = always_redraw(lambda: Arrow(pr.c2p(0, 0), pr.c2p(*(S @ x_of())), buff=0, color=AMBER, stroke_width=6,
                                           max_tip_length_to_length_ratio=0.15))
        self.play(Create(inl), Create(inr), Create(outl), Create(outr))
        nl = DecimalNumber(1.0, num_decimal_places=3, color=VIOLET, font_size=36)
        nr = DecimalNumber(1.0, num_decimal_places=3, color=AMBER, font_size=36)
        ll = eq(r"\|R_{30}x\| =", size=36, color=VIOLET)
        lr = eq(r"\|Sx\| =", size=36, color=AMBER)
        gl = VGroup(ll, nl).arrange(RIGHT, buff=0.15).next_to(pl, DOWN, buff=0.12)
        gr = VGroup(lr, nr).arrange(RIGHT, buff=0.15).next_to(pr, DOWN, buff=0.12)
        nl.add_updater(lambda m: m.set_value(float(np.linalg.norm(ROT30 @ x_of()))))
        nr.add_updater(lambda m: m.set_value(float(np.linalg.norm(S @ x_of()))))
        self.play(FadeIn(gl), FadeIn(gr))
        self.play(t.animate.set_value(2 * math.pi), run_time=10, rate_func=linear)
        self.wait(0.5)
        # show the extremes of the shear
        a_max = math.atan2(GOLD, 1)        # input direction (1, golden ratio) is stretched most
        self.play(t.animate.set_value(2 * math.pi + a_max), run_time=1.2)
        mx = label("longest: 1.618", 26, AMBER).move_to(pr.c2p(-0.9, 1.7))
        self.play(FadeIn(mx))
        self.play(t.animate.set_value(2 * math.pi + a_max + math.pi / 2), run_time=1.4)
        mn = label("shortest: 0.618", 26, AMBER).move_to(pr.c2p(0.9, -1.7))
        self.play(FadeIn(mn))
        both = label("det S = 1, yet lengths change: area is not length", 30, RED, "BOLD").move_to(title)
        self.play(FadeOut(title), FadeIn(both))
        self.wait(2)
