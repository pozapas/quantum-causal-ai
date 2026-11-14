"""Unit `level0-blueprint`: write the Level 0 unit syllabus and the model lesson (L0-04)
into the source of truth, ../src/data/level0.json.  Run from book/.

Design: backward design (outcomes, then evidence, then the learning plan); each
lesson follows activation -> demonstration -> application -> integration, with a
warm-up that retrieves the previous lesson (spaced practice) and a review check.
Child-facing text cites nothing; the grown-up guide cites verified sources.
"""
import json
import pathlib

BOOK = pathlib.Path(__file__).resolve().parents[1]
SRC = BOOK.parent / "src" / "data" / "level0.json"
d = json.loads(SRC.read_text(encoding="utf-8"))

d["title"] = "Notice, count, and ask"
d["audience"] = "Ages 6 to 9 (grades 1 to 3), learning with a grown-up"
d["intro"] = ("Start with objects, light, choices, and fair tests. These lessons prepare the ideas that later "
              "become probability, causal reasoning, and quantum science.")

d["unit"] = {
    "big_question": "How do we find out what makes things happen?",
    "summary": ("Children learn to look closely, count carefully, sort, and run small fair tests with things "
                "found at home. They practice telling what they saw apart from why it happened. Every later level "
                "of the course builds on these habits."),
    "for_whom": ("Children aged about 6 to 9 who can count to 20. A grown-up reads along, helps with materials, "
                 "and talks through the questions. No screen time is needed for the hands-on parts."),
    "time": {"lessons": 10, "minutes_per_lesson": 30, "project_sessions": 2,
             "pace": "Two lessons a week takes about six weeks, including the final project. Any lesson can be split into two sittings: story and activity one day, practice and checks the next. This helps most in the lessons with a 20-minute activity."},
    "session_flow": [
        "Warm up: remember the last lesson in two minutes.",
        "Read the story together.",
        "Do the hands-on activity and record what happens.",
        "Practice together, then try two on your own.",
        "Talk about it, then answer the three check questions. Say your answer out loud before you open a dropdown.",
        "Grown-ups: read the short guide at the end of the page.",
    ],
    "outcomes": [
        {"id": "O1", "text": "I can count a group carefully and write it down so someone else can check it.", "lessons": ["L0-01", "L0-02"]},
        {"id": "O2", "text": "I can sort things using one rule and tell which group has more.", "lessons": ["L0-02"]},
        {"id": "O3", "text": "I can tell what I saw before and after a change, without guessing why.", "lessons": ["L0-03", "L0-07"]},
        {"id": "O4", "text": "I can plan a fair test that changes only one thing.", "lessons": ["L0-04", "PROJECT"]},
        {"id": "O5", "text": "I can say if something is sure, maybe, or impossible, and try it more than once.", "lessons": ["L0-05"]},
        {"id": "O6", "text": "I can use a pattern to make a guess, then check it.", "lessons": ["L0-06"]},
        {"id": "O7", "text": "I can explain why a clue is not always a cause.", "lessons": ["L0-09"]},
        {"id": "O8", "text": "I can write a yes or no choice as 1 or 0, and name the three big ideas of this course.", "lessons": ["L0-08", "L0-10"]},
    ],
    "evidence": ("Progress shows up three ways. Each lesson ends with three check questions. From Lesson 2 on, one of them "
                 "looks back at an earlier lesson. Each hands-on activity produces a record (a tally, a table, or a drawing) that a grown-up "
                 "can look at. The final project uses a four-part checklist."),
    "materials": [
        "Small things to count and sort: buttons, blocks, dry pasta, or toy pieces (about 30), and a few bowls",
        "Paper, pencils, crayons or markers, and grid paper if you have it",
        "Sticky notes, small paper cards, and masking tape",
        "A toy car or a ball that rolls, two hardcover books, and a flat board or stiff cardboard",
        "An ice cube, a plate, and a clock or timer",
        "One coin and a paper cup",
        "Six matching paper or plastic cups and a ruler with centimeters",
        "A flashlight, clear plastic, wax paper, cardboard, white paper, and a small mirror (plastic if you have one)",
        "Four playing cards or paper squares",
        "For the final project: a ball or toy car, paper towels and a cup of water, or an ice cube and a plate",
    ],
    "safety": ("Choose activities that fit the child. Keep small parts and coins away from babies and toddlers. "
               "Never point a flashlight or a mirror spot into anyone's eyes, and never look straight at the sun. A grown-up "
               "holds anything glass and does the cutting. Keep water away from screens and plugs, and keep activities away from stairs."),
    "project": {
        "title": "My own fair test",
        "summary": "Over two sittings, the child picks a question, plans a fair test, runs it three times, and shares what they found.",
        "safety": "Roll balls and cars away from stairs. Wipe up water right away so no one slips. Never look straight at the sun.",
        "questions": [
            "Does a toy car roll farther on a smooth floor or on carpet?",
            "Which paper towel soaks up more water, a thick one or a thin one?",
            "Does an ice cube melt faster on a plate in a sunny spot or in the shade?",
        ],
        "steps": [
            "Pick one question.",
            "Say what you will change. Say what you will keep the same.",
            "Guess what will happen and why.",
            "Do the test three times for each choice. Write every result.",
            "Draw your results as a picture graph or a bar graph, with one square for each tile or step.",
            "Tell someone what you found, and one thing you are still not sure about.",
        ],
        "rubric": [
            {"part": "My question", "start": "I picked a question with help.", "got": "I picked a question I can test.", "explain": "I can say why the question matters to me."},
            {"part": "My fair plan", "start": "I changed one thing, with help.", "got": "I changed one thing and kept the rest the same.", "explain": "I can say what could make the test unfair."},
            {"part": "My record", "start": "I wrote some results.", "got": "I wrote three results for each choice.", "explain": "I can point to results that did not match and say why that is fine."},
            {"part": "What I found", "start": "I said what happened.", "got": "I said what happened and used my results.", "explain": "I said one thing I am still not sure about."},
        ],
    },
    "udl": [
        "Every story can be read aloud. Pictures and real objects come before symbols.",
        "Children can show what they know by talking, drawing, pointing, or writing.",
        "Each lesson has a way to make it easier and a way to make it harder.",
        "Activities use cheap household things, so every family can take part.",
    ],
    "standards": [
        {"code": "NGSS K-2 practices", "text": "Simple investigations based on fair tests, which provide data to support explanations.", "key": "ngss_appf"},
        {"code": "NGSS 1-PS4-2", "text": "Objects can be seen only when illuminated.", "key": "ngss_1ps4_2"},
        {"code": "NGSS 1-PS4-3", "text": "What happens when different materials are placed in a beam of light.", "key": "ngss_1ps4_3"},
        {"code": "CCSS K.CC.5", "text": "Count to answer \"how many?\" questions.", "key": "ccss_math"},
        {"code": "CCSS K.CC.6", "text": "Compare the number of objects in two groups: greater than, less than, or equal.", "key": "ccss_math"},
        {"code": "CCSS K.MD.3", "text": "Classify objects into categories and count each category.", "key": "ccss_math"},
        {"code": "CCSS 1.MD.4", "text": "Organize, represent, and interpret data with up to three categories.", "key": "ccss_math"},
        {"code": "CCSS 2.MD.1", "text": "Measure the length of an object with a tool such as a ruler.", "key": "ccss_math"},
        {"code": "CCSS 2.MD.10", "text": "Draw a picture graph and a bar graph for up to four categories.", "key": "ccss_math"},
    ],
    "approach": ("The unit was planned backward: first the eight outcomes, then the evidence that shows them, then the "
                 "lessons [@ubd_whitepaper]. Each lesson moves from remembering what the child knows, to watching an example, "
                 "to doing, to talking it through [@merrill2002]. Short check questions and a warm-up that looks back are "
                 "built in on purpose, because practice testing and spaced practice are among the best-supported ways to "
                 "learn [@dunlosky2013]. Young children already reason about causes from what they see [@gopnik2000; @gopnik2004]; "
                 "this unit gives that instinct words and a method. Options for different learners follow the Universal "
                 "Design for Learning guidelines [@udl]. When the child answers a question, let them say their answer before opening it, then open it "
                 "together and praise the thinking as well as the right answer."),
}

