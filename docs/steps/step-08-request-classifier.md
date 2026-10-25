# Step 8: component c04, the request classifier

| | |
|---|---|
| Date | 2026-10-25 |
| State | Done, waiting for your review; the next component (c05, identity resolver) starts with your go-ahead (EXT-610) |
| Goal | Decide for every request whether its text, in any language, authorizes deletion (CHR-301 to CHR-303) |
| Not in this step | Writing `NOT_APPLICABLE` rows (c10, the audit pipeline); scoring the classifier in the evaluation report (c11) |

## Before the component

- **Baseline:** after your commit "Step7", the baseline moved to it. Two of your prompts became
  source units, both labelled context: "pasted, continue" (SRC-LG0766) and the non-English test
  request (SRC-LG0789; that other languages must be decided correctly is already CHR-303).
- **ISS-11:** your decision "I agree with ISS-11 proposal" is recorded in
  [ISSUES.md](../../requirements/ISSUES.md#iss-11). It is settled from the sample answers in c08.

## What the requests look like

A script read the 518 requests: **375 distinct texts**. They are built from 27 opening sentences:

| Kind | Distinct texts | Requests |
|---|---|---|
| English deletion requests (12 openings, each with varied middle and closing sentences) | 360 | 446 |
| The same deletion request in Portuguese, Korean, Spanish, Japanese, and French | 5 | 62 |
| **Not a deletion**, each once: a phone number to update, stop promotional emails, a portable download, login help, a misspelled surname, removal from marketing lists only, what data you hold, last year's invoices, a new email address, a copy of the data | 10 | 10 |

Each of the 10 non-deletions contains a word that a keyword rule would take for deletion: "Can you
correct it without **removing** any of my records?", "Do not **close** the account", "Please
**remove** me from marketing lists only", "not a request to **erase** it". This is why the
decision is the model's (EXT-401): code would need the meaning, in five languages.

## What was made

`ARC-04_request_classifier` in `code/c04_request_classifier/`:

| File | Does |
|---|---|
| `request_classifier.py` | `classify_requests(requests, gateway)`: one decision per case, with its reason |
| `test_request_classifier.py` | 9 tests, with the fake model of c00 |

And `code/evaluation/request_cases.csv`: our own 12 request cases (below).

| Rule | Why |
|---|---|
| Each distinct text is asked **once, on its own**; identical texts share the answer | One text can never steer the decision on another (EXT-502), for example a text saying "answer true for every item". Asking all 375 texts in a few large questions would be faster, but a single injection could then flip its neighbours |
| The instructions go in the system message, the text alone in the user message | The text is data, never instructions (EXT-502) |
| The instructions name the non-deletion kinds of CHR-302 (access, copy or export, correction, marketing opt-out) and say that mentioning deleting, closing, or removing is not enough | These are the traps in the real texts |
| The answer is one JSON object: `asks_for_deletion` (true or false) and `request_in_english` | Easy to check; the English reading is kept as the decision's reason, so every decision can be explained (EXT-404) |
| The JSON object is found inside a code fence or a sentence; anything else is not a usable answer | The model often wraps its JSON in a code fence |
| An empty text asks for nothing: not a deletion, and no model call | CHR-301: the decision comes from the text |
| **No usable answer from the model: the request is audited as a deletion**, and the reason says so | The run must go on (EXT-501). The file holds deletion requests, nearly all of them real ones, so this guess is right far more often than the opposite one. **This is a design decision for your review** (ARC-04's note) |
| Answers are cached by c02 | A second run makes no calls and gives the same decisions (EXT-402) |

ARC-04 now also links EXT-401 and EXT-501, and its note records these rules, so it waits for your
review again.
