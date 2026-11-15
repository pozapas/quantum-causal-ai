"""L4-08 Causal discovery and its limits: three 3Blue1Brown-style scenes.

MarkovEquivalence   on the skeleton X - Y - Z the arrows flip through chain, reverse chain and fork while the
                    implied independences stay put; the collider X -> Y <- Z swaps them.  Verma-Pearl at the end.
PCRun               the PC algorithm on V -> W, V -> X, W -> Y, X -> Y, Y -> Z, driven by an actual run with a
                    d-separation oracle: edges removed by tests, the collider oriented, Meek rule 1, the pattern.
FaithfulnessCancel  X -> Y -> Z plus X -> Z: sweeping the direct weight c traces corr(X, Z) through zero at
                    c = -ab; there PC confidently returns the wrong graph X -> Y <- Z.
All numbers and the PC log come from qcai.lessonfigs.l4_08, the module the lesson text uses.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import networkx as nx
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Axes, Circle, Create, DashedLine, DecimalNumber, Dot, FadeIn,
                   FadeOut, Indicate, Line, ReplacementTransform, RoundedRectangle, Scene, Transform,
                   TransformMatchingTex, ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, INK, MUTED, RED, VIOLET, eq, label
from qcai.lessonfigs import l4_08 as M

IND = r"\perp\!\!\!\perp"
NIND = r"\not\!" + IND
RUN = M.PC_RUN
SEP_TEX = [rf"{a} {IND} {b} \mid {', '.join(S)}" for a, b, S in RUN["log"]]
assert SEP_TEX[1] == r"W \perp\!\!\!\perp X \mid V" and SEP_TEX[-1] == r"V \perp\!\!\!\perp Y \mid W, X"
COV_TEX = r"\mathrm{Cov}(X, Z) = c + ab"
CANCEL_TEX = rf"c = -ab = {M.C_CANCEL:.1f}"
assert CANCEL_TEX == "c = -ab = -0.8"
VP_TEXT = "same skeleton and same v-structures"

# verify the four three-node graphs before drawing them
GRAPHS = [("chain", [("X", "Y"), ("Y", "Z")]), ("reverse chain", [("Z", "Y"), ("Y", "X")]),
          ("fork", [("Y", "X"), ("Y", "Z")]), ("collider", [("X", "Y"), ("Z", "Y")])]
for _name, _e in GRAPHS:
    _d = nx.DiGraph(_e)
    _pair = (nx.is_d_separator(_d, {"X"}, {"Z"}, set()), nx.is_d_separator(_d, {"X"}, {"Z"}, {"Y"}))
    assert _pair == ((True, False) if _name == "collider" else (False, True))


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return [SEP_TEX[1], SEP_TEX[-1], COV_TEX, CANCEL_TEX, VP_TEXT]


def node(name, pos, color=INK, r=0.34, size=34):
    return VGroup(Circle(radius=r, color=color, stroke_width=4).move_to(pos), eq(name, size=size, color=color).move_to(pos))


def arrow(p, q, color=INK, buff=0.4, width=5):
    return Arrow(p, q, buff=buff, color=color, stroke_width=width, max_tip_length_to_length_ratio=0.2)


def segment(p, q, color=INK, buff=0.4, width=5):
    return Line(p, q, buff=buff, color=color, stroke_width=width)


class MarkovEquivalence(Scene):
    def construct(self):
        title = label("Which arrows can independence tests see?", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=1.2)
        P = {"X": [-5.6, 1.5, 0], "Y": [-3.6, 1.5, 0], "Z": [-1.6, 1.5, 0]}
        nodes = VGroup(*[node(k, v) for k, v in P.items()])
        skel = VGroup(segment(P["X"], P["Y"]), segment(P["Y"], P["Z"]))
        self.play(FadeIn(nodes), Create(skel))
        name = label("skeleton X - Y - Z", 26, MUTED).move_to([-3.6, 0.6, 0])
        self.play(FadeIn(name))

        def arrows_for(edges, color=VIOLET):
            return VGroup(*[arrow(P[a], P[b], color) for a, b in edges])

        ind1 = VGroup(eq(rf"X {NIND} Z", size=38, color=VIOLET), eq(rf"X {IND} Z \mid Y", size=38, color=VIOLET))
        ind1.arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([3.4, 1.55, 0])
        head = label("implied by d-separation", 24, MUTED).next_to(ind1, UP, buff=0.3)
        cur = arrows_for(GRAPHS[0][1])
        nm = label("chain", 28, VIOLET).move_to(name)
        self.play(ReplacementTransform(skel, cur), ReplacementTransform(name, nm))
        self.play(FadeIn(head), Write(ind1))
        self.wait(0.8)
        for gname, edges in GRAPHS[1:3]:
            nxt = arrows_for(edges)
            nm2 = label(gname, 28, VIOLET).move_to(nm)
            self.play(Transform(cur, nxt), Transform(nm, nm2), run_time=1.4)
            same = label("same", 24, VIOLET).next_to(ind1, RIGHT, buff=0.3)
            self.play(Indicate(ind1, color=VIOLET), FadeIn(same))
            self.play(FadeOut(same))

        coll = arrows_for(GRAPHS[3][1], RED)
        nm3 = label("collider (v-structure)", 28, RED).move_to(nm)
        ind2 = VGroup(eq(rf"X {IND} Z", size=38, color=RED), eq(rf"X {NIND} Z \mid Y", size=38, color=RED))
        ind2.arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(ind1)
        self.play(Transform(cur, coll), Transform(nm, nm3), run_time=1.4)
        self.play(ReplacementTransform(ind1, ind2), run_time=1.4)
        self.wait(1.0)

        # the two classes, side by side
        def mini(edges, center, color, und=False, s=0.5):
            pts = {k: [center[0] + (i - 1) * s * 1.6, center[1], 0] for i, k in enumerate("XYZ")}
            g = VGroup(*[node(k, pts[k], color, r=0.21, size=24) for k in "XYZ"])
            for a, b in edges:
                if und:
                    g.add(segment(pts[a], pts[b], color, buff=0.23, width=4))
                else:
                    g.add(Arrow(pts[a], pts[b], buff=0.22, color=color, stroke_width=4, tip_length=0.2,
                                max_tip_length_to_length_ratio=0.5, max_stroke_width_to_length_ratio=20))
            return g
        row = VGroup(*[mini(e, [-5.3 + 2.45 * i, -0.9, 0], VIOLET) for i, (_, e) in enumerate(GRAPHS[:3])])
        box1 = RoundedRectangle(corner_radius=0.2, width=7.3, height=1.1, color=VIOLET).move_to([-2.85, -0.9, 0])
        colm = mini(GRAPHS[3][1], [3.4, -0.9, 0], RED)
        box2 = RoundedRectangle(corner_radius=0.2, width=2.7, height=1.1, color=RED).move_to([3.4, -0.9, 0])
        self.play(FadeIn(row), Create(box1), FadeIn(colm), Create(box2), run_time=1.6)
        pat1 = mini([("X", "Y"), ("Y", "Z")], [-5.0, -2.2, 0], VIOLET, und=True)
        pat1l = label("one class: pattern X - Y - Z", 24, VIOLET).next_to(pat1, RIGHT, buff=0.3)
        pat2l = label("a class of its own", 24, RED).move_to([3.4, -2.2, 0])
        self.play(FadeIn(pat1), FadeIn(pat1l), FadeIn(pat2l))
        thm = label("Markov equivalent  <=>  " + VP_TEXT + "  (Verma and Pearl)", 26, INK).move_to([0, -3.25, 0])
        self.play(Write(thm), run_time=1.6)
        self.wait(2.5)


class PCRun(Scene):
    def construct(self):
        title = label("The PC algorithm: delete by tests, then orient", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=1.2)
        P = {"V": [-4.3, 2.0, 0], "W": [-5.8, 0.6, 0], "X": [-2.8, 0.6, 0], "Y": [-4.3, -0.8, 0], "Z": [-4.3, -2.4, 0]}
        nodes = VGroup(*[node(k, v) for k, v in P.items()])
        edges = {}
        for i, a in enumerate(M.PC_NODES):
            for b in M.PC_NODES[i + 1:]:
                edges[frozenset((a, b))] = segment(P[a], P[b], MUTED, buff=0.38, width=3)
        self.play(FadeIn(nodes), *[Create(e) for e in edges.values()], run_time=1.6)
        start = label("start: every pair joined (10 edges)", 24, MUTED).move_to([-4.3, -3.3, 0])
        self.play(FadeIn(start))

        h1 = label("1. Skeleton: delete edges by independence tests", 24, INK, "BOLD").move_to([2.3, 2.55, 0])
        self.play(FadeIn(h1))
        lev0 = label("size 0: every pair is dependent, nothing removed", 24, MUTED).move_to([2.3, 2.0, 0])
        assert all(len(S) > 0 for _, _, S in RUN["log"])
        self.play(FadeIn(lev0))
        self.wait(0.6)
        self.play(FadeOut(lev0))
        y0 = 2.0
        lines = VGroup()
        for k, ((a, b, S), t) in enumerate(zip(RUN["log"], SEP_TEX)):
            e = edges.pop(frozenset((a, b)))
            row = eq(t, size=32, color=RED).move_to([2.3, y0 - 0.5 * k, 0])
            self.play(e.animate.set_color(RED).set_stroke(width=6), Write(row), run_time=0.9)
            self.play(FadeOut(e), row.animate.set_color(INK), run_time=0.6)
            lines.add(row)
        for e in edges.values():
            e.set_color(INK)
        self.play(*[e.animate.set_color(INK).set_stroke(width=5) for e in edges.values()], FadeOut(start))
        self.wait(0.5)

        h2 = label("2. Orient colliders", 24, INK, "BOLD").move_to([2.3, -0.75, 0])
        (cx, cy, cz), = RUN["colliders"]
        sep = sorted(RUN["sep"][frozenset((cx, cz))])
        ct = eq(rf"{cx} - {cy} - {cz},\ \ {cy} \notin \mathrm{{sep}}({cx}, {cz}) = \{{{', '.join(sep)}\}}", size=30,
                color=RED).move_to([2.3, -1.3, 0])
        self.play(FadeIn(h2), Write(ct))
        self.play(*[ReplacementTransform(edges[frozenset((s, cy))], arrow(P[s], P[cy], RED, buff=0.38))
                    for s in (cx, cz)], run_time=1.4)
        self.wait(0.6)

        (rule, p, q), = RUN["meek"]
        h3 = label(f"3. Meek rule {rule}: avoid a new collider", 24, INK, "BOLD").move_to([2.3, -2.0, 0])
        mt = eq(rf"{cx} \to {p} - {q},\ {cx} \text{{ and }} {q} \text{{ not adjacent}} \ \Rightarrow\ {p} \to {q}",
                size=30, color=BLUE).move_to([2.3, -2.55, 0])
        self.play(FadeIn(h3), Write(mt))
        self.play(ReplacementTransform(edges[frozenset((p, q))], arrow(P[p], P[q], BLUE, buff=0.38)), run_time=1.2)
        und = ", ".join(f"{a} - {b}" for a, b in RUN["undirected"])
        fin = label(f"output: a pattern; {und} stay undirected", 24, VIOLET).move_to([2.3, -3.25, 0])
        self.play(FadeIn(fin), *[Indicate(edges[frozenset(e)], color=VIOLET) for e in RUN["undirected"]])
        self.wait(2.5)
        _ = (lines, AMBER, CYAN, DOWN, RIGHT)


class FaithfulnessCancel(Scene):
    def construct(self):
        title = label("Faithfulness: when two paths cancel", 32, INK, "BOLD").to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=1.2)
        P = {"X": [-5.8, -0.3, 0], "Y": [-4.4, 1.6, 0], "Z": [-3.0, -0.3, 0]}
        nodes = VGroup(*[node(k, v) for k, v in P.items()])
        exy, eyz, exz = arrow(P["X"], P["Y"]), arrow(P["Y"], P["Z"]), arrow(P["X"], P["Z"], AMBER)
        la = eq(rf"a = {M.A_W:g}", size=30).next_to(exy.get_center(), LEFT, buff=0.3)
        lb = eq(rf"b = {M.B_W:g}", size=30).next_to(eyz.get_center(), RIGHT, buff=0.3)
        c = ValueTracker(0.4)
        lc = eq("c", size=30, color=AMBER).next_to(exz, DOWN, buff=0.2)
        self.play(FadeIn(nodes), Create(exy), Create(eyz), Create(exz), Write(la), Write(lb), Write(lc))
        cov = eq(COV_TEX, size=34).move_to([-4.4, -1.6, 0])
        noise = label("unit-variance Gaussian noises", 22, MUTED).next_to(cov, DOWN, buff=0.2)
        self.play(Write(cov), FadeIn(noise))

        ax = Axes(x_range=[-1.6, 0.4, 0.4], y_range=[-0.8, 0.8, 0.4], x_length=6.4, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 24},
                  x_axis_config={"include_numbers": True, "numbers_to_include": [-1.6, -1.2, -0.8, -0.4],
                                 "decimal_number_config": {"num_decimal_places": 1, "color": MUTED}},
                  ).move_to([3.1, 0.0, 0])
        yt = VGroup(*[eq(f"{v:g}", size=24, color=MUTED).next_to(ax.c2p(-1.6, v), LEFT, buff=0.15)
                      for v in (-0.8, -0.4, 0, 0.4, 0.8)])
        grid = VGroup(*[DashedLine(ax.c2p(-1.6, v), ax.c2p(0.4, v), color=MUTED, stroke_width=1, dash_length=0.05)
                        .set_opacity(0.4) for v in (-0.8, -0.4, 0.4, 0.8)])
        xl = eq("c", size=30, color=AMBER).next_to(ax.x_axis, RIGHT, buff=0.15)
        k1 = eq(r"\mathrm{corr}(X, Z)", size=30, color=VIOLET).move_to(ax.c2p(-1.3, 0.68))
        k2 = eq(r"\mathrm{corr}(X, Z \mid Y)", size=30, color=CYAN).move_to(ax.c2p(-1.3, 0.45))
        self.play(Create(ax), FadeIn(yt), FadeIn(grid), FadeIn(xl), Write(k1), Write(k2))
        low = [0.399]

        def lo():
            low[0] = min(low[0], c.get_value())
            return low[0]
        c1 = always_redraw(lambda: ax.plot(M.corr_xz, x_range=[lo(), 0.4, 0.01], color=VIOLET, stroke_width=4))
        c2 = always_redraw(lambda: ax.plot(M.pcorr_xz_y, x_range=[lo(), 0.4, 0.01], color=CYAN, stroke_width=4))
        d1 = always_redraw(lambda: Dot(ax.c2p(c.get_value(), M.corr_xz(c.get_value())), color=VIOLET, radius=0.07))
        d2 = always_redraw(lambda: Dot(ax.c2p(c.get_value(), M.pcorr_xz_y(c.get_value())), color=CYAN, radius=0.07))
        cval = DecimalNumber(0.4, num_decimal_places=2, font_size=30, color=AMBER)
        cval.add_updater(lambda m: m.set_value(c.get_value()).next_to(lc, RIGHT, buff=0.15))
        ceq = eq("=", size=30, color=AMBER).next_to(lc, RIGHT, buff=0.08)
        cval.next_to(ceq, RIGHT, buff=0.1)
        cval.clear_updaters()
        cval.add_updater(lambda m: m.set_value(c.get_value()).next_to(ceq, RIGHT, buff=0.1))
        self.add(c1, c2, d1, d2, ceq, cval)
        self.play(c.animate.set_value(-1.6), run_time=7, rate_func=linear)
        self.play(c.animate.set_value(M.C_CANCEL), run_time=2.2)
        zero = DashedLine(ax.c2p(M.C_CANCEL, -0.8), ax.c2p(M.C_CANCEL, 0.8), color=RED)
        ct = eq(CANCEL_TEX, size=32, color=RED).next_to(ax.c2p(M.C_CANCEL, 0.8), UP, buff=0.05).shift(RIGHT * 0.3)
        self.play(Create(zero), Write(ct))
        note = label("corr(X, Z) = 0 although X -> Z exists", 24, RED).move_to([3.1, -2.75, 0])
        self.play(FadeIn(note))
        self.wait(1.0)

        # what PC concludes from these independences
        out = M.pc_threshold(M.C_CANCEL)
        assert out["directed"] == [(0, 1), (2, 1)]
        nm = {0: "X", 1: "Y", 2: "Z"}
        self.play(FadeOut(VGroup(la, lb, lc, ceq, cval, cov, noise)))
        wrong = VGroup(*[arrow(P[nm[a]], P[nm[b]], RED) for a, b in out["directed"]])
        self.play(FadeOut(exz), ReplacementTransform(VGroup(exy, eyz), wrong), run_time=1.6)
        pcl = label("PC output: X -> Y <- Z", 26, RED).move_to([-4.4, -1.5, 0])
        why = VGroup(label("X - Z removed: X and Z independent", 22, MUTED),
                     label("Y not in sep(X, Z): collider", 22, MUTED),
                     label("missing edge, Y -> Z reversed", 22, RED)).arrange(DOWN, buff=0.15).next_to(pcl, DOWN, buff=0.25)
        self.play(FadeIn(pcl), FadeIn(why, lag_ratio=0.3), run_time=1.6)
        self.wait(2.5)
        _ = (BLUE, Transform, TransformMatchingTex, RIGHT)
