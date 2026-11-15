"""L3-08 Entropy and uncertainty: three 3Blue1Brown-style scenes.

SurpriseToEntropy   the distribution (1/2, 1/4, 1/8, 1/8): probability bars turn into surprise bars
                    -log2 p = 1, 2, 3, 3, and the probability-weighted average collapses term by term
                    to H = 1.75 bits; observing D carries 3 bits of surprise, but H stays 1.75.
BinaryEntropySweep  a coin with P(heads) = p; as p sweeps from 0 to 1 the bars change and a live trace
                    draws the binary entropy h(p), with h(0.1) = 0.469 and h(0.5) = 1 marked.
QuestionTree        bits as yes/no questions: 8 equally likely outcomes need log2 8 = 3 questions; the
                    skewed distribution needs 1.75 questions on average, exactly H, because every
                    probability is a power of 1/2.
Numbers are computed here and checked against the lesson text by facts().
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Axes, Create, DashedLine, DecimalNumber, Dot, FadeIn, FadeOut, Indicate,
                   Line, Rectangle, Scene, SurroundingRectangle, TracedPath, Transform, TransformMatchingTex,
                   ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

P = [0.5, 0.25, 0.125, 0.125]
NAMES = ["A", "B", "C", "D"]
SURPRISE = [-math.log2(p) for p in P]                 # 1, 2, 3, 3 bits
H = sum(p * s for p, s in zip(P, SURPRISE))           # 1.75 bits
assert SURPRISE == [1.0, 2.0, 3.0, 3.0] and H == 1.75


def h2(p: float) -> float:
    """Binary entropy in bits, with 0 log 0 = 0."""
    return 0.0 if p in (0.0, 1.0) else -p * math.log2(p) - (1 - p) * math.log2(1 - p)


H01 = h2(0.1)
assert abs(H01 - 0.4690) < 1e-4 and h2(0.5) == 1.0
DEPTHS = [1, 2, 3, 3]                                  # questions needed in the skewed tree
EXPECTED_Q = sum(p * d for p, d in zip(P, DEPTHS))
assert EXPECTED_Q == H


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["1.75", f"{H01:.3f}", "h(p) = -p\\log_2 p - (1-p)\\log_2(1-p)", "\\log_2 8 = 3",
            "-\\log_2 p"]


class SurpriseToEntropy(Scene):
    def construct(self):
        title = label("Entropy is average surprise", 36, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)
        base = -0.9
        # left: probability bars
        lx = [-5.6 + 1.05 * i for i in range(4)]
        pbars = VGroup(*[Rectangle(width=0.7, height=p * 4.4, fill_color=BLUE, fill_opacity=0.85, stroke_width=0)
                         .move_to([x, base + p * 2.2, 0]) for x, p in zip(lx, P)])
        pnames = VGroup(*[label(n, 28, INK).move_to([x, base - 0.35, 0]) for x, n in zip(lx, NAMES)])
        pvals = VGroup(*[eq(t, size=38, color=BLUE).next_to(b, UP, buff=0.12)
                         for t, b in zip([r"\tfrac12", r"\tfrac14", r"\tfrac18", r"\tfrac18"], pbars)])
        ptitle = label("probability p", 28, BLUE).move_to([-4.0, 2.55, 0])
        axis_l = Line([-6.1, base, 0], [-1.9, base, 0], color=MUTED)
        self.play(Create(axis_l), FadeIn(pnames), FadeIn(ptitle))
        self.play(*[Create(b) for b in pbars], Write(pvals), run_time=1.4)
        self.wait(0.4)

        # right: surprise bars
        rx = [1.9 + 1.05 * i for i in range(4)]
        axis_r = Line([1.4, base, 0], [5.6, base, 0], color=MUTED)
        rnames = VGroup(*[label(n, 28, INK).move_to([x, base - 0.35, 0]) for x, n in zip(rx, NAMES)])
        rtitle = eq(r"\text{surprise } -\log_2 p", size=34, color=AMBER).move_to([3.5, 2.55, 0])
        sbars = VGroup(*[Rectangle(width=0.7, height=s * 0.8, fill_color=AMBER, fill_opacity=0.85, stroke_width=0)
                         .move_to([x, base + s * 0.4, 0]) for x, s in zip(rx, SURPRISE)])
        svals = VGroup(*[eq(f"{int(s)}", size=32, color=AMBER).next_to(b, UP, buff=0.12) for s, b in zip(SURPRISE, sbars)])
        self.play(Create(axis_r), FadeIn(rnames), Write(rtitle))
        self.play(*[Transform(pb.copy(), sb) for pb, sb in zip(pbars, sbars)], run_time=1.6)
        self.add(sbars)
        self.play(Write(svals))
        note = label("rare outcomes surprise more", 26, MUTED).move_to([3.5, -1.75, 0])
        self.play(FadeIn(note))
        self.wait(0.6)

        # weighted average, term by term
        f1 = eq("H", "=", r"\tfrac12\cdot 1", "+", r"\tfrac14\cdot 2", "+", r"\tfrac18\cdot 3", "+", r"\tfrac18\cdot 3",
                size=40).move_to([0, -2.5, 0])
        f2 = eq("H", "=", "0.5", "+", "0.5", "+", "0.375", "+", "0.375", size=40).move_to(f1)
        f3 = eq("H", "=", r"1.75 \text{ bits}", size=44, color=VIOLET).move_to(f1)
        assert abs(0.5 + 0.5 + 0.375 + 0.375 - H) < 1e-12
        self.play(Write(f1), run_time=1.6)
        self.wait(0.5)
        self.play(TransformMatchingTex(f1, f2), run_time=1.4)
        self.wait(0.4)
        self.play(TransformMatchingTex(f2, f3), run_time=1.4)
        self.play(Create(SurroundingRectangle(f3, color=VIOLET, buff=0.15)))
        self.wait(0.6)

        # one outcome versus the average
        box = SurroundingRectangle(VGroup(sbars[3], svals[3]), color=RED, buff=0.1)
        obs = label("you observe D: that outcome carries 3 bits", 26, RED).move_to([0, -3.4, 0])
        self.play(Create(box), FadeIn(obs))
        self.wait(1.0)
        obs2 = label("H = 1.75 bits is the average before you look", 26, VIOLET).move_to(obs)
        self.play(Transform(obs, obs2))
        self.wait(2.0)


class BinaryEntropySweep(Scene):
    def construct(self):
        title = label("Binary entropy: how uncertain is a coin?", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)
        p = ValueTracker(0.0)
        base = -2.4
        hmax = 2.8
        axis = Line([-6.3, base, 0], [-3.3, base, 0], color=MUTED)
        heads = always_redraw(lambda: Rectangle(width=0.9, height=max(p.get_value(), 1e-3) * hmax, fill_color=BLUE,
                                                fill_opacity=0.85, stroke_width=0)
                              .move_to([-5.5, base + max(p.get_value(), 1e-3) * hmax / 2, 0]))
        tails = always_redraw(lambda: Rectangle(width=0.9, height=max(1 - p.get_value(), 1e-3) * hmax, fill_color=CYAN,
                                                fill_opacity=0.85, stroke_width=0)
                              .move_to([-4.1, base + max(1 - p.get_value(), 1e-3) * hmax / 2, 0]))
        hn = label("heads", 24, BLUE).move_to([-5.5, base - 0.3, 0])
        tn = label("tails", 24, CYAN).move_to([-4.1, base - 0.3, 0])
        pr = VGroup(eq("p =", size=34), DecimalNumber(0, num_decimal_places=2, font_size=34, color=INK)).arrange(RIGHT, buff=0.15)
        pr.move_to([-4.8, 2.3, 0])
        pr[1].add_updater(lambda m: m.set_value(p.get_value()))
        self.play(Create(axis), FadeIn(heads), FadeIn(tails), FadeIn(hn), FadeIn(tn), FadeIn(pr))

        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 1, 0.25], x_length=6.0, y_length=4.0,
                  axis_config={"color": MUTED, "include_tip": False}).move_to([2.6, -0.45, 0])
        ticks = VGroup(*[label(t, 24, MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.15) for v, t in ((0, "0"), (0.5, "0.5"), (1, "1"))],
                       *[label(t, 24, MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.15) for v, t in ((0.5, "0.5"), (1, "1"))])
        xl = eq("p", size=32).next_to(ax.c2p(1, 0), RIGHT, buff=0.2)
        yl = eq(r"h(p)\ \text{bits}", size=32).next_to(ax.c2p(0, 1), UP, buff=0.2)
        grid = VGroup(*[DashedLine(ax.c2p(0, v), ax.c2p(1, v), color=GRID, stroke_width=1.5) for v in (0.5, 1)])
        self.play(Create(ax), FadeIn(ticks), Write(xl), Write(yl), Create(grid))
        hr = VGroup(eq("h =", size=34, color=RED), DecimalNumber(0, num_decimal_places=3, font_size=34, color=RED)).arrange(RIGHT, buff=0.15)
        hr.move_to([-4.8, 1.65, 0])
        hr[1].add_updater(lambda m: m.set_value(h2(min(max(p.get_value(), 0.0), 1.0))))
        dot = always_redraw(lambda: Dot(ax.c2p(p.get_value(), h2(min(max(p.get_value(), 0.0), 1.0))), color=RED, radius=0.07))
        trace = TracedPath(dot.get_center, stroke_color=RED, stroke_width=4)
        self.add(trace, dot)
        self.play(FadeIn(hr))
        self.play(p.animate.set_value(0.1), run_time=1.6, rate_func=linear)
        m1 = Dot(ax.c2p(0.1, H01), color=VIOLET, radius=0.08)
        t1 = eq(rf"h(0.1) = {H01:.3f}", size=32, color=VIOLET).next_to(m1, RIGHT, buff=0.2).shift(DOWN * 0.15)
        self.play(FadeIn(m1), Write(t1))
        self.wait(0.8)
        self.play(p.animate.set_value(0.5), run_time=2.4, rate_func=linear)
        m2 = Dot(ax.c2p(0.5, 1), color=VIOLET, radius=0.08)
        t2 = label("fair coin: 1 bit, the maximum", 24, VIOLET).next_to(m2, UP, buff=0.18)
        self.play(FadeIn(m2), FadeIn(t2))
        self.wait(0.8)
        self.play(p.animate.set_value(1.0), run_time=3.2, rate_func=linear)
        t3 = label("certain: 0 bits", 24, MUTED).next_to(ax.c2p(1, 0), UP + LEFT, buff=0.2)
        self.play(FadeIn(t3))
        formula = eq(r"h(p) = -p\log_2 p - (1-p)\log_2(1-p)", size=32, color=INK).move_to([2.6, -3.4, 0])
        self.play(Write(formula), run_time=1.6)
        sym = label("symmetric: h(p) = h(1 - p)", 24, MUTED).move_to([-4.75, -3.4, 0])
        self.play(FadeIn(sym))
        self.wait(2.0)


def tree(root, spread, depth_gap, levels, color):
    """Coordinates of a full binary tree; returns (nodes per level, edges)."""
    nodes = [[root]]
    edges = []
    for lv in range(levels):
        nxt = []
        s = spread / (2 ** lv)
        for x, y in nodes[-1]:
            for d in (-1, 1):
                c = (x + d * s, y - depth_gap)
                edges.append(Line([x, y, 0], [c[0], c[1], 0], color=color, stroke_width=3))
                nxt.append(c)
        nodes.append(nxt)
    return nodes, edges


class QuestionTree(Scene):
    def construct(self):
        title = label("A bit is one well-chosen yes/no question", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.0)
        # part 1: eight equally likely outcomes
        nodes, edges = tree((0, 2.3), 3.2, 1.25, 3, MUTED)
        dots = VGroup(*[Dot([x, y, 0], color=INK, radius=0.06) for lv in nodes[:-1] for x, y in lv])
        leaves = VGroup(*[label(str(i + 1), 28, INK).move_to([x, y - 0.3, 0]) for i, (x, y) in enumerate(nodes[-1])])
        self.play(*[Create(e) for e in edges], FadeIn(dots), run_time=1.6)
        self.play(FadeIn(leaves))
        q = label("Is it in 1 to 4?  Then 5 or 6?  Then 6?", 26, MUTED).move_to([0, -2.4, 0])
        self.play(FadeIn(q))
        # path to leaf 6: right, left, right
        path_pts = [nodes[0][0], nodes[1][1], nodes[2][2], nodes[3][5]]
        path = VGroup(*[Line([a[0], a[1], 0], [b[0], b[1], 0], color=VIOLET, stroke_width=7)
                        for a, b in zip(path_pts, path_pts[1:])])
        for seg in path:
            self.play(Create(seg), run_time=0.6)
        self.play(Indicate(leaves[5], color=VIOLET))
        r1 = eq(r"8 \text{ equally likely outcomes: } \log_2 8 = 3 \text{ questions}", size=34, color=VIOLET).move_to([0, -3.2, 0])
        self.play(Write(r1))
        self.wait(1.4)
        self.play(FadeOut(VGroup(*edges, dots, leaves, q, path, r1)))

        # part 2: the skewed distribution, a lopsided tree
        pts = {"r": (-2.5, 2.2), "A": (-4.2, 1.0), "n1": (-0.8, 1.0), "B": (-2.4, -0.2), "n2": (0.8, -0.2),
               "C": (-0.6, -1.4), "D": (2.2, -1.4)}
        links = [("r", "A", "yes"), ("r", "n1", "no"), ("n1", "B", "yes"), ("n1", "n2", "no"), ("n2", "C", "yes"), ("n2", "D", "no")]
        lines = VGroup()
        tags = VGroup()
        for a, b, t in links:
            pa, pb = pts[a], pts[b]
            ln = Line([pa[0], pa[1], 0], [pb[0], pb[1], 0], color=MUTED, stroke_width=3)
            lines.add(ln)
            mid = ln.get_center()
            tags.add(label(t, 24, MUTED).move_to(mid + (LEFT * 0.45 if t == "yes" else RIGHT * 0.4) + UP * 0.1))
        qs = VGroup(label("A?", 24, INK).next_to([*pts["r"], 0], UP, buff=0.12),
                    label("B?", 24, INK).next_to([*pts["n1"], 0], UP, buff=0.12).shift(RIGHT * 0.3),
                    label("C?", 24, INK).next_to([*pts["n2"], 0], UP, buff=0.12).shift(RIGHT * 0.3))
        probs = {"A": r"\tfrac12", "B": r"\tfrac14", "C": r"\tfrac18", "D": r"\tfrac18"}
        leafs = VGroup(*[eq(f"{k}\\ ({v})", size=32, color=BLUE).move_to([pts[k][0], pts[k][1] - 0.4, 0]) for k, v in probs.items()])
        self.play(Create(lines), FadeIn(tags), FadeIn(qs), run_time=1.6)
        self.play(Write(leafs))
        depth = VGroup(*[label(f"{d} question{'s' if d > 1 else ''}", 24, AMBER).next_to(leafs[i], DOWN, buff=0.12)
                         for i, d in enumerate(DEPTHS)])
        self.play(FadeIn(depth))
        f1 = eq(r"\text{average} = \tfrac12\cdot 1 + \tfrac14\cdot 2 + \tfrac18\cdot 3 + \tfrac18\cdot 3", size=32).move_to([0.6, -2.85, 0])
        f2 = eq(r"\text{average} = 1.75 = H", size=38, color=VIOLET).move_to(f1)
        self.play(Write(f1), run_time=1.4)
        self.play(TransformMatchingTex(f1, f2), run_time=1.2)
        why = label("exact here because every p is a power of 1/2", 24, MUTED).move_to([0.6, -3.5, 0])
        self.play(FadeIn(why))
        self.wait(1.2)
        # part 3: uniform on n outcomes
        table = VGroup(*[eq(rf"n = {n}:\ {int(math.log2(n))}\text{{ bit{'s' if n > 2 else ''}}}", size=32, color=CYAN)
                         for n in (2, 4, 8, 16)]).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([4.9, 1.0, 0])
        head = eq(r"\text{uniform: } H = \log_2 n", size=32, color=CYAN).next_to(table, UP, buff=0.3)
        self.play(Write(head))
        for row in table:
            self.play(FadeIn(row), run_time=0.45)
        self.wait(2.0)
        _ = (RED, Transform)
