"""L4-04 Backdoor adjustment: three 3Blue1Brown-style scenes.

BackdoorPathCheck  A six-node graph.  The directed path X -> W -> Y is kept open; the four
                   backdoor paths are listed and checked one by one for the candidate sets {}, {Z3}
                   and {Z1, Z3}.  {Z3} blocks three paths but opens the collider path; {Z1, Z3} works.
Standardize        Stratum risks as rectangles (width = weight, height = risk, area = average risk).
                   The widths slide from the group mix P(Z|X=x) to the population mix P(Z): the
                   observed risks 0.68 and 0.20 become the standardized risks 0.50 and 0.35.
IpwPseudo          A 2x2 grid of counts (X by Z).  Weighting each cell by 1/P(X=x|Z=z) grows every
                   cell to 500: in the pseudo-population X is independent of Z, and the plain
                   treated-minus-untreated contrast is the adjusted 0.15.
Numbers are computed here from the same model the lesson states and are checked by facts().
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Circle, Create, DecimalNumber, FadeIn, FadeOut, Indicate, Line,
                   Rectangle, Scene, SurroundingRectangle, Transform, TransformMatchingTex, ValueTracker, VGroup,
                   Write, always_redraw, smooth)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label

# ---- the running example (the same numbers as the lesson text) --------------------------------
PZ1 = 0.5                                   # P(Z = 1)
PX1 = {0: 0.2, 1: 0.8}                      # P(X = 1 | Z = z)
RISK = {(1, 0): 0.2, (1, 1): 0.8,           # P(Y = 1 | X = x, Z = z)
        (0, 0): 0.1, (0, 1): 0.6}
N = 1000                                    # population size used for counts


def pz(z):
    return PZ1 if z else 1 - PZ1


def px_given_z(x, z):
    return PX1[z] if x else 1 - PX1[z]


def pz_given_x(z, x):
    num = px_given_z(x, z) * pz(z)
    return num / sum(px_given_z(x, k) * pz(k) for k in (0, 1))


OBS = {x: sum(RISK[(x, z)] * pz_given_x(z, x) for z in (0, 1)) for x in (0, 1)}     # E[Y | X = x]
STD = {x: sum(RISK[(x, z)] * pz(z) for z in (0, 1)) for x in (0, 1)}                # P(Y=1 | do(X=x))
COUNT = {(x, z): N * pz(z) * px_given_z(x, z) for x in (0, 1) for z in (0, 1)}
WEIGHT = {(x, z): 1 / px_given_z(x, z) for x in (0, 1) for z in (0, 1)}
PSEUDO = {k: COUNT[k] * WEIGHT[k] for k in COUNT}
assert abs(OBS[1] - 0.68) < 1e-12 and abs(OBS[0] - 0.20) < 1e-12
assert abs(STD[1] - 0.50) < 1e-12 and abs(STD[0] - 0.35) < 1e-12
assert abs((STD[1] - STD[0]) - 0.15) < 1e-12 and abs((OBS[1] - OBS[0]) - 0.48) < 1e-12
assert all(abs(v - 500) < 1e-9 for v in PSEUDO.values())
assert COUNT[(1, 0)] == 100 and COUNT[(1, 1)] == 400 and WEIGHT[(1, 0)] == 5 and WEIGHT[(1, 1)] == 1.25


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return ["0.68", "0.35", "0.48", "0.15", "X \\leftarrow Z_1 \\rightarrow Z_3 \\leftarrow Z_2 \\rightarrow Y",
            "\\{Z_1, Z_3\\}", "500"]


# ---- small graph toolkit ------------------------------------------------------------------------
R_NODE = 0.34


def node(name, pos, color=INK):
    c = Circle(radius=R_NODE, color=color, stroke_width=3).set_fill("#ffffff", 1).move_to(pos)
    t = eq(name, size=34, color=color).move_to(pos)
    return VGroup(c, t)


def edge(a, b, color=MUTED, width=4):
    return Arrow(a, b, buff=R_NODE + 0.04, color=color, stroke_width=width, tip_length=0.2,
                 max_tip_length_to_length_ratio=0.25)


def segment(a, b, color, width=10):
    """A thick highlight laid under an edge (no tip, so the original arrow head stays visible)."""
    d = (b - a) / max(1e-9, ((b - a) ** 2).sum() ** 0.5)
    return Line(a + d * R_NODE, b - d * R_NODE, color=color, stroke_width=width, stroke_opacity=0.75)


class BackdoorPathCheck(Scene):
    def construct(self):
        title = label("The backdoor criterion, path by path", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        P = {"Z_1": LEFT * 5.4 + UP * 1.5, "Z_2": LEFT * 1.4 + UP * 1.5, "Z_3": LEFT * 3.4 + UP * 0.25,
             "X": LEFT * 5.4 + DOWN * 1.6, "W": LEFT * 3.4 + DOWN * 1.6, "Y": LEFT * 1.4 + DOWN * 1.6}
        E = [("Z_1", "X"), ("Z_1", "Z_3"), ("Z_2", "Z_3"), ("Z_2", "Y"), ("Z_3", "X"), ("Z_3", "Y"), ("X", "W"),
             ("W", "Y")]
        cols = {"X": VIOLET, "Y": VIOLET}
        nodes = {k: node(k, p, cols.get(k, INK)) for k, p in P.items()}
        arrows = {e: edge(P[e[0]], P[e[1]]) for e in E}
        self.play(Write(title), *[FadeIn(n) for n in nodes.values()], run_time=1.2)
        self.play(*[Create(a) for a in arrows.values()], run_time=1.4)

        # the causal path stays open
        causal = VGroup(segment(P["X"], P["W"], BLUE), segment(P["W"], P["Y"], BLUE))
        keep = label("directed path X → W → Y: keep it open", 26, BLUE).move_to(RIGHT * 3.3 + UP * 2.55)
        self.add_foreground_mobjects(*nodes.values())
        self.play(Create(causal), FadeIn(keep))
        self.wait(0.6)
        self.play(FadeOut(keep))

        # the four backdoor paths (each starts with an arrow INTO X)
        paths = [
            (r"X \leftarrow Z_3 \rightarrow Y", ["X", "Z_3", "Y"], set()),
            (r"X \leftarrow Z_1 \rightarrow Z_3 \rightarrow Y", ["X", "Z_1", "Z_3", "Y"], set()),
            (r"X \leftarrow Z_3 \leftarrow Z_2 \rightarrow Y", ["X", "Z_3", "Z_2", "Y"], set()),
            (r"X \leftarrow Z_1 \rightarrow Z_3 \leftarrow Z_2 \rightarrow Y", ["X", "Z_1", "Z_3", "Z_2", "Y"], {"Z_3"}),
        ]
        head = label("backdoor paths", 28, AMBER, "BOLD").move_to(RIGHT * 2.2 + UP * 2.55)
        rows = VGroup(*[eq(p[0], size=38) for p in paths]).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        rows.move_to(UP * 0.75)
        rows.shift(RIGHT * (-0.35 - rows.get_left()[0]))
        head.align_to(rows, LEFT)
        self.play(FadeIn(head))
        for (txt, seq, _), row in zip(paths, rows):
            hl = VGroup(*[segment(P[a], P[b], AMBER, 12) for a, b in zip(seq, seq[1:])])
            self.play(Create(hl), Write(row), run_time=1.0)
            self.wait(0.4)
            self.play(FadeOut(hl), run_time=0.4)

        def blocked(seq, colliders, S):
            inner = seq[1:-1]
            for v in inner:
                if v in colliders and v not in S:
                    return True
                if v not in colliders and v in S:
                    return True
            return False

        status = VGroup()
        set_label = None
        ring = VGroup()
        for S, name in ((set(), r"S = \{\}"), ({"Z_3"}, r"S = \{Z_3\}"), ({"Z_1", "Z_3"}, r"S = \{Z_1, Z_3\}")):
            new_label = eq(name, size=36, color=CYAN).move_to(RIGHT * 2.0 + DOWN * 1.35).align_to(rows, LEFT)
            new_ring = VGroup(*[SurroundingRectangle(nodes[v], color=CYAN, buff=0.06, stroke_width=4) for v in S])
            marks = []
            for (txt, seq, col), row in zip(paths, rows):
                b = blocked(seq, col, S)
                why = "blocked" if b else "open"
                if not b and S and col & S:
                    why = "opened!"
                m = label(why, 24, MUTED if b else RED).next_to(row, RIGHT, buff=0.25)
                marks.append(m)
            new_status = VGroup(*marks)
            anims = [FadeIn(new_status)]
            if set_label is None:
                anims += [Write(new_label)]
            else:
                anims += [Transform(set_label, new_label), FadeOut(status)]
            anims.append(Transform(ring, new_ring) if len(ring) else FadeIn(new_ring))
            self.play(*anims, run_time=1.1)
            if set_label is None:
                set_label = new_label
            status = new_status
            if S == {"Z_3"}:
                coll = VGroup(segment(P["Z_1"], P["Z_3"], RED), segment(P["Z_2"], P["Z_3"], RED))
                note = label("conditioning on a collider opens path 4", 24, RED).move_to(RIGHT * 2.9 + DOWN * 2.2)
                self.play(Create(coll), FadeIn(note))
                self.wait(1.0)
                self.play(FadeOut(coll), FadeOut(note))
            elif not S:
                note = label("path 4 is blocked by its collider Z3", 24, MUTED).move_to(RIGHT * 2.9 + DOWN * 2.2)
                self.play(FadeIn(note))
                self.wait(1.0)
                self.play(FadeOut(note))
            else:
                self.wait(1.0)
        ok = label("every backdoor path blocked: valid set", 26, CYAN, "BOLD").move_to(RIGHT * 2.9 + DOWN * 2.2)
        wnote = label("never adjust for W: it is a descendant of X", 24, MUTED).move_to(RIGHT * 2.9 + DOWN * 2.85)
        self.play(FadeIn(ok))
        self.play(FadeIn(wnote), Indicate(nodes["W"], color=RED))
        self.wait(1.8)


class Standardize(Scene):
    def construct(self):
        title = label("Standardization: same weights for both arms", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        formula = eq(r"P(Y=1 \mid \operatorname{do}(X=x)) = \sum_z P(Y=1 \mid x, z)\,P(z)", size=40)
        formula.next_to(title, DOWN, buff=0.3)
        self.play(Write(title))
        self.play(Write(formula))

        t = ValueTracker(0.0)              # 0: group mix P(z|x), 1: population mix P(z)
        WTOT, HS, BASE = 4.0, 2.6, -1.75

        def weight(x, z):
            a = pz_given_x(z, x)
            return a + (pz(z) - a) * t.get_value()

        def panel(x, cx, color):
            def rects():
                left = cx - WTOT / 2
                out = VGroup()
                for z in (0, 1):
                    w = weight(x, z) * WTOT
                    h = RISK[(x, z)] * HS
                    r = Rectangle(width=max(w, 1e-3), height=h, stroke_color=color, stroke_width=3)
                    r.set_fill(color if z else CYAN, 0.45 if z else 0.35)
                    r.move_to([left + w / 2, BASE + h / 2, 0])
                    out.add(r)
                    left += w
                return out

            boxes = always_redraw(rects)

            def risk_labels():
                g = VGroup()
                for z, r in zip((0, 1), boxes):
                    g.add(label(f"{RISK[(x, z)]:.1f}", 24, INK).next_to(r, UP, buff=0.08))
                return g

            def weight_labels():
                g = VGroup()
                for z, r in zip((0, 1), boxes):
                    g.add(label(f"Z={z}: {weight(x, z):.2f}", 22, MUTED).next_to(r, DOWN, buff=0.12))
                return g

            base = Line([cx - WTOT / 2 - 0.1, BASE, 0], [cx + WTOT / 2 + 0.1, BASE, 0], color=MUTED, stroke_width=2)
            head = label("treated, X = 1" if x else "untreated, X = 0", 26, color, "BOLD").move_to([cx - 0.7, 1.3, 0])
            val = always_redraw(lambda: DecimalNumber(sum(weight(x, z) * RISK[(x, z)] for z in (0, 1)), num_decimal_places=2,
                                                      font_size=40, color=RED).next_to(head, RIGHT, buff=0.35))
            return VGroup(base, head), boxes, always_redraw(risk_labels), always_redraw(weight_labels), val

        a = panel(1, -3.35, VIOLET)
        b = panel(0, 3.35, BLUE)
        for p in (a, b):
            self.play(FadeIn(p[0]), FadeIn(p[1]), FadeIn(p[2]), FadeIn(p[3]), FadeIn(p[4]), run_time=1.0)
        cap = label("width = weight of the stratum, height = risk, area = average risk", 24, MUTED)
        cap.move_to(DOWN * 2.72)
        self.play(FadeIn(cap))
        naive = eq(rf"\text{{observed: }} {OBS[1]:.2f} - {OBS[0]:.2f} = {OBS[1] - OBS[0]:.2f}", size=40, color=RED)
        naive.move_to(DOWN * 3.3)
        self.play(Write(naive))
        self.wait(1.2)
        hint = label("now give both arms the population mix P(Z) = (0.5, 0.5)", 24, CYAN).move_to(cap)
        self.play(FadeOut(cap), FadeIn(hint))
        self.play(t.animate.set_value(1.0), run_time=4, rate_func=smooth)
        self.wait(0.6)
        adj = eq(rf"\text{{standardized: }} {STD[1]:.2f} - {STD[0]:.2f} = {STD[1] - STD[0]:.2f}", size=40, color=CYAN)
        adj.move_to(naive)
        self.play(Transform(naive, adj))
        self.wait(2.0)


class IpwPseudo(Scene):
    def construct(self):
        title = label("Weighting builds a pseudo-population", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        S = 1.75 / (500 ** 0.5)              # side length per sqrt(count)
        centers = {(1, 0): [-4.6, 0.9, 0], (1, 1): [-2.2, 0.9, 0], (0, 0): [-4.6, -1.6, 0], (0, 1): [-2.2, -1.6, 0]}
        colhead = VGroup(label("Z = 0", 26, MUTED).move_to([-4.6, 2.35, 0]), label("Z = 1", 26, MUTED).move_to([-2.2, 2.35, 0]))
        rowhead = VGroup(label("X = 1", 26, VIOLET).move_to([-6.25, 0.9, 0]), label("X = 0", 26, BLUE).move_to([-6.25, -1.6, 0]))
        self.play(FadeIn(colhead), FadeIn(rowhead))
        n = {k: ValueTracker(COUNT[k]) for k in COUNT}

        def cell(k):
            def build():
                side = S * n[k].get_value() ** 0.5
                c = centers[k]
                sq = Rectangle(width=side, height=side, stroke_color=VIOLET if k[0] else BLUE, stroke_width=3)
                sq.set_fill("#ffffff", 1).move_to(c)
                frac = RISK[k]
                fill = Rectangle(width=side, height=side * frac, stroke_width=0).set_fill(RED, 0.35)
                fill.move_to([c[0], c[1] - side / 2 + side * frac / 2, 0])
                num = DecimalNumber(n[k].get_value(), num_decimal_places=0, font_size=30, color=INK).move_to(c)
                return VGroup(sq, fill, num)
            return always_redraw(build)

        cells = {k: cell(k) for k in COUNT}
        self.play(*[FadeIn(c) for c in cells.values()])
        obs = label("observed: most treated units have Z = 1", 24, MUTED).move_to([-3.75, -3.25, 0])
        self.play(FadeIn(obs))
        key = label("red share = risk of Y = 1 in the cell", 22, RED).move_to([2.9, 2.35, 0])
        self.play(FadeIn(key))

        wt = eq(r"w = \frac{1}{P(X = x \mid Z = z)}", size=40).move_to([2.9, 1.62, 0])
        self.play(Write(wt))
        wvals = VGroup(*[eq(rf"X={x},\ Z={z}:\ {COUNT[(x, z)]:.0f} \times {WEIGHT[(x, z)]:g} = {PSEUDO[(x, z)]:.0f}", size=36)
                         for x, z in ((1, 0), (1, 1), (0, 0), (0, 1))]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        wvals.move_to([2.9, -0.15, 0])
        self.play(Write(wvals), run_time=2.0)
        self.play(*[n[k].animate.set_value(PSEUDO[k]) for k in n], run_time=3.0)
        indep = label("every cell 500: X is independent of Z", 24, CYAN, "BOLD").move_to(obs)
        self.play(FadeOut(obs), FadeIn(indep))
        self.wait(0.8)
        r1 = eq(r"(500 \cdot 0.2 + 500 \cdot 0.8)/1000 = 0.50", size=36, color=VIOLET)
        r0 = eq(r"(500 \cdot 0.1 + 500 \cdot 0.6)/1000 = 0.35", size=36, color=BLUE)
        res = VGroup(r1, r0).arrange(DOWN, buff=0.2).move_to([2.9, -2.05, 0])
        self.play(Write(res), run_time=1.6)
        diff = eq(r"0.50 - 0.35 = 0.15", size=42, color=RED).next_to(res, DOWN, buff=0.3)
        self.play(Write(diff))
        self.wait(2.0)
        _ = (GRID, AMBER, TransformMatchingTex)
