---
name: paper-fit
description: Find the RIGHT research paper for a specific need (course assignment, project, real-world build), then guide deep reading and turn the paper into action. Use when someone asks for a paper for an assignment or project, "find me a paper on X for Y", "which paper should I use", "help me understand this paper", or "how do I use this paper in my project".
---

# Paper Fit (v0)

Finding papers is easy. Finding the paper that fits the actual need is the hard part.
This skill treats paper selection as a requirements problem: write down the need first,
then pick papers that satisfy it, with evidence and traceability.

Built for course-based graduate students and research labs in software engineering,
but the workflow works for any CS/AI topic.

## Principles (apply in every stage)

1. **Requirement before search.** Do not search until a Need Spec exists and the user has confirmed it.
2. **Precision over recall.** Return 3 to 5 papers that fit, not 20 that match keywords.
3. **Every fit claim is traceable.** Each "fits requirement R" claim points to evidence in the paper (section, table, or abstract). Every paper has a resolvable ID (arXiv ID, DOI, or URL) returned by a tool. Never invent papers, authors, venues, or numbers.
4. **"No good fit" is a valid answer.** Say so, and say which requirement nothing satisfied.
5. **"Not found" is not "does not exist."** Always report which sources and queries were used.
6. **The student does the graded work.** Explain, plan, and critique. Do not write graded assignment text for them. Follow the course's AI-use policy if they mention one.
7. **Clear language.** Many users are ESL. Short sentences, define terms on first use, no filler.

## Routing

| User brings | Start at | Then |
|---|---|---|
| A need ("I need a paper for...") | Stage 1 NEED | 2 FIND, offer 3 and 4 |
| A specific paper | Stage 3 READ (ask its purpose in one line first) | offer 4 |
| A paper + a project | Stage 3 READ | Stage 4 APPLY |
| "Is this paper right for X?" | Stage 1 (short) | Stage 2 fit check on that one paper |

## Stage 1: NEED (write the requirement)

Ask at most 5 questions, in one batch (use a multiple-choice question tool if available). Skip anything the user already said.

1. **Context:** which course, assignment, or project? Deadline?
2. **Purpose:** what must the paper do for you? Pick one or more:
   choose a method to implement / justify a design decision / find a baseline to compare against /
   cite as related work / replicate a result / learn a concept / critique a claim.
3. **Must-haves:** e.g. uses real-world data, has public code, evaluated on a named benchmark, peer-reviewed.
4. **Deal-breakers:** e.g. older than N years, needs GPUs you don't have, only theory, paywalled.
5. **Level:** intro (first paper in this area) or advanced (comfortable with the field)?

Write the **Need Spec** (goal-oriented, lightweight):

```
NEED SPEC
Context:      <course / assignment / project, deadline>
Goal:         <the one decision or outcome the paper must support>
Must (hard):  R1 ...  R2 ...  R3 ...
Should (soft): S1 ...  S2 ...           (quality preferences: readable, recent, well-cited, has code)
Deal-breakers: D1 ...  D2 ...
Level:        intro | advanced
Out of scope: <what we are NOT looking for>
```

**Gate:** show the spec and ask "Is this right?" Revise until the user confirms. Do not search before this.

## Stage 2: FIND (match papers to the requirement)

### 2a. Query plan
Derive 2 to 3 query groups from the spec, using the user's own terms:
- goal term + domain
- method or mechanism + task
- must-have constraint + topic (e.g. "benchmark", "empirical study", "dataset")

### 2b. Retrieve (use what is connected; fall back in order)
1. **alphaXiv** `discover_papers`: one broad call covering all facets (only 2 searches per message). Keywords must be the user's terms, no guessed expansions.
2. **Scholar Feed** `search_papers`: semantic search. Useful filters: `has_code=true` (if code is a must-have), `sort="balanced"` (relevant and well-cited), `contribution_type` (e.g. `empirical_study`, `benchmark`, `survey`). Semantic search can miss older canonical papers: if the top abstracts keep naming a baseline, look that paper up directly, or use `get_foundational_lineage`.
3. **Consensus** `search`: peer-reviewed coverage. Set `exclude_preprints=true` only if "peer-reviewed" is a must-have.
4. **Fallback:** web search limited to arxiv.org, dl.acm.org, ieeexplore.ieee.org, semanticscholar.org, dblp.org.
5. **One-hop expansion (optional):** for the best 1 to 2 candidates, check references and citations (Scholar Feed `get_citations`) for a better-fitting neighbour.

