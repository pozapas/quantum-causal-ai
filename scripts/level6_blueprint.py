"""Unit `level6-blueprint`: write the Level 6 unit syllabus into ../src/data/level6.json.  Run from book/.

Only the unit block and the title, audience and intro are replaced; the lessons are left untouched.
Lessons are written as drafts in _data/level6_drafts/ and merged by merge_level.py.
"""
import json
import pathlib

BOOK = pathlib.Path(__file__).resolve().parents[1]
SRC = BOOK.parent / "src" / "data" / "level6.json"
d = json.loads(SRC.read_text(encoding="utf-8"))

d["title"] = "Quantum causal models"
d["audience"] = "Graduate study and research entry"
d["intro"] = ("State causal hypotheses about quantum systems precisely. Represent channels and processes by Choi "
              "operators, read Bell's theorem as a test of a causal graph, define quantum causal models and their Markov "
              "condition, intervene at quantum nodes, and meet processes without a definite causal order.")
d["unit"] = {
    "tier": "advanced",
    "big_question": "What does it mean for one quantum system to cause another, and which causal claims can quantum experiments test?",
    "summary": ("Learners start from Bell's theorem read as a statement about one causal graph, then build the tools that "
                "quantum causal models need: Choi operators with explicit conventions, process operators, and a Markov "
                "condition made of commuting channel operators. They learn which classical results survive (Markovianity "
                "is equivalent to an underlying unitary circuit, and d-separation stays sound and complete for a quantum "
                "notion of independence) and which do not (screening off by a classical common cause, reading absent arrows "
                "off zero correlations). The second half covers interventions at quantum nodes, causal discovery and its "
                "limits, Bell and causal inequalities, process matrices without a fixed order, the quantum switch, and "
                "counterfactual questions, and ends with the design of a quantum causal experiment with stated assumptions."),
    "for_whom": ("Graduate students and advanced undergraduates who have completed Levels 4 and 5 or have equivalent "
                 "background: structural causal models and d-separation, density operators, channels in Kraus form, "
                 "and the CHSH test. It suits a graduate seminar, a reading course, or independent study before research "
                 "in quantum foundations, quantum information or causal inference."),
    "prerequisites": ("Comfort with linear algebra over complex numbers (tensor products, partial traces, spectral "
                      "decompositions), the density-operator and channel formalism of Level 5, and the causal graphs and "
                      "identification ideas of Level 4."),
    "time": {"lessons": 10, "minutes_per_lesson": 120, "project_sessions": 4,
             "pace": ("One lesson a week with a problem session fits a semester alongside the project. Each lesson splits "
                      "into a reading and animation session, a proof and computation session, and an exercise session.")},
    "session_flow": [
        "Before the session: watch the animations and read the definitions; write down one claim you doubt.",
        "Open with the motivating puzzle and the check question that reviews an earlier lesson.",
        "Work through the theorems and proofs at the board; state every convention (factor order, normalization, transposes).",
        "Run the code cells, change one parameter, and predict the output before running it again.",
        "Solve the core and stretch exercises in pairs; attempt one challenge exercise alone.",
        "Close with the caution section: what the lesson does not show and which assumptions it used.",
    ],
    "outcomes": [
        {"id": "O1", "text": "I can derive the CHSH bound from the Bell causal graph, name the assumption behind each step, and explain how a quantum common cause exceeds it without signalling.", "lessons": ["L6-01", "L6-06"]},
        {"id": "O2", "text": "I can build Choi operators in a stated convention, test complete positivity and trace preservation, and compose channels with the link product.", "lessons": ["L6-02", "L6-07"]},
        {"id": "O3", "text": "I can write the process operator of a quantum causal model, check the commutation conditions, and say which d-separation statements hold and in which sense.", "lessons": ["L6-03", "PROJECT"]},
        {"id": "O4", "text": "I can model an intervention at a quantum node as an instrument and compute its effect on downstream predictions.", "lessons": ["L6-04", "L6-09"]},
        {"id": "O5", "text": "I can explain what interventional and observational data can and cannot reveal about quantum causal structure.", "lessons": ["L6-05", "PROJECT"]},
        {"id": "O6", "text": "I can state the validity conditions of a process matrix and distinguish Bell inequalities from causal inequalities.", "lessons": ["L6-06", "L6-07"]},
        {"id": "O7", "text": "I can describe the quantum switch as a process and evaluate a claimed advantage with explicit resource accounting.", "lessons": ["L6-08"]},
        {"id": "O8", "text": "I can design a quantum causal experiment that states its hypotheses, conventions, assumptions and the data that would refute it.", "lessons": ["L6-10", "PROJECT"]},
    ],
    "evidence": ("Each lesson has three or four check questions (one reviews an earlier lesson) and graded exercises at core, stretch "
                 "and challenge level with complete solutions. Proof exercises are assessed for correct use of conventions. "
                 "The project is a written and computational report judged with a four-part rubric."),
    "materials": [
        "Python 3 with numpy, scipy, matplotlib, plotly and networkx (the course package qcai provides the shared helpers)",
        "The course labs on Bell tests, noise channels and quantum causal inference (Colab or Binder)",
        "A notebook for proofs and conventions; a shared document for the project report",
        "Access to the cited papers (all have open preprints)",
    ],
    "project": {
        "title": "A quantum causal model, end to end",
        "summary": ("Over four sessions, the learner chooses a small quantum causal hypothesis, writes it as a quantum causal "
                    "model in a stated convention, verifies it numerically, compares it with a rival hypothesis, and proposes "
                    "an experiment with explicit assumptions."),
        "questions": [
            "Can a fixed set of local measurements distinguish a shared entangled state from a channel between two qubits, and where do the two hypotheses predict the same data?",
            "A qubit passes through two noisy steps. When does the process factorize as a chain, and what signature would reveal an environment that keeps a memory between the steps?",
            "In a three-node network with one shared parent, which conditional independences does the graph force, and which interventions would expose a hidden influence that the data alone conceal?",
        ],
        "steps": [
            "State the question, the competing causal hypotheses as DAGs, and the formalism (Allen et al. or Barrett et al., or another with a reason).",
            "Fix and write down the conventions: Choi factor order, normalization, and where transposes enter.",
            "Build the process operators for each hypothesis and verify normalization, positivity and the Markov commutation conditions in code.",
            "Compute predictions for at least two choices of interventions, including one that separates the hypotheses if any does.",
            "Check the graph-implied independences with d-separation and say in which sense (quantum node, observed classical node, or setting and outcome) each holds.",
            "Write the report: claim, model, conventions, computations, assumptions (including faithfulness), what would refute the claim, and what the simulation does not show.",
        ],
        "rubric": [
            {"part": "Model statement", "start": "I drew a graph for my scenario.", "got": "I wrote the process operators for each hypothesis in a stated convention.", "explain": "I can justify the formalism and explain how the same experiment would be drawn in another one."},
            {"part": "Verification", "start": "I ran code that produces numbers.", "got": "My code checks normalization, positivity and commutation and matches direct simulation.", "explain": "I can show which check would fail for a wrong convention and why."},
            {"part": "Causal reasoning", "start": "I listed independences I observed.", "got": "I derived the independences the graph forces and the interventions that separate the hypotheses.", "explain": "I can say which conclusions need faithfulness and give an example where it fails."},
            {"part": "Report and limits", "start": "I stated a conclusion.", "got": "I stated assumptions, conventions and what would refute the claim.", "explain": "I can separate what the simulation shows from what an experiment would need, including resources and noise."},
        ],
    },
    "udl": [
        "Every animation has a full text description, and every interactive figure has a written summary of what it shows.",
        "Results are presented three ways where possible: a picture, a theorem with proof, and code that checks it numerically.",
        "Exercises come at three levels; learners may answer proof questions with a numerical counterexample search first and a proof second.",
        "Learners can present the project as a written report, a notebook, or a short talk with slides.",
    ],
    "readings": [
        {"key": "allen", "note": "Quantum common causes and the quantum Reichenbach principle; the foundation for L6-01 and L6-03."},
        {"key": "barrett", "note": "Quantum causal models from unitary circuits, quantum d-separation and do-calculus rules."},
        {"key": "watrous", "note": "Rigorous treatment of channels and the Choi representation."},
        {"key": "chiribella", "note": "Quantum networks and combs built with the link product."},
        {"key": "costa", "note": "A process-based formulation of quantum causal modelling."},
        {"key": "ocb", "note": "Process matrices and correlations with no definite causal order."},
        {"key": "pienaar", "note": "A graph-separation rule for quantum networks without the common-cause factorization."},
        {"key": "ried2015", "note": "An experiment showing a quantum advantage in inferring causal structure."},
    ],
    "approach": ("The unit was planned backward from its outcomes [@ubd_whitepaper], and each lesson moves from a puzzle and an "
                 "animation, to definitions and theorems with proofs, to computation and practice [@merrill2002], with a "
                 "review question in every check [@dunlosky2013]. Animations are made with Manim Community Edition "
                 "[@manim_ce] from the same numbers as the text. The causal content follows the quantum causal model "
                 "frameworks of Allen et al. and Barrett, Lorenz and Oreshkov [@allen; @barrett], compared with "
                 "process-based and network approaches [@costa; @chiribella; @pienaar; @hlp2014], and the channel "
                 "calculus follows Watrous [@watrous]. Conventions are stated in every lesson, because results in this "
                 "field change with factor orders and transposes."),
}
SRC.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Level 6 unit written to", SRC)
