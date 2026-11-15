"""Unit `level37-refs` (part 2): verify and record the primary sources the Level 3-7 writers requested.

Each entry gives a DOI (checked with Crossref) or an arXiv id (checked with the arXiv API) and the
title we expect.  An entry is recorded only if the fetched title matches (token Jaccard >= 0.6).
Run from book/.  Prints a line per entry: PASS or FAIL with the fetched title.
"""
import datetime
import html
import json
import pathlib
import re
import time

import requests

BOOK = pathlib.Path(__file__).resolve().parents[1]
UA = {"User-Agent": "Mozilla/5.0 (qcai-book-verifier/1.0)"}
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

E = [  # key, "doi:..." or "arxiv:...", expected title, levels, scope
    ("wilson1927", "doi:10.1080/01621459.1927.10502953", "Probable inference, the law of succession, and statistical inference", [3], "Wilson score interval for a binomial proportion"),
    ("browncai2001", "doi:10.1214/ss/1009213286", "Interval estimation for a binomial proportion", [3], "Coverage of the Wald and alternative binomial intervals"),
    ("hoeffding1963", "doi:10.1080/01621459.1963.10500830", "Probability inequalities for sums of bounded random variables", [3, 6, 7], "Hoeffding's inequality"),
    ("dunn1961", "doi:10.1080/01621459.1961.10482090", "Multiple comparisons among means", [3], "Bonferroni-type multiple comparison correction"),
    ("tianpearl2000", "doi:10.1023/A:1018912507879", "Probabilities of causation: bounds and identification", [4], "Bounds on probabilities of causation (PN, PS, PNS)"),
    ("kusner2017", "arxiv:1703.06856", "Counterfactual Fairness", [4], "Definition of counterfactual fairness"),
    ("pearlbareinboim2014", "doi:10.1214/14-STS486", "External validity: from do-calculus to transportability across populations", [4], "Selection diagrams and transportability"),
    ("bareinboimpearl2016", "doi:10.1073/pnas.1510507113", "Causal inference and the data-fusion problem", [4], "Data fusion and transportability overview"),
    ("robins1994", "doi:10.1080/01621459.1994.10476818", "Estimation of regression coefficients when some regressors are not always observed", [4], "Augmented inverse probability weighting"),
    ("chernozhukov2018", "arxiv:1608.00060", "Double/Debiased Machine Learning for Treatment and Causal Parameters", [4], "Double machine learning and cross-fitting"),
    ("kleinberg2016", "arxiv:1609.05807", "Inherent Trade-Offs in the Fair Determination of Risk Scores", [4], "Incompatibility of calibration and balance conditions"),
    ("chouldechova2017", "arxiv:1703.00056", "Fair prediction with disparate impact: A study of bias in recidivism prediction instruments", [4], "Incompatibility of fairness criteria under differing base rates"),
    ("hardt2016", "arxiv:1610.02413", "Equality of Opportunity in Supervised Learning", [4], "Equalized odds and equal opportunity"),
    ("geirhos2020", "arxiv:2004.07780", "Shortcut Learning in Deep Neural Networks", [4], "Shortcut learning"),
    ("lauritzen1990", "doi:10.1002/net.3230200503", "Independence properties of directed Markov fields", [4], "Moralization criterion for directed Markov properties"),
    ("geiger1990", "doi:10.1002/net.3230200504", "Identifying independence in Bayesian networks", [4], "Soundness and completeness of d-separation"),
    ("meek1995", "arxiv:1302.4972", "Causal inference and causal explanation with background knowledge", [4], "Orientation rules for equivalence classes"),
    ("huangvaltorta2006", "arxiv:1206.6831", "Pearl's Calculus of Intervention Is Complete", [4], "Completeness of do-calculus"),
    ("uhler2013", "doi:10.1214/12-AOS1080", "Geometry of the faithfulness assumption in causal inference", [4], "Near-faithfulness violations"),
    ("reisach2021", "arxiv:2102.13647", "Beware of the Simulated DAG! Causal Discovery Benchmarks May Be Easy To Game", [4, 7], "Varsortability in simulated causal discovery benchmarks"),
    ("imbensrubin2015", "doi:10.1017/CBO9781139025751", "Causal Inference for Statistics, Social, and Biomedical Sciences", [4], "Potential outcomes, Neyman variance for randomized experiments"),
    ("neyman1990", "doi:10.1214/ss/1177012031", "On the Application of Probability Theory to Agricultural Experiments. Essay on Principles. Section 9", [4], "Origin of potential outcomes and Neyman's variance"),
    ("rubin1974", "doi:10.1037/h0037350", "Estimating causal effects of treatments in randomized and nonrandomized studies", [4], "Potential outcomes for observational studies"),
    ("tsirelson1980", "doi:10.1007/BF00417500", "Quantum generalizations of Bell's inequality", [5, 6], "Tsirelson's bound 2 sqrt 2"),
    ("popescu1994", "doi:10.1007/BF02058098", "Quantum nonlocality as an axiom", [5, 6], "PR box, no-signalling CHSH value 4"),
    ("giustina2015", "doi:10.1103/PhysRevLett.115.250401", "Significant-Loophole-Free Test of Bell's Theorem with Entangled Photons", [5], "Loophole-free photonic Bell test"),
    ("shalm2015", "doi:10.1103/PhysRevLett.115.250402", "Strong Loophole-Free Test of Local Realism", [5], "Loophole-free photonic Bell test"),
    ("werner1989", "doi:10.1103/PhysRevA.40.4277", "Quantum states with Einstein-Podolsky-Rosen correlations admitting a hidden-variable model", [5, 6], "Werner states: entanglement without Bell violation"),
    ("luders1950", "doi:10.1002/andp.19504430510", "Über die Zustandsänderung durch den Meßprozeß", [5], "Lüders state-update rule"),
    ("peres1996", "doi:10.1103/PhysRevLett.77.1413", "Separability Criterion for Density Matrices", [5, 7], "Positive partial transpose criterion"),
    ("horodecki1996", "doi:10.1016/S0375-9601(96)00706-2", "Separability of mixed states: necessary and sufficient conditions", [5], "PPT is sufficient for 2x2 and 2x3"),
    ("choi1975", "doi:10.1016/0024-3795(75)90075-0", "Completely positive linear maps on complex matrices", [5, 6], "Choi's theorem"),
    ("fujiwara1999", "doi:10.1103/PhysRevA.59.3290", "One-to-one parametrization of quantum channels", [5], "Complete positivity conditions for qubit channels"),
    ("suresh2023", "arxiv:2302.11783", "A Semantics for Counterfactuals in Quantum Causal Models", [6], "Counterfactuals in quantum causal models"),
    ("fine1982", "doi:10.1103/PhysRevLett.48.291", "Hidden Variables, Joint Probability, and the Bell Inequalities", [6], "CHSH inequalities characterize local correlators"),
    ("branciard2016", "arxiv:1508.01704", "The simplest causal inequalities and their violation", [6], "Simplest causal inequalities"),
    ("chiribella2012", "arxiv:1109.5154", "Perfect discrimination of no-signalling channels via quantum superposition of causal structures", [6], "Switch discriminates commuting from anticommuting unitaries"),
    ("wierichs2022", "doi:10.22331/q-2022-03-30-677", "General parameter-shift rules for quantum gradients", [7], "General parameter-shift rules"),
    ("thanasilp2024", "doi:10.1038/s41467-024-49287-w", "Exponential concentration in quantum kernel methods", [7], "Exponential concentration of quantum kernels"),
    ("tsamardinos2006", "doi:10.1007/s10994-006-6889-7", "The max-min hill-climbing Bayesian network structure learning algorithm", [7], "Structural Hamming distance"),
    ("kaufman2012", "doi:10.1145/2382577.2382579", "Leakage in data mining", [7], "Data leakage"),
    ("cerezo2021", "doi:10.1038/s41467-021-21728-w", "Cost function dependent barren plateaus in shallow parametrized quantum circuits", [7], "Global vs local cost barren plateaus"),
    ("horodecki1996pra", "doi:10.1103/PhysRevA.54.1838", "Information-theoretic aspects of inseparability of mixed states", [7], "Bell-diagonal states tetrahedron"),
    ("grover1996", "arxiv:quant-ph/9605043", "A fast quantum mechanical algorithm for database search", [7], "Grover search query count"),
    ("bbbv1997", "arxiv:quant-ph/9701001", "Strengths and Weaknesses of Quantum Computing", [7], "Optimality of Grover search"),
    ("demkowicz2012", "doi:10.1038/ncomms2067", "The elusive Heisenberg limit in quantum-enhanced metrology", [7], "Noise reduces Heisenberg scaling to a constant factor"),
    ("armitage1969", "doi:10.2307/2343787", "Repeated significance tests on accumulating data", [7], "Optional stopping inflates false positives"),
    ("howard2021", "doi:10.1214/20-AOS1991", "Time-uniform, nonparametric, nonasymptotic confidence sequences", [7], "Confidence sequences and anytime-valid inference"),
    ("lan1983", "doi:10.1093/biomet/70.3.659", "Discrete sequential boundaries for clinical trials", [7], "Alpha-spending functions"),
    ("navascues2020", "arxiv:1707.06476", "The inflation technique completely solves the causal compatibility problem", [7], "Completeness of the classical inflation hierarchy"),
    ("wolfe2021", "arxiv:1909.10519", "Quantum inflation: A general approach to quantum causal compatibility", [7], "Quantum inflation"),
    ("ligthart2023", "arxiv:2110.14659", "A convergent inflation hierarchy for quantum causal structures", [7], "Convergent quantum inflation hierarchy"),
    ("tang2019", "arxiv:1807.04271", "A quantum-inspired classical algorithm for recommendation systems", [7], "Dequantization of recommendation systems"),
    ("cerezo2025", "arxiv:2312.09121", "Does provable absence of barren plateaus imply classical simulability?", [7], "Trainability versus classical simulability"),
    ("hjpw2004", "arxiv:quant-ph/0304007", "Structure of states which satisfy strong subadditivity of quantum entropy with equality", [6], "States with vanishing quantum conditional mutual information"),
]


