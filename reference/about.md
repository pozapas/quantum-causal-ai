---
title: About this book
subtitle: What it covers, how it is built, and how to cite it
---

Quantum Causal AI is a free, open course written by [Amir Rafe](https://pozapas.github.io/). It asks one question at every level: what does it take to say that one thing causes another, and what changes when the things involved are quantum systems? A reader can start with no background and finish at current research.

::::{grid} 1 1 2 2

:::{card} The course in numbers
![Compass icon](../_static/icons/qicon-compass.svg)

80 lessons in 8 levels, 11 interactive labs, 59 checked references, 49 videos, and 25 podcast episodes.
:::

:::{card} The core textbook
![Verified icon](../_static/icons/qicon-verified.svg)

For causal AI, the course follows Elias Bareinboim's *Causal Artificial Intelligence* [@bareinboim]. Lessons point to its chapters where they match.
:::

:::{card} Runs anywhere
![Code icon](../_static/icons/qicon-code.svg)

Every lab shows its results on the page. You can also open it in Google Colab or Binder, or download it, and run it again with only standard scientific Python.
:::

:::{card} Open licence
![Lab icon](../_static/icons/qicon-lab.svg)

Text and figures are CC BY 4.0, and code is MIT. Use them in your own teaching with attribution.
:::

::::

## The eight levels

| Level | Topic | Written for |
|---|---|---|
| ![Level 0 icon](../_static/icons/qicon-level-0.svg) Level 0 | Notice, count, and ask | Grades 1–3 |
| ![Level 1 icon](../_static/icons/qicon-level-1.svg) Level 1 | Chance, waves, and fair tests | Grades 4–6 |
| ![Level 2 icon](../_static/icons/qicon-level-2.svg) Level 2 | Algebra, evidence, and causal maps | Grades 7–9 |
| ![Level 3 icon](../_static/icons/qicon-level-3.svg) Level 3 | Mathematical tools for models | High-school bridge |
| ![Level 4 icon](../_static/icons/qicon-level-4.svg) Level 4 | Classical causal AI | Undergraduate |
| ![Level 5 icon](../_static/icons/qicon-level-5.svg) Level 5 | Quantum information | Advanced undergraduate |
| ![Level 6 icon](../_static/icons/qicon-level-6.svg) Level 6 | Quantum causal models | Graduate |
| ![Level 7 icon](../_static/icons/qicon-level-7.svg) Level 7 | Quantum Causal AI research | Doctoral & postdoctoral |

## How the course is checked

Programs, not opinions, decide what goes in. A unit-test suite compares the simulation code with exact formulas, every notebook runs during the build, and `assert` cells check the key numbers. Every reference, video, and link was fetched from its source before it was listed, and a browser test opens every page. None of this is peer review, so please report anything that looks wrong.

## How to cite

```bibtex
@misc{rafe_quantum_causal_ai,
  author = {Amir Rafe},
  title  = {Quantum Causal AI: An Open Course from Counting to the Research Frontier},
  year   = {2026},
  url    = {https://pozapas.github.io/quantum-causal-ai/}
}
```

## Corrections and contributions

Open an issue or a pull request at [github.com/pozapas/quantum-causal-ai](https://github.com/pozapas/quantum-causal-ai). Corrections to the science are the most welcome contributions.

## Built with

[Jupyter Book 2](https://jupyterbook.org) and [MyST](https://mystmd.org). Figures use Plotly and Matplotlib. The learning map and the placement check are small, dependency-free scripts that run in your browser.
