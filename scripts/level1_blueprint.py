"""Unit `level1-blueprint`: write the Level 1 unit syllabus into ../src/data/level1.json.  Run from book/.

Lessons are written as drafts in _data/level1_drafts/ and merged by merge_level.py.
"""
import json
import pathlib

BOOK = pathlib.Path(__file__).resolve().parents[1]
SRC = BOOK.parent / "src" / "data" / "level1.json"
d = json.loads(SRC.read_text(encoding="utf-8"))

d["title"] = "Chance, waves, and fair tests"
d["audience"] = "Ages 9 to 12 (grades 4 to 6), with a grown-up or teacher nearby"
d["intro"] = ("Use fractions and repeated tests to describe uncertain results. Learn why observations, actions, and wave "
              "effects need different explanations.")
d["unit"] = {
    "reading": {"max_fk": 5.5, "max_sentence": 25, "long_word_syllables": 5},
    "big_question": "How do we describe chance, test fairly, and tell what waves can do that coins cannot?",
    "summary": ("Learners turn counts into fractions and probabilities, compare what a model predicts with what really "
                "happens, and use random assignment to make a fair comparison. Then they meet waves, which can add up or "
                "cancel. That idea, adding first and then squaring, is the first step toward quantum physics."),
    "for_whom": ("Learners aged about 9 to 12 who have finished Level 0 or can count, compare, and read simple tables. "
                 "They can work through most of a lesson alone. A grown-up or teacher checks the record sheet and joins the talk questions."),
    "time": {"lessons": 10, "minutes_per_lesson": 40, "project_sessions": 3,
             "pace": "Two lessons a week takes about six weeks, including the final project. Any lesson can be split into two sittings: story, animation and activity one day, practice and checks the next."},
    "session_flow": [
        "Warm up: answer the look-back question from memory.",
        "Read the story and watch the animation.",
        "Do the hands-on activity and keep a record.",
        "Practice together, then try two on your own.",
        "Talk about it, then answer the three check questions. Say or write your answer before you open it.",
        "Grown-ups: read the short guide at the end of the page.",
    ],
    "outcomes": [
        {"id": "O1", "text": "I can write a fraction from a count and use it to describe part of a group.", "lessons": ["L1-01"]},
        {"id": "O2", "text": "I can build a probability model and find the probability of an event and of its opposite.", "lessons": ["L1-02"]},
        {"id": "O3", "text": "I can tell a probability apart from a frequency, and explain why more trials help.", "lessons": ["L1-03"]},
        {"id": "O4", "text": "I can find a probability inside a group by using the right total.", "lessons": ["L1-04"]},
        {"id": "O5", "text": "I can explain how random assignment makes a comparison fair.", "lessons": ["L1-05", "PROJECT"]},
        {"id": "O6", "text": "I can draw a common-cause diagram for two things that go up and down together.", "lessons": ["L1-06"]},
        {"id": "O7", "text": "I can describe a wave and explain how two waves can add up or cancel.", "lessons": ["L1-07", "L1-08"]},
        {"id": "O8", "text": "I can explain why not knowing a hidden result is different from the two-path experiment with light, and write a model that a test could prove wrong.", "lessons": ["L1-09", "L1-10", "PROJECT"]},
    ],
    "evidence": ("Progress shows up three ways. Each lesson ends with three check questions. From Lesson 2 on, one of them looks "
                 "back at an earlier lesson. Each activity produces a record (a table, a graph, or a diagram) that a grown-up can look at. "
                 "The final project uses a four-part checklist."),
    "materials": [
        "Two coins, two dice, and a paper cup",
        "Counters, beads, or building bricks in two or three colors, and a paper bag",
        "Graph paper or a printed grid, a ruler, pencils, and colored pencils",
        "A calculator (optional)",
        "A jump rope or a long, soft rope, or a toy spring coil",
        "A shallow tray or baking dish of water and a small cup",
        "Paper for paper airplanes or a paper cup tower, and masking tape",
    ],
    "safety": ("Keep coins, dice, and small counters away from babies and toddlers. Use water trays on a towel, away from screens "
               "and plugs, and wipe up spills right away. Swing ropes slowly, with space around you."),
    "project": {
        "title": "My chance and cause investigation",
        "summary": "Over three sittings, the learner runs a small experiment with random assignment, compares a model with real counts, and writes a model card.",
        "questions": [
            "Does a paper airplane with folded wing tips fly farther than one without? Flip a coin to decide which plane each throw uses.",
            "Do two dice add to 7 as often as a model predicts?",
            "Does a ball roll farther on carpet or on a hard floor? Use a coin to decide the order of the trials.",
        ],
        "steps": [
            "Pick a question. Write a prediction and the model behind it.",
            "Plan a fair test. Use a coin or a die to assign which choice each trial gets.",
            "Run at least 20 trials. Record every result in a table.",
            "Turn your counts into fractions, and compare them with your model.",
            "Make a graph of your results.",
            "Write a model card: question, assumptions, prediction, what would prove it wrong, and what happened.",
        ],
        "rubric": [
            {"part": "My question and model", "start": "I wrote a question.", "got": "I wrote a question and a prediction from a model.", "explain": "I can say what my model assumes."},
            {"part": "My fair test", "start": "I compared two choices.", "got": "I used a coin or die to assign the choices.", "explain": "I can say why random assignment makes it fair."},
            {"part": "My record", "start": "I wrote some results.", "got": "I recorded at least 20 trials and turned them into fractions.", "explain": "I can say why my fractions are not exactly what the model predicted."},
            {"part": "My model card", "start": "I said what happened.", "got": "I compared my results with my prediction.", "explain": "I named a result that would have proved my model wrong."},
        ],
        "safety": "Throw paper airplanes away from faces. Roll balls away from stairs. Keep dice away from babies and toddlers.",
    },
    "udl": [
        "Each story comes with an animation and a written description of what it shows.",
        "Learners can show what they know in a table, a graph, a drawing, or by explaining aloud.",
        "Each lesson has a way to make it easier and a way to make it harder.",
        "Activities use cheap household things, and the animations play without sound.",
    ],
    "standards": [
        {"code": "NGSS 3-5 practices", "text": "Plan and conduct fair tests in which variables are controlled and the number of trials considered.", "key": "ngss_appf"},
        {"code": "NGSS 4-PS4-1", "text": "Develop a model of waves to describe patterns in terms of amplitude and wavelength.", "key": "ngss_4ps4_1"},
        {"code": "CCSS 3.NF.1", "text": "Understand a fraction 1/b as one part of a whole cut into b equal parts.", "key": "ccss_math"},
        {"code": "CCSS 4.NF.1", "text": "Explain why two fractions are equivalent, using visual fraction models.", "key": "ccss_math"},
        {"code": "CCSS 6.SP.1", "text": "Recognize a statistical question as one that expects variability in the data.", "key": "ccss_math"},
        {"code": "CCSS 7.SP.5 to 7.SP.7", "text": "Probability as a number from 0 to 1; approximate it from data; build and compare probability models.", "key": "ccss_math"},
    ],
    "approach": ("Like Level 0, this unit was planned backward from its outcomes [@ubd_whitepaper], and each lesson moves from recall, to an "
                 "example, to doing, to talking it through [@merrill2002], with built-in retrieval and spaced review [@dunlosky2013]. "
                 "New in Level 1, each lesson has a short animation made with Manim Community Edition, an open-source animation library "
                 "forked from the tool Grant Sanderson created for his 3Blue1Brown videos [@manim_ce]. The animations use the course's own tested simulation code, so the numbers on screen match the text. "
                 "The probability ideas follow OpenStax Introductory Statistics [@openstax_prob; @openstax_design]; the wave ideas follow "
                 "OpenStax Physics [@openstax_waves; @openstax_interference]."),
}
SRC.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Level 1 unit written to", SRC)
