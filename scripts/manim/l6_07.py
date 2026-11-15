"""L6-07 Process matrices and validity: four 3Blue1Brown-style scenes.

BornRulePairing  two local laboratories inside a process W; the generalized Born rule
                 p(a,b|x,y) = Tr[W (M_a|x (x) M_b|y)], and its reduction to the ordinary Born rule
                 for W = rho (x) 1 (TransformMatchingTex derivation).
TermTypeSieve    the 16 Hilbert-Schmidt term types of a two-qubit-lab process; the three linear
                 validity conditions strike out 8 of them, leaving 88 of 256 real dimensions.
GrandfatherLoop  a positive W that wires Alice's output back into her input; total probability
                 |Tr U|^2 = 4 cos^2(theta/2) swings from 4 to 0 as her local rotation changes.
CausalGame       the OCB game: any causally separable process wins with probability at most 3/4,
                 the OCB process mixed with white noise wins with 1/2 + v sqrt(2)/4.
Every number is computed here; facts() lists strings that the lesson text repeats verbatim.
"""
import itertools
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DecimalNumber, DOWN, LEFT, RIGHT, UP, Arrow, Axes, Create, CurvedArrow, DashedLine, Dot, FadeIn, FadeOut,
                   Line, Rectangle, RoundedRectangle, Scene, SurroundingRectangle, TracedPath, TransformMatchingTex,
                   ValueTracker, VGroup, Write, always_redraw, linear)

from qcai_style import AMBER, BLUE, CYAN, GRID, INK, MUTED, RED, VIOLET, eq, label, tex

# ---------------------------------------------------------------- numbers shared with the text
I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]])
Z = np.diag([1, -1])
Y = np.array([[0, -1j], [1j, 0]])


def kron(*a):
    out = np.array([[1.0]])
    for m in a:
        out = np.kron(out, m)
    return out


W_OCB = 0.25 * (np.eye(16) + (kron(I2, Z, Z, I2) + kron(Z, I2, X, Z)) / math.sqrt(2))   # A_I A_O B_I B_O
EIG_OCB = np.linalg.eigvalsh(W_OCB)
assert abs(EIG_OCB.min()) < 1e-12 and abs(EIG_OCB.max() - 0.5) < 1e-12 and abs(np.trace(W_OCB) - 4) < 1e-12


def proj(v):
    v = np.array(v, dtype=float)
    return np.outer(v, v) / (v @ v)


def ocb_success(W):
    z = [proj([1, 0]), proj([0, 1])]
    xb = [proj([1, 1]), proj([1, -1])]
    s = 0.0
    for a, b, bp in itertools.product((0, 1), repeat=3):
        for x, y in itertools.product((0, 1), repeat=2):
            MA = np.kron(z[x], z[a])                                   # measure z -> x, prepare |a>
            MB = np.kron(z[y], z[0]) if bp == 1 else np.kron(xb[y], z[b ^ y])   # OCB: b' = 1, Bob guesses a
            p = float(np.trace(W @ np.kron(MA, MB)).real)
            s += p * ((y == a) if bp == 1 else (x == b)) / 8
    return s


P_OCB = ocb_success(W_OCB)
assert abs(P_OCB - (2 + math.sqrt(2)) / 4) < 1e-12
assert abs(ocb_success(np.eye(16) / 4) - 0.5) < 1e-12
V_CROSS = 1 / math.sqrt(2)                       # 1/2 + v sqrt2/4 = 3/4  <=>  v = 1/sqrt2
assert abs(0.5 + V_CROSS * math.sqrt(2) / 4 - 0.75) < 1e-12

# term-type counting: rows = Alice's part, columns = Bob's part
ROWS = [(), ("I",), ("O",), ("I", "O")]
COLS = [(), ("I",), ("O",), ("I", "O")]


def allowed(r, c):
    ao, bo, ai, bi = "O" in r, "O" in c, "I" in r, "I" in c
    if ao and bo:
        return False
    if ao and not c:            # A_O nontrivial while trivial on B_I B_O
        return False
    if bo and not r:            # B_O nontrivial while trivial on A_I A_O
        return False
    return True


DIMS = {(r, c): 3 ** (len(r) + len(c)) for r in ROWS for c in COLS}
N_ALLOWED = sum(d for k, d in DIMS.items() if allowed(*k))
assert sum(DIMS.values()) == 256 and N_ALLOWED == 88
assert sum(1 for k in DIMS if allowed(*k)) == 8

# grandfather loop: total probability |Tr U|^2 for U = exp(-i theta Y / 2)


