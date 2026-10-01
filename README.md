# Paper Fit

**Finding papers is easy. Finding the RIGHT paper for your need is the hard part.**

Paper Fit is a free add-on (a "skill") for Claude. You tell it what you need a paper *for*, and it:

1. **Asks what you need**: your assignment or project, what the paper must have, and what you want to avoid.
2. **Finds 3 to 5 papers that fit**: it checks each paper against your needs and shows you *where* in the paper the proof is. It also tells you why other papers were rejected.
3. **Helps you read it**: explains the paper in plain words, step by step, and quizzes you to check you understood.
4. **Helps you use it**: turns the paper into a plan for your assignment, a small experiment, or a project.

> Paper Fit will **not** write your assignment for you. It helps you find, understand, and plan. You do the work.

---

## Before you start

You need:

- ✅ A **Claude account on a paid plan** (Pro, Max, Team, or Enterprise). The free plan cannot add custom skills.
- ✅ About **5 minutes**.

No coding needed. You don't need to know GitHub.

---

## Install in 3 steps (Claude app: web, desktop, or mobile)

### Step 1: Download the skill

1. Open the **[latest release page](https://github.com/CrisH2307/papers_papers_and_papers/releases/latest)**.
2. Under **Assets**, click **`paper-fit-skill.zip`** to download it.
3. **Do not unzip it.** Claude needs the `.zip` file as it is.

> ⚠️ Download `paper-fit-skill.zip`, **not** "Source code (zip)". The source code file will not work.

### Step 2: Upload it to Claude

1. Open Claude and go to **Settings → Capabilities**.
2. Make sure **Code execution and file creation** is turned **on**. Skills need it.
3. Scroll down to **Skills** and click **Upload skill**.
4. Choose the `paper-fit-skill.zip` you downloaded.
5. Check that **paper-fit** now appears in your Skills list and is switched **on**.

### Step 3: Connect the paper search tools (recommended)

These let Paper Fit search real research databases. Without them it still works, but it only uses normal web search, so results are weaker.

1. In Claude, go to **Settings → Connectors**.
2. Find and add **alphaXiv** (arXiv papers). Sign in when asked.
3. Find and add **Consensus** (peer-reviewed papers). Sign in when asked.
4. Optional: add **Scholar Feed** if you see it.

🎉 **Done!** You only do this once.

> **Using a school or lab account?** Your organization's admin may need to allow custom skills and these connectors first. If you can't find the buttons above, ask your admin.

---

## Your first try (2 minutes)

Start a **new chat** in Claude and type something like:

```
I need a paper for my software maintenance course project.
I want to build a tool that finds "TODO"-style technical debt comments in code.
The paper must have public code.
```

Then:

1. **Answer its short questions.** It asks at most 5.
2. **Check its summary of your need** (it's called a "Need Spec"). If something is wrong, just say so. This is the most important step: a better description gives better papers.
3. **Read the Fit Report**, a table showing which papers match your needs:
   - ✓ = matches, and it tells you where in the paper
   - ~ = partly matches
   - ✗ = does not match
4. **Pick a paper** and say *"help me read it"* or *"help me use it for my project"*.

### More things you can say

| You want to... | Type |
|---|---|
| Find a paper | *"I need a paper for [assignment/project]. It must [requirement]."* |
| Check one paper | *"Is this paper right for my assignment? [paper link or arXiv ID]"* |
| Understand a paper | *"Help me understand this paper: [link]"* |
| Use a paper | *"Turn this paper into a small project I can do in 2 weeks."* |

**Tip:** if Paper Fit doesn't start by itself, say *"Use the paper-fit skill"* at the start of your message.

---

## Something not working?

| Problem | Fix |
|---|---|
| I can't find **Upload skill** | You may be on the free plan, or **Code execution and file creation** is off (Step 2). On a school or lab account, ask your admin. |
| Upload fails | You probably uploaded **Source code (zip)** or an unzipped folder. Download **`paper-fit-skill.zip`** again from the release page and upload it without unzipping. |
| Claude doesn't use the skill | Check that it's switched **on** in Settings → Capabilities → Skills, then start a **new chat** and say *"Use the paper-fit skill"*. |
| Results feel weak or random | Connect **alphaXiv** and **Consensus** (Step 3). Also make your need more specific: say what the paper *must* have. |
| It says "no good fit" | That's honest, not broken. Try removing one requirement, or widen the years you accept. |
| A paper link doesn't open | Tell Claude which one. Always open and read the top pick yourself before you cite it. |

---

## Updating to a new version

When a new version comes out:

1. Download the new `paper-fit-skill.zip` from the [latest release page](https://github.com/CrisH2307/papers_papers_and_papers/releases/latest).
2. In **Settings → Capabilities → Skills**, remove the old **paper-fit**, then upload the new zip.

---

## For developers: Claude Code

If you use [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) in a terminal:

```bash
claude plugin marketplace add CrisH2307/papers_papers_and_papers
claude plugin install paper-fit@paper-fit
```

The plugin adds the alphaXiv and Consensus connections automatically. Type `/mcp` inside Claude Code once to sign in to each.

To publish a new release (maintainers only): update `version` in `.claude-plugin/plugin.json`, commit, then push a matching tag, for example `git tag v0.1.1 && git push origin v0.1.1`. GitHub builds `paper-fit-skill.zip` automatically.

---

## Optional: Jev mode (advanced, saves tokens)

Paper Fit can hand the "read 30 abstracts and rank them" step to **[Jev](https://docs.typesafe.ai)** (by TypeSafe, via OpenRouter), a small model that only scores and sorts. Claude then reads a short ranked table instead of every abstract, and still does the checking and writing.

In our first test, Jev screened 17 arXiv papers in about 7 seconds for **less than $0.001**, and the result Claude had to read was **11 times smaller** than the raw abstracts.

**You need:** Claude Code (or a Claude chat linked to your computer) and your own [OpenRouter](https://openrouter.ai) API key.

1. Save your key on your computer (only once):
   ```bash
   mkdir -p ~/.config/jev && chmod 700 ~/.config/jev
   printf '%s' 'YOUR_OPENROUTER_KEY' > ~/.config/jev/openrouter_key && chmod 600 ~/.config/jev/openrouter_key
   ```
2. Use Paper Fit as usual. When a key is found, it switches to Jev mode for screening automatically and tells you.

**Privacy:** Jev mode sends your goal, your requirement wording and public paper abstracts to OpenRouter. Don't put private project details in your request when it's on. Jev mode searches **arXiv only**, so for peer-reviewed journals Paper Fit adds one Consensus search.

Without a key, nothing changes: Paper Fit uses the normal flow.

---

## Help make it better

After each Fit Report, Paper Fit asks: *"Was the top pick right for your need? (1 to 5)"*.

Please send me:
- your rating (1 to 5)
- one sentence on what went wrong, if anything

You can [open an issue](https://github.com/CrisH2307/papers_papers_and_papers/issues) or message Cris Huynh directly. `templates/paper-fit-log.csv` shows the full columns, and [docs/EVAL.md](docs/EVAL.md) explains how Paper Fit is compared against plain search.

## License

MIT. Free to use, share, and change.
