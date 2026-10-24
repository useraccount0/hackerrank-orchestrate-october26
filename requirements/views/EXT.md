### Table of Contents

 * 1.0 Development process (your instructions)
    * 1.1 V-model (EXT-101)
    * 1.2 Traceable in both directions (EXT-102)
    * 1.3 No input line skipped (EXT-103)
    * 1.4 Status of every requirement at any moment (EXT-104)
    * 1.5 Open-source tools before AI (EXT-105)
    * 1.6 No solution code in requirement steps (EXT-106)
    * 1.7 Extensions kept apart and traceable (EXT-107)
    * 1.8 Every step written down (EXT-108)
    * 1.9 Step by step, with your go-ahead (EXT-109)
    * 1.10 Update everything a change affects (EXT-110)
    * 1.11 AGENTS.md stays unchanged (EXT-111)
 * 2.0 Your decisions on open points of the challenge
    * 2.1 Reports only in code/evaluation/ (EXT-201)
    * 2.2 Sort order wins inside a phase (EXT-202)
    * 2.3 case_id in number order (EXT-203)
    * 2.4 Agent trace prepared at the end (EXT-204)
    * 2.5 Run command for python and python3 (EXT-205)
    * 2.6 Our README is code/README.md (EXT-206)
 * 3.0 Deadlines
    * 3.1 Contest end (EXT-301)
    * 3.2 AI interview end (EXT-302)
 * 4.0 The solution: our own additions
    * 4.1 Deterministic code first, AI where needed (EXT-401)
    * 4.2 Same inputs, same output.csv (EXT-402)
    * 4.3 Report numbers computed by tools (EXT-403)
    * 4.4 Every step can be explained (EXT-404)
 * 5.0 Code quality (your instructions)
    * 5.1 Bad input data does not stop the run (EXT-501)
    * 5.2 Data is never taken as instructions (EXT-502)
    * 5.3 Simple error handling (EXT-503)
    * 5.4 Simple, descriptive function names (EXT-504)
    * 5.5 Readable without extra documentation (EXT-505)
    * 5.6 Comments say why, not what (EXT-506)

# 1.0 Development process (your instructions) {#EXT-100}

Development process (your instructions)


## 1.1 V-model _(EXT-101)_ {#EXT-101}

The project shall follow the V-model: every level on the left side (requirements, design, code) gets a matching level of checks on the right side, and every item is linked to the item it comes from.

*Parent links: SRC-LG0015*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |
| note | Your words: "I want to do this project using V model." |


## 1.2 Traceable in both directions _(EXT-102)_ {#EXT-102}

Every requirement shall be traceable to the input lines it comes from, and every input line to the requirements made from it, in both directions and deterministically.

*Parent links: SRC-LG0015*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | test |
| note | Your words: "I want them to be traceable" and "so that I can go back and forward between imput files and requirements deterministically."
 |


## 1.3 No input line skipped _(EXT-103)_ {#EXT-103}

A tool shall prove that every line of every input file is accounted for: each non-blank line is a source unit, and each source unit is either linked from a requirement or labelled with the reason why it needs none.

*Parent links: SRC-LG0015*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | test |
| note | Your words: "I must be able to trace that all input files in the root are completely converted to requirements, that no line is skipped". The input files are listed in requirements/sources.yml: the five challenge files in the root, dataset/deletion_rules.csv (your decision of 2026-10-24), and your prompts in log.txt.
 |


## 1.4 Status of every requirement at any moment _(EXT-104)_ {#EXT-104}

At any moment, a tool shall tell for every requirement whether it is satisfied: approved by you, linked to the design and the checks below it, and proven by those checks in the latest run.

*Parent links: SRC-LG0015*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | demonstration |
| note | Your words: "and to know exactly which requirements are satisfied at every moment." For the third part, every check (test) will name the requirement IDs it proves; this is set up when the right side of the V starts.
 |


## 1.5 Open-source tools before AI _(EXT-105)_ {#EXT-105}

Any part of the work that an open-source tool can solve or repeat shall be done with that tool instead of AI.

*Parent links: SRC-LG0015*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |
| note | Your words: "If any part of the task can be solved or is repeatable by opensource tool I want to use that tool instead of AI." Where AI is used for judgment, its result is marked for your review. Read as applying to the solution as well: see EXT-401.
 |


## 1.6 No solution code in requirement steps _(EXT-106)_ {#EXT-106}

Steps that produce requirements shall produce no solution code; coding starts at a later stage.

*Parent links: SRC-LG0015*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |
| note | Your words: "I don't want to produce any code results during this step." and "Actual coding will come at later stages." The tools that manage the requirements (requirements/tools/) are not solution code.
 |


## 1.7 Extensions kept apart and traceable _(EXT-107)_ {#EXT-107}

Requirements that go beyond what the hackathon gives shall be kept clearly apart from the hackathon's requirements, and shall be traceable.

