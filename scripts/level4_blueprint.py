"""Unit `level4-blueprint`: write the Level 4 unit syllabus into ../src/data/level4.json.  Run from book/.

Only the title, audience, intro and unit block are replaced; the lessons list is left untouched.
Lessons are written as drafts in _data/level4_drafts/ and merged by merge_level.py.
"""
import json
import pathlib

BOOK = pathlib.Path(__file__).resolve().parents[1]
SRC = BOOK.parent / "src" / "data" / "level4.json"
d = json.loads(SRC.read_text(encoding="utf-8"))

d["title"] = "Classical causal AI"
d["audience"] = "Undergraduates in statistics, computer science, data science, or physics who know basic probability and linear algebra"
d["intro"] = ("Define the effect of an action with structural causal models and the do-operator. Read independences off causal "
              "graphs, choose what to adjust for, and prove when an effect can be computed from observational data. Then meet "
              "potential outcomes, causal discovery, counterfactuals, and the extra assumptions behind causal machine learning, "
              "transport, and fairness, before Level 5 turns to quantum systems.")
d["unit"] = {
    "tier": "advanced",
    "big_question": ("When can data that were only observed tell us what would happen if we acted, and what must we assume, "
                     "state, and test before a causal claim is justified?"),
    "summary": ("Students write structural causal models and compute interventions by replacing one mechanism. They read "
                "conditional independences off directed acyclic graphs with d-separation, sort variables into confounders, "
                "mediators, and colliders, and derive the backdoor and frontdoor formulas (full proofs for the core cases, cited sketches in general) that turn interventional questions into "
                "observational ones. They connect graphs to potential outcomes and randomized experiments, separate "
                "identification from estimation, and see why two models can fit the same data and disagree about an action. "
                "The unit closes with what data cannot reveal (Markov equivalence, faithfulness), counterfactuals by abduction, "
                "action, and prediction, and the extra assumptions needed for causal machine learning, transport between "
                "populations, and fairness claims."),
    "for_whom": ("Undergraduates who have finished Levels 2 and 3 of this course or an equivalent introduction to probability, "
                 "expectation, linear algebra, and regression. The lessons suit a one-semester course or a study group; each has "
                 "proofs for students who want them and runnable code for students who learn by computing."),
    "prerequisites": ("Conditional probability and Bayes' rule, expectation and variance, simple linear regression, and enough "
                      "Python to run and modify a NumPy notebook."),
    "time": {"lessons": 10, "minutes_per_lesson": 100, "project_sessions": 3,
             "pace": ("One lesson a week fits a semester with the project in the last three weeks; two lessons a week fits an "
                      "intensive half-term. Each lesson splits into an intuition and animation sitting and a proofs, code, and "
                      "exercises sitting.")},
    "session_flow": [
        "Warm up: predict the answer to the lesson's opening puzzle before any formula.",
        "Watch the animations and read the definitions; restate each in your own words.",
        "Work through the theorem and its proof, then the worked example by hand.",
        "Run and modify the code; confirm the hand calculation numerically and use the interactive figure to test a prediction.",
        "Solve the core and stretch exercises, then answer the check questions before opening the explanations.",
        "Close by writing the assumptions each result needed and where they could fail.",
    ],
    "outcomes": [
        {"id": "O1", "text": "Write a structural causal model, compute an intervention by graph surgery, and compare it with conditioning.",
         "lessons": ["L4-01", "L4-07"]},
        {"id": "O2", "text": "Decide d-separation in a causal graph and state precisely what the soundness theorem does and does not guarantee.",
         "lessons": ["L4-02", "L4-08"]},
        {"id": "O3", "text": "Choose an adjustment set by graph roles and compute the bias caused by adjusting for a mediator or a collider.",
         "lessons": ["L4-03", "L4-04", "PROJECT"]},
        {"id": "O4", "text": "Derive and apply the backdoor and frontdoor formulas, stating every graphical and positivity condition.",
         "lessons": ["L4-04", "L4-05", "PROJECT"]},
        {"id": "O5", "text": "Define average treatment effects with potential outcomes and explain how randomization identifies them.",
         "lessons": ["L4-06"]},
        {"id": "O6", "text": "Separate identification from estimation, and show with two models that the same data can support different causal answers.",
         "lessons": ["L4-07", "L4-08", "PROJECT"]},
        {"id": "O7", "text": "Answer a counterfactual question in an explicit structural model by abduction, action, and prediction.",
         "lessons": ["L4-09"]},
        {"id": "O8", "text": "State the additional assumptions behind causal machine learning, transport, and fairness claims, and audit a claim that omits them.",
         "lessons": ["L4-10", "PROJECT"]},
    ],
    "evidence": ("Each lesson has three or four check questions (one reviews an earlier lesson), exercises at core, stretch, and "
                 "challenge levels with complete solutions, and runnable code whose printed results must match the hand "
                 "calculation. The project is a written causal analysis with code, judged with a four-part rubric."),
    "materials": [
        "Python 3 with NumPy, SciPy, pandas, Matplotlib, Plotly, and networkx (the course notebooks run in Colab or Binder)",
        "The course package qcai, whose science module contains the binary structural causal model used in the lessons",
        "Paper and pencil for drawing graphs and checking paths by hand",
        "Optional: the DoWhy or causal-learn libraries for the project",
    ],
    "project": {
        "title": "A causal analysis you can defend",
        "summary": ("Over three sessions students state a causal question, draw and justify a graph, prove that the target effect is "
                    "identified (or show that it is not), estimate it on simulated or public data, and write an analysis that keeps "
                    "assumptions, identification, estimation, and limits apart."),
        "questions": [
            "In a simulated hospital dataset generated from a structural model the student writes, what is the effect of a treatment on recovery, and which covariates must be adjusted for?",
            "Using a public observational dataset described in a textbook (for example a job-training or smoking study), what effect can be identified under a stated graph, and how sensitive is the answer to one omitted confounder?",
            "For a prediction model trained in one population, which causal assumptions would justify using it in a second population, and what would a fairness audit of it need to assume?",
        ],
        "steps": [
            "State the causal question as a target quantity, such as the outcome distribution under an intervention or an average treatment effect, and say why prediction alone does not answer it.",
            "Draw the causal graph, justify every arrow and every missing arrow in one sentence each, and list the testable independences it implies.",
            "Prove identification with the backdoor or frontdoor criterion, or show by two models that the effect is not identified.",
            "Estimate the effect with a standardization or regression estimator and report an uncertainty interval.",
            "Test the graph's implied independences where data allow, and run one sensitivity analysis for an unmeasured confounder.",
            "Write the analysis: question, graph, identification proof, estimate, checks, and the limits of the claim.",
        ],
        "rubric": [
            {"part": "Causal question and target", "start": "I described a relationship I am interested in.",
             "got": "I stated a precise interventional or counterfactual target.",
             "explain": "I can explain why that target differs from the corresponding conditional quantity in my data."},
            {"part": "Graph and assumptions", "start": "I drew a graph.",
             "got": "I justified each arrow and listed the independences the graph implies.",
             "explain": "I can say which conclusions would change if a specific arrow were added or removed."},
            {"part": "Identification", "start": "I chose variables to adjust for.",
             "got": "I proved identification with a stated criterion, including positivity.",
             "explain": "I can show a second model that fits my data and gives a different answer when my assumptions fail."},
            {"part": "Estimation and limits", "start": "I computed an estimate.",
             "got": "I reported an estimate with uncertainty and at least one check of the graph.",
             "explain": "I can state what the estimate does not show and what new data or experiment would settle it."},
        ],
    },
    "udl": [
        "Every key idea appears three ways: a moving animation with a full text description, a formal statement with proof, and code whose output can be checked.",
        "Students can show mastery by a proof, a computation, a simulation, or an annotated causal graph.",
        "Each lesson has core, stretch, and challenge exercises, so the same lesson serves students who need consolidation and students who want depth.",
        "Interactive figures let students test a prediction by changing one quantity at a time before they read the explanation.",
    ],
    "readings": [
        {"key": "pearlcausality", "note": "The reference text for structural causal models, the do-operator, d-separation, and identification."},
        {"key": "hernan", "note": "Free textbook on causal inference from data, strong on confounding, selection bias, and potential outcomes."},
        {"key": "peters", "note": "Concise, mathematical treatment of SCMs, Markov properties, and causal discovery, free online."},
        {"key": "bradyneal", "note": "Lecture notes with many small worked graphs; a gentle companion to every lesson."},
        {"key": "seeing", "note": "Applied examples of graphs, adjustment, and identification strategies in social science data."},
        {"key": "spirtes", "note": "The source for faithfulness and constraint-based causal discovery."},
        {"key": "bareinboim", "note": "A roadmap connecting causal inference with artificial intelligence, transport, and fairness."},
    ],
    "approach": ("The unit was planned backward from its outcomes [@ubd_whitepaper]. Each lesson moves from a concrete puzzle to an "
                 "animation, then to a precise definition and theorem with proof, then to computation and practice, following "
                 "first principles of instruction [@merrill2002], with retrieval and spaced review through check questions that "
                 "revisit earlier lessons [@dunlosky2013]. Several 3Blue1Brown-style animations per lesson, made with Manim "
                 "Community Edition [@manim_ce] and driven by the same numbers as the text, show what static notation hides: "
                 "graph surgery, paths opening and closing, and selection creating correlation. Multiple representations follow "
                 "Universal Design for Learning [@udl]. The content follows Pearl's structural account of causation "
                 "[@pearlcausality; @pearl] together with the potential-outcomes treatment of Hernán and Robins [@hernan], the "
                 "Markov and discovery theory of Spirtes, Glymour and Scheines and of Peters, Janzing and Schölkopf [@spirtes; "
                 "@peters], and the causal AI roadmap of Bareinboim and colleagues [@bareinboim]."),
}
SRC.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Level 4 unit written to", SRC)
