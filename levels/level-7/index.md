---
title: "Level 7 · Quantum Causal AI research"
short_title: "Level 7 · Quantum Causal AI research"
subtitle: "Doctoral and postdoctoral study"
---

(level-7)=

:::{div}
:class: qcai-level-hero qcai-level-7
![Level 7 icon](../../_static/icons/qicon-level-7.svg) **Doctoral & postdoctoral**: Doctoral and postdoctoral study

**The central question:** When does a quantum learning method answer a causal question better than the alternatives, and what evidence, identification argument and resource count would establish it?

The unit treats Quantum Causal AI as a set of research questions, not a finished method. Learners first separate prediction, causal identification and quantum resource claims, then study the two workhorses of quantum learning, variational circuits with parameter-shift gradients and quantum kernels, with exact derivations and complete shot accounting. They analyze trainability and barren plateaus, prove identifiability before learning, and build resource ledgers that keep copies, queries, gates and time apart. Classical shadows show how observable structure controls estimation cost. The unit ends with reproducible benchmark design, a falsifiable research protocol with stopping rules, and a critical synthesis of open problems.
:::

## At a glance

| | |
|---|---|
| Who it is for | Doctoral students and postdoctoral researchers in physics, computer science, statistics or a quantitative field who have completed Levels 4 to 6 or know structural causal models, density operators and channels, and quantum causal models. Each lesson works as a seminar session, a reading-group module or self-study. |
| Prerequisites | Structural causal models and identification (Level 4), quantum states, channels and measurements (Level 5), quantum causal models and process descriptions (Level 6), and fluency with linear algebra, probability and Python with numpy. |
| Lessons | 10 lessons of about 120 minutes, plus a 4-session capstone |
| Pace | One lesson a week with the project running alongside fits a twelve-week seminar: ten lesson weeks and two project weeks. Each lesson splits into a derivation session (animations, theorems, proofs) and a computation session (code, interactive figures, exercises). |

## How each lesson is built

1. Before the session: read the motivation and attempt the review check from memory.
2. Watch the animations and reconstruct each derivation on paper before reading the proof.
3. Run the code blocks, change one parameter, and predict the output before running it again.
4. Work the worked example, then one core, one stretch and one challenge exercise.
5. Discuss: classify a recent paper's claims with the lesson's tools and write a short referee note.
6. Instructors: use the teaching notes and the assessment suggestion at the end of each lesson.

## Learning outcomes