L04 = {
    "id": "L0-04",
    "schema": 2,
    "title": "Compare fairly",
    "objective": "I can plan a fair test that changes only one thing.",
    "prerequisites": ["L0-03"],
    "time_minutes": 30,
    "big_idea": "To find out what a change does, change just one thing and keep everything else the same.",
    "i_can": [
        "I can pick one thing to change in a test.",
        "I can name the things I keep the same.",
        "I can do a test more than once and compare.",
    ],
    "words": [
        {"word": "fair test", "meaning": "A test where you change only one thing, so you can tell what made the difference."},
        {"word": "result", "meaning": "What happens at the end of a test, like how far a car rolled."},
    ],
    "warmup": {"recall_of": "L0-03",
               "prompt": "Last time you watched a change. Think of one thing you saw before and after. What changed? What stayed the same?"},
    "story_title": "The ramp race",
    "picture": {"file": "l0-04-ramps.svg", "alt": "Two ramps side by side. With one book the car rolls 4 tiles; with two books the same car rolls 7 tiles.",
                "caption": "Same car, same floor, same start line. Only the ramp height changes."},
    "story": [
        "Maya and Leo have two toy cars and a ramp made from a board and a pile of books. Leo says, \"A higher ramp makes a car go farther!\" Maya says, \"How can we find out?\"",
        "First they try it the messy way. Leo puts his red car on a high ramp. Maya puts her blue car on a low ramp. The red car goes farther, and Leo cheers. But Maya frowns. \"Your car is not my car. Maybe your car is just faster.\"",
        "So they try again. This time they use the same red car every time. They use the same floor and the same start line. They let go without a push. The only thing they change is how high the ramp is.",
        "From the low ramp, the car rolls 4 floor tiles. From the high ramp, it rolls 7 tiles. They try each ramp three times, and the high ramp wins every time. Only the ramp changed, so they can say the higher ramp helped this car go farther.",
    ],
    "activity": {
        "title": "Ramp race",
        "minutes": 15,
        "materials": [
            "A toy car, or a ball that rolls",
            "Two hardcover books",
            "A flat board or a piece of stiff cardboard",
            "Masking tape or a sticky note for the start line",
            "Paper and a pencil",
        ],
        "steps": [
            "Lean the board on one book. This is the low ramp.",
            "Put tape on the floor at the bottom of the ramp. This is the start line.",
            "Hold the car at the top. Let go. Do not push.",
            "Where did it stop? Count floor tiles or footsteps, or put a sticky note there.",
            "Do it two more times. Write down each result.",
            "Add the second book. Now it is a high ramp. Use the same car and the same start line.",
            "Do it three times again. Write down each result.",
            "Look at your results. Which ramp sent the car farther most of the time?",
        ],
        "record": "Make a table with two rows, Low ramp and High ramp, and three boxes in each row for your three tries.",
        "safety": "Use a clear floor away from stairs. Keep small toy parts away from babies and toddlers.",
    },
    "guided": {"prompt": "Look at Maya and Leo's first try. Which two things changed at the same time?",
               "answer": "The car changed and the ramp changed. With two changes, they could not tell which one made the difference."},
    "try_it": [
        {"prompt": "You want to know if a ball bounces higher on a hard floor or on a rug. What will you change? What will you keep the same?",
         "answer": "Change the place: floor or rug. Keep the same ball, drop it from the same height, and let go the same way each time, with no throwing."},
        {"prompt": "Sam folds two paper airplanes. One has sharp folds and one has soft folds. Sam throws the sharp one hard and the soft one gently. Is that fair? How could Sam fix it?",
         "answer": "It is not fair, because two things changed: the folds and the throw. Sam should throw both planes the same way, from the same spot, a few times each."},
    ],
    "talk": [
        "Why did Maya and Leo try each ramp three times, not just once?",
        "Can you think of a test that was not fair? What would make it fair?",
        "What is hard about keeping everything the same?",
    ],
    "check": [
        {"question": "You want to know if water helps a bean plant grow. Which test is fair?",
         "options": ["Two plants in the same kind of pot by the same window. One gets water and one does not.",
                     "One plant by the window gets water. One plant in a dark closet gets no water.",
                     "Water one plant and look at it a minute later."],
         "answer": 0,
         "explanation": "In the fair test, only the water is different. In the second test the light is different too, so you could not tell what made the difference."},
        {"question": "Why do we do a test more than once?",
         "options": ["One try can come out different just by chance.", "The first try is always wrong.", "It makes the test take longer."],
         "answer": 0,
         "explanation": "One try can be odd. A bump on the floor or a wobbly start can change it. If the same thing happens again and again, you can trust it more."},
        {"question": "Remember Lesson 3. When you watch a change, what do you write down first?",
         "options": ["What it looked like before and after", "Why it changed", "What you hoped would happen"],
         "answer": 0, "review_of": "L0-03",
         "explanation": "First write what you saw, before and after. The why comes later, after you test it."},
    ],
    "connect": ("Scientists call a test like this an experiment. Later in this course you will see why it is so useful. "
                "When you change one thing on purpose, you can find out what it causes. Much later, you will meet the world of "
                "very tiny things, where just looking can change what you look at. There, making a fair test becomes a real puzzle."),
    "grownups": {
        "why": ("This lesson introduces controlled comparison, the core of experimental science. In the Next Generation Science "
                "Standards, K-2 investigations build toward simple investigations based on fair tests, and planning investigations "
                "in which variables are controlled belongs to the grades 3 to 5 band [@ngss_appf]. So the goal here is the idea of "
                "changing one thing, not formal variable control. Young children already learn causes from evidence "
                "[@gopnik2000]; a fair test turns that instinct into a method."),
        "misconceptions": [
            "Changing several things at once is quicker, so it is better. (It hides which change mattered.)",
            "One try is enough if the result looks clear. (A single try can be a fluke.)",
            "If the high ramp won, higher ramps always win. (The result holds for this car on this floor; other cars or floors might differ.)",
        ],
        "simplify": "Use one change and two tries for each ramp. Let the child mark stopping spots with sticky notes instead of counting.",
        "extend": "Try three ramp heights and draw a picture graph of the results [@ccss_math]. Ask: does each extra book add the same distance?",
    },
    "caution": "Keeping the things you can see the same does not guarantee that every other cause is the same. A fair test makes a conclusion much more trustworthy, not certain.",
    "sources": ["ngss_appf", "gopnik2000", "ccss_math"],
    "lab": "causal",
}

d["lessons"] = [L04 if L["id"] == "L0-04" else L for L in d["lessons"]]
SRC.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Level 0 blueprint and model lesson written to", SRC)