def loop_total(theta):
    return (2 * math.cos(theta / 2)) ** 2


assert abs(loop_total(0) - 4) < 1e-12 and abs(loop_total(math.pi)) < 1e-12
assert abs(loop_total(1.0) - (2 + 2 * math.cos(1.0))) < 1e-12

FACT_BORN = r"\operatorname{Tr}_{A_O} M_{a|x} = E_{a|x}"
FACT_SUM = "1 + 3 + 3 + 9 + 9 + 27 + 9 + 27 = 88"
FACT_LOOP = r"|\operatorname{Tr} U|^2 = 4\cos^2(\theta/2)"
FACT_GAME = r"\tfrac12 + v\tfrac{\sqrt2}{4}"


def facts(L):
    """Strings the animations put on screen; each must also appear in the lesson text."""
    return [FACT_BORN, FACT_SUM, FACT_LOOP, FACT_GAME, "3/4", f"{P_OCB:.3f}"]


# ---------------------------------------------------------------- drawing helpers
def lab_box(name, center, color):
    box = RoundedRectangle(width=1.3, height=0.9, corner_radius=0.12, color=color, fill_color="#ffffff",
                           fill_opacity=1, stroke_width=4).move_to(center)
    txt = label(name, 34, color, "BOLD").move_to(box)
    win = Line(box.get_bottom() + DOWN * 0.75, box.get_bottom(), color=color, stroke_width=4)
    wout = Line(box.get_top(), box.get_top() + UP * 0.75, color=color, stroke_width=4)
    li = eq(rf"{name}_I", size=30, color=color).next_to(win, LEFT, buff=0.12)
    lo = eq(rf"{name}_O", size=30, color=color).next_to(wout, LEFT, buff=0.12)
    return VGroup(box, txt, win, wout, li, lo)


class BornRulePairing(Scene):
    def construct(self):
        title = label("A process matrix pairs with local instruments", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.2)

        env = RoundedRectangle(width=5.0, height=4.6, corner_radius=0.3, color=VIOLET, fill_color="#ede9fe",
                               fill_opacity=0.6, stroke_width=3).move_to(LEFT * 3.9 + DOWN * 0.45)
        wlab = eq("W", size=48, color=VIOLET).move_to(env.get_corner(UP + LEFT) + RIGHT * 0.45 + DOWN * 0.45)
        A = lab_box("A", LEFT * 5.0 + DOWN * 0.45, BLUE)
        B = lab_box("B", LEFT * 2.8 + DOWN * 0.45, AMBER)
        self.play(FadeIn(env), Write(wlab), run_time=1.0)
        self.play(FadeIn(A), FadeIn(B), run_time=1.2)
        cap = label("W is everything outside the two labs", 24, MUTED).next_to(env, DOWN, buff=0.12)
        self.play(FadeIn(cap))

        born = eq(r"p(a,b|x,y)", "=", r"\operatorname{Tr}\big[W\,(M_{a|x}\otimes M_{b|y})\big]", size=36)
        born.move_to(RIGHT * 3.2 + UP * 2.2)
        self.play(Write(born), run_time=1.6)
        note = label("M: transposed Choi operator of each local CP map", 24, MUTED).next_to(born, DOWN, buff=0.2)
        self.play(FadeIn(note))
        self.wait(0.8)

        # special case: W = rho (x) identity reproduces the ordinary Born rule
        case = label("Special case: shared state, outputs discarded", 26, VIOLET).move_to(RIGHT * 3.2 + UP * 0.6)
        self.play(FadeIn(case))
        s1 = eq(r"p", "=", r"\operatorname{Tr}\big[(\rho\otimes 1)", r"(M_{a|x}\otimes M_{b|y})", r"\big]", size=34)
        s2 = eq(r"p", "=", r"\operatorname{Tr}\big[\rho\,", r"(\operatorname{Tr}_{A_O}M_{a|x}\otimes\operatorname{Tr}_{B_O}M_{b|y})",
                r"\big]", size=34)
        s3 = eq(r"p", "=", r"\operatorname{Tr}\big[\rho\,", r"(E_{a|x}\otimes F_{b|y})", r"\big]", size=34)
        for s in (s1, s2, s3):
            s.move_to(RIGHT * 3.2 + DOWN * 0.4)
        self.play(Write(s1), run_time=1.4)
        self.wait(0.6)
        self.play(TransformMatchingTex(s1, s2), run_time=1.6)
        self.wait(0.6)
        self.play(TransformMatchingTex(s2, s3), run_time=1.6)
        key = eq(FACT_BORN, size=32, color=BLUE).move_to(RIGHT * 3.2 + DOWN * 1.5)
        self.play(Write(key))
        box = SurroundingRectangle(s3, color=CYAN, buff=0.12)
        last = label("the ordinary Born rule for a shared state", 26, CYAN).move_to(RIGHT * 3.2 + DOWN * 2.5)
        self.play(Create(box), FadeIn(last))
        self.wait(1.0)

        # the identity wire inside W connecting A_O to B_I: a channel from A to B
        wire = CurvedArrow(A[3].get_end(), B[2].get_start(), angle=-3.7, color=VIOLET, stroke_width=4)
        wnote = label("other W: A's output wired to B's input", 24, VIOLET).next_to(env, UP, buff=0.12)
        self.play(FadeOut(cap), Create(wire), FadeIn(wnote), run_time=1.6)
        self.wait(1.8)


