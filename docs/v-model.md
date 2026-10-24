# How this project follows the V-model

## The idea in one paragraph

The V-model splits the work into levels. On the **left side** we go *down*: from what is wanted
(requirements) to how it is built (design), ending at the code at the bottom. On the **right
side** we go *up again*: every level on the left gets a matching level of checks (tests). Every
item is **linked** to the item above it that it comes from, and to the checks that prove it. So
at any moment you can ask "where does this come from?", "what depends on it?" and "is it proven
yet?", and get an exact answer from the links.

## Our V

```text
 LEFT: what we want and how we build it                    RIGHT: how we prove it

 SRC  source units: the input files, line by line       (input; nothing to test)
  |
 CHR  challenge requirements (given by the hackathon)  <-- proven by -->  ACC  acceptance checks
  |                                                                         (output.csv format, 518 rows,
 EXT  extension requirements (beyond the hackathon)    <-- proven by -->    code.zip contents, log format,
  |                                                                         sample accuracy, ...)
 SYS  system requirements (precise, testable)          <-- proven by -->  SYT  system tests
    \                                                                      /
    ARC  architecture (components, interfaces)         <-- proven by -->  INT  integration tests
       \                                                                /
       DES  module design                              <-- proven by -->  UNT  unit tests
          \                                                          /
           '------------------------  CODE  ------------------------'
```

| Level | Holds | Step | State |
|---|---|---|---|
| SRC | The five challenge files, `dataset/deletion_rules.csv`, and your prompts in `log.txt`, cut into 526 verbatim source units | 1, 2 | 489 approved by you; the 36 added in step 2 wait for your review |
| CHR | 217 requirements stated by the hackathon files | 1, 2 | 202 approved by you; section 10 (the 15 policy rules, step 2) waits for your review |
| EXT | 36 requirements you decided (or we added), kept apart from CHR | 2, 3 | waiting for your review; EXT-601 to EXT-607 get their link to your words after your next commit |
| REV | Requirements revealed during analysis, implementation, or testing, kept apart from CHR and EXT (EXT-606) | 3 | 4 items, waiting for your review |
| ARC | The 11 code components and the delivery process, each linked to the requirements it implements | 3 | 12 items, design approved by you; items waiting for your review ([step 3](steps/step-03-data-analysis-and-design.md)) |
| DES | Module design inside each component | 3, 4 | not started |
| CODE | The solution | later | not started (`code/` is untouched) |
| UNT, INT, SYT, ACC | The checks for each level | later | not started |

Prefixes such as `EXT`, `SYS`, `ACC` are proposals; each is created when its step starts.

## How the status of a requirement is known

A requirement is **satisfied** only when all three of these are true. Each one is answered by a
tool, not by memory:

| Question | Answered by | Today |
|---|---|---|
| 1. Did you approve it? | Doorstop review fingerprints (`doorstop review`; `pending-user-review` means "not yet") | 112 items wait for you |
| 2. Is it connected? Every input line has a requirement, every requirement has a source, and later every requirement has a design element and a check | `srctrace.py check` and Doorstop's link checks | complete for SRC to CHR, EXT, and REV, except EXT-405, EXT-406, and EXT-601 to EXT-607 (linked after your next commit); every requirement is implemented by a component (ARC) |
| 3. Is it proven? The checks linked to it passed on the latest run | test results that carry requirement IDs (set up when the right side starts) | nothing proven yet: no code and no tests exist |

Because Doorstop fingerprints each item, a later change is never silent. If a source line or a
requirement changes, it is reported as `unreviewed changes`, and every link to it as a
`suspect link`, until someone looks at it again. This already happened once: when the
organizers fixed one line of AGENTS.md, exactly one requirement was flagged
([step 1.1](steps/step-01.1-rebaseline-agents-url-fix.md)).

## Keeping "beyond the hackathon" requirements apart (step 2)

You asked for the extension requirements to be clearly separated and traceable. This is how it
was done in step 2 ([record](steps/step-02-extension-requirements.md)):

1. Your own instructions are input lines like the organizers' lines, so your requirements are
   traceable to your words exactly like the challenge requirements are traceable to theirs. The
   plan was to copy your instructions into a file of their own. Instead, the tool reads them
   straight from `log.txt`, where AGENTS.md already requires every prompt to be logged word for
   word: only the lines of its "User Prompt" sections become source units (file code `LG`), by a
   fixed rule. So no AI retypes your words, and there is no second copy that could drift.
2. Extension requirements go into their own Doorstop document, `EXT`, never into `CHR`. A
   requirement that comes from our own analysis rather than from any input text is marked
   `derived: true` (Doorstop's built-in flag for this) and gets a written rationale.
3. So `CHR-…` always means "the hackathon requires it", and `EXT-…` always means "we decided it".
   The published views and the traceability matrix show the difference.

## Tools and why

| Tool | Open source? | Used for | Why this one |
|---|---|---|---|
| git | yes (GPL-2.0) | Freezing the baseline: inputs read from the commit recorded in [requirements/sources.yml](../requirements/sources.yml) | Already the project's version control; exact and repeatable |
| Doorstop 3.2 | yes (LGPL-3.0) | Storing items, links, review fingerprints, validation, publishing (Markdown, HTML, traceability matrix) | Plain YAML files in git (clean diffs); built-in parent/child coverage checks; `derived` flag for extensions; pure Python, so it runs here on Python 3.15 |
| PyYAML, Python | yes | Running Doorstop and the small checker | |
| `requirements/tools/srctrace.py` | ours, about 430 lines | Cutting files into units; proving line coverage; the line map | No existing tool checks that *every line* of a Markdown file is covered |

Considered but not chosen: **StrictDoc** (good tool, but needs many compiled packages that
are not yet available for Python 3.15 on Windows), **sphinx-needs** (needs a whole Sphinx
documentation build), **OpenFastTrace** (needs Java, which is not installed).

## Words used

| Word | Meaning here |
|---|---|
| Baseline | The exact version of the input files that was converted (git commit + SHA-256 per file) |
| Source unit (SRC) | One non-blank line of an input file, or one whole code block, copied verbatim |
| Requirement (CHR, EXT) | One short statement of something that must be true, written from source units (CHR: the hackathon's; EXT: ours) |
| Normative | "Contains a requirement" (Doorstop's word). Normative units must be linked from a requirement |
| Disposition | Our label for what a source unit is: requirement, heading, formatting, context, not-applicable |
| Link | "This requirement comes from that source unit." Stored in the requirement (the child) |
| Parent / child | The item a link points to is the parent; the item holding the link is the child |
| Traceability | Being able to follow links in both directions without guessing |
| Review fingerprint | A hash Doorstop stores when you approve an item; a later change breaks it |
| Suspect link | A link whose parent changed after the link was confirmed |
| Derived | Doorstop's flag for a requirement that has no parent, because we added it ourselves |
| Verification method | How a requirement will be checked: test, inspection, analysis, or demonstration |
