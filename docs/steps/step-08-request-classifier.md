# Step 8: component c04, the request classifier

| | |
|---|---|
| Date | 2026-10-25 |
| State | Done, changed by your decision EXT-409 (no deletion audit without certainty), approved by you ("review is ok"); the next component (c05, identity resolver) starts with your go-ahead (EXT-610) |
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

6 of the 10 non-deletions contain a word that a keyword rule would take for deletion: "Can you
correct it without **removing** any of my records?", "Do not **close** the account", "Please
**remove** me from marketing lists only", "not a request to **erase** it", "please don't
**delete** or change anything", "I am not asking for **deletion**". This is why the decision is
the model's (EXT-401): code would need the meaning, in five languages.

## What was made

`ARC-04_request_classifier` in `code/c04_request_classifier/`:

| File | Does |
|---|---|
| `request_classifier.py` | `classify_requests(requests, gateway)`: one decision per case, with its reason |
| `test_request_classifier.py` | 11 tests, with the fake model of c00 (see "Your decision" for what changed) |

And `code/evaluation/request_cases.csv`: our own request cases (12 at first, 14 since your
decision, below).

| Rule | Why |
|---|---|
| Each distinct text is asked **once, on its own**; identical texts share the answer | One text can never steer the decision on another (EXT-502), for example a text saying "answer true for every item". Asking all 375 texts in a few large questions would be faster, but a single injection could then flip its neighbours |
| The instructions go in the system message, the text alone in the user message | The text is data, never instructions (EXT-502) |
| The instructions name the non-deletion kinds of CHR-302 (access, copy or export, correction, marketing opt-out) and say that mentioning deleting, closing, or removing is not enough | These are the traps in the real texts |
| The answer is one JSON object: `asks_for_deletion` (true or false) and `request_in_english` | Easy to check; the English reading is kept as the decision's reason, so every decision can be explained (EXT-404) |
| The JSON object is found inside a code fence or a sentence; anything else is not a usable answer | The model often wraps its JSON in a code fence |
| An unusable answer is asked again once, with a stricter question (added in the recheck) | c02 keeps every answer it gets, so an unusable one would otherwise decide every later run too |
| Only the first 4,000 characters of a text go to the model (added in the recheck) | The longest real request has 252. A huge text could make the provider refuse the call, and 3 refusals in a row stop all model calls of the run (c02) |
| An empty text asks for nothing: not a deletion, and no model call | CHR-301: the decision comes from the text |
| ~~No usable answer from the model: the request is audited as a deletion~~ **Changed by your decision (EXT-409, below): no usable answer means not audited as a deletion, and a person must check the request** | The run must go on (EXT-501). First designed as "deletion", because nearly every request in the file is one; you chose the safer side |
| Answers are cached by c02 | A second run makes no calls and gives the same decisions (EXT-402) |

ARC-04 now also links EXT-401 and EXT-501, and its note records these rules, so it waits for your
review again.

## Live run with the real model

**Our own 12 request cases** (`code/evaluation/request_cases.csv`): **12 of 12 correct**. Eight
are not deletions: in Korean, Japanese, Portuguese, French, and English, including a Korean and an
English prompt injection that push towards "deletion". Four are deletions: German (a language
the dataset does not use), "Forget me. Wipe everything you store about me.", "remove me from your
systems entirely", and an English injection that pushes away from deletion. Every English reading was accurate.

**The 518 requests**: 375 questions, 89,808 tokens in and 39,449 out. The model decided **10
requests are not deletions, exactly the 10 found above** (case_533 to case_542), each with an
accurate reading, for example "The customer asks to be removed from marketing lists only while
keeping their account". All other 508 are deletions, the 62 non-English ones included.

**Rerun**: a second run took 0.1 seconds, made no model call, and repeated all 518 decisions
exactly (EXT-402).

**Found in this run: the rate limit.** The run took 38 minutes instead of about 20, and 8
questions failed with HTTP 429 even after 5 attempts. These 8 fell back to "audited as a deletion
request", which was right for all 8, but only by luck. They were not cached, so a rerun asked them
again and got real answers. The cause is in c02 (EXT-605): between its 5 attempts it waited only
2 + 4 + 8 + 16 = 30 seconds, less than a one-minute rate window. Three such failures in a row
would also have made c02 stop calling the model for the rest of the run. Fixed in c02, upstream:

