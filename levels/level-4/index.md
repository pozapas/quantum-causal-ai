---
title: "Level 4 · Classical causal AI"
short_title: "Level 4 · Classical causal AI"
subtitle: "Undergraduate causal inference and machine learning"
---

(level-4)=

:::{div}
:class: qcai-level-hero qcai-level-4
![Level 4 icon](../../_static/icons/qicon-level-4.svg) **Undergraduate**: Undergraduate causal inference and machine learning

Use causal models to define the effect of an action. Separate identification from estimation. Study graphs, experiments, hidden causes, discovery, and counterfactual reasoning before connecting these ideas to quantum systems.
:::

:::{tip} Core textbook for this level
Elias Bareinboim's *Causal Artificial Intelligence: A Roadmap for Building Causally Intelligent Systems* [@bareinboim] is the main reference for causal AI in this course. The draft is free at [causalai-book.net](https://causalai-book.net/). Lessons marked *Read alongside the textbook* point to the matching chapter.
:::

## Lessons in this level

| Lesson | Objective | Lab |
|---|---|---|
| [L4-01 · Structural causal models](#lesson-l4-01) | Replace a structural equation to calculate an intervention and compare it with observation. | [Confounding and intervention](../../labs/03-causal-inference.ipynb) |
| [L4-02 · DAGs and d-separation](#lesson-l4-02) | Use path rules to decide which conditional independences a causal graph implies. | [Confounding and intervention](../../labs/03-causal-inference.ipynb) |
| [L4-03 · Confounders, mediators, and colliders](#lesson-l4-03) | Choose adjustment variables by their graph role instead of adjusting for every available variable. | [Confounding and intervention](../../labs/03-causal-inference.ipynb) |
| [L4-04 · Backdoor adjustment](#lesson-l4-04) | Standardize outcome risks across a valid adjustment set to calculate an intervention effect. | [Confounding and intervention](../../labs/03-causal-inference.ipynb) |
| [L4-05 · Frontdoor identification](#lesson-l4-05) | Calculate a frontdoor effect and state all three graphical conditions that justify it. | [Confounding and intervention](../../labs/03-causal-inference.ipynb) |
| [L4-06 · Potential outcomes and randomization](#lesson-l4-06) | Define an average treatment effect and identify the assumptions that connect it to an observed contrast. | [Confounding and intervention](../../labs/03-causal-inference.ipynb) |
| [L4-07 · Identification before estimation](#lesson-l4-07) | Show how two models can fit the same observations and disagree about an intervention. | [Confounding and intervention](../../labs/03-causal-inference.ipynb) |
| [L4-08 · Causal discovery and its limits](#lesson-l4-08) | Explain Markov equivalence, faithfulness, and the limits of discovering directions from observational data. | [Confounding and intervention](../../labs/03-causal-inference.ipynb) |
| [L4-09 · Counterfactual reasoning](#lesson-l4-09) | Use abduction, action, and prediction to answer a counterfactual in an explicit structural model. | [Confounding and intervention](../../labs/03-causal-inference.ipynb) |
| [L4-10 · Causal machine learning, transport, and fairness](#lesson-l4-10) | Define a causal learning target and explain the additional assumptions needed for transport and fairness claims. | [Confounding and intervention](../../labs/03-causal-inference.ipynb) |

```{include} ../../media/_level-4.md
```
