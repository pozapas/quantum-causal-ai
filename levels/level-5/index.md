---
title: "Level 5 · Quantum information"
short_title: "Level 5 · Quantum information"
subtitle: "Advanced undergraduates in physics, computer science, mathematics or engineering"
---

(level-5)=

:::{div}
:class: qcai-level-hero qcai-level-5
![Level 5 icon](../../_static/icons/qicon-level-5.svg) **Advanced undergraduate**: Advanced undergraduates in physics, computer science, mathematics or engineering

**The central question:** What can be known about a quantum system from the outcomes of measurements on it, and which operations, correlations and kinds of noise does quantum theory allow?

Learners write qubit states in Dirac notation, turn amplitudes into probabilities with the Born rule, and picture states and gates on the Bloch sphere. They see relative phase become counts in an interferometer, build joint systems with tensor products and tell entanglement from classical correlation. Density operators, partial traces, Kraus operators and instruments then describe mixed states, noise and measurement in full generality. The unit closes with the CHSH test and its assumptions, entropy and state tomography, and a first quantum error-correcting code, separating a noise channel from the procedure that undoes it.
:::

## At a glance

| | |
|---|---|
| Who it is for | Advanced undergraduates, or beginning graduate students from other fields, who are comfortable with complex numbers, linear algebra over the complex numbers, basic probability and some Python, at the level of Levels 3 and 4 of this course. No previous course in quantum mechanics is assumed. |
| Prerequisites | Complex numbers, inner products, matrices, tensor products and eigenvectors (Level 3), probability, expectation and estimation (Level 3), and the causal vocabulary of Level 4 for the Bell lesson. |
| Lessons | 10 lessons of about 90 minutes, plus a 3-session capstone |
| Pace | About two lessons a week for six weeks, including the project. Each lesson splits into two sittings: intuition, animations and definitions first; proofs, code and exercises second. |

## How each lesson is built

1. Retrieve: answer the review check from an earlier lesson without notes.
2. See it: watch the animations and explore the interactive figure before reading the formal statements.
3. Prove it: read the definitions and theorems, and reconstruct one proof on paper.
4. Compute it: run and modify the code block, and confirm the numbers quoted in the text.
5. Practice: work the worked example, then at least one core, one stretch and one challenge exercise.
6. Reflect: answer the check questions and write two sentences on the lesson's caution and scope.

## Learning outcomes

