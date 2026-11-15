---
title: "Level 3 · Mathematical tools for models"
short_title: "Level 3 · Mathematical tools for models"
subtitle: "High school to early college bridge: learners comfortable with algebra, functions and basic probability"
---

(level-3)=

:::{div}
:class: qcai-level-hero qcai-level-3
![Level 3 icon](../../_static/icons/qicon-level-3.svg) **High-school bridge**: High school to early college bridge: learners comfortable with algebra, functions and basic probability

**The central question:** Which pieces of mathematics does a model of the world need, and how do we know that a calculation means what we claim it means?

Learners build ten tools that every later level relies on. Complex numbers carry phase, so contributions can cancel. Vectors, inner products and matrices describe states and transformations, tensor products describe joint systems, and eigenvectors connect matrices to measurement results. Derivatives and gradients measure local change and drive optimization. Expectation, variance and entropy summarize uncertainty, and estimation with confidence intervals and corrected tests says how much a finite sample can tell us. Every lesson pairs an animation and an interactive explorer with definitions, short proofs, worked numbers and runnable Python.
:::

## At a glance

| | |
|---|---|
| Who it is for | Students at the end of high school or the start of college who can solve equations, work with functions and graphs, and compute simple probabilities (Level 2 or equivalent). Self-learners can work alone; instructors can use the instructor notes, the check questions and the project rubric for a course module. |
| Prerequisites | Comfort with algebra, functions and their graphs, and probabilities from two-way tables, as in Level 2; no calculus or linear algebra is assumed beyond what the lessons build. |
| Lessons | 10 lessons of about 90 minutes, plus a 3-session capstone |
| Pace | About two lessons a week for five to six weeks, plus three project sessions. Each lesson splits into two sittings: motivation, animations and definitions first; proofs, code, exercises and checks second. |

## How each lesson is built

1. Retrieve: answer the review question from an earlier lesson without notes.
2. See it: read the motivating puzzle and watch the animations before any formula.
3. State it: work through the definitions, theorems and proofs, and redo each worked number by hand.
4. Explore and compute: use the interactive explorer, then run and modify the Python cells.
5. Practice: solve core, stretch and challenge exercises, then answer the check questions before opening the explanations.
6. Reflect: read the caution box and write one sentence on what the lesson's mathematics does not show.

## Learning outcomes

