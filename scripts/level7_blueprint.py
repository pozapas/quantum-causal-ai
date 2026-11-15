"""Unit `level7-blueprint`: write the Level 7 unit syllabus into ../src/data/level7.json.  Run from book/.

Only the title, audience, intro and the unit block are replaced; the lessons are left untouched.
Lessons are written as drafts in _data/level7_drafts/ and merged by merge_level.py.
"""
import json
import pathlib

BOOK = pathlib.Path(__file__).resolve().parents[1]
SRC = BOOK.parent / "src" / "data" / "level7.json"
d = json.loads(SRC.read_text(encoding="utf-8"))

d["title"] = "Quantum Causal AI research"
d["audience"] = "Doctoral and postdoctoral study"
d["intro"] = ("Define research tasks precisely, derive and price the gradients and kernels that quantum learning uses, "
              "prove identification before fitting, count every resource, and design reproducible benchmarks that "
              "separate prediction from causal recovery and from quantum advantage.")
d["unit"] = {
    "tier": "advanced",
    "big_question": ("When does a quantum learning method answer a causal question better than the alternatives, and what "
                     "evidence, identification argument and resource count would establish it?"),
    "summary": ("The unit treats Quantum Causal AI as a set of research questions, not a finished method. Learners first "
                "separate prediction, causal identification and quantum resource claims, then study the two workhorses of "
                "quantum learning, variational circuits with parameter-shift gradients and quantum kernels, with exact "
                "derivations and complete shot accounting. They analyze trainability and barren plateaus, prove "
                "identifiability before learning, and build resource ledgers that keep copies, queries, gates and time "
                "apart. Classical shadows show how observable structure controls estimation cost. The unit ends with "
                "reproducible benchmark design, a falsifiable research protocol with stopping rules, and a critical "
                "synthesis of open problems."),
    "for_whom": ("Doctoral students and postdoctoral researchers in physics, computer science, statistics or a quantitative "
                 "field who have completed Levels 4 to 6 or know structural causal models, density operators and channels, "
                 "and quantum causal models. Each lesson works as a seminar session, a reading-group module or self-study."),
    "prerequisites": ("Structural causal models and identification (Level 4), quantum states, channels and measurements "
                      "(Level 5), quantum causal models and process descriptions (Level 6), and fluency with linear "
                      "algebra, probability and Python with numpy."),
    "time": {"lessons": 10, "minutes_per_lesson": 120, "project_sessions": 4,
             "pace": ("One lesson a week with the project running alongside fits a twelve-week seminar: ten lesson weeks "
                      "and two project weeks. Each lesson splits into a derivation session (animations, theorems, "
                      "proofs) and a computation session (code, interactive figures, exercises).")},
    "session_flow": [
        "Before the session: read the motivation and attempt the review check from memory.",
        "Watch the animations and reconstruct each derivation on paper before reading the proof.",
        "Run the code blocks, change one parameter, and predict the output before running it again.",
        "Work the worked example, then one core, one stretch and one challenge exercise.",
        "Discuss: classify a recent paper's claims with the lesson's tools and write a short referee note.",
        "Instructors: use the teaching notes and the assessment suggestion at the end of each lesson.",
    ],
    "outcomes": [
        {"id": "O1", "text": "Specify a research task by its data access, target, model class, error criterion and budget, and separate prediction, causal and resource claims.", "lessons": ["L7-01", "PROJECT"]},
        {"id": "O2", "text": "Derive the parameter-shift rule from the spectrum of the generator and compare its bias, variance and circuit cost with finite differences under shot noise.", "lessons": ["L7-02"]},
        {"id": "O3", "text": "Evaluate a quantum kernel claim with its full cost: positive semidefiniteness, shots per Gram entry, concentration, and the geometric difference to classical kernels.", "lessons": ["L7-03", "PROJECT"]},
        {"id": "O4", "text": "Distinguish vanishing true gradients from noisy estimates and design a controlled trainability study across system sizes.", "lessons": ["L7-04"]},
        {"id": "O5", "text": "Prove or disprove identifiability of a target under a stated data map and model class before fitting a flexible model.", "lessons": ["L7-05", "PROJECT"]},
        {"id": "O6", "text": "Keep copies, queries, gates and wall-clock time apart in a resource ledger, and explain how observable structure controls classical-shadow cost.", "lessons": ["L7-06", "L7-07"]},
        {"id": "O7", "text": "Design a reproducible benchmark and a falsifiable protocol with stopping rules that separate prediction from causal recovery.", "lessons": ["L7-08", "L7-09", "PROJECT"]},
        {"id": "O8", "text": "Formulate an open research question with its evidence requirements, without presenting a proposal as a result.", "lessons": ["L7-10", "PROJECT"]},
    ],
    "evidence": ("Each lesson ends with four check questions, one reviewing an earlier lesson, and exercises at core, stretch "
                 "and challenge levels with complete solutions. Several challenge exercises are written as referee reports on "
                 "a described paper. The capstone is a pre-registered research protocol with a reproducible simulation study, "
                 "judged with a four-part rubric."),
    "materials": [
        "Python 3 with numpy, scipy, matplotlib and plotly (the course package qcai for the lab notebooks)",
        "A Jupyter environment (local, Colab or Binder) for the lessons' code and the labs",
        "Access to the cited papers (all have open arXiv versions)",
        "Optional: a quantum software framework such as PennyLane for comparison with the hand-written simulators",
        "Optional: access to a cloud quantum device, with its calibration data recorded",
    ],
    "project": {
        "title": "A pre-registered quantum causal learning study",
        "summary": ("Over four sessions the learner turns a research question into a specified task, proves or disproves "
                    "identification of its target, writes a protocol with resource budget and stopping rules, runs a "
                    "reproducible simulation study against strong classical baselines, and reports results with the limits "
                    "of what they show."),
        "questions": [
            "Can a variational or kernel model recover the effect of an intervention on a simulated quantum process better than a classical learner given the same measurement records, and what identifies that effect?",
            "For a family of feature maps, how does the geometric difference to tuned classical kernels scale with qubits, and at what shot budget do Gram matrix estimates stop being informative?",
            "Under a fixed shot budget, which gradient estimator and initialization strategy keeps a variational circuit trainable as it grows, and how would you tell a barren plateau from estimation noise?",
        ],
        "steps": [
            "Write the task specification: data access, target formula, model class, error criterion and resource budget.",
            "Prove identification of the target under the stated access, or construct two data-equivalent models that disprove it and revise the design.",
            "Pre-register the protocol: hypotheses, metrics, classical baselines, system sizes, seeds, shot budgets and stopping rules.",
            "Implement the simulation with fixed seeds, unit tests against closed forms, and a complete resource ledger.",
            "Run the study across sizes, report uncertainty for every metric, and compare with the tuned baselines.",
            "Write the report: claims matched to evidence, limits, and what result would have falsified the hypothesis.",
        ],
        "rubric": [
            {"part": "Task and identification", "start": "The task is described in words and the target is implicit.",
             "got": "The target is a formula, and identification is argued under stated assumptions.",
             "explain": "Identification is proved, or disproved by a constructed counterexample, and the design is adjusted accordingly."},
            {"part": "Resource accounting", "start": "Some costs are reported, such as circuit depth.",
             "got": "Shots, circuit settings, data loading and classical post-processing are counted.",
             "explain": "Costs are given as functions of size and accuracy, and the comparison fixes the access model for all methods."},
            {"part": "Baselines and statistics", "start": "One classical method is run with default settings.",
             "got": "Tuned classical baselines and uncertainty intervals are reported for every metric.",
             "explain": "Baselines are chosen to be the strongest available for the access model, and conclusions survive the uncertainty."},
            {"part": "Reproducibility and claims", "start": "Code runs, but seeds and settings are incomplete.",
             "got": "Seeds, versions, protocol and stopping rules are fixed in advance and reported.",
             "explain": "Every claim is matched to its evidence, limits are explicit, and a falsifying outcome is stated."},
        ],
    },
    "udl": [
        "Every derivation appears three ways: as an animation with a full text description, as a theorem with proof, and as runnable code.",
        "Interactive figures let learners vary one parameter at a time, and each comes with a written description of what changes.",
        "Learners can show mastery through proofs, code, written referee reports or an oral presentation of the project.",
        "Exercises are tiered core, stretch and challenge, so a seminar can assign different depths to different participants.",
    ],
    "readings": [
        {"key": "qml", "note": "A survey of quantum machine learning task classes and the access assumptions behind them."},
        {"key": "vqa", "note": "Review of variational quantum algorithms, their training and their limitations."},
        {"key": "schuld", "note": "Conditions under which parameter-shift rules give exact gradients on hardware."},
        {"key": "advantage", "note": "The power-of-data analysis: when classical learners with data match quantum models."},
        {"key": "plateaus", "note": "Gradient concentration in random parametrized circuits."},
        {"key": "costa", "note": "Process-based quantum causal modelling, the framework for causal questions about quantum systems."},
        {"key": "bareinboim", "note": "Causal AI from structural causal models through identification and learning."},
        {"key": "shadows", "note": "Classical shadows and how observable structure controls estimation cost."},
    ],
    "approach": ("The unit is planned backward from research outcomes [@ubd_whitepaper]: each lesson moves from a motivating "
                 "failure to a precise statement, a proof or proof sketch, computation, and practice [@merrill2002], with a "
                 "review question in every check for spaced retrieval [@dunlosky2013]. Animations are made with Manim "
                 "Community Edition [@manim_ce] from the same numbers the text states, and every lesson offers several ways "
                 "to engage and to show understanding [@udl]. The quantum learning content follows the primary literature on "
                 "variational algorithms and gradients [@vqa; @mitarai; @schuld], kernels and the power of data "
                 "[@kernels; @advantage], and trainability [@plateaus; @noise]; the causal content follows Pearl and "
                 "Bareinboim [@pearlcausality; @bareinboim] and process-based quantum causal modelling [@costa]. Claims of "
                 "quantum advantage are always paired with resource accounting and classical baselines."),
}
SRC.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Level 7 unit written to", SRC)