| | By the end you can... | Practised in |
|---|---|---|
| O1 | Compute Born-rule probabilities for pure states in any stated orthonormal basis, place states on the Bloch sphere, and prove that global phases are unobservable. | [L5-01](#lesson-l5-01) |
| O2 | Translate a circuit into a matrix product in the correct order, describe single-qubit gates as Bloch rotations, and predict interference after a relative phase change. | [L5-02](#lesson-l5-02), [L5-03](#lesson-l5-03), capstone |
| O3 | Build joint states with tensor products and decide whether a pure two-qubit state is entangled. | [L5-04](#lesson-l5-04) |
| O4 | Work with density operators: purity, the Bloch ball, and reduced states from a partial trace. | [L5-05](#lesson-l5-05), capstone |
| O5 | Check that a map is a quantum channel from its Kraus operators, and separate outcome probabilities from post-measurement states with instruments. | [L5-06](#lesson-l5-06), [L5-07](#lesson-l5-07), capstone |
| O6 | Calculate a CHSH value, state the assumptions behind the classical bound, and account for statistical error in a claimed violation. | [L5-08](#lesson-l5-08), capstone |
| O7 | Reconstruct a qubit state from repeated measurements in several bases measure how mixed a state is with von Neumann entropy, and state the estimation error from finite shots. | [L5-09](#lesson-l5-09), capstone |
| O8 | Distinguish a noise channel from an error-correction procedure and compute when a simple code helps. | [L5-10](#lesson-l5-10), capstone |

## Lessons

| Lesson | Big idea | Worked example |
|---|---|---|
| [L5-01 · States and the Born rule](#lesson-l5-01) | A qubit state is a unit vector of complex amplitudes; the Born rule turns the amplitudes in a chosen basis into probabilities, and a global phase never changes any of them while a relative phase can. | One state, three bases |
| [L5-02 · Gates and circuit order](#lesson-l5-02) | Gates are unitary matrices, and on one qubit they are rotations of the Bloch sphere; a circuit applies them in time order, so its matrix is the product written in reverse, and because rotations do not commute, the order can change the result. | Hadamard, T, Hadamard |
| [L5-03 · Phase and interference](#lesson-l5-03) | A phase on one path is invisible on its own, but a second beam splitter adds the two path amplitudes, so the relative phase $\varphi$ becomes the count rate $\frac{1 + \cos\varphi}{2}$; information about which path was taken shrinks that fringe. | A phase of sixty degrees, with and without a marker |
| [L5-04 · Tensor products and entanglement](#lesson-l5-04) | A two-qubit pure state is a 2 x 2 matrix of amplitudes; it is a product state exactly when that matrix has rank one, and an entangled state shows correlations in several bases at once that no coin-flip mixture of product states can reproduce. | Schmidt form of a four-term state |
| [L5-05 · Density operators and reduced states](#lesson-l5-05) | A density operator stores exactly what every measurement on a system can reveal; many different preparations, including half of an entangled pair, share one density operator, and the partial trace is the rule that extracts a subsystem's density operator from the whole. | Reduced state of a three-term state |
| [L5-06 · Quantum channels and complete positivity](#lesson-l5-06) | Every physical process on a quantum system is a completely positive, trace-preserving map: a Kraus sum that comes from a unitary on the system and an environment followed by a partial trace; a map such as the transpose can send every state to a state and still be unphysical, because it fails once an entangled partner is included. | Amplitude damping on a superposition |
| [L5-07 · Measurements and instruments](#lesson-l5-07) | A measurement has two jobs: a POVM says how likely each record is, and an instrument says what state each record leaves for the next laboratory; equal probabilities never imply equal aftermaths. | A weak measurement of |+> with strength 0.6 |
| [L5-08 · Bell correlations and the CHSH test](#lesson-l5-08) | Every model in which outcomes depend only on local settings and a shared cause chosen independently of the settings obeys $|S| \le 2$; entangled qubits reach $2\sqrt{2}$ without allowing any signal, so a careful violation rules out that whole class of causal explanations. | A noisy source at the optimal angles |
| [L5-09 · Entropy and quantum tomography](#lesson-l5-09) | Mixedness is the Shannon entropy of a density operator's eigenvalues, and the density operator itself can only be estimated, never read off, by measuring many identical copies in enough different bases. | From counts to a physical state |
| [L5-10 · Noise, encoding, and error correction](#lesson-l5-10) | Noise is a channel that shrinks the Bloch ball; error correction is a different channel, built from encoding, parity measurements and conditional recovery, that undoes a chosen set of errors and turns a physical error rate $p$ into a logical rate of order $p^2$. | Logical error rate at p = 0.1 |

## Capstone: Characterizing a noisy qubit in simulation

Over three sessions, the learner plays experimentalist and theorist for a simulated device: prepares states, measures them with a finite number of shots, estimates a noise parameter from interference and tomography data, and decides, with error bars, whether a Bell test or an error-correcting code succeeds at that noise level.

**Choose a question, or propose your own:**

- A dephasing channel of unknown strength acts between the two Hadamards of an interferometer. How well can its strength be estimated from fringe visibility with 1000 shots per phase setting?
- A two-qubit Werner state has visibility v. For which v does the CHSH value exceed 2, and how many shots are needed before the violation is larger than three standard errors?
- Under independent bit flips with probability p, where is the break-even point at which the three-qubit repetition code starts to beat an unencoded qubit?

**Milestones:**

1. State the model precisely: states, gates, channel and measurement, with every convention written down.
2. Derive the ideal prediction on paper (fringe, CHSH value, or logical error rate) as a function of the noise parameter.
3. Write a seeded simulation that draws finite-shot counts from the Born rule, and check it against the derivation.
4. Estimate the noise parameter or the test statistic from the simulated counts, with a standard error.
5. Repeat across noise levels and plot estimate against truth with error bars.
6. Write a two-page report: claim, model, assumptions, results with uncertainty, and what a hardware run would add.

**Assessment rubric.**

| Criterion | Developing | Proficient | Advanced |
|---|---|---|---|
| Model and conventions | I described the experiment in words. | I wrote the states, gates, channel and measurement with their conventions. | I can say which conclusions would change under a different convention and which would not. |
| Derivation | I quoted a formula. | I derived the prediction and checked special cases. | I can prove the result and state the assumptions it needs. |
| Simulation and statistics | I ran a simulation. | My seeded simulation matches the derivation within the expected error. | I can justify the number of shots from a standard-error calculation. |
| Claims and limits | I stated a conclusion. | I reported estimates with error bars and listed the assumptions. | I can explain why a simulation is not an experiment and what loopholes or noise sources a real device adds. |

## Tools

- Python 3 with numpy, scipy, matplotlib and plotly (the course package qcai provides the quantum helpers)
- A browser for the interactive figures and the course notebooks (Colab or Binder work)
- Paper for derivations; a computer algebra system is optional
- Optional: free access to a cloud quantum computer to compare simulations with hardware counts

## How progress is assessed

Each lesson ends with three or four check questions, one of which reviews an earlier lesson, and graded exercises at core, stretch and challenge levels with full solutions. The project is a reproducible notebook and a short report, judged with a four-part rubric that rewards correct derivations, honest error bars and clearly stated assumptions.

## Core readings

- [@nielsenchuang]: Chapters 1, 2, 4, 8, 10 and 11 are the main reference for the whole unit.
- [@preskill]: Lecture notes with a physicist's view of measurement, decoherence, entanglement and error correction.
- [@watrous]: Rigorous treatment of states, channels, measurements and the Choi representation, used again in Level 6.
- [@ibm]: A free course that builds the same notation with runnable examples on simulators and hardware.
- [@feynman]: Volume III motivates amplitudes and interference from two-path experiments.
- [@chsh]: The original proposal of the CHSH inequality used in L5-08.
- [@nisq]: Context on what present-day noisy devices can and cannot do.

:::{dropdown} For instructors: how this level is designed

The unit is planned backward from its outcomes [@ubd_whitepaper]. Each lesson moves from a puzzle and a moving picture to formal definitions, theorems with proofs, computation and graded practice [@merrill2002], with a review question in every lesson to space retrieval [@dunlosky2013]. The animations are made with Manim Community Edition [@manim_ce] from the same numbers as the text, and every page offers several ways in, following Universal Design for Learning [@udl]. The mathematics follows Nielsen and Chuang and Watrous [@nielsenchuang; @watrous], with physical motivation from Preskill and Feynman [@preskill; @feynman] and hands-on examples in the style of IBM's course [@ibm]. Claims about devices are kept modest and tied to the noisy hardware that exists today [@nisq].

**Ways to adapt it.**

- Every animation has a full text description, and every interactive figure has a written summary of what it shows.
- Each idea appears as a picture, a formula, a proof and runnable code, so learners can enter through the form that suits them.
- Exercises are tiered (core, stretch, challenge); the project questions can be chosen to match interest and background.
- Learners may show mastery through derivations, annotated code, short recorded explanations, or written reports.
:::

```{include} ../../media/_level-5.md
```
