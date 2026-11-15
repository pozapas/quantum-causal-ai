"""Unit `level5-blueprint`: write the Level 5 unit syllabus into ../src/data/level5.json.  Run from book/.

Only the title, audience, intro and the unit block are replaced; the lessons are left untouched.
Lessons are written as drafts in _data/level5_drafts/ and merged by merge_level.py.
"""
import json
import pathlib

BOOK = pathlib.Path(__file__).resolve().parents[1]
SRC = BOOK.parent / "src" / "data" / "level5.json"
d = json.loads(SRC.read_text(encoding="utf-8"))

d["title"] = "Quantum information"
d["audience"] = "Advanced undergraduates in physics, computer science, mathematics or engineering"
d["intro"] = ("Build the language of quantum information from the ground up: state vectors and the Born rule, gates and "
              "interference, entanglement, density operators, channels, measurements, Bell tests, tomography and error "
              "correction. Every result is derived, computed in Python, and pictured, and each tool is one that quantum "
              "causal models will need.")
d["unit"] = {
    "tier": "advanced",
    "big_question": ("What can be known about a quantum system from the outcomes of measurements on it, and which "
                     "operations, correlations and kinds of noise does quantum theory allow?"),
    "summary": ("Learners write qubit states in Dirac notation, turn amplitudes into probabilities with the Born rule, and "
                "picture states and gates on the Bloch sphere. They see relative phase become counts in an interferometer, "
                "build joint systems with tensor products and tell entanglement from classical correlation. Density operators, "
                "partial traces, Kraus operators and instruments then describe mixed states, noise and measurement in full "
                "generality. The unit closes with the CHSH test and its assumptions, entropy and state tomography, and a first "
                "quantum error-correcting code, separating a noise channel from the procedure that undoes it."),
    "for_whom": ("Advanced undergraduates, or beginning graduate students from other fields, who are comfortable with complex "
                 "numbers, linear algebra over the complex numbers, basic probability and some Python, at the level of "
                 "Levels 3 and 4 of this course. No previous course in quantum mechanics is assumed."),
    "prerequisites": ("Complex numbers, inner products, matrices, tensor products and eigenvectors (Level 3), probability, "
                      "expectation and estimation (Level 3), and the causal vocabulary of Level 4 for the Bell lesson."),
    "time": {"lessons": 10, "minutes_per_lesson": 90, "project_sessions": 3,
             "pace": ("About two lessons a week for six weeks, including the project. Each lesson splits into two sittings: "
                      "intuition, animations and definitions first; proofs, code and exercises second.")},
    "session_flow": [
        "Retrieve: answer the review check from an earlier lesson without notes.",
        "See it: watch the animations and explore the interactive figure before reading the formal statements.",
        "Prove it: read the definitions and theorems, and reconstruct one proof on paper.",
        "Compute it: run and modify the code block, and confirm the numbers quoted in the text.",
        "Practice: work the worked example, then at least one core, one stretch and one challenge exercise.",
        "Reflect: answer the check questions and write two sentences on the lesson's caution and scope.",
    ],
    "outcomes": [
        {"id": "O1", "text": "Compute Born-rule probabilities for pure states in any stated orthonormal basis, place states on the Bloch sphere, and prove that global phases are unobservable.", "lessons": ["L5-01"]},
        {"id": "O2", "text": "Translate a circuit into a matrix product in the correct order, describe single-qubit gates as Bloch rotations, and predict interference after a relative phase change.", "lessons": ["L5-02", "L5-03", "PROJECT"]},
        {"id": "O3", "text": "Build joint states with tensor products and decide whether a pure two-qubit state is entangled.", "lessons": ["L5-04"]},
        {"id": "O4", "text": "Work with density operators: purity, the Bloch ball, and reduced states from a partial trace.", "lessons": ["L5-05", "PROJECT"]},
        {"id": "O5", "text": "Check that a map is a quantum channel from its Kraus operators, and separate outcome probabilities from post-measurement states with instruments.", "lessons": ["L5-06", "L5-07", "PROJECT"]},
        {"id": "O6", "text": "Calculate a CHSH value, state the assumptions behind the classical bound, and account for statistical error in a claimed violation.", "lessons": ["L5-08", "PROJECT"]},
        {"id": "O7", "text": "Reconstruct a qubit state from repeated measurements in several bases measure how mixed a state is with von Neumann entropy, and state the estimation error from finite shots.", "lessons": ["L5-09", "PROJECT"]},
        {"id": "O8", "text": "Distinguish a noise channel from an error-correction procedure and compute when a simple code helps.", "lessons": ["L5-10", "PROJECT"]},
    ],
    "evidence": ("Each lesson ends with three or four check questions, one of which reviews an earlier lesson, and graded "
                 "exercises at core, stretch and challenge levels with full solutions. The project is a reproducible "
                 "notebook and a short report, judged with a four-part rubric that rewards correct derivations, honest "
                 "error bars and clearly stated assumptions."),
    "materials": [
        "Python 3 with numpy, scipy, matplotlib and plotly (the course package qcai provides the quantum helpers)",
        "A browser for the interactive figures and the course notebooks (Colab or Binder work)",
        "Paper for derivations; a computer algebra system is optional",
        "Optional: free access to a cloud quantum computer to compare simulations with hardware counts",
    ],
    "project": {
        "title": "Characterizing a noisy qubit in simulation",
        "summary": ("Over three sessions, the learner plays experimentalist and theorist for a simulated device: prepares "
                    "states, measures them with a finite number of shots, estimates a noise parameter from interference "
                    "and tomography data, and decides, with error bars, whether a Bell test or an error-correcting code "
                    "succeeds at that noise level."),
        "questions": [
            "A dephasing channel of unknown strength acts between the two Hadamards of an interferometer. How well can its strength be estimated from fringe visibility with 1000 shots per phase setting?",
            "A two-qubit Werner state has visibility v. For which v does the CHSH value exceed 2, and how many shots are needed before the violation is larger than three standard errors?",
            "Under independent bit flips with probability p, where is the break-even point at which the three-qubit repetition code starts to beat an unencoded qubit?",
        ],
        "steps": [
            "State the model precisely: states, gates, channel and measurement, with every convention written down.",
            "Derive the ideal prediction on paper (fringe, CHSH value, or logical error rate) as a function of the noise parameter.",
            "Write a seeded simulation that draws finite-shot counts from the Born rule, and check it against the derivation.",
            "Estimate the noise parameter or the test statistic from the simulated counts, with a standard error.",
            "Repeat across noise levels and plot estimate against truth with error bars.",
            "Write a two-page report: claim, model, assumptions, results with uncertainty, and what a hardware run would add.",
        ],
        "rubric": [
            {"part": "Model and conventions", "start": "I described the experiment in words.", "got": "I wrote the states, gates, channel and measurement with their conventions.", "explain": "I can say which conclusions would change under a different convention and which would not."},
            {"part": "Derivation", "start": "I quoted a formula.", "got": "I derived the prediction and checked special cases.", "explain": "I can prove the result and state the assumptions it needs."},
            {"part": "Simulation and statistics", "start": "I ran a simulation.", "got": "My seeded simulation matches the derivation within the expected error.", "explain": "I can justify the number of shots from a standard-error calculation."},
            {"part": "Claims and limits", "start": "I stated a conclusion.", "got": "I reported estimates with error bars and listed the assumptions.", "explain": "I can explain why a simulation is not an experiment and what loopholes or noise sources a real device adds."},
        ],
    },
    "udl": [
        "Every animation has a full text description, and every interactive figure has a written summary of what it shows.",
        "Each idea appears as a picture, a formula, a proof and runnable code, so learners can enter through the form that suits them.",
        "Exercises are tiered (core, stretch, challenge); the project questions can be chosen to match interest and background.",
        "Learners may show mastery through derivations, annotated code, short recorded explanations, or written reports.",
    ],
    "readings": [
        {"key": "nielsenchuang", "note": "Chapters 1, 2, 4, 8, 10 and 11 are the main reference for the whole unit."},
        {"key": "preskill", "note": "Lecture notes with a physicist's view of measurement, decoherence, entanglement and error correction."},
        {"key": "watrous", "note": "Rigorous treatment of states, channels, measurements and the Choi representation, used again in Level 6."},
        {"key": "ibm", "note": "A free course that builds the same notation with runnable examples on simulators and hardware."},
        {"key": "feynman", "note": "Volume III motivates amplitudes and interference from two-path experiments."},
        {"key": "chsh", "note": "The original proposal of the CHSH inequality used in L5-08."},
        {"key": "nisq", "note": "Context on what present-day noisy devices can and cannot do."},
    ],
    "approach": ("The unit is planned backward from its outcomes [@ubd_whitepaper]. Each lesson moves from a puzzle and a "
                 "moving picture to formal definitions, theorems with proofs, computation and graded practice "
                 "[@merrill2002], with a review question in every lesson to space retrieval [@dunlosky2013]. The "
                 "animations are made with Manim Community Edition [@manim_ce] from the same numbers as the text, and "
                 "every page offers several ways in, following Universal Design for Learning [@udl]. The mathematics "
                 "follows Nielsen and Chuang and Watrous [@nielsenchuang; @watrous], with physical motivation from "
                 "Preskill and Feynman [@preskill; @feynman] and hands-on examples in the style of IBM's course [@ibm]. "
                 "Claims about devices are kept modest and tied to the noisy hardware that exists today [@nisq]."),
}
SRC.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Level 5 unit written to", SRC)
