"""Write index.ipynb (home page with the placement dialog) and start/roadmap.ipynb.  Run from book/."""
import json
import pathlib

import nbformat as nbf

BOOK = pathlib.Path(__file__).resolve().parents[1]
lv = [json.loads((BOOK / f"_data/levels/level{n}.json").read_text(encoding="utf-8")) for n in range(8)]
STAGE = ["Grades 1-3", "Grades 4-6", "Grades 7-9", "High-school bridge", "Undergraduate",
         "Advanced undergraduate", "Graduate", "Doctoral and postdoctoral"]
KS = {"kernelspec": {"name": "qcai", "display_name": "Python 3 (qcai)", "language": "python"}}
BOOT = """import sys, pathlib
root = next(p for p in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents] if (p / "qcai").is_dir())
sys.path.insert(0, str(root))"""
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
hide = {"tags": ["remove-input"]}


def first_sentence(t):
    return t.split(". ")[0].rstrip(".") + "."


cards = "\n".join(
    f""":::{{card}} Level {n} · {l['title']}
:link: levels/level-{n}/index.md
![Level {n} icon](_static/icons/qicon-level-{n}.svg)

{STAGE[n]} · {len(l['lessons'])} lessons

{first_sentence(l['intro'])}
:::
""" for n, l in enumerate(lv))

home = [
    md("""---
title: Quantum Causal AI
subtitle: An open course that starts with counting and ends at the research frontier
---

:::{div}
:class: qcai-hero

## Learn how causes work, then learn how quantum physics changes the question.

You can start this course with no background at all. The first lessons count objects and run fair tests. Later lessons build probability, causal graphs, linear algebra, and quantum information, one checked step at a time. The last levels reach current research on quantum causal models, indefinite causal order, and quantum machine learning.

80 lessons · 8 levels · 11 interactive labs · every source checked

[Start at Level 0](levels/level-0/index.md) · [Open the learning map](start/roadmap.ipynb) · [How to use this book](start/how-to-use.md)
:::"""),
    code(BOOT, metadata=hide),
    code("from qcai.widgets import placement\nplacement(base=\"./\")", metadata=hide),
    md(f"""## Choose a level

Each level is a teaching guide, not a certificate. Open a level and try two of its exercises. If they feel easy, move up.

::::{{grid}} 1 2 2 2
:class: qcai-levels

{cards}
::::

## What you get

::::{{grid}} 1 1 2 2

:::{{card}} Run the science
![Lab icon](_static/icons/qicon-lab.svg)

Each lab is a Jupyter notebook with figures you can drag, rotate, and replay in the browser. You can also download it and run it yourself. Unit tests check the simulation code against exact formulas.
:::

:::{{card}} Check every source
![Verified sources icon](_static/icons/qicon-verified.svg)

A script matched each reference against arXiv, Crossref, or the publisher's page before it was cited. The full list is in the [bibliography](reference/bibliography.md).
:::

:::{{card}} Read the core textbook
![Book icon](_static/icons/qicon-verified.svg)

For causal AI, the course follows Elias Bareinboim's *Causal Artificial Intelligence* [@bareinboim]. Lessons in Levels 2, 4, and 7 point to the matching chapter of the free draft at [causalai-book.net](https://causalai-book.net/).
:::

:::{{card}} Watch and listen
![Media icon](_static/icons/qicon-media.svg)

Lectures, explainers, and podcast episodes for every level. Each title and channel was fetched from the source itself. See [Watch and listen](media/watch-listen.md).
:::

::::

:::{{important}} What this course does not claim
Quantum causal models, indefinite causal order, and quantum machine learning are separate research programs that ask different questions. This course shows where they meet. It does not claim a general quantum advantage for causal inference. The labs are classical simulations of textbook equations and do not run on quantum hardware.
:::

:::{{note}} How this course is checked
Automated tests check the simulation code against exact formulas, every notebook runs during the build, and every reference and link was checked against its source. That is not peer review, so corrections are welcome.
:::"""),
]
nb = nbf.v4.new_notebook(cells=home, metadata=KS)
nbf.write(nb, BOOK / "index.ipynb")

road = [
    md("""---
title: The learning map
subtitle: Every lesson, and what it builds on
---

Each circle is a lesson, and each row is a level. Hover over a circle, tap it, or move to it with the Tab key. Violet marks every lesson it builds on, and cyan marks every lesson it unlocks. Click a circle to pin it, then open the lesson from the panel below the map. The chips filter by level, and the search box finds lessons by name or objective.

The lines show teaching order. They are not physical causes."""),
    code(BOOT, metadata=hide),
    code("from qcai.widgets import learning_map\nlearning_map(base=\"../../\")", metadata=hide),
    md("""## How many lessons each lab supports

Click a level to zoom in. The outer ring shows which lab goes with those lessons."""),
    code("""import collections, json
import plotly.graph_objects as go
from qcai.viz import show
from qcai.widgets import COLORS

levels = [json.loads((root / "_data" / "levels" / f"level{n}.json").read_text(encoding="utf-8")) for n in range(8)]
rows = collections.Counter((lv["level"], L["lab"]) for lv in levels for L in lv["lessons"])
ids, labels, parents, vals, colors = [], [], [], [], []
for k, lv in enumerate(levels):
    ids.append(f"L{k}"); labels.append(f"Level {k}"); parents.append(""); vals.append(0); colors.append(COLORS[k])
for (k, lab), c in sorted(rows.items()):
    ids.append(f"L{k}-{lab}"); labels.append(lab); parents.append(f"L{k}"); vals.append(c); colors.append(COLORS[k])
fig = go.Figure(go.Sunburst(ids=ids, labels=labels, parents=parents, values=vals, branchvalues="remainder",
                            marker=dict(colors=colors, line=dict(color="white", width=2)),
                            insidetextorientation="radial", hovertemplate="%{label}: %{value} lessons<extra></extra>"))
fig.update_layout(height=520, margin=dict(t=10, l=0, r=0, b=0), font=dict(family="Inter, Segoe UI, sans-serif"))
assert sum(rows.values()) == 80
show(fig)""", metadata=hide),
]
nb = nbf.v4.new_notebook(cells=road, metadata=KS)
nbf.write(nb, BOOK / "start" / "roadmap.ipynb")
print("index.ipynb and start/roadmap.ipynb written")
