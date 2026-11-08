"""Verify the curated media list for the QCAI book (unit: media).

  python scripts/verify_media.py          # produce: fetch + verify candidates, write outputs
  python scripts/verify_media.py --check  # re-fetch every stored item, assert exact match + coverage

Produce writes _data/media.json, _data/media-verification.json, evidence/media-summary.json.
Every stored title/channel/date comes from a response fetched by this script:
  videos   -> YouTube oEmbed (HTTP 200 required; title = oEmbed title verbatim),
              optional lengthSeconds/publishDate/shortDescription from the watch page.
  podcasts -> iTunes Search API (match by trackId; episode = trackName verbatim),
              fallback in --check: the show's RSS feed (<item><title> exact match).
Candidates were found with scripts/discover_media.py; level/topic/why are editorial and
must be supported by the fetched title (and description where recorded).
"""
import datetime, json, pathlib, re, sys, time
import xml.etree.ElementTree as ET
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
PAUSE = 1.2
OEMBED = "https://www.youtube.com/oembed"

# (id, level, topic, why) -- "why" states only what the fetched title/channel supports
VIDEOS = [
    # Level 0: counting, questions, fair tests, light
    ("OinudV2LWlo", 0, "counting", "A very short Khan Academy Kids clip about counting to 10."),
    ("BXFU86GNmrg", 0, "fair tests", "Crash Course Kids episode on isolating variables, the core idea of a fair test."),
    ("DJDBTNbAWOE", 0, "light", "SciShow Kids explains how we see color."),
    ("bcVr13Fw7w8", 0, "light", "SciShow Kids answers why the sky is blue."),
    ("E6iB5B3Lz9I", 0, "asking questions", "SciShow Kids invites children to be field scientists who observe and ask questions."),
    # Level 1: fractions, chance, randomization, waves, models
    ("kZzoVCmUyKg", 1, "fractions", "Khan Academy introduction to fractions."),
    ("KFgvOQtH0Z0", 1, "chance", "Khan Academy builds an intuitive sense of probabilities."),
    ("IAiNqQi30-Y", 1, "chance", "TED-Ed coin-flip puzzle that tests intuitions about probability."),
    ("jL9en6NvQfk", 1, "randomness", "Crash Course Statistics episode on randomness."),
    ("kkBDa-ICvyY", 1, "randomization", "Crash Course Statistics episode on controlled experiments."),
    ("V2yO8biphSo", 1, "waves", "SciShow Kids explains what waves are."),
    # Level 2: algebra, Bayes, causal graphs, evidence
    ("HZGCoVF3YvM", 2, "Bayes' rule", "3Blue1Brown presents Bayes' theorem as the geometry of changing beliefs."),
    ("lG4VkPoG3ko", 2, "evidence", "3Blue1Brown uses the medical test paradox to show how evidence updates probabilities."),
    ("GtV-VYdNt_g", 2, "correlation vs causation", "Crash Course Statistics explains why correlation does not equal causation."),
    ("DXBPtpBhGqo", 2, "intro to causal inference", "Brady Neal's course-preview lecture giving a brief introduction to causal inference."),
    # Level 3: complex numbers, vectors, matrices, tensors, calculus, entropy
    ("5PcpBw5Hbwo", 3, "complex numbers", "3Blue1Brown live lecture on complex number fundamentals."),
    ("fNk_zzaMoSs", 3, "vectors", "Chapter 1 of 3Blue1Brown's Essence of Linear Algebra, on vectors."),
    ("kYB8IZa5AuE", 3, "matrices", "3Blue1Brown shows matrices as linear transformations."),
    ("f5liqUk0ZTw", 3, "tensors", "Dan Fleisch gives a short visual answer to the question of what a tensor is."),
    ("WUvTyaaNkzM", 3, "calculus", "Opening chapter of 3Blue1Brown's Essence of Calculus."),
    ("v68zYyaEmEA", 3, "entropy", "3Blue1Brown uses Wordle to introduce information-theoretic entropy."),
    # Level 4: classical causal AI
    ("AuZu0L0PEgk", 4, "structural causal models", "Brady Neal's lecture on causal models."),
    ("M-mF6bXlxHI", 4, "do-calculus", "Brady Neal's lecture segment on Pearl's do-calculus."),
    ("mujOFx5oZUQ", 4, "d-separation and do-calculus", "Simons Institute tutorial on causal graphical models, d-separation and do-calculus."),
    ("fvQJ9gelUg0", 4, "causal discovery", "Simons Institute tutorial on classical strategies and concepts in causal discovery."),
    ("ZaPV1OSEpHw", 4, "causal AI overview", "Judea Pearl's PyData keynote on the new science of cause and effect."),
    ("13idxIjOdNQ", 4, "causal representation learning", "Mila talk arguing causal representation learning is a natural fit for mechanistic interpretability."),
    ("btmJtThWmhA", 4, "causality for machine learning", "Bernhard Schoelkopf's MLSS 2020 lecture on causality (part 1)."),
    # Level 5: quantum information
    ("3-c4xJa7Flk", 5, "qubits and states", "Lesson 1 of John Watrous's Qiskit course: single quantum systems."),
    ("DfZZS8Spe7U", 5, "multiple qubits", "Lesson 2 of the Watrous Qiskit course: multiple systems."),
    ("CeK9ry8G8HQ", 5, "density matrices", "Watrous Qiskit lesson on density matrices."),
    ("GSsElSQgMbU", 5, "entanglement", "Lesson 4 of the Watrous Qiskit course: entanglement in action."),
    ("Xi9YTYzQErY", 5, "measurement", "Watrous Qiskit lesson 11 on general measurements."),
    ("cMl-xIDSmXI", 5, "channels", "Watrous Qiskit lesson on quantum channels."),
    ("9OM0jSTeeBg", 5, "Bell tests", "Qiskit explainer on Bell's inequality, tied to the 2022 Nobel Prize."),
    ("mKpURUtQgZ4", 5, "noise", "First lecture of Tobias Osborne's course on the theory of quantum noise and decoherence."),
    # Level 6: quantum causal models
    ("1qzA-SKb4AM", 6, "quantum causal inference", "Perimeter Institute public lecture by Robert Spekkens and Elie Wolfe on the quantum physicist as causal detective."),
    ("-ul2XJ1-1Rc", 6, "classical vs quantum causal inference", "First class of Robert Spekkens's ICTP-SAIFR course on classical and quantum causal inference."),
    ("D2N3M9-QWk0", 6, "quantum causal models", "Robin Lorenz gives an introduction and overview of quantum causal models."),
    ("V356Lb5RH8c", 6, "indefinite causal order", "Ognyan Oreshkov on indefinite causal order in quantum mechanics."),
    ("vLLw_uQNR8s", 6, "process matrices", "QPL 2020 talk by Timothee Hoffreumon on the multi-round process matrix."),
    ("LLDaoLdwyrk", 6, "quantum switch", "Giulio Chiribella reviews ten years of the quantum SWITCH."),
    ("NSUCVJdLtto", 6, "indefinite causal order", "Caslav Brukner on quantum correlations with indefinite causal order."),
    # Level 7: research integration
    ("qiRtUUZ5s9s", 7, "variational quantum algorithms", "PennyLane tutorial on the variational quantum eigensolver."),
    ("VVY8xcps3N4", 7, "quantum machine learning", "Maria Schuld's IPAM talk on how to rethink quantum machine learning."),
    ("zw3JYUrS-v8", 7, "quantum kernels", "Qiskit lecture on quantum feature spaces and kernels."),
    ("Q0XEvj0GsaE", 7, "barren plateaus", "Patrick Coles on barren plateau landscapes in variational quantum algorithms."),
    ("XwfLGq6f5_A", 7, "classical shadows", "Stefan Sack on avoiding barren plateaus using classical shadows."),
    ("CUHIa_O06Dg", 7, "quantum causal inference", "Simons Institute talk on causal discovery in the quantum context."),
]