class TermTypeSieve(Scene):
    def construct(self):
        title = label("Which terms may a process matrix contain?", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.2)
        rl = [r"1", r"A_I", r"A_O", r"A_IA_O"]
        cl = [r"1", r"B_I", r"B_O", r"B_IB_O"]
        w, h = 1.15, 0.78
        origin = LEFT * 4.3 + UP * 1.35
        tiles = {}
        grp = VGroup()
        for i, r in enumerate(ROWS):
            for j, c in enumerate(COLS):
                pos = origin + RIGHT * (j * (w + 0.12)) + DOWN * (i * (h + 0.12))
                t = Rectangle(width=w, height=h, color=MUTED, fill_color=GRID, fill_opacity=1, stroke_width=2).move_to(pos)
                n = eq(str(DIMS[(r, c)]), size=34, color=INK).move_to(pos)
                tiles[(i, j)] = VGroup(t, n)
                grp.add(tiles[(i, j)])
        heads_c = VGroup(*[eq(s, size=30, color=AMBER).next_to(tiles[(0, j)], UP, buff=0.15) for j, s in enumerate(cl)])
        heads_r = VGroup(*[eq(s, size=30, color=BLUE).next_to(tiles[(i, 0)], LEFT, buff=0.18) for i, s in enumerate(rl)])
        self.play(FadeIn(grp, lag_ratio=0.05), Write(heads_c), Write(heads_r), run_time=2.2)
        expl = label("tile = term type; number = real dimension", 24, MUTED).next_to(grp, DOWN, buff=0.35)
        tot = eq(r"1 + 3 + \dots = 4^4 = 256", size=32).next_to(expl, DOWN, buff=0.2)
        self.play(FadeIn(expl), Write(tot))
        self.wait(0.8)

        rx = RIGHT * 3.55
        r1 = VGroup(tex(r"1. no term acts on both outputs", 32),
                    eq(r"(1-{}_{A_O})(1-{}_{B_O})W = 0", size=36)).arrange(DOWN, buff=0.12).move_to(rx + UP * 1.7)
        r2 = VGroup(tex(r"2. $A_O$ alone: Bob's part must contain $B_I$", 32),
                    eq(r"{}_{B_IB_O}W = {}_{A_OB_IB_O}W", size=36)).arrange(DOWN, buff=0.12).move_to(rx + UP * 0.1)
        r3 = VGroup(tex(r"3. $B_O$ alone: Alice's part must contain $A_I$", 32),
                    eq(r"{}_{A_IA_O}W = {}_{A_IA_OB_O}W", size=36)).arrange(DOWN, buff=0.12).move_to(rx + DOWN * 1.5)
        groups = [(r1, [(i, j) for i in (2, 3) for j in (2, 3)]), (r2, [(2, 0), (3, 0)]), (r3, [(0, 2), (0, 3)])]
        for rule, cells in groups:
            self.play(FadeIn(rule), run_time=1.0)
            self.play(*[tiles[k][0].animate.set_fill(RED, opacity=0.85) for k in cells], run_time=0.9)
            self.play(*[tiles[k].animate.set_opacity(0.15) for k in cells], run_time=0.7)
            self.wait(0.4)
        for i, r in enumerate(ROWS):
            for j, c in enumerate(COLS):
                ok = allowed(r, c)
                assert ok == ((i, j) not in [k for _, cells in groups for k in cells])
        state = [(0, 0), (1, 0), (0, 1), (1, 1)]
        ab = [(2, 1), (3, 1)]
        ba = [(1, 2), (1, 3)]
        self.play(*[tiles[k][0].animate.set_fill(CYAN, opacity=0.55) for k in state],
                  *[tiles[k][0].animate.set_fill(VIOLET, opacity=0.45) for k in ab],
                  *[tiles[k][0].animate.set_fill(AMBER, opacity=0.55) for k in ba], run_time=1.2)
        key = VGroup(label("cyan: shared state", 24, CYAN), label("violet: A signals to B", 24, VIOLET),
                     label("amber: B signals to A", 24, AMBER)).arrange(RIGHT, buff=0.4)
        summ = eq(FACT_SUM, size=34, color=INK)
        self.play(FadeOut(VGroup(expl, tot)))
        key.next_to(grp, DOWN, buff=0.3).align_to(grp, LEFT)
        summ.next_to(key, DOWN, buff=0.22).align_to(grp, LEFT)
        self.play(FadeIn(key), Write(summ), run_time=1.6)
        self.wait(2.0)


