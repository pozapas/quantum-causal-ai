"""Unit `level2-blueprint`: write the Level 2 unit syllabus into ../src/data/level2.json.  Run from book/.

Lessons are written as drafts in _data/level2_drafts/ and merged by merge_level.py.
"""
import json
import pathlib

BOOK = pathlib.Path(__file__).resolve().parents[1]
SRC = BOOK.parent / "src" / "data" / "level2.json"
d = json.loads(SRC.read_text(encoding="utf-8"))

d["title"] = "Algebra, evidence, and causal maps"
d["audience"] = "Ages 12 to 15 (grades 7 to 9), working mostly on their own"
d["intro"] = ("Turn questions into variables, functions, and tables. Calculate conditional probabilities, see how a comparison "
              "can flip, draw causal maps, and meet the vectors that quantum physics is written in.")
d["unit"] = {
    "reading": {"max_fk": 8.0, "max_sentence": 28, "long_word_syllables": 6},
    "big_question": "When does a pattern in data tell us what causes what, and how would we check?",
    "summary": ("Learners write rules with variables and functions, read graphs with care, and calculate probabilities inside a group. "
                "They use natural frequencies to reverse a condition, see a comparison flip when groups are combined, and draw causal "
                "maps with chains, common causes, and colliders. They learn why setting a value is different from selecting records "
                "with that value. Finally they write a two-outcome chance as a vector and compare it with the state vectors used in "
                "quantum physics."),
    "for_whom": ("Learners aged about 12 to 15 who have finished Level 1 or are comfortable with fractions, simple probability, "
                 "and reading tables. They can work through a lesson alone. A teacher, parent, or study partner can join the "
                 "discussion questions and look over the project."),
    "time": {"lessons": 10, "minutes_per_lesson": 45, "project_sessions": 3,
             "pace": "Two lessons a week takes about six weeks, including the final project. Each lesson splits well into two sittings: story, animation and activity first, practice and checks second."},
    "session_flow": [
        "Warm up: answer the look-back question from memory.",
        "Read the story and watch the animation.",
        "Do the activity and keep a record.",
        "Work through the guided example, then try two on your own.",
        "Discuss, then answer the three check questions. Commit to an answer before you open it.",
        "Teachers and parents: read the short guide at the end of the page.",
    ],
    "outcomes": [
        {"id": "O1", "text": "I can name quantities with variables and units and write a rule as an equation.", "lessons": ["L2-01"]},
        {"id": "O2", "text": "I can use a function rule and tell a model's output apart from a measured value.", "lessons": ["L2-02"]},
        {"id": "O3", "text": "I can read a scatter plot, describe its trend, and say what it cannot show.", "lessons": ["L2-03", "PROJECT"]},
        {"id": "O4", "text": "I can calculate a conditional probability from a two-way table and test whether two events are independent.", "lessons": ["L2-04", "PROJECT"]},
        {"id": "O5", "text": "I can reverse a condition with natural frequencies, taking the base rate into account.", "lessons": ["L2-05"]},
        {"id": "O6", "text": "I can show how a comparison can flip when groups of different sizes are combined.", "lessons": ["L2-06"]},
        {"id": "O7", "text": "I can read a causal map and tell observing apart from intervening.", "lessons": ["L2-07", "L2-08", "PROJECT"]},
        {"id": "O8", "text": "I can write a two-outcome chance as a vector, and state a claim with its evidence and limits.", "lessons": ["L2-09", "L2-10", "PROJECT"]},
    ],
    "evidence": ("Each lesson ends with three check questions, one of which looks back at an earlier lesson. Each activity produces "
                 "a record (a table, a graph, a calculation, or a causal map). The final project is an evidence record judged with "
                 "a four-part rubric."),
    "materials": [
        "Graph paper, a ruler, pencils in three colors",
        "A calculator or a spreadsheet",
        "Two coins and two dice",
        "Index cards or sticky notes",
        "A computer with a web browser for the optional notebooks (Colab or Binder)",
    ],
    "safety": ("No special hazards. When collecting data from other people, ask permission, keep names off your records, "
               "and never collect private or medical information."),
    "project": {
        "title": "My evidence record",
        "summary": "Over three sittings, the learner investigates a question with a two-way table, draws a causal map, and writes an evidence record that states what the data can and cannot show.",
        "questions": [
            "Among classmates or family members who agree to answer, is having a pet linked to time spent outdoors? (Use first names only, or none.)",
            "In 100 rolls of two dice, is getting a double independent of getting a sum above 7?",
            "Use a public table from a textbook or a government statistics site and ask whether a comparison changes when you split it into groups.",
        ],
        "steps": [
            "Write the question, the variables, and their possible values.",
            "Collect or copy the data into a two-way table (at least 40 records).",
            "Calculate at least two conditional probabilities and say whether the events look independent.",
            "Draw a causal map with at least one other variable that could explain the pattern.",
            "Say what experiment, if any, would test the causal claim, and why it might not be possible.",
            "Write the evidence record: claim, source, assumptions, calculation, uncertainty, and scope.",
        ],
        "rubric": [
            {"part": "Question and variables", "start": "I wrote a question.", "got": "I named my variables and their values.", "explain": "I can say why my question is a statistical question."},
            {"part": "Calculations", "start": "I made a table.", "got": "I calculated conditional probabilities correctly.", "explain": "I can explain what each denominator is."},
            {"part": "Causal map", "start": "I drew arrows.", "got": "I drew a map with a possible common cause.", "explain": "I can say how the map changes what my numbers mean."},
            {"part": "Evidence record", "start": "I stated a conclusion.", "got": "I listed my assumptions and uncertainty.", "explain": "I can say what new data would change my mind."},
        ],
        "safety": "Survey only people who agree. Record no names or private details.",
    },
    "udl": [
        "Each story comes with an animation and a written description of what it shows.",
        "Learners can show what they know with a table, a graph, a diagram, a calculation, or a spoken explanation.",
        "Each lesson has a way to make it easier and a way to go further.",
        "Optional notebooks let learners run the same calculations in Python.",
    ],
    "standards": [
        {"code": "CCSS 6.EE.6", "text": "Use variables to represent numbers and write expressions for real-world problems.", "key": "ccss_math"},
        {"code": "CCSS 8.F.1", "text": "A function is a rule that assigns to each input exactly one output.", "key": "ccss_math"},
        {"code": "CCSS 8.SP.1, 8.SP.4", "text": "Construct and interpret scatter plots and two-way tables.", "key": "ccss_math"},
        {"code": "CCSS 7.SP.8", "text": "Find probabilities of compound events with tables, tree diagrams, and simulation.", "key": "ccss_math"},
        {"code": "CCSS S-CP.3", "text": "Conditional probability of A given B as P(A and B)/P(B), and independence.", "key": "ccss_math"},
        {"code": "CCSS S-ID.9", "text": "Distinguish between correlation and causation.", "key": "ccss_math"},
        {"code": "NGSS 6-8 practices", "text": "Analyze and interpret data; construct explanations supported by evidence.", "key": "ngss_appf"},
    ],
    "approach": ("Like the earlier levels, this unit was planned backward from its outcomes [@ubd_whitepaper], and each lesson moves "
                 "from recall, to a worked example, to practice, to discussion [@merrill2002], with retrieval and spaced review built in "
                 "[@dunlosky2013]. Each lesson has a short animation made with Manim Community Edition [@manim_ce], driven by the same "
                 "numbers as the text. The probability ideas follow OpenStax Introductory Statistics [@openstax_contingency; "
                 "@openstax_independent; @openstax_trees], Bayes' rule is taught with natural frequencies, which research shows people "
                 "reason with more accurately [@gigerenzer1995], the reversal lesson draws on a classic admissions study [@bickel1975], "
                 "and the causal maps follow Pearl's framework [@pearl; @bareinboim]."),
}
SRC.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Level 2 unit written to", SRC)