# (search_term, trackId, level, topic, why)
PODCASTS = [
    ("How do lightbulbs work? Brains On", 1000773852958, 0, "light", "Brains On!, a science podcast for kids, explains how lightbulbs work."),
    ("Glow for it! How do creatures make light? Brains On", 1000600784145, 0, "light", "Brains On! episode on how living creatures make their own light."),
    ("Causal Inference, Clinical Trials & Randomization Stephen Senn", 1000649609807, 1, "randomization", "Causal Bandits episode with Stephen Senn on causal inference, clinical trials and randomization."),
    ("Branden Fitelson on the Logic and Use of Probability", 1000708995363, 2, "probability and evidence", "Mindscape conversation with Branden Fitelson on the logic and use of probability."),
    ("Causality 101 with Robert Osazuwa Ness", 1000463832600, 2, "causal graphs", "TWIML introductory episode on causality with Robert Osazuwa Ness."),
    ("Judea Pearl on Cause and Effect", 1000560068180, 4, "causal AI", "Sean Carroll talks with Judea Pearl about cause and effect."),
    ("Judea Pearl: Causal Reasoning, Counterfactuals, Bayesian Networks, and the Path to AGI", 1000459318976, 4, "counterfactuals", "Lex Fridman interviews Judea Pearl on causal reasoning, counterfactuals and Bayesian networks."),
    ("Weakly Supervised Causal Representation Learning with Johann Brehmer", 1000590314852, 4, "causal representation learning", "TWIML episode with Johann Brehmer on weakly supervised causal representation learning."),
    ("Graphs for Causal AI Data Skeptic", 1000709692552, 4, "causal graphs in AI", "Data Skeptic episode on graphs for causal AI."),
    ("Scott Aaronson: Quantum Computing Lex Fridman", 1000465877765, 5, "quantum computing", "Lex Fridman interviews Scott Aaronson about quantum computing."),
    ("Rob Spekkens: Why the Quantum Wave Function Is Not Real", 1000747749302, 6, "quantum foundations", "Theories of Everything interview with Robert Spekkens on why he holds the quantum wave function is not real."),
    ("Pragmatic Quantum Machine Learning with Peter Wittek", 1000433910923, 7, "quantum machine learning", "TWIML episode with Peter Wittek on pragmatic quantum machine learning."),
    ("A Quantum Machine Learning Algorithm Takedown with Ewin Tang", 1000433910924, 7, "dequantization", "TWIML bonus episode with Ewin Tang on a quantum machine learning algorithm takedown."),
    ("Quantum Machine Learning, with Dr. Amira Abbas", 1000662769630, 7, "quantum machine learning", "Super Data Science episode with Amira Abbas on quantum machine learning."),
]

