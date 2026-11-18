---
title: "Level 6 · Quantum causal models"
short_title: "Level 6 · Quantum causal models"
subtitle: "Graduate study and research entry"
---

(level-6)=

:::{div}
:class: qcai-level-hero qcai-level-6
![Level 6 icon](../../_static/icons/qicon-level-6.svg) **Graduate**: Graduate study and research entry

**The central question:** What does it mean for one quantum system to cause another, and which causal claims can quantum experiments test?

Learners start from Bell's theorem read as a statement about one causal graph, then build the tools that quantum causal models need: Choi operators with explicit conventions, process operators, and a Markov condition made of commuting channel operators. They learn which classical results survive (Markovianity is equivalent to an underlying unitary circuit, and d-separation stays sound and complete for a quantum notion of independence) and which do not (screening off by a classical common cause, reading absent arrows off zero correlations). The second half covers interventions at quantum nodes, causal discovery and its limits, Bell and causal inequalities, process matrices without a fixed order, the quantum switch, and counterfactual questions, and ends with the design of a quantum causal experiment with stated assumptions.
:::

## At a glance

| | |
|---|---|
| Who it is for | Graduate students and advanced undergraduates who have completed Levels 4 and 5 or have equivalent background: structural causal models and d-separation, density operators, channels in Kraus form, and the CHSH test. It suits a graduate seminar, a reading course, or independent study before research in quantum foundations, quantum information or causal inference. |
| Prerequisites | Comfort with linear algebra over complex numbers (tensor products, partial traces, spectral decompositions), the density-operator and channel formalism of Level 5, and the causal graphs and identification ideas of Level 4. |
| Lessons | 10 lessons of about 120 minutes, plus a 4-session capstone |
| Pace | One lesson a week with a problem session fits a semester alongside the project. Each lesson splits into a reading and animation session, a proof and computation session, and an exercise session. |

## How each lesson is built

1. Before the session: watch the animations and read the definitions; write down one claim you doubt.
2. Open with the motivating puzzle and the check question that reviews an earlier lesson.
3. Work through the theorems and proofs at the board; state every convention (factor order, normalization, transposes).
4. Run the code cells, change one parameter, and predict the output before running it again.
5. Solve the core and stretch exercises in pairs; attempt one challenge exercise alone.
6. Close with the caution section: what the lesson does not show and which assumptions it used.

## Learning outcomes