def norm(t):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return set(re.findall(r"[a-z0-9]+", t.lower().replace("ü", "u").replace("ß", "ss")))


def fetch(ident):
    if ident.startswith("doi:"):
        doi = ident[4:]
        r = requests.get(f"https://api.crossref.org/works/{doi}", headers=UA, timeout=40)
        if r.status_code != 200:
            return None, r.status_code
        m = r.json()["message"]
        t = re.sub(r"\s+", " ", (m.get("title") or [""])[0]).strip()
        auth = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in m.get("author", [])]
        year = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
        venue = (m.get("container-title") or [m.get("publisher", "")])[0]
        return {"title": t, "authors": auth, "year": year, "venue": venue, "doi": doi, "url": f"https://doi.org/{doi}",
                "method": "Crossref works/<doi>", "checked": r.url}, 200
    aid = ident[6:]
    r = requests.get(f"http://export.arxiv.org/api/query?id_list={aid}", headers=UA, timeout=40)
    if r.status_code != 200:
        return None, r.status_code
    x = r.text
    ent = x.split("<entry>", 1)[1] if "<entry>" in x else ""
    t = re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", ent, re.S).group(1)).strip() if ent else ""
    auth = [re.sub(r"\s+", " ", a).strip() for a in re.findall(r"<name>(.*?)</name>", ent, re.S)]
    year = int(re.search(r"<published>(\d{4})", ent).group(1)) if ent else None
    return {"title": t, "authors": auth, "year": year, "venue": f"arXiv:{aid}", "url": f"https://arxiv.org/abs/{aid}",
            "method": "arXiv API id_list", "checked": r.url}, 200