# screened out during discovery without fetching (not counted as verified)
SCREENED = [
    {"kind": "video", "id": "_Qh0F3B6kOU", "reason": "irrelevant (fan clip, not educational)"},
    {"kind": "video", "id": "42OiBzfdE2o", "reason": "series trailer only (0:39); full lessons preferred"},
    {"kind": "video", "id": "ub98C4OUD0E", "reason": "short podcast clip; full Pearl talks/podcasts preferred"},
    {"kind": "video", "id": "B3U1NDUiwSA", "reason": "not from a preferred reputable educational source"},
    {"kind": "podcast", "id": "1000788652587", "reason": "unknown show (The Quantum Computing Revolution Podcast); provenance/quality unclear"},
]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def get(url, **kw):
    for i in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=30, **kw)
            if r.status_code in (403, 429, 500, 502, 503) and i < 2:
                time.sleep(5 * (i + 1))
                continue
            return r
        except requests.RequestException as e:
            if i == 2:
                return e
            time.sleep(5)


def oembed(vid):
    url = f"https://www.youtube.com/watch?v={vid}"
    r = get(OEMBED, params={"url": url, "format": "json"})
    rec = {"endpoint": f"{OEMBED}?url={url}&format=json", "checked_at": now()}
    if isinstance(r, Exception):
        rec.update(status=None, error=str(r))
        return rec, None
    rec["status"] = r.status_code
    if r.status_code != 200:
        return rec, None
    j = r.json()
    rec.update(fetched_title=j.get("title"), author_name=j.get("author_name"), author_url=j.get("author_url"))
    return rec, j