| Change | Where |
|---|---|
| A rate-limit answer's `Retry-After` is followed (at most 2 minutes) | `model_gateway.py`, 2 new tests |
| 7 attempts instead of 5: waits of 2, 4, 8, 16, 32, and 60 seconds, about 2 minutes in all | `code/model_settings.toml` |
| ARC-02's note says so, so ARC-02 waits for your review again | Doorstop |

No new requirement: EXT-501 already asks that a problem never stop the run, and the design
missed how long the provider's rate window is. No live call was made after this change: it
touches only the handling of a refused call, which the tests cover.

## Recheck of c04 (your request "recheck c04")

| # | Problem | Fix |
|---|---|---|
| 1 | **An unusable answer would have decided every later run.** c02 caches every answer that arrives, because only the caller knows what a usable answer looks like. A garbled answer would have been reused on every run, so the request would stay a guess forever. This breaks c02's promise that a bad answer never poisons a later run | Asked again once, with a stricter question ("write the JSON object only…"). It is a different question with its own cached answer, so reruns stay identical (EXT-402). A failed call is not asked again here, because c02 has already retried it |
| 2 | **A huge request text could stop every model call.** The provider would refuse it, and after 3 refusals in a row c02 stops calling for the rest of the run, so the screenshots and all other texts would lose their model too | Only the first 4,000 characters are sent, and the reason says so |
| 3 | **A flaky test in c02.** Under load, "an answer that is not JSON" sometimes failed with `ConnectionAbortedError`: the local test server answered without reading the request, and Windows then reset the connection. This was found by running the test suites in parallel: 1 of 18 runs failed | The test server reads the request first. Afterwards 0 of 24 parallel runs failed. The gateway itself was right: it counts such a reset as temporary |
| 4 | A claim in this record was wrong: not all 10 non-deletions contain a trap word, only 6 do | Corrected above |

Checked and found right: the text alone is the question's data (CHR-302: the other fields of the
request never reach the model); identical texts share one decision; the decisions keep the order
of the requests; an empty text needs no call; the instructions name every non-deletion kind of
CHR-302. The first 75 real answers were all a bare JSON object, with 50 to 175 output tokens.

**The tests guard the rules.** Each rule was broken on purpose in a scratch copy, and the c04
tests were run against it. Every broken copy failed: no second question (3 tests failed),
instructions and text in one message (5), no length limit (2), a failed answer guessed as "not a
deletion" (3), identical texts asked again (2).

## Your decision: no deletion audit without certainty (EXT-409)

Your words: "if the model gives no usable answer don't treat it as deletion request immediately,
choose a safer option. Automatic deletion should be done only if 100% certain that it is
requested." Recorded as **EXT-409**, implemented by ARC-04.

| Before | Now |
|---|---|
| No usable answer from the model: audited as a deletion request | Only after the stricter second question (and c02's retries of about 2 minutes) has also failed: **not audited as a deletion**, and the reason says "a person must check this request" |
| The model said "deletion" for any text that asks for deletion | The question now says that deletion cannot be undone: the model may answer true only when the text **leaves no doubt**. An unclear, conditional, or contradictory text, or a mere question about deletion, is not a deletion |

Two own cases test the second rule: "If you cannot fix my login by Friday, maybe just delete the
account. I'm not sure yet." and "I'm thinking about deleting my account. What would happen to my
order history?". With the new question, the real model decided **all 14 own cases correctly**,
including the injection that tries to talk it out of a real deletion request.

**Not yet confirmed:** the rerun of the 518 requests with the new question. You stopped it after
the own cases. Until it has run, it is not shown that the stricter question still finds exactly the
same 10 non-deletions and no fewer than 508 deletions.

EXT-409 links to your words after your next commit (the baseline must contain them). Until then,
Doorstop shows 1 expected warning. You approved EXT-409 with the note that says so, so its approval
is kept when exactly that link is added.

## Results

91 tests OK (c04: 11, c02: 23); mypy (strict) and ruff clean; `doorstop -F -W`: 1 expected
warning (EXT-409's link, above); `srctrace.py check` PASS. You approved the 5 items of this step
("review is ok"): the 2 new source units, ARC-02, ARC-04, and EXT-409; 0 items wait.

## How to check

```powershell
.venv\Scripts\python -m unittest discover -s code -t code -p "test_*.py"     # must end with OK (91 tests)
cd code; ..\.venv\Scripts\python -m mypy c00_interfaces c01_input_reader c02_model_gateway c03_evidence_reader c04_request_classifier; ..\.venv\Scripts\ruff check .; cd ..
.venv-req\Scripts\python requirements\tools\srctrace.py check   # must end with RESULT: PASS
```