| | By the end you can... | Practised in |
|---|---|---|
| O1 | Specify a research task by its data access, target, model class, error criterion and budget, and separate prediction, causal and resource claims. | [L7-01](#lesson-l7-01), capstone |
| O2 | Derive the parameter-shift rule from the spectrum of the generator and compare its bias, variance and circuit cost with finite differences under shot noise. | [L7-02](#lesson-l7-02) |
| O3 | Evaluate a quantum kernel claim with its full cost: positive semidefiniteness, shots per Gram entry, concentration, and the geometric difference to classical kernels. | [L7-03](#lesson-l7-03), capstone |
| O4 | Distinguish vanishing true gradients from noisy estimates and design a controlled trainability study across system sizes. | [L7-04](#lesson-l7-04) |
| O5 | Prove or disprove identifiability of a target under a stated data map and model class before fitting a flexible model. | [L7-05](#lesson-l7-05), capstone |
| O6 | Keep copies, queries, gates and wall-clock time apart in a resource ledger, and explain how observable structure controls classical-shadow cost. | [L7-06](#lesson-l7-06), [L7-07](#lesson-l7-07) |
| O7 | Design a reproducible benchmark and a falsifiable protocol with stopping rules that separate prediction from causal recovery. | [L7-08](#lesson-l7-08), [L7-09](#lesson-l7-09), capstone |
| O8 | Formulate an open research question with its evidence requirements, without presenting a proposal as a result. | [L7-10](#lesson-l7-10), capstone |

## Lessons

| Lesson | Big idea | Worked example |
|---|---|---|
| [L7-01 · Define the learning task](#lesson-l7-01) | A method answers the question its target and data make answerable: prediction accuracy, an identified causal effect, and a quantum resource saving are different claims with different evidence, and a quantum processor changes cost and function class, never what the data identify. | Rewriting an overloaded claim as three specified tasks |
| [L7-02 · Variational circuits and parameter-shift gradients](#lesson-l7-02) | For a gate $e^{-i\theta P/2}$ with $P^2 = I$ the expectation is a single sinusoid in $\theta$, so two evaluations a quarter turn apart give the exact derivative; on hardware the rule removes bias, not shot noise, and it costs two circuit settings per parameter. | A full gradient step for a two-parameter model, with its cost |
| [L7-03 · Quantum kernels and data access](#lesson-l7-03) | A quantum kernel is an inner product of embedded states, estimated entry by entry from shots; whether it helps depends on how the embedding's geometry differs from strong classical kernels on the given data, and on the cost of estimating roughly $M^2/2$ noisy entries, not on how hard one entry is to compute. | Pricing a small quantum kernel experiment |
| [L7-04 · Barren plateaus and trainability](#lesson-l7-04) | If the circuit before a parameter scrambles like a unitary 2-design, the gradient has mean zero and variance of order $2^{-n}$ or smaller, so resolving it costs exponentially many shots; global costs and hardware noise make it worse by separate mechanisms. | Budget for a 10-qubit study |
| [L7-05 · Identifiability before quantum causal learning](#lesson-l7-05) | A target is learnable only if every model that fits the accessible data gives it the same value; no estimator, however flexible, can do better, but quantum measurements in several bases can identify a causal direction that classical correlations cannot. | How much direct cause must there be? |
| [L7-06 · Sample complexity and resource accounting](#lesson-l7-06) | A speedup is a statement about one resource under one access model; Hoeffding gives reproducible shot counts for fixed designs, and counting data loading, depth and noise can turn a quadratic or Heisenberg-type gain into nothing or into a constant factor. | Budget for a causal-effect estimate on hardware |
| [L7-07 · Classical shadows and observable structure](#lesson-l7-07) | A classical shadow inverts the average effect of a random measurement, so one data set estimates many observables; the price of each observable is its shadow norm, which for random Pauli measurements grows like 3 to the power of its weight, not with the number of observables or qubits. | Budgeting a shadow experiment |
| [L7-08 · Reproducible quantum causal benchmarks](#lesson-l7-08) | A causal benchmark must score what a method claims, interventions and structure rather than prediction on the training distribution, and its numbers mean something only when generators, seeds, splits, tuning and resources are fixed in advance and reported. | Designing the held-out test for a dephasing learner |
| [L7-09 · A research protocol from question to result](#lesson-l7-09) | A result means what its protocol lets it mean: the false-positive rate is a property of the whole plan, including when you stop, so the plan has to exist before the data do. | Running the preregistered depolarizing test |
| [L7-10 · Open problems and critical synthesis](#lesson-l7-10) | A frontier is mapped by precise statements: what is proved, under which assumptions and against which baseline, what is only observed, and what test would close each open question. | Auditing a hypothetical claim to its supported form |

## Capstone: A pre-registered quantum causal learning study

Over four sessions the learner turns a research question into a specified task, proves or disproves identification of its target, writes a protocol with resource budget and stopping rules, runs a reproducible simulation study against strong classical baselines, and reports results with the limits of what they show.

**Choose a question, or propose your own:**

- Can a variational or kernel model recover the effect of an intervention on a simulated quantum process better than a classical learner given the same measurement records, and what identifies that effect?
- For a family of feature maps, how does the geometric difference to tuned classical kernels scale with qubits, and at what shot budget do Gram matrix estimates stop being informative?
- Under a fixed shot budget, which gradient estimator and initialization strategy keeps a variational circuit trainable as it grows, and how would you tell a barren plateau from estimation noise?

**Milestones:**

1. Write the task specification: data access, target formula, model class, error criterion and resource budget.
2. Prove identification of the target under the stated access, or construct two data-equivalent models that disprove it and revise the design.
3. Pre-register the protocol: hypotheses, metrics, classical baselines, system sizes, seeds, shot budgets and stopping rules.
4. Implement the simulation with fixed seeds, unit tests against closed forms, and a complete resource ledger.
5. Run the study across sizes, report uncertainty for every metric, and compare with the tuned baselines.
6. Write the report: claims matched to evidence, limits, and what result would have falsified the hypothesis.

**Assessment rubric.**

| Criterion | Developing | Proficient | Advanced |
|---|---|---|---|
| Task and identification | The task is described in words and the target is implicit. | The target is a formula, and identification is argued under stated assumptions. | Identification is proved, or disproved by a constructed counterexample, and the design is adjusted accordingly. |
| Resource accounting | Some costs are reported, such as circuit depth. | Shots, circuit settings, data loading and classical post-processing are counted. | Costs are given as functions of size and accuracy, and the comparison fixes the access model for all methods. |
| Baselines and statistics | One classical method is run with default settings. | Tuned classical baselines and uncertainty intervals are reported for every metric. | Baselines are chosen to be the strongest available for the access model, and conclusions survive the uncertainty. |
| Reproducibility and claims | Code runs, but seeds and settings are incomplete. | Seeds, versions, protocol and stopping rules are fixed in advance and reported. | Every claim is matched to its evidence, limits are explicit, and a falsifying outcome is stated. |

## Tools

- Python 3 with numpy, scipy, matplotlib and plotly (the course package qcai for the lab notebooks)
- A Jupyter environment (local, Colab or Binder) for the lessons' code and the labs
- Access to the cited papers (all have open arXiv versions)
- Optional: a quantum software framework such as PennyLane for comparison with the hand-written simulators
- Optional: access to a cloud quantum device, with its calibration data recorded

## How progress is assessed

Each lesson ends with four check questions, one reviewing an earlier lesson, and exercises at core, stretch and challenge levels with complete solutions. Several challenge exercises are written as referee reports on a described paper. The capstone is a pre-registered research protocol with a reproducible simulation study, judged with a four-part rubric.

## Core readings

- [@qml]: A survey of quantum machine learning task classes and the access assumptions behind them.
- [@vqa]: Review of variational quantum algorithms, their training and their limitations.
- [@schuld]: Conditions under which parameter-shift rules give exact gradients on hardware.
- [@advantage]: The power-of-data analysis: when classical learners with data match quantum models.
- [@plateaus]: Gradient concentration in random parametrized circuits.
- [@costa]: Process-based quantum causal modelling, the framework for causal questions about quantum systems.
- [@bareinboim]: Causal AI from structural causal models through identification and learning.
- [@shadows]: Classical shadows and how observable structure controls estimation cost.

:::{dropdown} For instructors: how this level is designed

The unit is planned backward from research outcomes [@ubd_whitepaper]: each lesson moves from a motivating failure to a precise statement, a proof or proof sketch, computation, and practice [@merrill2002], with a review question in every check for spaced retrieval [@dunlosky2013]. Animations are made with Manim Community Edition [@manim_ce] from the same numbers the text states, and every lesson offers several ways to engage and to show understanding [@udl]. The quantum learning content follows the primary literature on variational algorithms and gradients [@vqa; @mitarai; @schuld], kernels and the power of data [@kernels; @advantage], and trainability [@plateaus; @noise]; the causal content follows Pearl and Bareinboim [@pearlcausality; @bareinboim] and process-based quantum causal modelling [@costa]. Claims of quantum advantage are always paired with resource accounting and classical baselines.

**Ways to adapt it.**

- Every derivation appears three ways: as an animation with a full text description, as a theorem with proof, and as runnable code.
- Interactive figures let learners vary one parameter at a time, and each comes with a written description of what changes.
- Learners can show mastery through proofs, code, written referee reports or an oral presentation of the project.
- Exercises are tiered core, stretch and challenge, so a seminar can assign different depths to different participants.
:::

```{include} ../../media/_level-7.md
```