def watch_meta(vid):
    r = get(f"https://www.youtube.com/watch?v={vid}")
    out = {}
    if isinstance(r, Exception) or r.status_code != 200:
        return out
    t = r.text
    m = re.search(r'"lengthSeconds":"(\d+)"', t)
    if m:
        out["duration_s"] = int(m.group(1))
    m = re.search(r'"publishDate":"([^"]+)"', t)
    if m:
        out["published"] = m.group(1)[:10]
    m = re.search(r'"shortDescription":"((?:[^"\\]|\\.)*)"', t)
    if m:
        try:
            out["description_snippet"] = json.loads('"' + m.group(1) + '"')[:400]
        except ValueError:
            pass
    return out


def itunes_search(term):
    r = get("https://itunes.apple.com/search",
            params={"term": term, "media": "podcast", "entity": "podcastEpisode", "limit": 50})
    if isinstance(r, Exception):
        return None, [], str(r)
    if r.status_code != 200:
        return r.status_code, [], ""
    try:
        return 200, r.json().get("results", []), ""
    except ValueError:
        return r.status_code, [], "bad json"


def rss_has_title(feed_url, title):
    r = get(feed_url)
    if isinstance(r, Exception) or r.status_code != 200:
        return getattr(r, "status_code", None), False
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        return r.status_code, False
    titles = {(it.findtext("title") or "").strip() for it in root.iter("item")}
    return r.status_code, title.strip() in titles