class GrandfatherLoop(Scene):
    def construct(self):
        title = label("Positive is not enough: a loop through Alice's lab", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.2)
        A = lab_box("A", LEFT * 4.6 + UP * 0.9, BLUE)
        U = eq("U", size=34, color=BLUE).move_to(A[0])
        loop = CurvedArrow(A[3].get_end(), A[2].get_start(), angle=-3.6, color=RED, stroke_width=4)
        self.play(FadeIn(A[0]), FadeIn(A[2:]), Write(U))
        self.play(Create(loop), run_time=1.4)
        wl = eq(r"W_{\rm loop} = |1\rangle\!\rangle\langle\!\langle 1|^{A_IA_O}", size=30, color=RED)
        wl.next_to(A, DOWN, buff=0.75).shift(RIGHT * 0.3)
        self.play(Write(wl))
        pos = tex(r"$W_{\rm loop}\ge 0$, trace $2 = d_{A_O}$", 32, MUTED).next_to(wl, DOWN, buff=0.15)
        self.play(FadeIn(pos))

        d1 = eq(r"\operatorname{Tr}[W_{\rm loop}M_U]", "=", r"\langle\!\langle 1|M_U|1\rangle\!\rangle", size=32)
        d2 = eq(r"\operatorname{Tr}[W_{\rm loop}M_U]", "=", r"|\langle\!\langle 1|(1\otimes U)|1\rangle\!\rangle|^2", size=32)
        d3 = eq(r"\operatorname{Tr}[W_{\rm loop}M_U]", "=", r"|\operatorname{Tr} U|^2", size=32)
        for d in (d1, d2, d3):
            d.move_to(RIGHT * 2.9 + UP * 2.2)
        self.play(Write(d1), run_time=1.2)
        self.play(TransformMatchingTex(d1, d2), run_time=1.4)
        self.play(TransformMatchingTex(d2, d3), run_time=1.4)
        fl = eq(FACT_LOOP, size=32, color=RED).next_to(d3, DOWN, buff=0.2)
        ulab = eq(r"U = e^{-i\theta Y/2}", size=30, color=BLUE).next_to(fl, DOWN, buff=0.15)
        self.play(Write(fl), Write(ulab))

        ax = Axes(x_range=[0, 2 * math.pi, math.pi / 2], y_range=[0, 4.2, 1], x_length=5.6, y_length=2.6,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 2.9 + DOWN * 1.9)
        ylab = label("total probability", 24, MUTED).next_to(ax, UP, buff=0.05).align_to(ax, LEFT)
        xlab = eq(r"\theta", size=30).next_to(ax.x_axis, RIGHT, buff=0.1)
        ticks = VGroup(*[eq(s, size=30, color=MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.12)
                         for s, v in ((r"0", 0), (r"\pi", math.pi), (r"2\pi", 2 * math.pi))])
        yt = VGroup(*[eq(str(k), size=30, color=MUTED).next_to(ax.c2p(0, k), LEFT, buff=0.1) for k in (1, 4)])
        one = DashedLine(ax.c2p(0, 1), ax.c2p(2 * math.pi, 1), color=CYAN, stroke_width=3)
        onel = label("dashed: any valid W gives 1", 22, CYAN).next_to(ylab, RIGHT, buff=0.4)
        self.play(Create(ax), FadeIn(ylab), Write(xlab), FadeIn(ticks), FadeIn(yt), run_time=1.2)
        self.play(Create(one), FadeIn(onel))
        th = ValueTracker(0.0)
        dot = always_redraw(lambda: Dot(ax.c2p(th.get_value(), loop_total(th.get_value())), color=RED, radius=0.07))
        trace = TracedPath(dot.get_center, stroke_color=RED, stroke_width=4)
        tl = eq(r"\theta =", size=32, color=BLUE).next_to(pos, DOWN, buff=0.3).align_to(pos, LEFT)
        num = DecimalNumber(0, num_decimal_places=2, font_size=32, color=BLUE).next_to(tl, RIGHT, buff=0.12)
        num.add_updater(lambda m: m.set_value(th.get_value()))
        self.add(trace, dot, tl, num)
        self.play(th.animate.set_value(2 * math.pi), run_time=8, rate_func=linear)
        m4 = label("identity: 4 > 1", 24, RED).move_to(ax.c2p(math.pi, 3.3))
        m0 = label("flip: 0", 24, RED).next_to(ax.c2p(math.pi, 0), UP, buff=0.12)
        self.play(FadeIn(m4), FadeIn(m0))
        self.wait(2.0)


