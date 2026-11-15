---
title: "Level 4 · Classical causal AI"
short_title: "Level 4 · Classical causal AI"
subtitle: "Undergraduates in statistics, computer science, data science, or physics who know basic probability and linear algebra"
---

(level-4)=

:::{div}
:class: qcai-level-hero qcai-level-4
![Level 4 icon](../../_static/icons/qicon-level-4.svg) **Undergraduate**: Undergraduates in statistics, computer science, data science, or physics who know basic probability and linear algebra

**The central question:** When can data that were only observed tell us what would happen if we acted, and what must we assume, state, and test before a causal claim is justified?

Students write structural causal models and compute interventions by replacing one mechanism. They read conditional independences off directed acyclic graphs with d-separation, sort variables into confounders, mediators, and colliders, and derive the backdoor and frontdoor formulas (full proofs for the core cases, cited sketches in general) that turn interventional questions into observational ones. They connect graphs to potential outcomes and randomized experiments, separate identification from estimation, and see why two models can fit the same data and disagree about an action. The unit closes with what data cannot reveal (Markov equivalence, faithfulness), counterfactuals by abduction, action, and prediction, and the extra assumptions needed for causal machine learning, transport between populations, and fairness claims.
:::

## At a glance

| | |
|---|---|
| Who it is for | Undergraduates who have finished Levels 2 and 3 of this course or an equivalent introduction to probability, expectation, linear algebra, and regression. The lessons suit a one-semester course or a study group; each has proofs for students who want them and runnable code for students who learn by computing. |
| Prerequisites | Conditional probability and Bayes' rule, expectation and variance, simple linear regression, and enough Python to run and modify a NumPy notebook. |
| Lessons | 10 lessons of about 100 minutes, plus a 3-session capstone |
| Pace | One lesson a week fits a semester with the project in the last three weeks; two lessons a week fits an intensive half-term. Each lesson splits into an intuition and animation sitting and a proofs, code, and exercises sitting. |

## How each lesson is built

1. Warm up: predict the answer to the lesson's opening puzzle before any formula.
2. Watch the animations and read the definitions; restate each in your own words.
3. Work through the theorem and its proof, then the worked example by hand.
4. Run and modify the code; confirm the hand calculation numerically and use the interactive figure to test a prediction.
5. Solve the core and stretch exercises, then answer the check questions before opening the explanations.
6. Close by writing the assumptions each result needed and where they could fail.

## Learning outcomes