| | By the end you can... | Practised in |
|---|---|---|
| O1 | Compute with complex numbers in Cartesian and polar form and explain how relative phase makes contributions add or cancel. | [L3-01](#lesson-l3-01) |
| O2 | Normalize vectors, compute inner products and overlaps, and apply matrices as transformations, testing whether they preserve length. | [L3-02](#lesson-l3-02), [L3-03](#lesson-l3-03) |
| O3 | Build joint vectors with tensor products and distinguish product states from correlated states. | [L3-04](#lesson-l3-04) |
| O4 | Find eigenvalues and eigenvectors of small matrices and connect them to possible measurement results. | [L3-05](#lesson-l3-05) |
| O5 | Compute derivatives and gradients, run gradient descent with a stable step size, and judge a fitted model on held-out data. | [L3-06](#lesson-l3-06), [L3-09](#lesson-l3-09), capstone |
| O6 | Compute expectation, variance and entropy of a distribution, and distinguish the average from any single outcome. | [L3-07](#lesson-l3-07), [L3-08](#lesson-l3-08) |
| O7 | Estimate a probability with a standard error and confidence interval, interpret its coverage, and correct for repeated tests. | [L3-10](#lesson-l3-10), capstone |
| O8 | Report a quantitative result with its assumptions, uncertainty and limits, and check it numerically. | capstone |

## Lessons

| Lesson | Big idea | Media |
|---|---|---|
| [L3-01 · Complex numbers and phase](#lesson-l3-01) | A complex number is an arrow with a length and an angle; multiplying arrows multiplies lengths and adds angles, and that is why phase can make quantities cancel. | 2 animations, interactive, 1 figures, code |
| [L3-02 · Vectors and inner products](#lesson-l3-02) | The inner product measures how much of one vector lies along another: for a unit vector it is the signed length of a shadow, it never exceeds the product of the lengths, and for complex entries it needs a conjugate so that every nonzero vector has positive length. | 3 animations, interactive, 1 figures, code |
| [L3-03 · Matrices as transformations](#lesson-l3-03) | A matrix is a recipe for moving the whole plane: its columns say where the basis vectors go, the determinant says how areas scale, and the unitary matrices are exactly the moves that keep every length and every inner product. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L3-04 · Tensor products and joint systems](#lesson-l3-04) | Joint systems multiply: a 2-outcome system and a 3-outcome system have 2 x 3 = 6 joint outcomes, a product vector fills that grid with products of entries, and a joint vector whose grid does not have rank 1 cannot be split into two separate parts. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L3-05 · Eigenvectors and observables](#lesson-l3-05) | An eigenvector is a direction a matrix only stretches; for a Hermitian matrix these directions are perpendicular, the matrix is a weighted sum of projections onto them, and the weights are the only values a measurement can return. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L3-06 · Derivatives and gradients](#lesson-l3-06) | Zoom in far enough on a smooth function and it looks linear; the derivative, and in several variables the gradient, is the slope of that linear picture, and the gradient points straight uphill across the level curves. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L3-07 · Expectation and variance](#lesson-l3-07) | The expectation is the balance point of a distribution and the variance is its average squared distance from that point; averaging n independent draws keeps the balance point and divides the variance by n. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L3-08 · Entropy and uncertainty](#lesson-l3-08) | Entropy is the average surprise of a random outcome, measured in bits: it is a property of the whole distribution, not of the outcome you happen to see, and it counts how many yes/no questions you need on average. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L3-09 · Optimization and learning](#lesson-l3-09) | Learning means walking downhill on a loss surface, one gradient step at a time; the step size decides whether the walk converges, and only data the model has not seen can tell whether the bottom it found is any good. | 3 animations, interactive, 1 figures, 1 diagrams, code |
| [L3-10 · Estimation, intervals, and repeated tests](#lesson-l3-10) | An estimate is one draw from a sampling distribution whose spread shrinks like $1/\sqrt{n}$; a 95% interval is a recipe that captures the truth in about 95% of repetitions, and running many tests guarantees some false alarms unless the threshold is adjusted. | 3 animations, interactive, 1 figures, code |

## Capstone: Measure, fit, and report: a small model from end to end

Over three sessions the learner simulates or collects repeated measurements of a two-outcome process, fits a one-parameter model by gradient descent, quantifies the uncertainty of the estimate, and writes a short report that states what the analysis shows and what it does not.

**Choose a question, or propose your own:**

- A simulated qubit is prepared as cos(t)|0> + sin(t)|1> and measured many times. How well can the angle t be recovered from 200, 800 and 3200 shots?
- A coin-like device may be biased. How many trials are needed to estimate its bias within 0.05, and does a test of fairness agree with the interval?
- A noisy sensor's readings follow a line through the origin. How does the fitted slope change with the step size and number of descent steps, and how uncertain is it?

**Milestones:**

1. State the question, the model, its parameter, and the assumptions (independence, constant probability, noise model).
2. Generate or collect the data with a fixed random seed or a documented procedure, and keep a held-out portion.
3. Write the loss, derive its gradient by hand, and fit the parameter by gradient descent; justify the step size.
4. Compute the estimate's standard error and a 95% confidence interval, and check its coverage by repeated simulation.
5. Compute the entropy of the fitted outcome distribution and explain what it says about predictability.
6. Write a two-page report with figures: result, uncertainty, assumptions, a check that failed or surprised you, and limits.

**Assessment rubric.**

| Criterion | Developing | Proficient | Advanced |
|---|---|---|---|
| Model and assumptions | I named a model and its parameter. | I stated the model, its parameter and every assumption the analysis uses. | I can say which result would change, and how, if each assumption failed. |
| Derivation and fitting | I ran gradient descent with code I was given. | I derived the gradient by hand, chose a stable step size and showed the loss decreasing. | I can predict the largest stable step size from the curvature and confirm it numerically. |
| Uncertainty | I reported an estimate. | I reported a standard error and a correctly interpreted 95% interval. | I checked the interval's coverage by simulation and explained any shortfall. |
| Report and limits | I stated a conclusion. | I separated what the data show from what I assumed, with figures and numbers that match the code. | I can explain why a good fit or a small p-value would not, by itself, establish a causal or physical claim. |

## Tools

- Python 3 with numpy, scipy, matplotlib and plotly (in the browser through Colab or Binder, or installed locally)
- Paper, pencil and a scientific calculator for hand derivations
- A web browser for the animations and interactive explorers
- Optional: graph paper for sketching vectors, contour maps and loss curves

## How progress is assessed

Each lesson has three or four check questions (one reviews an earlier lesson), exercises with complete solutions at three levels, and runnable code whose output can be compared with hand calculations. The unit ends with a project: a short technical report and notebook judged with a four-part rubric.

## Core readings

- [@openstax_polar]: Polar form of complex numbers and De Moivre's theorem (L3-01).
- [@openstax_matrices]: Matrix operations with many worked examples (L3-03).
- [@mml]: Linear algebra, vector calculus, probability and optimization for machine learning (L3-02 to L3-10).
- [@openstax_derivative]: The derivative as a limit and as a rate of change (L3-06, L3-09).
- [@openstax_expected]: Expected value and standard deviation of discrete distributions (L3-07, L3-10).
- [@coverthomas]: Entropy, relative entropy and the source coding theorem, chapters 2 and 5 (L3-08).
- [@openstax_ci]: Confidence intervals and their interpretation (L3-10).
- [@nielsenchuang]: Chapter 2 reviews the linear algebra used from Level 5 on.

:::{dropdown} For instructors: how this level is designed

The unit is planned backward from its outcomes [@ubd_whitepaper]. Each lesson follows the cycle of activation, demonstration, application and integration [@merrill2002]: a puzzle or failure first, then a moving picture, then a careful statement with a proof, then computation and practice, with retrieval questions spaced across lessons [@dunlosky2013]. The animations are made with Manim Community Edition [@manim_ce] from the same numbers as the text, and every figure and code cell is reproducible. The mathematics follows standard open references [@openstax_polar; @openstax_matrices; @openstax_derivative; @openstax_expected; @openstax_ci], with linear algebra, calculus and optimization as in Mathematics for Machine Learning [@mml], information theory as in Cover and Thomas [@coverthomas], and conventions chosen to match the quantum information levels that follow [@nielsenchuang].

**Ways to adapt it.**

- Every animation has a full text description, and every interactive has a written summary of what it shows.
- Each idea appears as a picture, a formula, a worked number and runnable code, so learners can enter through the form that suits them.
- Exercises come at three levels with complete solutions; learners can show mastery through a derivation, a computation, or an explained figure.
- Instructor notes suggest live activities (twenty questions, class-wide interval collection) and ways to extend or shorten each lesson.
:::

```{include} ../../media/_level-3.md
```