def main():
    src = json.loads((BOOK / "_data/sources.json").read_text(encoding="utf-8"))
    ver = json.loads((BOOK / "_data/verification.json").read_text(encoding="utf-8"))
    bib = (BOOK / "references.bib").read_text(encoding="utf-8")
    have = {s["id"] for s in src}
    entries, ok = [], 0
    for key, ident, title, levels, scope in E:
        if key in have:
            print("SKIP (exists)", key)
            continue
        m, status = fetch(ident)
        time.sleep(1.0)
        if not m or not m["title"]:
            print("FAIL", key, ident, status)
            continue
        a, b = norm(title), norm(m["title"])
        jac = len(a & b) / max(1, len(a | b))
        if jac < 0.6:
            print(f"FAIL {key} {ident} jaccard {jac:.2f} fetched: {m['title']}")
            continue
        ok += 1
        print(f"PASS {key} ({jac:.2f}) {m['title']} | {m['year']}")
        rec = {"id": key, "title": m["title"], "authors": ", ".join(m["authors"]), "year": m["year"], "venue": m["venue"],
               "url": m["url"], "kind": "paper", "scope": scope, "levels": levels}
        if m.get("doi"):
            rec["doi"] = m["doi"]
        src.append(rec)
        ver[key] = {"status": "PASS", "method": m["method"], "url_checked": m["checked"], "http": 200,
                    "fetched_title": m["title"], "jaccard": round(jac, 3), "checked_at": NOW}
        t = m["title"].replace("{", "").replace("}", "")
        fields = [f"  title = {{{{{t}}}}}", f"  author = {{{' and '.join(m['authors'])}}}", f"  year = {{{m['year']}}}"]
        if m.get("doi"):
            fields += [f"  journal = {{{m['venue']}}}", f"  doi = {{{m['doi']}}}"]
        else:
            fields += [f"  howpublished = {{{m['venue']}}}"]
        fields.append(f"  url = {{{m['url']}}}")
        entries.append(("@article" if m.get("doi") else "@misc") + "{" + key + ",\n" + ",\n".join(fields) + "\n}\n")
    src.sort(key=lambda s: s["id"])
    (BOOK / "_data/sources.json").write_text(json.dumps(src, indent=1, ensure_ascii=False), encoding="utf-8")
    (BOOK / "_data/verification.json").write_text(json.dumps(ver, indent=1, ensure_ascii=False), encoding="utf-8")
    if entries:
        (BOOK / "references.bib").write_text(bib.rstrip() + "\n\n" + "\n".join(entries), encoding="utf-8")
    print(f"recorded {ok} of {len(E)} requested sources")


if __name__ == "__main__":
    main()
