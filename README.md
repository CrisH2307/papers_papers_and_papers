# Paper Fit

**Finding papers is easy. Finding the RIGHT paper for your need is the hard part.**

Paper Fit is a Claude skill that treats paper selection as a requirements problem:

1. **NEED**: write down what the paper must do for you (goal, must-haves, deal-breakers).
2. **FIND**: search several academic indexes, check each must-have against the paper's actual text, and return 3 to 5 papers with evidence, plus why the near-misses were rejected.
3. **READ**: guided three-pass reading (what it is, how it works, can I trust it), connected to your course.
4. **APPLY**: turn the paper into an assignment angle, a mini replication, a project plan, or a critique memo.

> It will not write graded assignment text for you. It helps you find, understand, plan and critique. You do the work.

## Install

### Option A: claude.ai (web, desktop, mobile)

1. Download `paper-fit-skill.zip` from the [latest release](https://github.com/CrisH2307/papers_papers_and_papers/releases/latest).
2. In Claude's settings, find the Skills section and upload the zip.
3. Connect the research connectors in Claude's connector settings: **alphaXiv**, **Consensus**, and **Scholar Feed** if available.
4. Start a chat: *"I need a paper for my ENGR 5570 project on ..."*

If your account belongs to an organization (for example a lab workspace), the admin may need to allow custom skills and these connectors.

### Option B: Claude Code

```bash
claude plugin marketplace add CrisH2307/papers_papers_and_papers
claude plugin install paper-fit@paper-fit
```

The plugin registers the alphaXiv and Consensus MCP servers. Run `/mcp` once to sign in to each.

## Try it

- "Find me a paper for my maintenance course project: I want to build a tool that detects self-admitted technical debt, and it must have public code."
- "Is this paper right for my assignment? arXiv:2601.06266"
- "Help me understand this paper and turn it into a small replication."

## Help us evaluate it

After each Fit Report, Paper Fit asks: *"Was the top pick right for your need? (1 to 5)"*.
Please send me your row (`templates/paper-fit-log.csv` shows the columns), or open an issue with it.
See [docs/EVAL.md](docs/EVAL.md) for how we compare it against plain search.

## Feedback

Open an issue, or message Cris Huynh directly.

## License

MIT
# papers_papers_and_papers