Target a candidate pool of 15 to 30. Deduplicate by ID.

### 2c. Screen, then verify
- **Screen** titles and abstracts against deal-breakers. Keep about 8.
- **Verify** the top ~8 against each must-have using the paper text, not just the abstract: alphaXiv `answer_pdf_queries` (batch all requirement questions for one paper into one call) or Scholar Feed `fetch_fulltext` with only the sections needed (usually `method` and `results`).

### 2d. Output: Fit Report

```
FIT REPORT for: <Goal from Need Spec>

| Paper (year, ID) | R1 | R2 | R3 | Soft goals | Fit |
|---|---|---|---|---|---|
| Title (2025, arXiv:xxxx) | ✓ Sec 4 | ~ only synthetic data | ✓ Table 2 | has code, readable | Strong |

✓ = satisfied (with evidence pointer)   ~ = partial (say what is missing)   ✗ = not satisfied

TOP PICK: <title> because <one sentence tied to the Goal>.
Risk: <e.g. preprint, no code, heavy math>

NEAR-MISSES (why rejected):
- <title>: fails R2 (<reason>)

COVERAGE: searched <sources> with <query groups>. Not finding a paper here does not prove it does not exist.
```

Fit levels: **Strong** = all musts ✓. **Good** = all musts ✓ or ~, no ✗. **Weak** = any must ✗ (only show if nothing better exists, and label it).

**Gate:** ask the user which paper to go deeper on. Offer to save the shortlist to an alphaXiv folder named after the Goal (`save_papers_to_folder`).

## Stage 3: READ (understand it well)

Adapted from Keshav's three-pass method. Pace it: deliver one pass, then check in.

**Pass 1: What is this paper? (skim level)**
- Category: method / empirical study / tool / benchmark / survey / position.
- Problem, in one sentence a classmate would understand.
- Main contribution(s), max 3 bullets.
- Why it matters for the user's Goal.

**Pass 2: How does it work? (method and evidence)**
- The method in plain steps (numbered).
- Claim → evidence map: each main claim, and which table/figure/section supports it.
- Glossary of 3 to 8 terms the user needs.
- Explain the key figure or table: what the axes/columns mean, what to look at.

**Pass 3: Can I trust it? (critical reading)**
- Assumptions the method depends on.
- Threats to validity (SE convention): construct, internal, external, conclusion.
- What they did not test that matters for the user's Goal.
- Is there code/data? Could a student reproduce the core result?

**Connect to the course:** link concepts in the paper to what the user said they are studying. If unknown, ask which course topics this relates to.

**Check understanding:** ask 3 to 5 questions (use a quiz tool if available), mixing recall ("what dataset?") and reasoning ("why would this fail on small projects?"). Correct misconceptions directly.

Quote sparingly. Paraphrase and point to sections instead of reproducing text.

## Stage 4: APPLY (turn it into doing)

Offer the options that fit the Goal:

| Option | Output |
|---|---|
| **Assignment angle** | How the paper supports the assignment: which claim to cite, what to compare, what to critique. An outline the student writes themselves. |
| **Mini replication** | The smallest experiment that tests the core claim: data, code, steps, expected result, time estimate. |
| **Real-world build** | A project plan: what to build, which part of the paper it uses, milestones, risks. |
| **Critique memo** | Structure for a 1-page critique: claim, evidence, weakness, what they would test next. |

Every option ends with **one first step the user can finish in under 2 hours.**

## Feedback log (v0 evaluation)

After a Fit Report, ask one question: "Was the top pick right for your need? (1 = no, 5 = exactly)".

If a working directory is available, append a row to `paper-fit-log.csv`:
`date, goal_summary, top3_ids, user_rating, minutes_spent, notes`

Otherwise print that row in a code block so the user can paste it into their own log.

This log is how v0 gets evaluated against plain search before rolling out to the lab.