| | By the end you can... | Practised in |
|---|---|---|
| O1 | I can derive the CHSH bound from the Bell causal graph, name the assumption behind each step, and explain how a quantum common cause exceeds it without signalling. | [L6-01](#lesson-l6-01), [L6-06](#lesson-l6-06) |
| O2 | I can build Choi operators in a stated convention, test complete positivity and trace preservation, and compose channels with the link product. | [L6-02](#lesson-l6-02), [L6-07](#lesson-l6-07) |
| O3 | I can write the process operator of a quantum causal model, check the commutation conditions, and say which d-separation statements hold and in which sense. | [L6-03](#lesson-l6-03), capstone |
| O4 | I can model an intervention at a quantum node as an instrument and compute its effect on downstream predictions. | [L6-04](#lesson-l6-04), [L6-09](#lesson-l6-09) |
| O5 | I can explain what interventional and observational data can and cannot reveal about quantum causal structure. | [L6-05](#lesson-l6-05), capstone |
| O6 | I can state the validity conditions of a process matrix and distinguish Bell inequalities from causal inequalities. | [L6-06](#lesson-l6-06), [L6-07](#lesson-l6-07) |
| O7 | I can describe the quantum switch as a process and evaluate a claimed advantage with explicit resource accounting. | [L6-08](#lesson-l6-08) |
| O8 | I can design a quantum causal experiment that states its hypotheses, conventions, assumptions and the data that would refute it. | [L6-10](#lesson-l6-10), capstone |

## Lessons

| Lesson | Big idea | Worked example |
|---|---|---|
| [L6-01 · Quantum common causes](#lesson-l6-01) | Bell correlations rule out a classical complete common cause under stated causal assumptions, but they are explained by a quantum common cause: the channel from the source factorizes as $\rho_{AB|C} = \rho_{A|C}\,\rho_{B|C}$ while the shared state is entangled. | A Werner source at the edge of violation |
| [L6-02 · Channels in the Choi representation](#lesson-l6-02) | Feeding half of a maximally entangled pair through a channel stores the whole channel in one operator $J$: complete positivity becomes $J \succeq 0$, trace preservation becomes $\operatorname{Tr}_{\mathrm{out}} J = I$, and every output is a partial trace with a transpose. | Recovering an amplitude-damped $|{+i}\rangle$ |
| [L6-03 · Quantum DAGs and Markov assumptions](#lesson-l6-03) | In a quantum causal model each node is a place to intervene, each node's parents feed it through a channel, and the process operator is a product of those channels that must commute where they share a parent; with these definitions Markovianity is equivalent to an underlying unitary circuit, and d-separation stays sound and complete for a quantum notion of independence. | Composing a dephasing and a depolarizing step |
| [L6-04 · Operational interventions](#lesson-l6-04) | In a quantum process there is no passive look: every operation at a node is an instrument, and an input-independent replacement is the operation that cuts the incoming arrow the way Pearl's do does. | The sign of the bias depends on the basis |
| [L6-05 · Discovery and informational access](#lesson-l6-05) | What can be discovered depends on the operations available: classical observation of two variables never separates a common cause from a direct cause, quantum passive observation sometimes does because a common cause flips the sign of one correlation, and Bell correlations show that faithful classical causal models are impossible. | Classifying a measured triple |
| [L6-06 · Bell inequalities and causal inequalities](#lesson-l6-06) | A Bell inequality tests whether correlations between two separated wings fit a classical common cause; a causal inequality tests whether correlations between two laboratories fit any definite causal order; different null models give different certificates. | Reading two reported numbers |
| [L6-07 · Process matrices and validity](#lesson-l6-07) | A process matrix is whatever assigns probabilities to every choice of local quantum operations; demanding that those probabilities be non-negative and sum to 1 for every local choice gives W ≥ 0 plus linear constraints, and those constraints still allow processes with no definite causal order. | Is a wire from Alice to Bob a valid process? |
| [L6-08 · The quantum switch](#lesson-l6-08) | A control qubit in superposition routes a target through U_A then U_B and through U_B then U_A at once; interference between the two orders writes the commutation relation into the control, which no classical mixture of orders can do, but certifying indefinite causal order still needs a witness built on trusted operations. | Two Pauli gates and one input |
| [L6-09 · Quantum counterfactual questions](#lesson-l6-09) | A channel fixes every interventional prediction but not the counterfactual: a counterfactual also needs a dilation, a rule for updating the background on the facts, and a decision about what to hold fixed, and in quantum theory even a fixed dilation leaves the update rule open. | The two-branch dilation at a quarter turn |
| [L6-10 · Design a quantum causal experiment](#lesson-l6-10) | A causal experiment is designed backwards from what each hypothesis forbids: find a statistic whose allowed ranges differ, size the run so that sampling error cannot fake a violation, add controls for every assumption the ranges rely on, and report an overlap as a non-result. | Sizing a run for a weaker alternative |

## Capstone: A quantum causal model, end to end

Over four sessions, the learner chooses a small quantum causal hypothesis, writes it as a quantum causal model in a stated convention, verifies it numerically, compares it with a rival hypothesis, and proposes an experiment with explicit assumptions.

**Choose a question, or propose your own:**

- Can a fixed set of local measurements distinguish a shared entangled state from a channel between two qubits, and where do the two hypotheses predict the same data?
- A qubit passes through two noisy steps. When does the process factorize as a chain, and what signature would reveal an environment that keeps a memory between the steps?
- In a three-node network with one shared parent, which conditional independences does the graph force, and which interventions would expose a hidden influence that the data alone conceal?

**Milestones:**

1. State the question, the competing causal hypotheses as DAGs, and the formalism (Allen et al. or Barrett et al., or another with a reason).
2. Fix and write down the conventions: Choi factor order, normalization, and where transposes enter.
3. Build the process operators for each hypothesis and verify normalization, positivity and the Markov commutation conditions in code.
4. Compute predictions for at least two choices of interventions, including one that separates the hypotheses if any does.
5. Check the graph-implied independences with d-separation and say in which sense (quantum node, observed classical node, or setting and outcome) each holds.
6. Write the report: claim, model, conventions, computations, assumptions (including faithfulness), what would refute the claim, and what the simulation does not show.

**Assessment rubric.**

| Criterion | Developing | Proficient | Advanced |
|---|---|---|---|
| Model statement | I drew a graph for my scenario. | I wrote the process operators for each hypothesis in a stated convention. | I can justify the formalism and explain how the same experiment would be drawn in another one. |
| Verification | I ran code that produces numbers. | My code checks normalization, positivity and commutation and matches direct simulation. | I can show which check would fail for a wrong convention and why. |
| Causal reasoning | I listed independences I observed. | I derived the independences the graph forces and the interventions that separate the hypotheses. | I can say which conclusions need faithfulness and give an example where it fails. |
| Report and limits | I stated a conclusion. | I stated assumptions, conventions and what would refute the claim. | I can separate what the simulation shows from what an experiment would need, including resources and noise. |

## Tools

- Python 3 with numpy, scipy, matplotlib, plotly and networkx (the course package qcai provides the shared helpers)
- The course labs on Bell tests, noise channels and quantum causal inference (Colab or Binder)
- A notebook for proofs and conventions; a shared document for the project report
- Access to the cited papers (all have open preprints)

## How progress is assessed

Each lesson has three or four check questions (one reviews an earlier lesson) and graded exercises at core, stretch and challenge level with complete solutions. Proof exercises are assessed for correct use of conventions. The project is a written and computational report judged with a four-part rubric.

## Core readings

- [@allen]: Quantum common causes and the quantum Reichenbach principle; the foundation for L6-01 and L6-03.
- [@barrett]: Quantum causal models from unitary circuits, quantum d-separation and do-calculus rules.
- [@watrous]: Rigorous treatment of channels and the Choi representation.
- [@chiribella]: Quantum networks and combs built with the link product.
- [@costa]: A process-based formulation of quantum causal modelling.
- [@ocb]: Process matrices and correlations with no definite causal order.
- [@pienaar]: A graph-separation rule for quantum networks without the common-cause factorization.
- [@ried2015]: An experiment showing a quantum advantage in inferring causal structure.

:::{dropdown} For instructors: how this level is designed

The unit was planned backward from its outcomes [@ubd_whitepaper], and each lesson moves from a puzzle and an animation, to definitions and theorems with proofs, to computation and practice [@merrill2002], with a review question in every check [@dunlosky2013]. Animations are made with Manim Community Edition [@manim_ce] from the same numbers as the text. The causal content follows the quantum causal model frameworks of Allen et al. and Barrett, Lorenz and Oreshkov [@allen; @barrett], compared with process-based and network approaches [@costa; @chiribella; @pienaar; @hlp2014], and the channel calculus follows Watrous [@watrous]. Conventions are stated in every lesson, because results in this field change with factor orders and transposes.

**Ways to adapt it.**

- Every animation has a full text description, and every interactive figure has a written summary of what it shows.
- Results are presented three ways where possible: a picture, a theorem with proof, and code that checks it numerically.
- Exercises come at three levels; learners may answer proof questions with a numerical counterexample search first and a proof second.
- Learners can present the project as a written report, a notebook, or a short talk with slides.
:::

```{include} ../../media/_level-6.md
```
