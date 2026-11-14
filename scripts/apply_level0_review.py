"""Unit `level0-review-fix`: apply evidence/review-level0.json fixes.  Run from book/.

Edits the Level 0 drafts, two pictures, the unit blueprint, the lesson template
and the source records with exact, asserted substitutions; then the normal flow
(blueprint -> merge -> convert) rebuilds the pages.
"""
import io
import json
import pathlib
import re

import requests
from pypdf import PdfReader

B = pathlib.Path(__file__).resolve().parents[1]
D = B / "_data" / "level0_drafts"


def load(i):
    return json.loads((D / f"L0-{i:02d}.json").read_text(encoding="utf-8"))


def save(L):
    (D / f"{L['id']}.json").write_text(json.dumps(L, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sub_text(s, old, new, label):
    assert s.count(old) == 1, (label, old[:60], s.count(old))
    return s.replace(old, new)


def sub_file(rel, pairs):
    p = B / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        s = sub_text(s, old, new, rel)
    p.write_text(s, encoding="utf-8")


# K.CC.6 wording must be in the official standards PDF before we cite it
pdf = requests.get("https://learning.ccsso.org/wp-content/uploads/2022/11/Math_Standards1.pdf",
                   headers={"User-Agent": "Mozilla/5.0 (qcai-book-verifier/1.0)"}, timeout=60).content
std = re.sub(r"\s+", " ", " ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(pdf)).pages))
assert "greater than, less than, or equal to the number of objects in another group" in std, "K.CC.6 not found"

# ---- L0-01 ------------------------------------------------------------------------
L = load(1)
L["picture"]["caption"] = "Two new piles, like the ones you will count. Each button gets one tally mark. Pile A has 12. Pile B has 9. Pile A has more."
L["grownups"]["why"] = sub_text(L["grownups"]["why"], "(K.CC.5 and K.CC.7)", "(K.CC.5 and K.CC.6)", "L0-01 why")
save(L)

# ---- L0-02 ------------------------------------------------------------------------
L = load(2)
L["activity"]["steps"][3] = sub_text(L["activity"]["steps"][3], "into 3 or 4 groups", "into 2, 3, or 4 groups", "L0-02 step")
save(L)

# ---- L0-03 ------------------------------------------------------------------------
L = load(3)
L["words"] = [w if w["word"] != "melt" else {"word": "melt", "meaning": "When something solid, like ice or butter, warms up and turns runny."} for w in L["words"]]
save(L)
sub_file("_static/lessons/l0-03-ice.svg", [
    ('<ellipse cx="274" cy="118" rx="33" ry="11"', '<ellipse cx="274" cy="118" rx="28" ry="9"'),
    ('<rect x="256" y="82" width="36" height="36" rx="6"', '<rect x="254" y="78" width="40" height="40" rx="6"'),
    ('<line x1="262" y1="89" x2="273" y2="89"', '<line x1="260" y1="85" x2="272" y2="85"'),
    ('<ellipse cx="446" cy="118" rx="45" ry="15"', '<ellipse cx="446" cy="118" rx="36" ry="12"'),
    ('<rect x="432" y="90" width="28" height="28" rx="8"', '<rect x="428" y="82" width="36" height="36" rx="7"'),
    ('<line x1="438" y1="97" x2="446" y2="97"', '<line x1="434" y1="89" x2="445" y2="89"'),
    ('<ellipse cx="618" cy="118" rx="55" ry="18"', '<ellipse cx="618" cy="118" rx="44" ry="15"'),
    ('<rect x="609" y="100" width="18" height="18" rx="10"', '<rect x="602" y="86" width="32" height="32" rx="9"'),
    ('<line x1="615" y1="107" x2="620" y2="107"', '<line x1="608" y1="93" x2="618" y2="93"'),
    ("At 15 minutes a small piece of ice is still there in a big puddle.", "At 15 minutes a smaller cube is still there in a bigger puddle."),
])

# ---- L0-04 ------------------------------------------------------------------------
L = load(4)
L["story"][0] = sub_text(L["story"][0], "two toy cars and a ramp made from a board and a pile of books.",
                         "two toy cars, two boards, and a pile of books for making ramps.", "L0-04 story")
L["connect"] = sub_text(L["connect"], "Much later, you will meet the world of very tiny things, where just looking can change what you look at. There, making a fair test becomes a real puzzle.",
                        "Much later, you will meet the world of very tiny things. There, measuring something can change it. Then making a fair test becomes a real puzzle.", "L0-04 connect")
save(L)

# ---- L0-05 ------------------------------------------------------------------------
L = load(5)
L["grownups"]["why"] = L["grownups"]["why"].replace("[@openstax]", "[@openstax_prob]")
L["sources"] = ["openstax_prob" if s == "openstax" else s for s in L["sources"]]
L["grownups"]["extend"] = sub_text(L["grownups"]["extend"], "Is the total closer to half and half than one person's 20 flips?",
                                   "Is the share of heads closer to half than in one person's 20 flips? Compare the share (for example 52 out of 100), not the difference in counts, which often gets bigger.", "L0-05 extend")
save(L)

# ---- L0-07 ------------------------------------------------------------------------
L = load(7)
L["objective"] = "I can test what different things do to light, and write what I saw before I guess why."
L["big_idea"] = "We see things when light from them reaches our eyes. Some things let light through, some block it, and some bounce it back."
L["try_it"][1] = {"prompt": "Which group would a piece of foil go in? Make a guess, then test it if you can.",
                  "answer": "No spot shows behind the foil. Shiny foil bounces light back, like a mirror. So it goes in bounces light back."}
L["activity"]["safety"] = "Never shine a flashlight or a mirror spot into anyone's eyes. Use a flashlight, never a laser pointer. Move slowly in a dim room. A grown-up should hold a glass mirror."
L["grownups"]["extend"] = sub_text(L["grownups"]["extend"], "a glass of water", "a clear plastic cup of water, set on a towel", "L0-07 extend")
L["connect"] = sub_text(L["connect"], "In the world of very tiny things, just looking can change what you look at.",
                        "With very tiny things, measuring something can change it.", "L0-07 connect")
save(L)

# ---- L0-08 ------------------------------------------------------------------------
L = load(8)
L["story"][0] = "Maya wants to ask Leo four questions. Leo wants to answer without saying a word. Maya has an idea. \"Let's use cards!\""
L["prerequisites"] = ["L0-02"]
save(L)

# ---- L0-09 ------------------------------------------------------------------------
L = load(9)
L["big_idea"] = "A clue can tell you about something without making it happen."
save(L)

# ---- L0-10 ------------------------------------------------------------------------
L = load(10)
L["activity"]["steps"][3] = "Here are some ideas to use. A fair test. A clue is not a cause. Tiny things follow surprising rules. A bit holds 1 or 0. A pattern helps you guess."
s = L["grownups"]["simplify"]
s = sub_text(s, "light helps us see goes in Tiny things, because light is one of the things whose surprising rules the course studies later, even though Lesson 7 only used ordinary light.",
             "tiny things follow surprising rules goes in Tiny things.", "L0-10 key")
s = sub_text(s, "The picture's note that just looking can change tiny things previews a later idea about measurement; it is not shown in Level 0.",
             "The picture's note that measuring tiny things can change them previews a later idea; it is not shown in Level 0.", "L0-10 note")
L["grownups"]["simplify"] = s
L["picture"]["alt"] = sub_text(L["picture"]["alt"], "with the notes fair test, light, and patterns", "with the notes fair test, surprising rules, and patterns", "alt1")
L["picture"]["alt"] = sub_text(L["picture"]["alt"], "just looking can change tiny things", "measuring tiny things can change them", "alt2")
L["connect"] = sub_text(L["connect"], "Level 1 comes next.", "When you are ready, Level 1 comes next.", "L0-10 connect")
L["check"][2] = {"question": "Remember Lesson 8. The cards are up, down, down. How do you write that?",
                 "options": ["1 0 0", "0 1 1", "1 1 0"], "answer": 0, "review_of": "L0-08",
                 "explanation": "Face up is 1 and face down is 0. So up, down, down is 1 0 0."}
save(L)
sub_file("_static/lessons/l0-10-big-ideas.svg", [
    ('<text class="ex" x="380" y="124" text-anchor="middle">light</text>',
     '<text class="ex" x="380" y="116" text-anchor="middle">surprising</text>\n<text class="ex" x="380" y="136" text-anchor="middle">rules</text>'),
    ('<text class="sub" x="52" y="72">Just looking can</text>', '<text class="sub" x="52" y="72">Measuring tiny things</text>'),
    ('<text class="sub" x="52" y="94">change tiny things.</text>', '<text class="sub" x="52" y="94">can change them.</text>'),
    ("holds the note light.", "holds the note surprising rules."),
    ("just looking can change tiny things.", "measuring tiny things can change them."),
])

# ---- lesson template: honest lab line ------------------------------------------------
sub_file("scripts/coursebook.py", [(
    'f"**On the computer.** Grown-ups can see the same idea simulated in [Lab: {lab_title}](../../labs/{lab_file}.ipynb), "\n            "written for older learners.", ""]',
    'f"**On the computer.** Grown-ups can see where this idea leads later in [Lab: {lab_title}](../../labs/{lab_file}.ipynb), "\n            "written for older learners.", ""]')])

# ---- unit blueprint -------------------------------------------------------------------
sub_file("scripts/level0_blueprint.py", [
    ('"lessons": ["L0-05", "L0-06"]},', '"lessons": ["L0-05"]},'),
    ('"lessons": ["L0-06", "L0-09"]},', '"lessons": ["L0-06"]},'),
    ('"Small things to count and sort: buttons, blocks, dry pasta, or toy pieces (about 20)",',
     '"Small things to count and sort: buttons, blocks, dry pasta, or toy pieces (about 30), and a few bowls",'),
    ('"Four playing cards or paper squares",\n',
     '"Four playing cards or paper squares",\n        "For the final project: a ball or toy car, paper towels and a cup of water, or an ice cube and a plate",\n'),
    ('"evidence": ("Progress shows up three ways. Each lesson ends with three check questions, one of which looks back at an "\n                 "earlier lesson. ',
     '"evidence": ("Progress shows up three ways. Each lesson ends with three check questions. From Lesson 2 on, one of them "\n                 "looks back at an earlier lesson. '),
    ('"safety": ("Choose activities that fit the child. Keep small parts away from babies and toddlers. "\n               "Never point a flashlight into anyone\'s eyes. Keep water away from screens and plugs."),',
     '"safety": ("Choose activities that fit the child. Keep small parts and coins away from babies and toddlers. "\n               "Never point a flashlight or a mirror spot into anyone\'s eyes, and never look straight at the sun. A grown-up "\n               "holds anything glass and does the cutting. Keep water away from screens and plugs, and keep activities away from stairs."),'),
    ('            "Does a ball bounce higher on a hard floor or on a rug?",\n', ''),
    ('            "Does a paper airplane fly farther with sharp folds or soft folds?",\n',
     '            "Does an ice cube melt faster on a plate in a sunny spot or in the shade?",\n'),
    ('"Draw a picture graph of your results.",', '"Draw your results as a picture graph or a bar graph, with one square for each tile or step.",'),
    ('"summary": "Over two sittings, the child picks a question, plans a fair test, runs it three times, and shares what they found.",',
     '"summary": "Over two sittings, the child picks a question, plans a fair test, runs it three times, and shares what they found.",\n'
     '        "safety": "Roll balls and cars away from stairs. Wipe up water right away so no one slips. Never look straight at the sun.",'),
    ('"Practise together, then try two on your own.",', '"Practice together, then try two on your own.",'),
    ('"Talk about it, then answer the three check questions.",',
     '"Talk about it, then answer the three check questions. Say your answer out loud before you open a dropdown.",'),
    ('Each lesson can also be split into two 15-minute sittings: explore one day, practise and check the next.',
     'Any lesson can be split into two sittings: story and activity one day, practice and checks the next. This helps most in the lessons with a 20-minute activity.'),
    ('They practise telling what they saw apart from why it happened.', 'They practice telling what they saw apart from why it happened.'),
    ('Design for Learning guidelines [@udl]."),',
     'Design for Learning guidelines [@udl]. When the child answers a question, let them say their answer before opening it, then open it "\n'
     '                 "together and praise the thinking as well as the right answer."),'),
    ('        {"code": "CCSS K.MD.3",', '        {"code": "CCSS K.CC.6", "text": "Compare the number of objects in two groups: greater than, less than, or equal.", "key": "ccss_math"},\n'
     '        {"code": "CCSS K.MD.3",'),
    ('        {"code": "CCSS 2.MD.10",', '        {"code": "CCSS 2.MD.1", "text": "Measure the length of an object with a tool such as a ruler.", "key": "ccss_math"},\n'
     '        {"code": "CCSS 2.MD.10",'),
])
# project safety is rendered on the unit page
sub_file("scripts/coursebook.py", [(
    '    out += ["", "**Steps:**", "", *[f"{i}. {esc(s)}" for i, s in enumerate(p["steps"], 1)], "",',
    '    out += ["", "**Steps:**", "", *[f"{i}. {esc(s)}" for i, s in enumerate(p["steps"], 1)], "",\n'
    '            *([":::{warning} Project safety", esc(p["safety"]), ":::", ""] if p.get("safety") else []),')])

# ---- sources: OpenStax probability section, Level 0 tags ------------------------------
sub_file("scripts/add_level0_refs.py", [(
    '    ("csunplugged_binary", ',
    '    ("openstax_prob", "https://openstax.org/books/introductory-statistics-2e/pages/3-1-terminology",\n'
    '     "3.1 Terminology", "Barbara Illowsky and Susan Dean", 2023, "OpenStax, Introductory Statistics 2e", "web", [0, 1],\n'
    '     "Probability as long-run relative frequency; the law of large numbers with coin tosses", "law of large numbers"),\n'
    '    ("csunplugged_binary", ')])
print("review fixes applied")
