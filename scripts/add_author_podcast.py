"""Unit `author-podcast`: add Decoding Causality (Season 1) episodes, verified via Spotify oEmbed.  Run from book/.

Titles are copied from Spotify's oEmbed response (whitespace trimmed).  Levels and
"why" lines follow the show page's own episode descriptions
(https://pozapas.github.io/podcasts/decoding-causality/).
"""
import datetime
import json
import pathlib
import time

import requests

BOOK = pathlib.Path(__file__).resolve().parents[1]
SHOW = "Decoding Causality (the course author's podcast)"
PAGE = "https://pozapas.github.io/podcasts/decoding-causality/"
EPS = [  # spotify id, level, topic, why (from the show page's description)
    ("6gXdZ6jQhUm2xND0mfAS30", 2, "asking why", "How people moved from collecting data to asking why things happen; a gentle start for Level 2."),
    ("3vJJNCdtotb3WWTak1oW13", 2, "history of causal inference", "From Galton to the statistical revolution: how causal questions became science."),
    ("5nyqFj3QdEkTNW5yEs0AOz", 2, "Bayes and evidence", "Reasoning from effect to cause with Bayes' rule; pairs with lesson L2-05."),
    ("5D1Sbm80tpOy05jUB7p3qH", 4, "confounding", "Confounding and how experiments, causal diagrams, and adjustment remove it; pairs with L4-03 and L4-04."),
    ("4iiPLwWoXq4TdGy0qPmGla", 4, "observational causal inference", "How to argue for causation when an experiment is impossible or unethical."),
    ("7C1YCvYz4NAEOuJ19LrNvn", 2, "Simpson's paradox", "Simpson's paradox and other puzzles where data mislead intuition; pairs with L2-06."),
    ("3Bchlql1C5pRfSu6oArUkt", 4, "interventions", "Predicting the effect of an intervention, the second rung of the ladder of causation; pairs with L4-05."),
    ("1OVkpXRALANG3DZoPc9q9p", 4, "counterfactuals", "Counterfactuals with structural causal models and potential outcomes; pairs with L4-09."),
    ("2CQ7mLuX7XpNHGeqDZjNMX", 4, "mediation", "Mediation: how causes travel to their effects, with path diagrams."),
    ("4XrnLDGvJZBN2TAza6VrCu", 7, "causal AI", "Whether machines can learn to ask why; the gap between prediction and causal understanding."),
    ("6s4vONEdxmI3eEUYWS8VYc", 4, "season recap", "A closing recap that ties the ladder of causation, counterfactuals, mediation, and bias together."),
]
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
page = requests.get(PAGE, timeout=30)
assert page.status_code == 200 and "Decoding Causality" in page.text and "Season 1: The Book of Why" in page.text

media = json.loads((BOOK / "_data/media.json").read_text(encoding="utf-8"))
mv = json.loads((BOOK / "_data/media-verification.json").read_text(encoding="utf-8"))
media["podcasts"] = [p for p in media["podcasts"] if not p.get("author")]
mv["podcasts"] = [r for r in mv["podcasts"] if r.get("source") != "spotify-oembed-author"]
for sid, level, topic, why in EPS:
    url = f"https://open.spotify.com/episode/{sid}"
    assert sid in page.text, sid  # the episode is embedded on the show page
    r = requests.get("https://open.spotify.com/oembed", params={"url": url},
                     headers={"User-Agent": "qcai-book-verifier/1.0"}, timeout=30)
    title = r.json()["title"].strip()
    media["podcasts"].append({"show": SHOW, "episode": title, "url": url, "level": level, "topic": topic,
                              "why": why, "verified_via": "Spotify oEmbed", "author": True})
    mv["podcasts"].append({"source": "spotify-oembed-author", "endpoint": r.url, "status": r.status_code, "result": "PASS" if r.ok else "FAIL",
                           "fetched_title": title, "episodeUrl": url, "show_page": PAGE, "checked_at": now})
    time.sleep(0.5)
media["author_podcast"] = {"show": "Decoding Causality", "page": PAGE,
                           "playlist": "https://www.youtube.com/playlist?list=PLHU8z2HGsZgYCjYki2tRmCFdRejf7VV4K",
                           "note": ""}
(BOOK / "_data/media.json").write_text(json.dumps(media, indent=1, ensure_ascii=False), encoding="utf-8")
(BOOK / "_data/media-verification.json").write_text(json.dumps(mv, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"added {len(EPS)} verified episodes")
