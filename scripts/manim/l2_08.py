"""L2-08 Observe or intervene: the watched gap versus the assigned gap.

Every rate comes from qcai.science.causal() with the parameters stored in the lesson JSON
(animation.params.model). The 200 made-up students are drawn at the model's expected counts,
so each group of 100 shows exact whole numbers. The coin assignment positions come from the
seeded generator qcai.science.rng (animation.params.seed).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Circle, Create, Dot, FadeIn, FadeOut, GrowArrow, Line, RoundedRectangle,
                   Scene, VGroup, Write)

from qcai_style import AMBER, CYAN, GRID, INK, MUTED, RED, VIOLET, label, params

LESSON = "L2-08"


def numbers(p):
    from qcai import science
    m = p["model"]
    r = science.causal(**m)
    half = p["students"] // 2                 # students per motivation group
    pct = {k: round(r[k] * 100) for k in ("treated", "untreated", "do1", "do0")}
    obs_gap = pct["treated"] - pct["untreated"]
    do_gap = pct["do1"] - pct["do0"]
    users_z1 = round(half * m["high"])        # motivated students who choose the app
    users_z0 = round(half * m["low"])         # other students who choose the app
    assert users_z1 + users_z0 == half, "watched app users should make a group of 100"
    assert obs_gap == round(r["observed"] * 100) and do_gap == round(r["ate"] * 100)
    return r, half, pct, obs_gap, do_gap, users_z1, users_z0


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    _, half, pct, obs_gap, do_gap, _, _ = numbers(L["animation"]["params"])
    return [f"{2 * half} made-up students", f"{pct['treated']} out of 100", f"{pct['untreated']} out of 100",
            f"{pct['do1']} out of 100", f"{pct['do0']} out of 100", f"{obs_gap} points", f"{do_gap} points"]


def node(text, col):
    t = label(text, 26, col, "BOLD")
    r = RoundedRectangle(width=t.width + 0.3, height=t.height + 0.28, corner_radius=0.12, stroke_color=col, stroke_width=3)
    return VGroup(r, t)


def scissors(at):
    blade1 = Line(at + LEFT * 0.32 + DOWN * 0.32, at + RIGHT * 0.32 + UP * 0.32, color=RED, stroke_width=6)
    blade2 = Line(at + LEFT * 0.32 + UP * 0.32, at + RIGHT * 0.32 + DOWN * 0.32, color=RED, stroke_width=6)
    h1 = Circle(radius=0.12, color=RED, stroke_width=5).move_to(at + LEFT * 0.42 + DOWN * 0.42)
    h2 = Circle(radius=0.12, color=RED, stroke_width=5).move_to(at + LEFT * 0.42 + UP * 0.42)
    return VGroup(blade1, blade2, h1, h2)


class ObserveOrIntervene(Scene):
    def construct(self):
        p = params(LESSON)
        r, half, pct, obs_gap, do_gap, users_z1, users_z0 = numbers(p)
        from qcai import science

        title = label("Watching or assigning?", 40, INK, "BOLD").to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=0.9)

        # causal graph, top right
        z, x, y = node("motivated", VIOLET), node("uses app", CYAN), node("passes", INK)
        z.move_to([4.3, 2.35, 0]); x.move_to([2.7, 1.05, 0]); y.move_to([5.9, 1.05, 0])
        zx = Arrow(z.get_bottom(), x.get_top(), buff=0.08, color=VIOLET, stroke_width=5, tip_length=0.2)
        zy = Arrow(z.get_bottom(), y.get_top(), buff=0.08, color=VIOLET, stroke_width=5, tip_length=0.2)
        xy = Arrow(x.get_right(), y.get_left(), buff=0.08, color=CYAN, stroke_width=5, tip_length=0.2)
        self.play(FadeIn(z), FadeIn(x), FadeIn(y), GrowArrow(zx), GrowArrow(zy), GrowArrow(xy), run_time=1.2)

        # 200 students: left half motivated, right half not
        cols, rows, gap = 20, 10, 0.27
        origin = [-6.35, 0.35, 0]
        pos = [[origin[0] + c * gap, origin[1] - rr * gap, 0] for c in range(cols) for rr in range(rows)]
        motivated = [c < cols // 2 for c in range(cols) for _ in range(rows)]
        people = VGroup(*[Dot(q, radius=0.08, color=VIOLET if m else MUTED) for q, m in zip(pos, motivated)])
        crowd = label(f"{2 * half} made-up students", 28, INK, "BOLD").next_to(people, UP, buff=0.55)
        key = VGroup(VGroup(Dot(radius=0.08, color=VIOLET), label("motivated", 24, VIOLET)).arrange(RIGHT, buff=0.12),
                     VGroup(Dot(radius=0.08, color=MUTED), label("not motivated", 24, MUTED)).arrange(RIGHT, buff=0.12),
                     VGroup(Circle(radius=0.12, color=CYAN, stroke_width=4), label("uses app", 24, CYAN)).arrange(RIGHT, buff=0.12)
                     ).arrange(RIGHT, buff=0.35).next_to(people, DOWN, buff=0.4)
        self.play(FadeIn(people, lag_ratio=0.01), FadeIn(crowd), FadeIn(key), run_time=1.6)

        z1 = [i for i, m in enumerate(motivated) if m]
        z0 = [i for i, m in enumerate(motivated) if not m]

        def rings(idx):
            return VGroup(*[Circle(radius=0.12, color=CYAN, stroke_width=3.5).move_to(pos[i]) for i in idx])

        # watch: motivated students choose the app more (first rows of each half, in order)
        watch_idx = z1[:users_z1] + z0[:users_z0]
        watch = rings(watch_idx)
        w_head = label("Watch: students choose", 28, INK, "BOLD").move_to([4.3, -0.1, 0])
        self.play(FadeIn(watch, lag_ratio=0.01), FadeIn(w_head), run_time=1.6)
        w1 = label(f"app users: {pct['treated']} out of 100 pass", 26, INK).next_to(w_head, DOWN, buff=0.3)
        w2 = label(f"non-users: {pct['untreated']} out of 100 pass", 26, INK).next_to(w1, DOWN, buff=0.18)
        w3 = label(f"gap: {obs_gap} points", 30, AMBER, "BOLD").next_to(w2, DOWN, buff=0.28)
        self.play(FadeIn(w1), run_time=0.7)
        self.play(FadeIn(w2), run_time=0.7)
        self.play(FadeIn(w3), run_time=0.7)
        self.wait(2.2)

        # intervene: cut the arrow from motivation to app use; a coin decides
        cut = scissors(zx.get_center()).scale(0.65)
        self.play(FadeIn(cut, scale=1.4), run_time=0.7)
        self.play(FadeOut(zx), FadeOut(cut), FadeOut(watch), FadeOut(w_head), FadeOut(w1), FadeOut(w2),
                  w3.animate.scale(0.8).move_to([4.75, -2.85, 0]).set_color(MUTED), run_time=1.0)
        coin = label("coin", 26, AMBER, "BOLD").move_to([2.7, 2.35, 0])
        cx = Arrow(coin.get_bottom(), x.get_top(), buff=0.08, color=AMBER, stroke_width=5, tip_length=0.2)
        self.play(FadeIn(coin), GrowArrow(cx), run_time=0.8)

        rand = science.rng(p["seed"])
        pick1 = sorted(z1, key=lambda _: rand())[:half // 2]
        pick0 = sorted(z0, key=lambda _: rand())[:half // 2]
        assign = rings(pick1 + pick0)
        a_head = label("Assign: a coin decides", 28, INK, "BOLD").move_to([4.3, -0.1, 0])
        self.play(FadeIn(assign, lag_ratio=0.01), FadeIn(a_head), run_time=1.6)
        a1 = label(f"given app: {pct['do1']} out of 100 pass", 26, INK).next_to(a_head, DOWN, buff=0.3)
        a2 = label(f"no app: {pct['do0']} out of 100 pass", 26, INK).next_to(a1, DOWN, buff=0.18)
        a3 = label(f"gap: {do_gap} points", 30, CYAN, "BOLD").next_to(a2, DOWN, buff=0.28)
        self.play(FadeIn(a1), run_time=0.7)
        self.play(FadeIn(a2), run_time=0.7)
        self.play(FadeIn(a3), run_time=0.7)
        self.wait(1.0)

        w_lbl = label("watched", 24, MUTED).next_to(w3, LEFT, buff=0.2)
        self.play(FadeIn(w_lbl), run_time=0.5)
        sub = label("Same students. The coin takes away the head start from motivation.", 26, INK)
        sub.to_edge(DOWN, buff=0.3)
        self.play(FadeOut(key), FadeIn(sub), run_time=0.8)
        self.wait(3.0)
        _ = (GRID, r)
