import pathlib, sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # noqa: E401,E702
"""L2-01 Name quantities with variables: a ticket table becomes points, then the line y = 3x + 2.

The ticket price, booking fee and ticket counts are stored in the lesson JSON
(animation.params). No randomness is used.
"""

from manim import (DOWN, LEFT, RIGHT, UP, Axes, Create, DashedLine, Dot, FadeIn, Indicate, Line, Scene, SurroundingRectangle,
                   VGroup, Write)

from qcai_style import AMBER, CYAN, INK, MUTED, VIOLET, label, params

LESSON = "L2-01"


def rows(p):
    return [(x, p["price"] * x + p["fee"]) for x in p["tickets"]]


def rule(p):
    return f"y = {p['price']}x + {p['fee']}"


def facts(L):
    """Statements the animation shows that the lesson text must also contain."""
    p = L["animation"]["params"]
    return [rule(p), f"+1 across, +{p['price']} up"] + [f"({x}, {y})" for x, y in rows(p)]


class TicketLine(Scene):
    def construct(self):
        p = params(LESSON)
        data = rows(p)
        price, fee = p["price"], p["fee"]

        title = label(f"Tickets: {price} dollars each, plus a {fee} dollar fee", 36, INK, "BOLD").to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=1.2)

        # table on the left, built from plain labels
        hx = label("x  (tickets)", 26, VIOLET, "BOLD")
        hy = label("y  (dollars)", 26, CYAN, "BOLD")
        head = VGroup(hx, hy).arrange(RIGHT, buff=0.6)
        head.move_to(LEFT * 4.4 + UP * 2.0)
        rule_line = Line(head.get_left() + DOWN * 0.3, head.get_right() + DOWN * 0.3, color=MUTED, stroke_width=2)
        self.play(FadeIn(head), Create(rule_line), run_time=0.8)

        ax = Axes(x_range=[0, 5, 1], y_range=[0, 18, 2], x_length=6.2, y_length=5.0,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 28},
                  x_axis_config={"numbers_to_include": list(range(0, 6))},
                  y_axis_config={"numbers_to_include": list(range(0, 17, 4))}).move_to(RIGHT * 2.6 + DOWN * 0.55)
        for axis in (ax.x_axis, ax.y_axis):
            axis.numbers.set_color(MUTED)
            for num in axis.numbers:
                num.scale(1.25)
        xl = label("tickets, x", 26, VIOLET).next_to(ax.x_axis, DOWN, buff=0.4)
        yl = label("dollars, y", 26, CYAN).next_to(ax.y_axis, UP, buff=0.15).shift(RIGHT * 0.4)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.2)

        dots = VGroup()
        for i, (x, y) in enumerate(data):
            cx = label(str(x), 30, INK).move_to([hx.get_center()[0], rule_line.get_y() - 0.45 - 0.62 * i, 0])
            cy = label(str(y), 30, INK).move_to([hy.get_center()[0], cx.get_y(), 0])
            d = Dot(ax.c2p(x, y), radius=0.1, color=AMBER)
            pt = label(f"({x}, {y})", 24, MUTED)
            if x == 0:
                pt.next_to(d, RIGHT, buff=0.2).shift(DOWN * 0.3)
            else:
                pt.next_to(d, LEFT, buff=0.15).shift(UP * 0.28)
            self.play(FadeIn(cx), FadeIn(cy), run_time=0.45)
            self.play(FadeIn(d, scale=0.5), FadeIn(pt), run_time=0.55)
            dots.add(VGroup(d, pt))
        self.wait(0.5)

        line = Line(ax.c2p(0, fee), ax.c2p(5, price * 5 + fee), color=VIOLET, stroke_width=5)
        eq = label(rule(p), 40, VIOLET, "BOLD").move_to(LEFT * 4.4 + DOWN * 1.95)
        self.play(Create(line), Write(eq), run_time=1.5)
        self.wait(0.6)

        # slope steps between x = 1 and x = 2
        x0, y0 = data[1]
        a = ax.c2p(x0, y0)
        b = ax.c2p(x0 + 1, y0)
        c = ax.c2p(x0 + 1, y0 + price)
        run_ = Line(a, b, color=AMBER, stroke_width=6)
        rise = Line(b, c, color=AMBER, stroke_width=6)
        step_lbl = label(f"+1 across, +{price} up", 28, AMBER, "BOLD").move_to(ax.c2p(3.55, 3.2))
        self.play(Create(run_), run_time=0.7)
        self.play(Create(rise), FadeIn(step_lbl), run_time=0.8)
        coef = label(f"{price} = price per ticket (coefficient)", 26, INK).next_to(eq, DOWN, buff=0.3)
        self.play(FadeIn(coef), Indicate(step_lbl, color=AMBER), run_time=1.0)
        self.wait(1.2)

        # intercept
        start = Dot(ax.c2p(0, fee), radius=0.14, color=CYAN)
        ring = SurroundingRectangle(start, color=CYAN, buff=0.08, corner_radius=0.1)
        const = label(f"{fee} = booking fee (constant)", 26, INK).next_to(coef, DOWN, buff=0.15)
        self.play(FadeIn(start), Create(ring), FadeIn(const), run_time=1.0)
        self.wait(3.0)
        _ = (UP, DOWN, LEFT, RIGHT, dots)