class CausalGame(Scene):
    def construct(self):
        title = label("The OCB causal game: bound 3/4", 34, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1.2)
        rules = VGroup(label("a, b, b' random bits", 26, INK),
                       label("b' = 0: Alice must output x = b", 26, BLUE),
                       label("b' = 1: Bob must output y = a", 26, AMBER)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        rules.move_to(LEFT * 3.6 + UP * 1.7)
        self.play(FadeIn(rules, lag_ratio=0.3), run_time=1.6)
        arg = VGroup(label("If A acts first, nothing about b", 24, MUTED),
                     label("reaches Alice: her guess wins 1/2.", 24, MUTED),
                     eq(r"p_{\rm succ}\le \tfrac12\cdot 1 + \tfrac12\cdot\tfrac12 = 3/4", size=32)).arrange(
            DOWN, aligned_edge=LEFT, buff=0.14).move_to(LEFT * 3.6 + DOWN * 0.25)
        self.play(FadeIn(arg[0]), FadeIn(arg[1]))
        self.play(Write(arg[2]), run_time=1.4)
        mix = label("mixtures of orders: still at most 3/4", 24, MUTED).next_to(arg, DOWN, buff=0.2).align_to(arg, LEFT)
        self.play(FadeIn(mix))

        ax = Axes(x_range=[0, 1, 0.25], y_range=[0.5, 0.9, 0.1], x_length=4.6, y_length=3.1,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 3.6 + DOWN * 0.75)
        xl = label("visibility v", 24, MUTED).next_to(ax, DOWN, buff=0.15)
        yl = eq(r"p_{\rm succ}", size=30).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        yt = VGroup(*[eq(f"{k:.2f}", size=28, color=MUTED).next_to(ax.c2p(0, k), LEFT, buff=0.08) for k in (0.5, 0.75)])
        bound = DashedLine(ax.c2p(0, 0.75), ax.c2p(1, 0.75), color=MUTED, stroke_width=3)
        self.play(Create(ax), FadeIn(xl), Write(yl), FadeIn(yt), Create(bound))
        law = eq(r"W_v = v\,W_{\rm OCB} + (1-v)\tfrac{1}{4}1", size=32, color=VIOLET).move_to(RIGHT * 3.6 + UP * 2.35)
        lw = eq(r"p_{\rm succ} =", FACT_GAME, size=32, color=VIOLET).next_to(law, DOWN, buff=0.15)
        self.play(Write(law), Write(lw), run_time=1.4)
        v = ValueTracker(0.0)
        dot = always_redraw(lambda: Dot(ax.c2p(v.get_value(), 0.5 + v.get_value() * math.sqrt(2) / 4),
                                        color=VIOLET, radius=0.07))
        tr = TracedPath(dot.get_center, stroke_color=VIOLET, stroke_width=4)
        self.add(tr, dot)
        self.play(v.animate.set_value(V_CROSS), run_time=3, rate_func=linear)
        cross = DashedLine(ax.c2p(V_CROSS, 0.5), ax.c2p(V_CROSS, 0.75), color=RED, stroke_width=3)
        cl = eq(r"v = 1/\sqrt2", size=26, color=RED).next_to(ax.c2p(V_CROSS, 0.5), UP, buff=0.1).shift(RIGHT * 0.75)
        self.play(Create(cross), Write(cl))
        self.play(v.animate.set_value(1.0), run_time=2.5, rate_func=linear)
        top = eq(rf"(2+\sqrt2)/4 \approx {P_OCB:.3f}", size=30, color=VIOLET).move_to(ax.c2p(0.33, 0.84))
        self.play(Write(top))
        concl = label("above 3/4: no mixture of definite orders", 24, RED).to_edge(DOWN, buff=0.25).shift(RIGHT * 2.2)
        self.play(FadeIn(concl))
        self.wait(2.0)
        _ = (Arrow, BLUE, Line)
