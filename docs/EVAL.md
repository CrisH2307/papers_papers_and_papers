# Evaluation Protocol (v0 → v1)

**Question:** does Paper Fit pick papers that fit the student's need better than the search they would do anyway?

## Design (small, blind, paired)

For each real request from a lab member:

1. The requester writes the need in one or two sentences (before any tool is used).
2. **Paper Fit** produces its top 3.
3. **Baseline** produces a top 3: the requester's own Google Scholar search (15 minutes max), or plain Claude with no skill and the same connectors.
4. Merge the 6 papers, shuffle, remove the method labels.
5. The requester and one rater (Kundi or a senior lab member) rate each paper's fit to the need, 1 to 5, without knowing which method picked it.
6. Log time spent for each method.

## Metrics

| Metric | Definition |
|---|---|
| Top-1 fit | Rating of each method's first pick |
| Mean top-3 fit | Average rating of each method's top 3 |
| Useful@3 | Share of top-3 papers rated 4 or 5 |
| Time | Minutes from need to shortlist |
| Agreement | Requester vs rater agreement (weighted kappa), to check the ratings are consistent |

## Decision rules

| Stage | Sample | Move on when |
|---|---|---|
| v0 (Cris only) | 3 requests | Kundi agrees the top picks are right on at least 2 of 3 |
| v1 (lab) | 10 to 15 requests | Paper Fit beats baseline on Useful@3 in most requests, and saves time |
| v2 (ENGR 5570 / courses) | 20+ requests | Students use it again without being reminded |

## Failure log

Record every case where Paper Fit was worse, with one line on why:
wrong Need Spec, missed a canonical paper, verified a requirement wrongly, too slow, other.
These cases drive the next version of `SKILL.md`.

## Ethics note

Only log the need summary and paper IDs. Do not log grades, student names, or assignment text.
If results become a paper, check with Kundi about whether an ethics review is needed for student feedback data.