def produce():
    videos, pods = [], []
    ver = {"generated_at": now(), "videos": [], "podcasts": [], "rejected": []}
    for vid, level, topic, why in VIDEOS:
        rec, j = oembed(vid)
        time.sleep(PAUSE)
        rec["id"] = vid
        if not j:
            rec["result"] = "REJECTED"
            rec["reason"] = f"oEmbed HTTP {rec.get('status')}"
            ver["rejected"].append(rec)
            print("REJECT", vid, rec.get("status"))
            continue
        meta = watch_meta(vid)
        time.sleep(PAUSE)
        rec["watch_page"] = meta
        rec["result"] = "PASS"
        ver["videos"].append(rec)
        item = {"id": vid, "title": j["title"], "channel": j["author_name"], "channel_url": j["author_url"],
                "url": f"https://www.youtube.com/watch?v={vid}", "level": level, "topic": topic, "why": why}
        for k in ("duration_s", "published"):
            if k in meta:
                item[k] = meta[k]
        videos.append(item)
        print("OK", level, vid, j["title"], "|", j["author_name"])
    for term, tid, level, topic, why in PODCASTS:
        status, res, err = itunes_search(term)
        time.sleep(PAUSE)
        endpoint = ("https://itunes.apple.com/search?term=" + requests.utils.quote(term)
                    + "&media=podcast&entity=podcastEpisode&limit=50")
        hit = next((x for x in res if x.get("trackId") == tid), None)
        rec = {"trackId": tid, "search_term": term, "endpoint": endpoint, "status": status, "checked_at": now()}
        if not hit:
            rec.update(result="REJECTED", reason=f"trackId not in iTunes results (HTTP {status}) {err}".strip())
            ver["rejected"].append(rec)
            print("REJECT pod", tid, status)
            continue
        rec.update(result="PASS", fetched_title=hit.get("trackName"), collectionName=hit.get("collectionName"),
                   releaseDate=hit.get("releaseDate"), trackViewUrl=hit.get("trackViewUrl"),
                   episodeUrl=hit.get("episodeUrl"), feedUrl=hit.get("feedUrl"),
                   trackTimeMillis=hit.get("trackTimeMillis"))
        ver["podcasts"].append(rec)
        item = {"show": hit["collectionName"], "episode": hit["trackName"],
                "released": (hit.get("releaseDate") or "")[:10], "url": hit.get("trackViewUrl"),
                "level": level, "topic": topic, "why": why,
                "verified_via": f"iTunes Search API (term={term!r}, trackId={tid})", "itunes_track_id": tid}
        if hit.get("trackTimeMillis"):
            item["duration_min"] = round(hit["trackTimeMillis"] / 60000)
        if hit.get("feedUrl"):
            item["feed_url"] = hit["feedUrl"]
        pods.append(item)
        print("OK pod", level, hit["trackName"], "|", hit["collectionName"])
    for s in SCREENED:
        ver["rejected"].append(dict(s, result="SCREENED_OUT", checked_at=None))
    videos.sort(key=lambda v: v["level"])
    pods.sort(key=lambda p: p["level"])
    (ROOT / "_data").mkdir(exist_ok=True)
    (ROOT / "evidence").mkdir(exist_ok=True)
    (ROOT / "_data/media.json").write_text(
        json.dumps({"videos": videos, "podcasts": pods}, indent=1, ensure_ascii=False), encoding="utf-8")
    (ROOT / "_data/media-verification.json").write_text(json.dumps(ver, indent=1, ensure_ascii=False), encoding="utf-8")
    summary = {"generated_at": now(), "videos_total": len(videos), "podcasts_total": len(pods),
               "videos_per_level": {str(l): sum(v["level"] == l for v in videos) for l in range(8)},
               "podcasts_per_level": {str(l): sum(p["level"] == l for p in pods) for l in range(8)},
               "rejected_after_fetch": sum(r["result"] == "REJECTED" for r in ver["rejected"]),
               "screened_out_before_fetch": sum(r["result"] == "SCREENED_OUT" for r in ver["rejected"])}
    (ROOT / "evidence/media-summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


def check():
    data = json.loads((ROOT / "_data/media.json").read_text(encoding="utf-8"))
    fails, log = [], {"checked_at": now(), "videos": [], "podcasts": []}
    for v in data["videos"]:
        rec, j = oembed(v["id"])
        time.sleep(PAUSE)
        ok = bool(j) and j.get("title") == v["title"] and j.get("author_name") == v["channel"]
        log["videos"].append({"id": v["id"], "status": rec.get("status"), "fetched_title": rec.get("fetched_title"), "pass": ok})
        if not ok:
            fails.append(f"video {v['id']}: status={rec.get('status')} fetched={rec.get('fetched_title')!r} stored={v['title']!r}")
    for p in data["podcasts"]:
        term = re.search(r"term=('.*?'|\".*?\"), trackId", p["verified_via"]).group(1)[1:-1]
        status, res, err = itunes_search(term)
        time.sleep(PAUSE)
        hit = next((x for x in res if x.get("trackId") == p["itunes_track_id"]), None)
        how = "itunes"
        ok = (status == 200 and hit is not None and hit.get("trackName") == p["episode"]
              and hit.get("collectionName") == p["show"])
        if not ok and p.get("feed_url"):
            st, found = rss_has_title(p["feed_url"], p["episode"])
            time.sleep(PAUSE)
            how = f"rss(HTTP {st})"
            ok = st == 200 and found
        log["podcasts"].append({"episode": p["episode"], "itunes_status": status, "via": how, "pass": ok})
        if not ok:
            fails.append(f"podcast {p['episode']!r}: itunes={status} via={how}")
    per = {l: sum(v["level"] == l for v in data["videos"]) for l in range(8)}
    for l, n in per.items():
        if n < 2:
            fails.append(f"level {l} has only {n} videos")
    log.update(videos_per_level=per, failures=fails, verdict="PASS" if not fails else "FAIL")
    (ROOT / "evidence/media-check.json").write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"videos checked: {len(data['videos'])}, podcasts checked: {len(data['podcasts'])}")
    print("videos per level:", per)
    for f in fails:
        print("FAIL:", f)
    print("RESULT:", log["verdict"])
    return 0 if not fails else 1


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    produce()
