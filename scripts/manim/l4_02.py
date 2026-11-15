"""L4-02 DAGs and d-separation: three scenes.

ThreeJunctions   chain, fork and collider side by side: a token of dependence travels from X to Y; then M is
                 conditioned on and the verdicts flip (chain and fork close, the collider opens).
DSepSweep        the six-node graph A -> C <- B -> E, C -> D -> F <- E: both paths from A to E are walked
                 node by node for Z = {}, {D}, {B, D}, with the blocking node marked and the verdict written.
MoralizeProof    the moralization criterion behind the soundness proof: keep ancestors, marry parents,
                 drop directions, delete Z, test whether A can still reach E.
Verdicts are computed here with the lesson's own d-separation code and checked against networkx.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import networkx as nx
import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Circle, Circumscribe, Create, Cross, DashedLine, Dot, FadeIn, FadeOut, Indicate,
                   Line, MoveAlongPath, ReplacementTransform, Scene, SurroundingRectangle, VGroup, VMobject, Write,
                   linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label
from qcai.lessonfigs.l4_02 import EDGES, G, NODES, PATHS_AE, POS, d_separated, path_open

GREY = "#cbd5e1"
ROUNDS = [(), ("D",), ("B", "D")]
VERDICT = {(): r"A \perp_d E", ("D",): r"A \not\perp_d E \mid \{D\}", ("B", "D"): r"A \perp_d E \mid \{B, D\}"}
for zs in ROUNDS:                                   # the on-screen verdicts agree with both implementations
    s = d_separated(G, {"A"}, {"E"}, set(zs))
    assert s == nx.is_d_separator(G, {"A"}, {"E"}, set(zs))
    assert s == ("not" not in VERDICT[zs])
assert [path_open(G, p, ())[1] for p in PATHS_AE] == ["C", "F"]
assert [path_open(G, p, ("D",)) for p in PATHS_AE] == [(True, None), (False, "D")]
assert [path_open(G, p, ("B", "D"))[1] for p in PATHS_AE] == ["B", "D"]


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return [VERDICT[()], VERDICT[("D",)], VERDICT[("B", "D")], r"A \to C \leftarrow B \to E",
            r"A \to C \to D \to F \leftarrow E", r"X \perp\!\!\!\perp Y \mid M"]


def P(v):
    x, y = POS[v]
    return np.array([x * 1.45 - 6.2, y * 1.45 - 0.55, 0.0])


def make_node(name, pos, color=INK, r=0.38, size=38):
    c = Circle(radius=r, color=color, stroke_width=4).set_fill("#ffffff", 1).move_to(pos)
    return VGroup(c, eq(name, size=size, color=color).move_to(pos))


def arrow(p, q, color=MUTED, buff=0.42):
    return Arrow(p, q, buff=buff, color=color, stroke_width=5, max_tip_length_to_length_ratio=0.2)


def six_graph():
    nodes = {v: make_node(v, P(v), VIOLET if v in ("A", "E") else INK) for v in NODES}
    edges = {(a, b): arrow(P(a), P(b)) for a, b in EDGES}
    return nodes, edges


def polyline(points):
    m = VMobject()
    m.set_points_as_corners([np.array(p) for p in points])
    return m


class ThreeJunctions(Scene):
    def construct(self):
        title = label("Three junctions decide whether dependence flows", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title))
        cols = [-4.6, 0.0, 4.6]
        names = ["chain", "fork", "collider"]
        # arrows: (from, to) in terms of positions X (left), M (middle), Y (right)
        kinds = [[("X", "M"), ("M", "Y")], [("M", "X"), ("M", "Y")], [("X", "M"), ("Y", "M")]]
        groups, mids, tracks = [], [], []
        for cx, nm, ks in zip(cols, names, kinds):
            pos = {"X": np.array([cx - 1.6, 1.3, 0]), "M": np.array([cx, 1.3, 0]), "Y": np.array([cx + 1.6, 1.3, 0])}
            nd = {k: make_node(k, p, BLUE if k != "M" else INK, r=0.45, size=42) for k, p in pos.items()}
            ar = [arrow(pos[a], pos[b], buff=0.5) for a, b in ks]
            head = label(nm, 32, INK, "BOLD").move_to([cx, 2.35, 0])
            g = VGroup(head, *nd.values(), *ar)
            groups.append(g)
            mids.append(nd["M"])
            tracks.append(pos)
        self.play(*[FadeIn(g) for g in groups], run_time=1.4)

        def run(open_flags, caption):
            cap = label(caption, 28, MUTED).move_to([0, 0.3, 0])
            self.play(FadeIn(cap))
            dots, marks, tags = [], [], []
            anims = []
            for pos, ok in zip(tracks, open_flags):
                end = pos["Y"] + LEFT * 0.47 if ok else pos["M"] + LEFT * 0.47
                d = Dot(pos["X"] + RIGHT * 0.47, color=AMBER, radius=0.12)
                dots.append(d)
                anims.append(MoveAlongPath(d, Line(pos["X"] + RIGHT * 0.47, end), rate_func=linear))
            self.add(*dots)
            self.play(*anims, run_time=1.6)
            for pos, ok, d, mid in zip(tracks, open_flags, dots, mids):
                if ok:
                    t = label("open", 28, AMBER, "BOLD").move_to(pos["M"] + DOWN * 1.85)
                else:
                    marks.append(Cross(mid, stroke_color=RED, stroke_width=6, scale_factor=0.75))
                    t = label("blocked", 28, RED, "BOLD").move_to(pos["M"] + DOWN * 1.85)
                tags.append(t)
            self.play(*[Create(m) for m in marks], *[FadeIn(t) for t in tags])
            self.wait(0.8)
            return VGroup(cap, *dots, *marks, *tags)

        r1 = run([True, True, False], "nothing conditioned on")
        self.play(FadeOut(r1))
        self.play(*[m[0].animate.set_fill(GREY, 1) for m in mids], run_time=0.8)
        r2 = run([False, False, True], "condition on M (grey)")
        rules = VGroup(eq(r"X \perp\!\!\!\perp Y \mid M", size=40), eq(r"X \perp\!\!\!\perp Y \mid M", size=40),
                       VGroup(eq(r"X \perp\!\!\!\perp Y", size=40), eq(r"\text{but not given } M", size=34)).arrange(DOWN, buff=0.12))
        for r, cx in zip(rules, cols):
            r.move_to([cx, -1.65, 0])
        self.play(*[Write(r) for r in rules])
        sub = label("Conditioning on the middle closes chains and forks, and opens colliders.", 28, INK).move_to([0, -3.1, 0])
        self.play(FadeIn(sub))
        self.wait(1.8)
        _ = r2


class DSepSweep(Scene):
    def construct(self):
        title = label("d-separation: walk every path, node by node", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        nodes, edges = six_graph()
        self.play(Write(title), *[FadeIn(n) for n in nodes.values()], run_time=1.2)
        self.play(*[Create(e) for e in edges.values()], run_time=1.2)
        XL = -0.2
        q = eq(r"\text{Is } A \perp_d E \mid Z\,?", size=36).move_to([2.6, 2.5, 0]).align_to([XL, 0, 0], LEFT)
        p1 = eq(r"1:\ A \to C \leftarrow B \to E", size=34).move_to([2.6, 1.75, 0]).align_to([XL, 0, 0], LEFT)
        p2 = eq(r"2:\ A \to C \to D \to F \leftarrow E", size=34).move_to([2.6, 0.75, 0]).align_to([XL, 0, 0], LEFT)
        self.play(Write(q))
        self.play(Write(p1), Write(p2))
        verdicts = VGroup()
        for k, zs in enumerate(ROUNDS):
            for v in NODES:
                fill = GREY if v in zs else "#ffffff"
                nodes[v][0].set_fill(fill, 1)
            zt = r"Z = \emptyset" if not zs else r"Z = \{" + ", ".join(zs) + r"\}"
            ztag = eq(zt, size=34, color=MUTED).move_to([2.6, -0.35, 0]).align_to([XL, 0, 0], LEFT)
            self.play(FadeIn(ztag), *[Circumscribe(nodes[v], color=MUTED, shape=Circle) for v in zs], run_time=0.9)
            results = []
            for path, plabel in zip(PATHS_AE, (p1, p2)):
                ok, where = path_open(G, path, zs)
                stop = len(path) if ok else path.index(where) + 1
                pts = [P(v) for v in path[:stop]]
                trail = polyline(pts).set_stroke(AMBER if ok else RED, 9, opacity=0.6)
                d = Dot(pts[0], color=AMBER, radius=0.12)
                self.add(d)
                self.play(Create(trail), MoveAlongPath(d, polyline(pts)), run_time=0.45 * stop, rate_func=linear)
                if ok:
                    note = label("open", 26, AMBER, "BOLD").next_to(plabel, DOWN, buff=0.12).align_to([XL + 0.5, 0, 0], LEFT)
                    self.play(FadeIn(note), Indicate(plabel, color=AMBER))
                    results.append(VGroup(trail, d, note))
                else:
                    x = Cross(nodes[where], stroke_color=RED, stroke_width=6, scale_factor=0.9)
                    why = "collider" if (path[path.index(where) - 1], where) in EDGES and (path[path.index(where) + 1], where) in EDGES else "in Z"
                    note = label(f"blocked at {where} ({why})", 24, RED).next_to(plabel, DOWN, buff=0.12).align_to([XL + 0.5, 0, 0], LEFT)
                    self.play(Create(x), FadeIn(note))
                    results.append(VGroup(trail, d, x, note))
            v = eq(VERDICT[zs], size=36, color=AMBER if "not" in VERDICT[zs] else VIOLET)
            v.move_to([2.6, -1.1 - 0.7 * k, 0]).align_to([XL, 0, 0], LEFT)
            self.play(Write(v))
            if zs == ("D",):
                hint = label("D is a descendant of the collider C, so C opens", 24, MUTED).next_to(v, DOWN, buff=0.15).align_to([XL, 0, 0], LEFT)
                self.play(FadeIn(hint))
                self.wait(0.6)
                self.play(FadeOut(hint))
            verdicts.add(v)
            self.wait(0.6)
            self.play(FadeOut(VGroup(*results)), FadeOut(ztag))
        box = SurroundingRectangle(verdicts, color=MUTED, buff=0.15)
        self.play(Create(box))
        self.wait(1.5)
        _ = (BLUE, CYAN, GRID, DashedLine, ReplacementTransform)


class MoralizeProof(Scene):
    def construct(self):
        title = label("Why d-separation works: moralize, then cut", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        nodes, edges = six_graph()
        self.play(Write(title), *[FadeIn(n) for n in nodes.values()], *[Create(e) for e in edges.values()], run_time=1.4)
        q = eq(r"\text{Query: } A \perp_d E \mid \{D\}\,?", size=34).move_to([2.7, 2.45, 0])
        self.play(Write(q))
        steps = ["1. keep the ancestors of A, E, D", "2. marry parents of a common child",
                 "3. drop the arrow directions", "4. delete the conditioning set",
                 "5. can A still reach E?"]
        st = VGroup(*[label(s, 26, INK) for s in steps]).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([2.7, 0.55, 0])

        # 1. ancestral set of {A, E, D} is everything except F
        anc = set().union(*(nx.ancestors(G, v) | {v} for v in ("A", "E", "D")))
        assert anc == {"A", "B", "C", "D", "E"}
        self.play(FadeIn(st[0]))
        gone = [nodes["F"], edges[("D", "F")], edges[("E", "F")]]
        self.play(*[g.animate.set_opacity(0.12) for g in gone])
        self.play(*[FadeOut(g) for g in gone])
        # 2. marry A and B, the parents of C
        self.play(FadeIn(st[1]))
        marry = DashedLine(P("A"), P("B"), color=RED, stroke_width=5, buff=0.4)
        self.play(Create(marry), Circumscribe(nodes["C"], color=RED, shape=Circle))
        # 3. drop directions
        self.play(FadeIn(st[2]))
        lines = {}
        for (a, b), e in list(edges.items()):
            if "F" in (a, b):
                continue
            lines[(a, b)] = Line(P(a), P(b), color=MUTED, stroke_width=5, buff=0.4)
        ab = Line(P("A"), P("B"), color=MUTED, stroke_width=5, buff=0.4)
        self.play(*[ReplacementTransform(edges[k], lines[k]) for k in lines], ReplacementTransform(marry, ab), run_time=1.2)
        # 4. delete D
        self.play(FadeIn(st[3]))
        self.play(FadeOut(nodes["D"]), FadeOut(lines[("C", "D")]))
        # 5. reachability: A - B - E survives
        self.play(FadeIn(st[4]))
        trail = polyline([P("A"), P("B"), P("E")]).set_stroke(AMBER, 10, opacity=0.6)
        self.play(Create(trail), run_time=1.2)
        v1 = eq(VERDICT[("D",)], size=34, color=AMBER).move_to([2.7, -1.75, 0])
        why1 = label("the path A - B - E survives", 24, MUTED).next_to(v1, DOWN, buff=0.12)
        self.play(Write(v1), FadeIn(why1))
        self.wait(1.0)
        # same moral graph for Z = {B, D}: delete B as well
        self.play(FadeOut(trail), FadeOut(why1))
        self.play(FadeOut(nodes["B"]), FadeOut(ab), FadeOut(lines[("B", "C")]), FadeOut(lines[("B", "E")]))
        v2 = eq(VERDICT[("B", "D")], size=34, color=VIOLET).move_to([2.7, -2.5, 0])
        why2 = label("without B, nothing joins A to E", 24, MUTED).next_to(v2, DOWN, buff=0.12)
        self.play(Write(v2), FadeIn(why2))
        thm = eq(r"\text{d-separated in } G \iff \text{separated in the moral ancestral graph}", size=30)
        thm.to_edge(DOWN, buff=0.25)
        self.play(FadeOut(why2), Write(thm))
        self.wait(1.8)