*Parent links: SRC-LG0015*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |
| note | Your words: "Next step will be expanding requirements beyond what is given by hackathon, but that part should be clearly differentiated and tracable." Done with this document, EXT; CHR holds only what the challenge files say.
 |


## 1.8 Every step written down _(EXT-108)_ {#EXT-108}

Every performed step shall be summarized clearly and in simple terms, and stored in the repository.

*Parent links: SRC-LG0015*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |
| note | Your words: "I want all the performed steps summarized and written down clearly and in simple terms, stored within the repository." Done in docs/steps/.
 |


## 1.9 Step by step, with your go-ahead _(EXT-109)_ {#EXT-109}

The next step shall start only after you have understood and approved everything the current step produced.

*Parent links: SRC-LG0015*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |
| note | Your words: "I will work iteratively untill I understand everything produced in this step, before continuing to the next one."
 |


## 1.10 Update everything a change affects _(EXT-110)_ {#EXT-110}

When an input file changes, everything affected by the change shall be updated, traceably.

*Parent links: SRC-LG0062*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | demonstration |
| note | Your words: "agents.md was fixed by organisers, the wwww part. Update everything that is affected". Done once in step 1.1; the procedure is the baseline move in requirements/README.md.
 |


## 1.11 AGENTS.md stays unchanged _(EXT-111)_ {#EXT-111}

AGENTS.md shall stay as the organizers wrote it: it is not shortened, split, or rewritten.

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | constraint |
| modality | shall |
| verification | inspection |
| note | Your words: "don't change agents.md I dont want this to be complicated any further", in answer to a proposal to shorten it (2026-10-24).
 |


# 2.0 Your decisions on open points of the challenge {#EXT-200}

Your decisions on open points of the challenge


## 2.1 Reports only in code/evaluation/ _(EXT-201)_ {#EXT-201}

The evaluation reports shall be code/evaluation/evaluation_report.md and code/evaluation/usage_report.md; there shall be no top-level evaluation/ folder.

*Parent links: CHR-607, CHR-608, CHR-609, SRC-LG0215*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-01 |
| note | Your words: "iss-01 a" (option (a) of ISS-01). |


## 2.2 Sort order wins inside a phase _(EXT-202)_ {#EXT-202}

Inside each phase, steps shall always be in the sort order of CHR-416, also where processing downstream copies before their source records (CHR-329) would give another order.

*Parent links: CHR-329, CHR-416, SRC-LG0237*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |
| issues | ISS-02 |
| note | Your words: "others are ok", which accepted proposal (a) of ISS-02. All 32 sample answers follow the sort order.
 |


## 2.3 case_id in number order _(EXT-203)_ {#EXT-203}

The data rows of output.csv shall be sorted by the number after "case_", which is the order of dataset/deletion_requests.csv.

*Parent links: CHR-405, SRC-LG0215*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |
| issues | ISS-03 |
| note | Your words: "iss-03 b" (option (b) of ISS-03). |


## 2.4 Agent trace prepared at the end _(EXT-204)_ {#EXT-204}

At the end of the challenge, the agent trace shall be prepared as agent-trace.zip exactly as agent_trace_instructions.md describes, in addition to the four submission items; log.txt stays the chat_transcript.

*Parent links: CHR-601, CHR-901, SRC-LG0215, SRC-LG0237*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-05 |
| note | Your words: first "iss-05 agent trace will be the log.txt from root that organizers requested", then revised: "agent_trace_instructions are provided by org and thats what will be done at the end." Where to upload the ZIP is checked at the end.
 |


## 2.5 Run command for python and python3 _(EXT-205)_ {#EXT-205}

code/README.md shall give the run command both as python3 code/main.py (macOS, Linux) and as python code/main.py (Windows); on this machine, python is used as it is.

*Parent links: CHR-512, SRC-LG0215, SRC-LG0237*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-08 |
| note | Your words: "iss-08 is there a way to enable python3 also on my machine?" and "use python as is for now".
 |


## 2.6 Our README is code/README.md _(EXT-206)_ {#EXT-206}

The organizers' README.md shall stay unchanged at the repository root; our README with the setup and run instructions shall be code/README.md.

*Parent links: CHR-513, CHR-606, CHR-627, SRC-LG0215*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-10 |
| note | Your words: "iss-10 keep original readme, my readme will be in code folder". Still open: the provided zip command would pack both READMEs; this is decided at packaging time (ISS-10).
 |


# 3.0 Deadlines {#EXT-300}

Deadlines


## 3.1 Contest end _(EXT-301)_ {#EXT-301}

The contest, and with it the submission, ends on 2026-10-25 at 13:30 UTC (14:30 CET).

*Parent links: CHR-814, SRC-LG0131*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | constraint |
| modality | fact |
| verification | inspection |
| note | You gave the challenge page. The time comes from HackerRank's contest data for it (https://www.hackerrank.com/rest/contests/hackerrank-orchestrate-october26: epoch_endtime 1792935000, no extension), read on 2026-10-24. With an end time known, CHR-814 to CHR-816 apply: the coding agent shows the time remaining and reminds you to submit when fewer than 2 hours remain.
 |