| | By the end you can... | Practised in |
|---|---|---|
| O1 | Write a structural causal model, compute an intervention by graph surgery, and compare it with conditioning. | [L4-01](#lesson-l4-01), [L4-07](#lesson-l4-07) |
| O2 | Decide d-separation in a causal graph and state precisely what the soundness theorem does and does not guarantee. | [L4-02](#lesson-l4-02), [L4-08](#lesson-l4-08) |
| O3 | Choose an adjustment set by graph roles and compute the bias caused by adjusting for a mediator or a collider. | [L4-03](#lesson-l4-03), [L4-04](#lesson-l4-04), capstone |
| O4 | Derive and apply the backdoor and frontdoor formulas, stating every graphical and positivity condition. | [L4-04](#lesson-l4-04), [L4-05](#lesson-l4-05), capstone |
| O5 | Define average treatment effects with potential outcomes and explain how randomization identifies them. | [L4-06](#lesson-l4-06) |
| O6 | Separate identification from estimation, and show with two models that the same data can support different causal answers. | [L4-07](#lesson-l4-07), [L4-08](#lesson-l4-08), capstone |
| O7 | Answer a counterfactual question in an explicit structural model by abduction, action, and prediction. | [L4-09](#lesson-l4-09) |
| O8 | State the additional assumptions behind causal machine learning, transport, and fairness claims, and audit a claim that omits them. | [L4-10](#lesson-l4-10), capstone |

## Lessons

| Lesson | Big idea | Media |
|---|---|---|
| [L4-01 · Structural causal models](#lesson-l4-01) | A causal model is a set of mechanisms; an intervention replaces one mechanism and keeps the others, so seeing $X = x$ and setting $X = x$ can give different answers from the same model. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L4-02 · DAGs and d-separation](#lesson-l4-02) | A causal graph is a compact list of conditional independences: two sets are independent given $Z$ whenever every path between them is blocked by $Z$, and conditioning closes chains and forks but opens colliders. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L4-03 · Confounders, mediators, and colliders](#lesson-l4-03) | The same act, adding a variable to a regression or stratifying on it, removes bias when the variable is a confounder, removes part of the effect when it is a mediator, and creates bias when it is a collider; the graph, not the data, tells you which. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L4-04 · Backdoor adjustment](#lesson-l4-04) | If a measured set blocks every noncausal path into the treatment without touching its descendants, then reweighting stratum risks to one common covariate mix turns an observed contrast into a causal effect. | 3 animations, interactive, 1 figures, 2 diagrams, code |
| [L4-05 · Frontdoor identification](#lesson-l4-05) | When every backdoor path runs through a hidden cause, a measured mediator that carries all of the effect and is shielded from that cause lets us identify the effect in two backdoor steps: treatment to mediator, then mediator to outcome. | 3 animations, interactive, 1 figures, 2 diagrams, code |
| [L4-06 · Potential outcomes and randomization](#lesson-l4-06) | Each unit has an outcome for every treatment but shows only one, so causal effects are averages over a table we can never see in full; randomization makes the visible half a fair sample of each invisible column. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L4-07 · Identification before estimation](#lesson-l4-07) | If two models that fit the same exact distribution disagree about an intervention, no estimator and no sample size can settle the question; identification depends on assumptions and distributions, estimation on data. | 3 animations, interactive, 1 figures, 2 diagrams, code |
| [L4-08 · Causal discovery and its limits](#lesson-l4-08) | Under the Markov and faithfulness assumptions, perfect independence tests reveal a graph's skeleton and its v-structures and nothing more; every further arrow needs extra assumptions, interventions, or restrictions on the mechanisms. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L4-09 · Counterfactual reasoning](#lesson-l4-09) | A counterfactual keeps the background factors of the unit you actually observed and changes one mechanism, so it can say more about that unit than any population average, but only as much as the structural model can be trusted. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L4-10 · Causal machine learning, transport, and fairness](#lesson-l4-10) | Machine learning can estimate a causal quantity only after the quantity is defined and identified; carrying it to a new population, trusting it under shift, or calling a predictor fair each adds assumptions about which mechanisms stay the same and which paths matter. | 3 animations, interactive, 1 figures, 2 diagrams, code |

## Capstone: A causal analysis you can defend

Over three sessions students state a causal question, draw and justify a graph, prove that the target effect is identified (or show that it is not), estimate it on simulated or public data, and write an analysis that keeps assumptions, identification, estimation, and limits apart.

**Choose a question, or propose your own:**

- In a simulated hospital dataset generated from a structural model the student writes, what is the effect of a treatment on recovery, and which covariates must be adjusted for?
- Using a public observational dataset described in a textbook (for example a job-training or smoking study), what effect can be identified under a stated graph, and how sensitive is the answer to one omitted confounder?
- For a prediction model trained in one population, which causal assumptions would justify using it in a second population, and what would a fairness audit of it need to assume?

**Milestones:**

1. State the causal question as a target quantity, such as the outcome distribution under an intervention or an average treatment effect, and say why prediction alone does not answer it.
2. Draw the causal graph, justify every arrow and every missing arrow in one sentence each, and list the testable independences it implies.
3. Prove identification with the backdoor or frontdoor criterion, or show by two models that the effect is not identified.
4. Estimate the effect with a standardization or regression estimator and report an uncertainty interval.
5. Test the graph's implied independences where data allow, and run one sensitivity analysis for an unmeasured confounder.
6. Write the analysis: question, graph, identification proof, estimate, checks, and the limits of the claim.

**Assessment rubric.**

| Criterion | Developing | Proficient | Advanced |
|---|---|---|---|
| Causal question and target | I described a relationship I am interested in. | I stated a precise interventional or counterfactual target. | I can explain why that target differs from the corresponding conditional quantity in my data. |
| Graph and assumptions | I drew a graph. | I justified each arrow and listed the independences the graph implies. | I can say which conclusions would change if a specific arrow were added or removed. |
| Identification | I chose variables to adjust for. | I proved identification with a stated criterion, including positivity. | I can show a second model that fits my data and gives a different answer when my assumptions fail. |
| Estimation and limits | I computed an estimate. | I reported an estimate with uncertainty and at least one check of the graph. | I can state what the estimate does not show and what new data or experiment would settle it. |

## Tools

- Python 3 with NumPy, SciPy, pandas, Matplotlib, Plotly, and networkx (the course notebooks run in Colab or Binder)
- The course package qcai, whose science module contains the binary structural causal model used in the lessons
- Paper and pencil for drawing graphs and checking paths by hand
- Optional: the DoWhy or causal-learn libraries for the project

## How progress is assessed

Each lesson has three or four check questions (one reviews an earlier lesson), exercises at core, stretch, and challenge levels with complete solutions, and runnable code whose printed results must match the hand calculation. The project is a written causal analysis with code, judged with a four-part rubric.

## Core readings

- [@pearlcausality]: The reference text for structural causal models, the do-operator, d-separation, and identification.
- [@hernan]: Free textbook on causal inference from data, strong on confounding, selection bias, and potential outcomes.
- [@peters]: Concise, mathematical treatment of SCMs, Markov properties, and causal discovery, free online.
- [@bradyneal]: Lecture notes with many small worked graphs; a gentle companion to every lesson.
- [@seeing]: Applied examples of graphs, adjustment, and identification strategies in social science data.
- [@spirtes]: The source for faithfulness and constraint-based causal discovery.
- [@bareinboim]: A roadmap connecting causal inference with artificial intelligence, transport, and fairness.

:::{dropdown} For instructors: how this level is designed

The unit was planned backward from its outcomes [@ubd_whitepaper]. Each lesson moves from a concrete puzzle to an animation, then to a precise definition and theorem with proof, then to computation and practice, following first principles of instruction [@merrill2002], with retrieval and spaced review through check questions that revisit earlier lessons [@dunlosky2013]. Several 3Blue1Brown-style animations per lesson, made with Manim Community Edition [@manim_ce] and driven by the same numbers as the text, show what static notation hides: graph surgery, paths opening and closing, and selection creating correlation. Multiple representations follow Universal Design for Learning [@udl]. The content follows Pearl's structural account of causation [@pearlcausality; @pearl] together with the potential-outcomes treatment of Hernán and Robins [@hernan], the Markov and discovery theory of Spirtes, Glymour and Scheines and of Peters, Janzing and Schölkopf [@spirtes; @peters], and the causal AI roadmap of Bareinboim and colleagues [@bareinboim].

**Ways to adapt it.**

- Every key idea appears three ways: a moving animation with a full text description, a formal statement with proof, and code whose output can be checked.
- Students can show mastery by a proof, a computation, a simulation, or an annotated causal graph.
- Each lesson has core, stretch, and challenge exercises, so the same lesson serves students who need consolidation and students who want depth.
- Interactive figures let students test a prediction by changing one quantity at a time before they read the explanation.
:::

```{include} ../../media/_level-4.md
```
