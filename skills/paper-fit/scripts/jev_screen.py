#!/usr/bin/env python3
"""Paper Fit, Jev mode: search arXiv and screen candidates with TypeSafe Jev.

Moves the "read 30 abstracts and rank them" step out of Claude's context.
Jev judges each paper against the Need Spec; this script does the arithmetic
and returns a short ranked table. Claude then verifies the top few and writes.

Usage:
    python3 jev_screen.py spec.json            # search + screen, prints compact JSON
    python3 jev_screen.py spec.json --dry-run  # show what would be sent to Jev, no API call

spec.json:
{
  "goal": "one sentence: the decision or outcome the paper must support",
  "queries": ["2-3 search phrases in the user's own terms"],
  "must": {"R1": "hard requirement", "R2": "..."},
  "deal_breakers": {"D1": "..."},          # optional
  "year_min": 2018,                        # optional
  "max_candidates": 30,                    # optional
  "top_k": 6                               # optional
}

Privacy: only `goal`, the requirement wording, and public titles/abstracts are
sent to Jev (via OpenRouter). Do not put private project details in the spec.

Key: $OPENROUTER_API_KEY, else $JEV_DIR/openrouter_key (default ~/.config/jev).
The key is never printed. Exit code 2 = no key (fall back to the normal flow).
"""
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

JEV_URL = "https://openrouter.ai/api/alpha/decisions"
JEV_MODEL = "typesafe/jev-1.13"
ARXIV_URL = "https://export.arxiv.org/api/query"
ATOM = {"a": "http://www.w3.org/2005/Atom"}
STOP = {"a", "an", "the", "of", "for", "in", "on", "and", "or", "to", "with", "using", "via", "from"}

# Jev confidence thresholds (from the jev-sort skill; tune on real data)
CONF_MIN = 0.7
NOUL_UNSURE = (0.3, 0.7)

FIT_LEVELS = [
    "Different subject: the paper is not about the topic of `goal`.",
    "Same broad area as `goal`, but it studies a different problem than the one `goal` needs.",
    "Studies the problem in `goal`, but would only serve as background or related work for it.",
    "Directly usable for `goal`: its method, data, tool or results could be applied, reproduced or compared against.",
]


def load_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        f = Path(os.environ.get("JEV_DIR", Path.home() / ".config" / "jev")) / "openrouter_key"
        if f.exists():
            key = f.read_text().strip()
    return key