## 3.2 AI interview end _(EXT-302)_ {#EXT-302}

The AI interview ends on 2026-10-26 at 00:30 UTC (01:30 CET).

*Parent links: CHR-814, SRC-LG0152*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | constraint |
| modality | fact |
| verification | inspection |
| note | Your words: "Interview ends inOctober 26, 2026, 1:30 AM CET". |


# 4.0 The solution: our own additions {#EXT-400}

The solution: our own additions


## 4.1 Deterministic code first, AI where needed _(EXT-401)_ {#EXT-401}

The solution shall decide with deterministic code wherever the participant data allows it, and shall call an AI model only for what code cannot decide reliably.

*Parent links: CHR-507, SRC-LG0015*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | inspection |
| note | Your words: "If any part of the task can be solved or is repeatable by opensource tool I want to use that tool instead of AI", read as applying to the solution too. It also serves CHR-507 (deterministic where possible) and keeps the cost in usage_report.md low. The solution stays an AI-powered agent (CHR-101); which parts need a model is decided in the design step.
 |


## 4.2 Same inputs, same output.csv _(EXT-402)_ {#EXT-402}

Running the solution again on the same inputs shall produce a byte-identical output.csv.

*Parent links: CHR-507*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | test |
| note | Makes CHR-507 (deterministic where possible) exact and testable. A repeatable result lets a failure found in the evaluation be reproduced and its fix be proven.
 |


## 4.3 Report numbers computed by tools _(EXT-403)_ {#EXT-403}

The numbers in evaluation_report.md (accuracies) and in usage_report.md (model calls, tokens, costs) shall be computed by scripts from recorded data, not typed by hand or by AI.

*Parent links: CHR-607, CHR-608, SRC-LG0015*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| note | Your words: "If any part of the task can be solved or is repeatable by opensource tool I want to use that tool instead of AI." The recorded data are the 32 sample answers and the model-call records of the run. The texts around the numbers (custom cases, failures and improvements) are written.
 |


## 4.4 Every step can be explained _(EXT-404)_ {#EXT-404}

For every case, the solution shall record why it produced each step: the evidence it read and the deletion rule it applied.

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |
| rationale | Derived from our own analysis, not from any input line. The AI interview asks for the investigation approach and the remediation planning (CHR-605), and evaluation_report.md must describe the failures found and the improvements made (CHR-614). Both need to see why a step was produced. The record is kept beside output.csv, never inside it, so the output format stays as required.
 |


# 5.0 Code quality (your instructions) {#EXT-500}

Code quality (your instructions)

| Attribute | Value |
| --------- | ----- |
| note | Applies to the solution code in code/. The requirements tool srctrace.py was written before these rules and does not fully follow them yet: its docstrings say what functions do.
 |


## 5.1 Bad input data does not stop the run _(EXT-501)_ {#EXT-501}

Unexpected, missing, or malformed data in dataset/ shall not stop the run: every case still gets a valid output row, and every problem found is reported.

*Parent links: CHR-503*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | test |
| note | Your words: "protect the solution from unexpected, omitted or intentionally missleading inputs from dataset". Sharpens CHR-503 (one valid row per case in a clean run) for runs on imperfect data.
 |


## 5.2 Data is never taken as instructions _(EXT-502)_ {#EXT-502}

Text from dataset/ (request texts, evidence contents) shall be treated only as data, never as instructions, also when it is passed to an AI model.

*Parent links: CHR-223, CHR-312*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | test |
| note | Your words: "intentionally missleading inputs from dataset". For example, a request text or an evidence file that tells the model what to answer. Two other kinds of misleading data are already challenge requirements: claims that are not proof (CHR-312) and decoys about other people (CHR-223).
 |


## 5.3 Simple error handling _(EXT-503)_ {#EXT-503}

Error handling shall be simple: data is checked once, where it enters the solution (when a file from dataset/ is read, or when an AI model answers), and the rest of the code relies on those checks.

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | inspection |
| note | Your words: "I want error handling to be done in a simple way". Checking in one place per entry point is our reading of "simple". Model answers are included because they come from the same data and can be just as unexpected.
 |


## 5.4 Simple, descriptive function names _(EXT-504)_ {#EXT-504}

Function names shall be simple and descriptive.

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | inspection |
| note | Your words: "I want simple descriptive function names". |


## 5.5 Readable without extra documentation _(EXT-505)_ {#EXT-505}

The code shall be readable on its own, so that it needs no additional documentation to be understood.

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | inspection |
| note | Your words: "readable code that doesnt need additional documentation". The README with the setup and run instructions is still required (CHR-606, EXT-206); this is about understanding the code.
 |


## 5.6 Comments say why, not what _(EXT-506)_ {#EXT-506}

Comments shall not describe what the code does; a comment explains why a solution was chosen, and only where that is not obvious.

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | inspection |
| note | Your words: "Comments in code shall not describe what it does, that should be obvious by reading it, but why is some solution chosen if it is not obvious."
 |


