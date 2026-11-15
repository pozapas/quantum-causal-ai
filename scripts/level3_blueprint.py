"""Unit `level3-blueprint`: write the Level 3 unit syllabus into ../src/data/level3.json.  Run from book/.

Advanced tier.  Lessons are written as drafts in _data/level3_drafts/ and merged by merge_level.py; this
script replaces only the title, audience, intro and unit block, never the lessons.
"""
import json
import pathlib

BOOK = pathlib.Path(__file__).resolve().parents[1]
SRC = BOOK.parent / "src" / "data" / "level3.json"
d = json.loads(SRC.read_text(encoding="utf-8"))

d["title"] = "Mathematical tools for models"
d["audience"] = "High school to early college bridge: learners comfortable with algebra, functions and basic probability"
d["intro"] = ("Build the mathematics that causal and quantum models are written in: complex numbers and phase, vectors and "
              "inner products, matrices, tensor products and eigenvectors, derivatives and gradients, expectation, entropy, "
              "optimization, and estimation from data. Each idea is shown moving, stated carefully, proved where the proof is "
              "short, and checked in code. A correct calculation does not by itself show that a model describes a real system.")
d["unit"] = {
    "tier": "advanced",
    "big_question": ("Which pieces of mathematics does a model of the world need, and how do we know that a calculation "
                     "means what we claim it means?"),
    "summary": ("Learners build ten tools that every later level relies on. Complex numbers carry phase, so contributions can "
                "cancel. Vectors, inner products and matrices describe states and transformations, tensor products describe "
                "joint systems, and eigenvectors connect matrices to measurement results. Derivatives and gradients measure "
                "local change and drive optimization. Expectation, variance and entropy summarize uncertainty, and estimation "
                "with confidence intervals and corrected tests says how much a finite sample can tell us. Every lesson pairs "
                "an animation and an interactive explorer with definitions, short proofs, worked numbers and runnable Python."),
    "for_whom": ("Students at the end of high school or the start of college who can solve equations, work with functions and "
                 "graphs, and compute simple probabilities (Level 2 or equivalent). Self-learners can work alone; instructors "
                 "can use the instructor notes, the check questions and the project rubric for a course module."),
    "prerequisites": ("Comfort with algebra, functions and their graphs, and probabilities from two-way tables, as in Level 2; "
                      "no calculus or linear algebra is assumed beyond what the lessons build."),
    "time": {"lessons": 10, "minutes_per_lesson": 90, "project_sessions": 3,
             "pace": ("About two lessons a week for five to six weeks, plus three project sessions. Each lesson splits into "
                      "two sittings: motivation, animations and definitions first; proofs, code, exercises and checks second.")},
    "session_flow": [
        "Retrieve: answer the review question from an earlier lesson without notes.",
        "See it: read the motivating puzzle and watch the animations before any formula.",
        "State it: work through the definitions, theorems and proofs, and redo each worked number by hand.",
        "Explore and compute: use the interactive explorer, then run and modify the Python cells.",
        "Practice: solve core, stretch and challenge exercises, then answer the check questions before opening the explanations.",
        "Reflect: read the caution box and write one sentence on what the lesson's mathematics does not show.",
    ],
    "outcomes": [
        {"id": "O1", "text": "Compute with complex numbers in Cartesian and polar form and explain how relative phase makes contributions add or cancel.", "lessons": ["L3-01"]},
        {"id": "O2", "text": "Normalize vectors, compute inner products and overlaps, and apply matrices as transformations, testing whether they preserve length.", "lessons": ["L3-02", "L3-03"]},
        {"id": "O3", "text": "Build joint vectors with tensor products and distinguish product states from correlated states.", "lessons": ["L3-04"]},
        {"id": "O4", "text": "Find eigenvalues and eigenvectors of small matrices and connect them to possible measurement results.", "lessons": ["L3-05"]},
        {"id": "O5", "text": "Compute derivatives and gradients, run gradient descent with a stable step size, and judge a fitted model on held-out data.", "lessons": ["L3-06", "L3-09", "PROJECT"]},
        {"id": "O6", "text": "Compute expectation, variance and entropy of a distribution, and distinguish the average from any single outcome.", "lessons": ["L3-07", "L3-08"]},
        {"id": "O7", "text": "Estimate a probability with a standard error and confidence interval, interpret its coverage, and correct for repeated tests.", "lessons": ["L3-10", "PROJECT"]},
        {"id": "O8", "text": "Report a quantitative result with its assumptions, uncertainty and limits, and check it numerically.", "lessons": ["PROJECT"]},
    ],
    "evidence": ("Each lesson has three or four check questions (one reviews an earlier lesson), exercises with complete "
                 "solutions at three levels, and runnable code whose output can be compared with hand calculations. The unit "
                 "ends with a project: a short technical report and notebook judged with a four-part rubric."),
    "materials": [
        "Python 3 with numpy, scipy, matplotlib and plotly (in the browser through Colab or Binder, or installed locally)",
        "Paper, pencil and a scientific calculator for hand derivations",
        "A web browser for the animations and interactive explorers",
        "Optional: graph paper for sketching vectors, contour maps and loss curves",
    ],
    "project": {
        "title": "Measure, fit, and report: a small model from end to end",
        "summary": ("Over three sessions the learner simulates or collects repeated measurements of a two-outcome process, "
                    "fits a one-parameter model by gradient descent, quantifies the uncertainty of the estimate, and writes a "
                    "short report that states what the analysis shows and what it does not."),
        "questions": [
            "A simulated qubit is prepared as cos(t)|0> + sin(t)|1> and measured many times. How well can the angle t be recovered from 200, 800 and 3200 shots?",
            "A coin-like device may be biased. How many trials are needed to estimate its bias within 0.05, and does a test of fairness agree with the interval?",
            "A noisy sensor's readings follow a line through the origin. How does the fitted slope change with the step size and number of descent steps, and how uncertain is it?",
        ],
        "steps": [
            "State the question, the model, its parameter, and the assumptions (independence, constant probability, noise model).",
            "Generate or collect the data with a fixed random seed or a documented procedure, and keep a held-out portion.",
            "Write the loss, derive its gradient by hand, and fit the parameter by gradient descent; justify the step size.",
            "Compute the estimate's standard error and a 95% confidence interval, and check its coverage by repeated simulation.",
            "Compute the entropy of the fitted outcome distribution and explain what it says about predictability.",
            "Write a two-page report with figures: result, uncertainty, assumptions, a check that failed or surprised you, and limits.",
        ],
        "rubric": [
            {"part": "Model and assumptions", "start": "I named a model and its parameter.",
             "got": "I stated the model, its parameter and every assumption the analysis uses.",
             "explain": "I can say which result would change, and how, if each assumption failed."},
            {"part": "Derivation and fitting", "start": "I ran gradient descent with code I was given.",
             "got": "I derived the gradient by hand, chose a stable step size and showed the loss decreasing.",
             "explain": "I can predict the largest stable step size from the curvature and confirm it numerically."},
            {"part": "Uncertainty", "start": "I reported an estimate.",
             "got": "I reported a standard error and a correctly interpreted 95% interval.",
             "explain": "I checked the interval's coverage by simulation and explained any shortfall."},
            {"part": "Report and limits", "start": "I stated a conclusion.",
             "got": "I separated what the data show from what I assumed, with figures and numbers that match the code.",
             "explain": "I can explain why a good fit or a small p-value would not, by itself, establish a causal or physical claim."},
        ],
    },
    "udl": [
        "Every animation has a full text description, and every interactive has a written summary of what it shows.",
        "Each idea appears as a picture, a formula, a worked number and runnable code, so learners can enter through the form that suits them.",
        "Exercises come at three levels with complete solutions; learners can show mastery through a derivation, a computation, or an explained figure.",
        "Instructor notes suggest live activities (twenty questions, class-wide interval collection) and ways to extend or shorten each lesson.",
    ],
    "readings": [
        {"key": "openstax_polar", "note": "Polar form of complex numbers and De Moivre's theorem (L3-01)."},
        {"key": "openstax_matrices", "note": "Matrix operations with many worked examples (L3-03)."},
        {"key": "mml", "note": "Linear algebra, vector calculus, probability and optimization for machine learning (L3-02 to L3-10)."},
        {"key": "openstax_derivative", "note": "The derivative as a limit and as a rate of change (L3-06, L3-09)."},
        {"key": "openstax_expected", "note": "Expected value and standard deviation of discrete distributions (L3-07, L3-10)."},
        {"key": "coverthomas", "note": "Entropy, relative entropy and the source coding theorem, chapters 2 and 5 (L3-08)."},
        {"key": "openstax_ci", "note": "Confidence intervals and their interpretation (L3-10)."},
        {"key": "nielsenchuang", "note": "Chapter 2 reviews the linear algebra used from Level 5 on."},
    ],
    "approach": ("The unit is planned backward from its outcomes [@ubd_whitepaper]. Each lesson follows the cycle of activation, "
                 "demonstration, application and integration [@merrill2002]: a puzzle or failure first, then a moving picture, "
                 "then a careful statement with a proof, then computation and practice, with retrieval questions spaced across "
                 "lessons [@dunlosky2013]. The animations are made with Manim Community Edition [@manim_ce] from the same "
                 "numbers as the text, and every figure and code cell is reproducible. The mathematics follows standard open "
                 "references [@openstax_polar; @openstax_matrices; @openstax_derivative; @openstax_expected; @openstax_ci], "
                 "with linear algebra, calculus and optimization as in Mathematics for Machine Learning [@mml], information "
                 "theory as in Cover and Thomas [@coverthomas], and conventions chosen to match the quantum information "
                 "levels that follow [@nielsenchuang]."),
}
SRC.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Level 3 unit written to", SRC)