def http(req, timeout, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1:
                time.sleep(2 ** i * 1.5)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if i < tries - 1:
                time.sleep(2 ** i)
                continue
            raise


def search_arxiv(queries, max_candidates, year_min):
    per_q = max(5, -(-max_candidates // max(1, len(queries))))
    seen, out = set(), []
    for n, q in enumerate(queries):
        if n:
            time.sleep(3)  # arXiv API etiquette
        params = urllib.parse.urlencode({
            "search_query": " AND ".join(f"all:{w}" for w in q.split() if w.lower() not in STOP),
            "start": 0, "max_results": per_q, "sortBy": "relevance",
        })
        root = ET.fromstring(http(urllib.request.Request(f"{ARXIV_URL}?{params}"), 30))
        for e in root.findall("a:entry", ATOM):
            aid = e.findtext("a:id", "", ATOM).rsplit("/abs/", 1)[-1].split("v")[0]
            year = int(e.findtext("a:published", "0000", ATOM)[:4])
            if not aid or aid in seen or (year_min and year < year_min):
                continue
            seen.add(aid)
            out.append({
                "id": aid,
                "year": year,
                "title": " ".join(e.findtext("a:title", "", ATOM).split()),
                "abstract": " ".join(e.findtext("a:summary", "", ATOM).split()),
            })
    return out[:max_candidates]


def build_questions(spec):
    qs = {"fit": {
        "type": "score",
        "instructions": "How useful is the paper described by `title` and `abstract` for `goal`?",
        "criteria": FIT_LEVELS,
    }}
    for rid, text in spec.get("must", {}).items():
        qs[f"must_{rid}"] = {
            "type": "noul",
            "instructions": f"Based only on `title` and `abstract`, does this paper satisfy this requirement: {text}",
            "criteria": {"true": f"The abstract clearly indicates: {text}",
                         "false": "The abstract does not indicate this, or indicates the opposite."},
        }
    for did, text in spec.get("deal_breakers", {}).items():
        qs[f"deal_{did}"] = {
            "type": "noul",
            "instructions": f"Based only on `title` and `abstract`, does this apply to the paper: {text}",
            "criteria": {"true": f"The abstract clearly indicates: {text}",
                         "false": "The abstract does not indicate this."},
        }
    return qs


def ask_jev(key, spec, paper, questions):
    payload = {"model": JEV_MODEL, "questions": questions,
               "state": {"goal": spec["goal"], "title": paper["title"], "abstract": paper["abstract"]}}
    req = urllib.request.Request(JEV_URL, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    t0 = time.time()
    body = json.loads(http(req, 30))
    return body, time.time() - t0


def label(p):
    lo, hi = NOUL_UNSURE
    return "yes" if p >= hi else "not stated" if p <= lo else "?"


def judge(paper, body, spec):
    a = body["answers"]
    fit = a["fit"]
    row = {
        "id": paper["id"], "year": paper["year"], "title": paper["title"][:110],
        "fit": round(float(fit["score"]), 2), "fit_conf": round(float(fit.get("confidence", 0)), 2),
        "must": {}, "deal": {}, "flags": [],
    }
    must_p = []
    for rid in spec.get("must", {}):
        p = float(a[f"must_{rid}"]["noul"])
        must_p.append(p)
        row["must"][rid] = label(p)
        if row["must"][rid] == "?":
            row["flags"].append(f"verify {rid}")
    excluded = False
    for did in spec.get("deal_breakers", {}):
        p = float(a[f"deal_{did}"]["noul"])
        row["deal"][did] = label(p)
        if p >= NOUL_UNSURE[1]:
            excluded = True
        elif row["deal"][did] == "?":
            row["flags"].append(f"check {did}")
    if row["fit_conf"] < CONF_MIN:
        row["flags"].append("Claude's call: fit unsure")
    # Ranking is plain arithmetic in code (Jev is not used for math).
    fit_norm = row["fit"] / (len(FIT_LEVELS) - 1)
    must_mean = statistics.mean(must_p) if must_p else 1.0
    row["rank_score"] = round(0.6 * fit_norm + 0.4 * must_mean, 3)
    return row, excluded, float(body.get("usage", {}).get("cost", 0) or 0)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    spec = json.loads(Path(argv[1]).read_text())
    for field in ("goal", "queries", "must"):
        if not spec.get(field):
            print(json.dumps({"error": f"spec is missing '{field}'"}))
            return 1
    top_k = int(spec.get("top_k", 6))
    papers = search_arxiv(spec["queries"], int(spec.get("max_candidates", 30)), spec.get("year_min"))
    questions = build_questions(spec)

    if "--dry-run" in argv:
        print(json.dumps({"would_send_per_paper": {"state_fields": ["goal", "title", "abstract"],
                                                   "goal": spec["goal"], "questions": questions},
                          "n_candidates": len(papers)}, indent=2))
        return 0

    key = load_key()
    if not key:
        print(json.dumps({"error": "no OpenRouter key found; use the normal Paper Fit flow"}))
        return 2

    rows, excluded, costs, lat, failed = [], [], [], [], []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(ask_jev, key, spec, p, questions): p for p in papers}
        for fut, p in futures.items():
            try:
                body, dt = fut.result()
                row, is_out, cost = judge(p, body, spec)
                (excluded if is_out else rows).append(row if not is_out else {"id": row["id"], "title": row["title"], "deal": row["deal"]})
                costs.append(cost)
                lat.append(dt)
            except Exception as e:  # never include request headers in errors
                failed.append({"id": p["id"], "error": type(e).__name__})

    rows.sort(key=lambda r: r["rank_score"], reverse=True)
    abstract_chars = sum(len(p["abstract"]) for p in papers)
    out = {
        "goal": spec["goal"],
        "source": "arXiv",
        "top": rows[:top_k],
        "excluded_by_deal_breaker": excluded[:10],
        "stats": {
            "candidates": len(papers), "screened": len(rows) + len(excluded), "failed": len(failed),
            "jev_cost_usd": round(sum(costs), 5),
            "median_latency_s": round(statistics.median(lat), 2) if lat else None,
            "abstract_chars_kept_out_of_context": abstract_chars,
        },
        "legend": {"fit": "0-3: 0 different subject, 1 different problem, 2 background only, 3 directly usable",
                   "must": "yes = abstract says so; ? = unclear; not stated = abstract silent (often true for code/data, verify in full text)"},
    }
    if failed:
        out["failed"] = failed
    print(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
