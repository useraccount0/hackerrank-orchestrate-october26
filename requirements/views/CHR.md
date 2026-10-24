### Table of Contents

 * 1.0 Purpose and scope
    * 1.1 AI-powered deletion-audit agent (CHR-101)
    * 1.2 Where personal data can remain (CHR-102)
    * 1.3 Deleted data can come back (CHR-103)
 * 2.0 Inputs (dataset contract)
    * 2.1 Read the inputs from dataset/ (CHR-201)
    * 2.2 Participant-facing files (CHR-202)
    * 2.3 deletion_requests.csv (CHR-203)
    * 2.4 Request fields (CHR-204)
    * 2.5 case_id (CHR-205)
    * 2.6 email (CHR-206)
    * 2.7 requested_at (CHR-207)
    * 2.8 reported_status (CHR-208)
    * 2.9 reported_at (CHR-209)
    * 2.10 audit_at (CHR-210)
    * 2.11 request_text (CHR-211)
    * 2.12 Sample requests (CHR-212)
    * 2.13 Sample answers (CHR-213)
    * 2.14 user_identities.csv (CHR-214)
    * 2.15 user_audit_log.csv (CHR-215)
    * 2.16 system_activity.csv (CHR-216)
    * 2.17 deletion_rules.csv (CHR-217)
    * 2.18 evidence_files.csv (CHR-218)
    * 2.19 Blank output template (CHR-219)
    * 2.20 Evidence formats (CHR-220)
    * 2.21 SQL snapshots (CHR-221)
    * 2.22 Only the requests need answers (CHR-222)
    * 2.23 Decoys and unrelated records (CHR-223)
 * 3.0 Deletion audit logic
    * 3.1 Decide first whether deletion was requested (CHR-301)
    * 3.2 Non-deletion requests (CHR-302)
    * 3.3 Requests in different languages (CHR-303)
    * 3.4 Resolve current and historical identifiers (CHR-304)
    * 3.5 The request email may be old (CHR-305)
    * 3.6 Use the identity history (CHR-306)
    * 3.7 Search activity and evidence (CHR-307)
    * 3.8 Find evidence via the manifest, then read it (CHR-308)
    * 3.9 Grounded matching (CHR-309)
    * 3.10 Read images and PDFs (CHR-310)
    * 3.11 Replication drift (CHR-311)
    * 3.12 Claims are not proof (CHR-312)
    * 3.13 Reconstruct the state at audit_at (CHR-313)
    * 3.14 Nothing after audit_at (CHR-314)
    * 3.15 Find what still exposes the user (CHR-315)
    * 3.16 Find what can recreate the data (CHR-316)
    * 3.17 Apply the deletion policy everywhere (CHR-317)
    * 3.18 Do not over-delete (CHR-318)
    * 3.19 Keep records the policy requires (CHR-319)
    * 3.20 Account tombstones (CHR-320)
    * 3.21 Decide COMPLETE or INCOMPLETE (CHR-321)
    * 3.22 COMPLETE needs: every copy treated (CHR-322)
    * 3.23 COMPLETE needs: nothing can recreate the data (CHR-323)
    * 3.24 COMPLETE needs: only permitted identifiers kept (CHR-324)
    * 3.25 COMPLETE needs: required records still available (CHR-325)
    * 3.26 Report every violation and risk (CHR-326)
    * 3.27 Complete remediation plan (CHR-327)
    * 3.28 Stop flows and restores first (CHR-328)
    * 3.29 Downstream copies before their sources (CHR-329)
    * 3.30 Checks after remediation (CHR-330)
    * 3.31 Proof for complete deletions (CHR-331)
 * 4.0 Output file (output.csv and steps_json)
    * 4.1 Write output.csv in the repository root (CHR-401)
    * 4.2 Exact header (CHR-402)
    * 4.3 One row per case (CHR-403)
    * 4.4 518 data rows (CHR-404)
    * 4.5 Sorted by case_id (CHR-405)
    * 4.6 Meaning of the columns (CHR-406)
    * 4.7 deletion_status values (CHR-407)
    * 4.8 Rows for non-deletion requests (CHR-408)
    * 4.9 steps_json is a JSON array (CHR-409)
    * 4.10 How the grader reads steps_json (CHR-410)
    * 4.11 Fields of a step (CHR-411)
    * 4.12 Types of the step fields (CHR-412)
    * 4.13 Step numbers (CHR-413)
    * 4.14 Phase values (CHR-414)
    * 4.15 Phase order (CHR-415)
    * 4.16 Order inside a phase (CHR-416)
    * 4.17 No invented phases, operations, or states (CHR-417)
    * 4.18 REPORT_REMAINING_RECORD (FINDING) (CHR-418)
    * 4.19 REPORT_EXPOSED_PII (FINDING) (CHR-419)
    * 4.20 REPORT_ACTIVE_DATA_FLOW (FINDING) (CHR-420)
    * 4.21 REPORT_RESTORE_RISK (FINDING) (CHR-421)
    * 4.22 DISABLE_DATA_FLOW (REMEDIATION) (CHR-422)
    * 4.23 BLOCK_RESTORE (REMEDIATION) (CHR-423)
    * 4.24 DELETE_RECORD (REMEDIATION) (CHR-424)
    * 4.25 REDACT_RECORD (REMEDIATION) (CHR-425)
    * 4.26 ANONYMIZE_RECORD (REMEDIATION) (CHR-426)
    * 4.27 VERIFY_RECORD_ABSENT (VERIFICATION) (CHR-427)
    * 4.28 VERIFY_RECORD_PRESENT (VERIFICATION) (CHR-428)
    * 4.29 VERIFY_RECORD_REDACTED (VERIFICATION) (CHR-429)
    * 4.30 VERIFY_RECORD_ANONYMIZED (VERIFICATION) (CHR-430)
    * 4.31 VERIFY_DATA_FLOW_DISABLED (VERIFICATION) (CHR-431)
    * 4.32 VERIFY_RESTORE_BLOCKED (VERIFICATION) (CHR-432)
    * 4.33 What a COMPLETE row contains (CHR-433)
    * 4.34 What an INCOMPLETE row contains (CHR-434)
    * 4.35 Findings cite evidence (CHR-435)
    * 4.36 COMPLETE checks cite evidence (CHR-436)
    * 4.37 Future steps have an empty evidence_id (CHR-437)
    * 4.38 Evidence that must never be cited (CHR-438)
    * 4.39 Format reference (CHR-439)
 * 5.0 Solution constraints
    * 5.1 Conform to the project contract (CHR-501)
    * 5.2 Runs from the terminal (CHR-502)
    * 5.3 A clean run does everything (CHR-503)
    * 5.4 Only participant-facing data (CHR-504)
    * 5.5 No organizer-only files (CHR-505)
    * 5.6 No hardcoded labels or shortcuts (CHR-506)
    * 5.7 Deterministic behavior (CHR-507)
    * 5.8 Secrets from environment variables (CHR-508)
    * 5.9 Never commit or submit secrets (CHR-509)
    * 5.10 Paths relative to the repository root (CHR-510)
    * 5.11 Free choice of technology (CHR-511)
    * 5.12 Python entry point (CHR-512)
    * 5.13 Run instructions for other languages (CHR-513)
 * 6.0 Submission deliverables
    * 6.1 What is submitted (CHR-601)
    * 6.2 Contents of code.zip (CHR-602)
    * 6.3 output.csv is submitted (CHR-603)
    * 6.4 log.txt is the chat transcript (CHR-604)
    * 6.5 AI interview (CHR-605)
    * 6.6 README with setup and run instructions (CHR-606)
    * 6.7 Evaluation report file (CHR-607)
    * 6.8 Usage report file (CHR-608)
    * 6.9 Where the reports are placed (CHR-609)
    * 6.10 Report: case-level accuracy (CHR-610)
    * 6.11 Report: step-level and field-level accuracy (CHR-611)
    * 6.12 Report: sequence accuracy (CHR-612)
    * 6.13 Report: own evaluation cases (CHR-613)
    * 6.14 Report: failures and improvements (CHR-614)
    * 6.15 Usage report: the final full run (CHR-615)
    * 6.16 Usage report: providers and models (CHR-616)
    * 6.17 Usage report: model calls (CHR-617)
    * 6.18 Usage report: tokens (CHR-618)
    * 6.19 Usage report: tokens per request (CHR-619)
    * 6.20 Usage report: cost (CHR-620)
    * 6.21 Usage report: per-model totals (CHR-621)
    * 6.22 Details written in the Markdown files (CHR-622)
    * 6.23 Prompts in source code or Markdown (CHR-623)
    * 6.24 The code judge ignores raw data files (CHR-624)
    * 6.25 What code.zip must not contain (CHR-625)
    * 6.26 No nested archives (CHR-626)
    * 6.27 Packaging commands (CHR-627)
    * 6.28 Packaging on Windows (CHR-628)
    * 6.29 Checklist before submitting (CHR-629)
 * 7.0 Evaluation by the organizers
    * 7.1 Hidden canonical answers (CHR-701)
    * 7.2 Scored: deletion status (CHR-702)
    * 7.3 Scored: identity resolution (CHR-703)
    * 7.4 Scored: records and risks found (CHR-704)
    * 7.5 Scored: policy decisions (CHR-705)
    * 7.6 Scored: evidence references (CHR-706)
    * 7.7 Scored: steps complete and in order (CHR-707)
    * 7.8 Encouraged improvements (CHR-708)
 * 8.0 Development process and chat transcript
    * 8.1 AGENTS.md is the source of truth (CHR-801)
    * 8.2 Read AGENTS.md first (CHR-802)
    * 8.3 Start the coding tool from the repository root (CHR-803)
    * 8.4 The problem statement is the full specification (CHR-804)
    * 8.5 Minimal tool-specific configuration (CHR-805)
    * 8.6 Nested AGENTS.md files (CHR-806)
    * 8.7 Do not assume bash (CHR-807)
    * 8.8 Prefer language-native APIs (CHR-808)
    * 8.9 Session start sequence (CHR-809)
    * 8.10 Check the log file path (CHR-810)
    * 8.11 Append a SESSION START entry (CHR-811)
    * 8.12 Greeting (CHR-812)
    * 8.13 No invented deadline (CHR-813)
    * 8.14 Show the time remaining (CHR-814)
    * 8.15 Remind to submit (CHR-815)
    * 8.16 Deadline passed (CHR-816)
    * 8.17 No confirmation phrase (CHR-817)
    * 8.18 Follow the project contract (CHR-818)
    * 8.19 Quick checklist (CHR-819)
    * 8.20 Name and place of the log file (CHR-820)
    * 8.21 Find the log path relative to AGENTS.md (CHR-821)
    * 8.22 Create the log if missing (CHR-822)
    * 8.23 Append only (CHR-823)
    * 8.24 One shared log (CHR-824)
    * 8.25 Log every turn (CHR-825)
    * 8.26 Format of the SESSION START entry (CHR-826)
    * 8.27 Format of the per-turn entry (CHR-827)
    * 8.28 The user prompt, word for word (CHR-828)
    * 8.29 The tool= line (CHR-829)
    * 8.30 The model= line (CHR-830)
    * 8.31 Re-read and correct the entry (CHR-831)
    * 8.32 Entries of sub-agents (CHR-832)
    * 8.33 No secrets or personal data in the log (CHR-833)
    * 8.34 No large content in the log (CHR-834)
    * 8.35 UTF-8 and LF line endings (CHR-835)
    * 8.36 The submission URL (CHR-836)
    * 8.37 Give the exact URL when asked (CHR-837)
    * 8.38 No substitute URLs (CHR-838)
    * 8.39 The URL, not directions (CHR-839)
    * 8.40 Also in combined questions (CHR-840)
 * 9.0 Agent trace submission
    * 9.1 Submit agent-trace.zip (CHR-901)
    * 9.2 Every session and every harness (CHR-902)
    * 9.3 Keep the original formats (CHR-903)
    * 9.4 Quit before copying (CHR-904)
    * 9.5 Staging folder (CHR-905)
    * 9.6 Only this challenge's sessions (CHR-906)
    * 9.7 Review and redact (CHR-907)
    * 9.8 Create the ZIP (CHR-908)
    * 9.9 Check the ZIP (CHR-909)
    * 9.10 Claude Code session files (CHR-910)
    * 9.11 Claude Code /export (CHR-911)
    * 9.12 Claude web or desktop chat, if used (CHR-912)
    * 9.13 OpenAI Codex, if used (CHR-913)
    * 9.14 Google Antigravity, if used (CHR-914)
    * 9.15 OpenCode, if used (CHR-915)
    * 9.16 Other harnesses, if used (CHR-916)

# 1.0 Purpose and scope {#CHR-100}

Purpose and scope


## 1.1 AI-powered deletion-audit agent _(CHR-101)_ {#CHR-101}

The system shall be an AI-powered deletion-audit agent that audits, for each request, whether a user's personal data was actually deleted, and that can prove whether the data is truly gone.

*Parent links: SRC-AG0029, SRC-PS0007, SRC-RM0005*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | purpose |
| modality | shall |
| verification | inspection |


## 1.2 Where personal data can remain _(CHR-102)_ {#CHR-102}

The audit shall cover every place where personal data can remain although a deletion workflow reports "Complete": primary and secondary databases and their replicas, logs, support attachments, exports, search indexes, analytics records and exports, archives, and backups.

*Parent links: SRC-AG0031, SRC-PS0005, SRC-RM0007*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | purpose |
| modality | shall |
| verification | analysis |


## 1.3 Deleted data can come back _(CHR-103)_ {#CHR-103}

The audit shall take into account that active synchronization and restore processes can copy or recreate data that was already deleted from its original source.

*Parent links: SRC-AG0031, SRC-PS0005, SRC-RM0007*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | purpose |
| modality | shall |
| verification | analysis |


# 2.0 Inputs (dataset contract) {#CHR-200}

Inputs (dataset contract)


## 2.1 Read the inputs from dataset/ _(CHR-201)_ {#CHR-201}

The system shall read its input files from the dataset/ directory, which holds all participant-facing files.

*Parent links: SRC-AG0173, SRC-AG0321, SRC-PS0033, SRC-RM0028, SRC-RM0030, SRC-RM0045*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 2.2 Participant-facing files _(CHR-202)_ {#CHR-202}

dataset/ contains deletion_requests.csv, sample_deletion_requests.csv, sample_output.csv, user_identities.csv, user_audit_log.csv, system_activity.csv, deletion_rules.csv, evidence_files.csv, output.csv, and the folder evidence/ with the subfolders databases/, documents/, images/, logs/, and records/.

*Parent links: SRC-AG0175, SRC-RM0045*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | inspection |


## 2.3 deletion_requests.csv _(CHR-203)_ {#CHR-203}

dataset/deletion_requests.csv contains the 518 evaluation requests that must be audited; each row is one case.

*Parent links: SRC-AG0194, SRC-PS0037, SRC-PS0051, SRC-RM0049*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.4 Request fields _(CHR-204)_ {#CHR-204}

Each request has the fields case_id, email, requested_at, reported_status, reported_at, audit_at, request_text, in this order.

*Parent links: SRC-AG0210, SRC-AG0212, SRC-PS0051, SRC-PS0053*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.5 case_id _(CHR-205)_ {#CHR-205}

case_id uniquely identifies a request and its output row.

*Parent links: SRC-AG0216*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.6 email _(CHR-206)_ {#CHR-206}

email is the identity supplied with the request; it may be a current or a historical email address.

*Parent links: SRC-AG0217*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.7 requested_at _(CHR-207)_ {#CHR-207}

requested_at is the time when the request was submitted.

*Parent links: SRC-AG0218*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.8 reported_status _(CHR-208)_ {#CHR-208}

reported_status is the existing deletion workflow's claim and is one of COMPLETE, PARTIALLY_COMPLETE, or NOT_STARTED; it is not proof of the true state.

*Parent links: SRC-AG0219, SRC-PS0057*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.9 reported_at _(CHR-209)_ {#CHR-209}

reported_at is the time when the workflow's claim was reported.

*Parent links: SRC-AG0220*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.10 audit_at _(CHR-210)_ {#CHR-210}

audit_at is the cutoff time for which the answer of the case is required.

*Parent links: SRC-AG0221*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.11 request_text _(CHR-211)_ {#CHR-211}

request_text contains the person's request and may be written in different languages.

*Parent links: SRC-AG0222*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.12 Sample requests _(CHR-212)_ {#CHR-212}

dataset/sample_deletion_requests.csv contains 32 public sample requests.

*Parent links: SRC-AG0195, SRC-PS0038, SRC-RM0050*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | inspection |


## 2.13 Sample answers _(CHR-213)_ {#CHR-213}

dataset/sample_output.csv contains the correct outputs for the sample requests and demonstrates the required decision and serialization format.

*Parent links: SRC-AG0195, SRC-PS0039, SRC-RM0051*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | inspection |


## 2.14 user_identities.csv _(CHR-214)_ {#CHR-214}

dataset/user_identities.csv contains the current identity snapshot for each user: the stable user_id, name, email, phone, email hash, and the snapshot update time.

*Parent links: SRC-AG0196, SRC-PS0040, SRC-RM0052*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.15 user_audit_log.csv _(CHR-215)_ {#CHR-215}

dataset/user_audit_log.csv records historical changes to identity fields.

*Parent links: SRC-AG0197, SRC-PS0041, SRC-RM0053*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.16 system_activity.csv _(CHR-216)_ {#CHR-216}

dataset/system_activity.csv is a global stream of deletion, synchronization, export, backup, restore, indexing, audit, and related operational events across services and data processes; its rows may describe unrelated people.

*Parent links: SRC-AG0198, SRC-PS0042, SRC-RM0054*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.17 deletion_rules.csv _(CHR-217)_ {#CHR-217}

dataset/deletion_rules.csv defines the required action (treatment) for each data category and condition; the actions include deleting the whole record, redacting prohibited identifiers, anonymizing the record, retaining it, or preserving an account tombstone with only the permitted stable reference.

*Parent links: SRC-AG0199, SRC-PS0043, SRC-RM0055*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.18 evidence_files.csv _(CHR-218)_ {#CHR-218}

dataset/evidence_files.csv is the manifest of the evidence files under dataset/evidence/: it maps each file_id to its path, source origin, and capture time; it does not say which case or user a file concerns.

*Parent links: SRC-AG0200, SRC-PS0044, SRC-RM0056*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.19 Blank output template _(CHR-219)_ {#CHR-219}

dataset/output.csv is a blank output template provided as a reference; it is not the file that is submitted.

*Parent links: SRC-AG0201, SRC-PS0045, SRC-RM0040, SRC-RM0057*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | inspection |


## 2.20 Evidence formats _(CHR-220)_ {#CHR-220}

Evidence under dataset/evidence/ may be PDF documents, images (application screenshots), logs, JSON, plain-text records, and SQLite-compatible SQL snapshot exports.

*Parent links: SRC-AG0202, SRC-PS0047, SRC-RM0059*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |
| issues | ISS-09 |
| note | Decision ISS-09 (you, 2026-10-24): the union of the lists, so plain text is included.
 |


## 2.21 SQL snapshots _(CHR-221)_ {#CHR-221}

SQL evidence files are readable text and can be executed with SQLite; a capture may contain a primary database, regional replicas, a reporting replica, or a failover replica, so that replication drift can be investigated directly.

*Parent links: SRC-AG0202, SRC-AG0312, SRC-RM0059*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 2.22 Only the requests need answers _(CHR-222)_ {#CHR-222}

Only deletion_requests.csv requires predictions (answers); the other participant-facing files provide identity, policy, activity, and evidence context.

*Parent links: SRC-AG0204, SRC-RM0061*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | inspection |


## 2.23 Decoys and unrelated records _(CHR-223)_ {#CHR-223}

Global data (activity and evidence) can contain decoys and records about unrelated people.

*Parent links: SRC-AG0198, SRC-AG0204*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


# 3.0 Deletion audit logic {#CHR-300}

Deletion audit logic


## 3.1 Decide first whether deletion was requested _(CHR-301)_ {#CHR-301}

For each request, the system shall first determine from request_text whether the person actually requested (authorized) deletion, before auditing any deletion state.

*Parent links: SRC-AG0029, SRC-AG0222, SRC-AG0296, SRC-RM0009*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.2 Non-deletion requests _(CHR-302)_ {#CHR-302}

The system shall classify a request for access, correction, export, marketing opt-out, or any other non-deletion action as NOT_APPLICABLE, even if other fields of the request resemble a deletion case.

*Parent links: SRC-AG0296, SRC-PS0019*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.3 Requests in different languages _(CHR-303)_ {#CHR-303}

The system shall determine whether a request authorizes deletion also when the request text is written in a language other than English.

*Parent links: SRC-AG0222*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.4 Resolve current and historical identifiers _(CHR-304)_ {#CHR-304}

For an authorized deletion, the system shall resolve the subject's current and historical identifiers.

*Parent links: SRC-AG0029, SRC-AG0297, SRC-PS0009, SRC-PS0123*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.5 The request email may be old _(CHR-305)_ {#CHR-305}

The system shall identify the subject when the request email matches either a current or a historical email address.

*Parent links: SRC-AG0217, SRC-AG0297*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.6 Use the identity history _(CHR-306)_ {#CHR-306}

The system shall use user_audit_log.csv together with the current snapshot in user_identities.csv to recover identifiers that may still appear in older systems and evidence.

*Parent links: SRC-AG0197*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.7 Search activity and evidence _(CHR-307)_ {#CHR-307}

For an authorized deletion, the system shall investigate the supplied records by searching the global activity stream and the evidence for data about the subject.

*Parent links: SRC-AG0029, SRC-PS0009*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.8 Find evidence via the manifest, then read it _(CHR-308)_ {#CHR-308}

The system shall use evidence_files.csv to locate evidence files and then inspect their contents; it shall not infer which case a file belongs to from the manifest alone.

*Parent links: SRC-AG0200, SRC-AG0309*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.9 Grounded matching _(CHR-309)_ {#CHR-309}

The system shall match evidence to the subject through current identifiers, historical identifiers, hashes, resource IDs, system IDs, timestamps, and other grounded links in the contents.

*Parent links: SRC-AG0200, SRC-AG0310*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.10 Read images and PDFs _(CHR-310)_ {#CHR-310}

The system shall extract the facts contained in images and PDFs; these are ordinary business artifacts (for example invoices, support records, handover documents, and internal product screens) and do not contain an explicit deletion verdict.

*Parent links: SRC-AG0311*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.11 Replication drift _(CHR-311)_ {#CHR-311}

When investigating replication drift, the system shall compare the relevant tables and the snapshot times of the SQL replicas (primary, regional, reporting, failover).

*Parent links: SRC-AG0312, SRC-RM0059*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.12 Claims are not proof _(CHR-312)_ {#CHR-312}

The system shall treat reported_status, reported_result values, workflow statuses, operation results, activity logs, and system messages as claims, and shall not accept them as proof of a resource's state unless the available evidence establishes that state.

*Parent links: SRC-AG0031, SRC-AG0198, SRC-AG0298, SRC-AG0308, SRC-PS0057, SRC-PS0124, SRC-RM0073*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.13 Reconstruct the state at audit_at _(CHR-313)_ {#CHR-313}

The system shall reconstruct what happened across systems and determine the true state of each relevant resource at the case's audit_at from the available evidence.

*Parent links: SRC-AG0031, SRC-AG0298, SRC-PS0009, SRC-PS0124, SRC-RM0073*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.14 Nothing after audit_at _(CHR-314)_ {#CHR-314}

The system shall decide a case using only information available at or before its audit_at; evidence created later shall not change the answer for that case.

*Parent links: SRC-AG0224, SRC-AG0298*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.15 Find what still exposes the user _(CHR-315)_ {#CHR-315}

The system shall determine which records or identifiers still expose the user.

*Parent links: SRC-AG0033, SRC-PS0017, SRC-PS0020*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.16 Find what can recreate the data _(CHR-316)_ {#CHR-316}

The system shall determine which active processes can copy or recreate the user's deleted data, and which backup or restore paths can bring deleted data back.

*Parent links: SRC-AG0033, SRC-PS0017, SRC-PS0021*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.17 Apply the deletion policy everywhere _(CHR-317)_ {#CHR-317}

The system shall apply deletion_rules.csv to every relevant record, including account tombstones, active data flows, and restore risks.

*Parent links: SRC-AG0029, SRC-AG0299, SRC-PS0125*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.18 Do not over-delete _(CHR-318)_ {#CHR-318}

The system shall not delete, or propose deleting, data that the policy requires to be retained, redacted, anonymized, or preserved as a tombstone.

*Parent links: SRC-AG0299*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.19 Keep records the policy requires _(CHR-319)_ {#CHR-319}

The system shall preserve the records that the supplied policy requires the organization to retain.

*Parent links: SRC-AG0033, SRC-PS0011*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.20 Account tombstones _(CHR-320)_ {#CHR-320}

For an ACCOUNT_TOMBSTONE, the system shall keep the stable internal user reference (user_id), so that permitted records can still reference it, and shall require the removal of the name, email, phone, email hash, and any other direct identifiers required by the applicable REDACT rule.

*Parent links: SRC-AG0033, SRC-AG0300, SRC-PS0013*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.21 Decide COMPLETE or INCOMPLETE _(CHR-321)_ {#CHR-321}

For an authorized deletion, the system shall decide whether the deletion is actually complete (COMPLETE) or not (INCOMPLETE).

*Parent links: SRC-AG0029, SRC-PS0009, SRC-PS0017, SRC-PS0019, SRC-RM0009*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.22 COMPLETE needs: every copy treated _(CHR-322)_ {#CHR-322}

The system shall judge a deletion COMPLETE only if every relevant copy has received the treatment required by deletion_rules.csv.

*Parent links: SRC-AG0301, SRC-PS0024, SRC-PS0026*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.23 COMPLETE needs: nothing can recreate the data _(CHR-323)_ {#CHR-323}

The system shall judge a deletion COMPLETE only if no active sync, import, or restore path can recreate the prohibited data.

*Parent links: SRC-AG0301, SRC-PS0024, SRC-PS0027*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.24 COMPLETE needs: only permitted identifiers kept _(CHR-324)_ {#CHR-324}

The system shall judge a deletion COMPLETE only if the retained records contain only the identifiers permitted by the rules.

*Parent links: SRC-PS0024, SRC-PS0028*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.25 COMPLETE needs: required records still available _(CHR-325)_ {#CHR-325}

The system shall judge a deletion COMPLETE only if every record that must be retained remains available.

*Parent links: SRC-AG0301, SRC-PS0024, SRC-PS0029*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.26 Report every violation and risk _(CHR-326)_ {#CHR-326}

For an incomplete case, the system shall report every relevant policy violation (remaining records, exposed identifiers) and every recreation risk (active data flows, restore paths) that participant-visible evidence supports.

*Parent links: SRC-AG0033, SRC-AG0302, SRC-RM0009*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.27 Complete remediation plan _(CHR-327)_ {#CHR-327}

For an incomplete case, the system shall produce a safe, complete, ordered remediation plan: the steps required to remove, redact, or anonymize the remaining data and to stop recreation, so that the deletion request is completed.

*Parent links: SRC-AG0033, SRC-PS0011, SRC-PS0017, SRC-PS0022, SRC-RM0009*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.28 Stop flows and restores first _(CHR-328)_ {#CHR-328}

Within remediation, the system shall disable data flows and block unsafe restores before changing dependent records.

*Parent links: SRC-AG0303*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.29 Downstream copies before their sources _(CHR-329)_ {#CHR-329}

Within remediation, the system shall process downstream copies before their source records when the dependency requires it.

*Parent links: SRC-AG0303*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |
| issues | ISS-02 |
| note | Decision ISS-02 (you, 2026-10-24): where this conflicts with the sort order of CHR-416, the sort order wins, as in all 32 sample answers (case_16 and case_24 list the source before its downstream copy).
 |


## 3.30 Checks after remediation _(CHR-330)_ {#CHR-330}

For an incomplete case, the system shall state the verification checks that must pass after remediation; together they shall cover the required final state of every remediated record or process.

*Parent links: SRC-AG0033, SRC-AG0304, SRC-RM0009*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


## 3.31 Proof for complete deletions _(CHR-331)_ {#CHR-331}

For a complete case, the system shall produce the evidence-backed verification checks that prove the required state.

*Parent links: SRC-AG0033, SRC-PS0007, SRC-PS0011*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | functional |
| modality | shall |
| verification | test |


# 4.0 Output file (output.csv and steps_json) {#CHR-400}

Output file (output.csv and steps_json)


## 4.1 Write output.csv in the repository root _(CHR-401)_ {#CHR-401}

The system shall write its final predictions to output.csv in the repository root; this root-level file, not dataset/output.csv, is the file that is submitted.

*Parent links: SRC-AG0035, SRC-AG0201, SRC-AG0322, SRC-RM0028, SRC-RM0032, SRC-RM0040*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.2 Exact header _(CHR-402)_ {#CHR-402}

output.csv shall have the header case_id,deletion_status,steps_json: exactly these columns, in this order.

*Parent links: SRC-AG0035, SRC-AG0037, SRC-AG0228, SRC-AG0230, SRC-PS0061, SRC-PS0063, SRC-RM0067, SRC-RM0069, SRC-RM0151*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.3 One row per case _(CHR-403)_ {#CHR-403}

output.csv shall contain exactly one data row for every case_id in dataset/deletion_requests.csv.

*Parent links: SRC-AG0194, SRC-AG0216, SRC-AG0236, SRC-PS0061, SRC-RM0028, SRC-RM0031, SRC-RM0073*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.4 518 data rows _(CHR-404)_ {#CHR-404}

output.csv shall contain exactly 518 data rows plus the header row.

*Parent links: SRC-AG0236, SRC-PS0073, SRC-RM0075, SRC-RM0151*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.5 Sorted by case_id _(CHR-405)_ {#CHR-405}

The data rows of output.csv shall be sorted by case_id.

*Parent links: SRC-AG0237, SRC-PS0073, SRC-RM0075, SRC-RM0151*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |
| issues | ISS-03 |
| note | Decision ISS-03 (you, 2026-10-24): number order, i.e. sorted by the number after 'case_'. This is exactly the order of dataset/deletion_requests.csv.
 |


## 4.6 Meaning of the columns _(CHR-406)_ {#CHR-406}

In output.csv, case_id is the case being audited, deletion_status is the audit result, and steps_json is the ordered JSON array of findings, remediation actions, and verification checks.

*Parent links: SRC-PS0069, SRC-PS0070, SRC-PS0071, SRC-RM0073*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | fact |
| verification | test |


## 4.7 deletion_status values _(CHR-407)_ {#CHR-407}

deletion_status shall be one of COMPLETE, INCOMPLETE, or NOT_APPLICABLE.

*Parent links: SRC-AG0238, SRC-PS0019, SRC-PS0070, SRC-RM0009, SRC-RM0073*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.8 Rows for non-deletion requests _(CHR-408)_ {#CHR-408}

When the request does not authorize deletion, the row shall have deletion_status NOT_APPLICABLE and steps_json [] (an empty JSON array), for example case_000,NOT_APPLICABLE,[], because no deletion or deletion verification is authorized.

*Parent links: SRC-AG0239, SRC-PS0091, SRC-PS0093, SRC-PS0095, SRC-RM0073*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.9 steps_json is a JSON array _(CHR-409)_ {#CHR-409}

Every steps_json value shall be a valid JSON array.

*Parent links: SRC-AG0240, SRC-RM0073, SRC-RM0152*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.10 How the grader reads steps_json _(CHR-410)_ {#CHR-410}

The grader parses steps_json as JSON: object-key order and whitespace are ignored, but array order is significant.

*Parent links: SRC-AG0240, SRC-PS0089, SRC-PS0099, SRC-RM0075*

| Attribute | Value |
| --------- | ----- |
| party | organizer |
| kind | evaluation |
| modality | fact |
| verification | n/a |


## 4.11 Fields of a step _(CHR-411)_ {#CHR-411}

Each step object shall contain exactly the fields step_no, phase, system_id, resource_id, operation, state, and evidence_id.

*Parent links: SRC-AG0244, SRC-AG0246, SRC-PS0075, SRC-PS0077*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.12 Types of the step fields _(CHR-412)_ {#CHR-412}

In each step object, step_no shall be a JSON integer, and phase, system_id, resource_id, operation, state, and evidence_id shall be JSON strings.

*Parent links: SRC-AG0246, SRC-PS0077*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |
| note | The types are read from the example step object; the sources do not state them in words. Evidence (2026-10-24): all 193 steps in the 32 sample answers have exactly these 7 fields, with step_no an integer and the other six strings.
 |


## 4.13 Step numbers _(CHR-413)_ {#CHR-413}

step_no shall start at 1 and increase by 1 from step to step, in array order.

*Parent links: SRC-AG0241, SRC-PS0089, SRC-RM0152*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.14 Phase values _(CHR-414)_ {#CHR-414}

phase shall be one of FINDING, REMEDIATION, or VERIFICATION.

*Parent links: SRC-PS0089*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.15 Phase order _(CHR-415)_ {#CHR-415}

Steps shall be ordered by phase: all FINDING steps first, then all REMEDIATION steps, then all VERIFICATION steps.

*Parent links: SRC-AG0242, SRC-PS0126, SRC-RM0075*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.16 Order inside a phase _(CHR-416)_ {#CHR-416}

Inside each phase, steps shall be ordered by the operation order of the allowed-operations table (CHR-418 to CHR-432), then by system_id ascending, then by resource_id ascending.

*Parent links: SRC-PS0126, SRC-RM0075*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |
| issues | ISS-02 |
| note | Decision ISS-02 (you, 2026-10-24): always this sort order; all 51 multi-step phase blocks of the 32 sample answers follow it.
 |


## 4.17 No invented phases, operations, or states _(CHR-417)_ {#CHR-417}

Steps shall use only the allowed combinations of phase, operation, and state (CHR-418 to CHR-432); no other phases, operations, or states shall be invented.

*Parent links: SRC-AG0292*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |
| note | Evidence (2026-10-24): all 15 operations occur in the 32 sample answers, each only with the phase and state of its table row (CHR-418 to CHR-432).
 |


## 4.18 REPORT_REMAINING_RECORD (FINDING) _(CHR-418)_ {#CHR-418}

Operation REPORT_REMAINING_RECORD shall be used only in phase FINDING, always with state PRESENT, and means: a record that should have been deleted still exists.

*Parent links: SRC-AG0262, SRC-AG0266, SRC-PS0105*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.19 REPORT_EXPOSED_PII (FINDING) _(CHR-419)_ {#CHR-419}

Operation REPORT_EXPOSED_PII shall be used only in phase FINDING, always with state PRESENT, and means: a record may remain, but it still exposes identifiers that the policy requires to be redacted or anonymized.

*Parent links: SRC-AG0262, SRC-AG0267, SRC-PS0106*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.20 REPORT_ACTIVE_DATA_FLOW (FINDING) _(CHR-420)_ {#CHR-420}

Operation REPORT_ACTIVE_DATA_FLOW shall be used only in phase FINDING, always with state ACTIVE, and means: an active process can copy or recreate the user's data.

*Parent links: SRC-AG0262, SRC-AG0268, SRC-PS0107*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.21 REPORT_RESTORE_RISK (FINDING) _(CHR-421)_ {#CHR-421}

Operation REPORT_RESTORE_RISK shall be used only in phase FINDING, always with state ACTIVE, and means: a backup or restore path can bring deleted data back.

*Parent links: SRC-AG0262, SRC-AG0269, SRC-PS0108*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.22 DISABLE_DATA_FLOW (REMEDIATION) _(CHR-422)_ {#CHR-422}

Operation DISABLE_DATA_FLOW shall be used only in phase REMEDIATION, always with state DISABLED, and means: stop the process that can copy or recreate the data.

*Parent links: SRC-AG0271, SRC-AG0275, SRC-PS0109*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.23 BLOCK_RESTORE (REMEDIATION) _(CHR-423)_ {#CHR-423}

Operation BLOCK_RESTORE shall be used only in phase REMEDIATION, always with state BLOCKED, and means: prevent the affected backup from restoring the user's data.

*Parent links: SRC-AG0271, SRC-AG0276, SRC-PS0110*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.24 DELETE_RECORD (REMEDIATION) _(CHR-424)_ {#CHR-424}

Operation DELETE_RECORD shall be used only in phase REMEDIATION, always with state ABSENT, and means: remove the entire record.

*Parent links: SRC-AG0271, SRC-AG0277, SRC-PS0111*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.25 REDACT_RECORD (REMEDIATION) _(CHR-425)_ {#CHR-425}

Operation REDACT_RECORD shall be used only in phase REMEDIATION, always with state REDACTED, and means: keep the record but remove the identifying fields required by the policy.

*Parent links: SRC-AG0271, SRC-AG0278, SRC-PS0112*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.26 ANONYMIZE_RECORD (REMEDIATION) _(CHR-426)_ {#CHR-426}

Operation ANONYMIZE_RECORD shall be used only in phase REMEDIATION, always with state ANONYMIZED, and means: keep the record after irreversibly unlinking it from the user.

*Parent links: SRC-AG0271, SRC-AG0279, SRC-PS0113*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.27 VERIFY_RECORD_ABSENT (VERIFICATION) _(CHR-427)_ {#CHR-427}

Operation VERIFY_RECORD_ABSENT shall be used only in phase VERIFICATION, always with state ABSENT, and means: confirm that a record no longer exists.

*Parent links: SRC-AG0281, SRC-AG0285, SRC-PS0114*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.28 VERIFY_RECORD_PRESENT (VERIFICATION) _(CHR-428)_ {#CHR-428}

Operation VERIFY_RECORD_PRESENT shall be used only in phase VERIFICATION, always with state PRESENT, and means: confirm that a record that the policy requires to be retained still exists.

*Parent links: SRC-AG0281, SRC-AG0286, SRC-PS0115*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.29 VERIFY_RECORD_REDACTED (VERIFICATION) _(CHR-429)_ {#CHR-429}

Operation VERIFY_RECORD_REDACTED shall be used only in phase VERIFICATION, always with state REDACTED, and means: confirm that the required identifying fields have been removed.

*Parent links: SRC-AG0281, SRC-AG0287, SRC-PS0116*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.30 VERIFY_RECORD_ANONYMIZED (VERIFICATION) _(CHR-430)_ {#CHR-430}

Operation VERIFY_RECORD_ANONYMIZED shall be used only in phase VERIFICATION, always with state ANONYMIZED, and means: confirm that the record can no longer be linked to the user.

*Parent links: SRC-AG0281, SRC-AG0288, SRC-PS0117*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.31 VERIFY_DATA_FLOW_DISABLED (VERIFICATION) _(CHR-431)_ {#CHR-431}

Operation VERIFY_DATA_FLOW_DISABLED shall be used only in phase VERIFICATION, always with state DISABLED, and means: confirm that the relevant data flow is inactive.

*Parent links: SRC-AG0281, SRC-AG0289, SRC-PS0118*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.32 VERIFY_RESTORE_BLOCKED (VERIFICATION) _(CHR-432)_ {#CHR-432}

Operation VERIFY_RESTORE_BLOCKED shall be used only in phase VERIFICATION, always with state BLOCKED, and means: confirm that the affected data cannot be restored.

*Parent links: SRC-AG0281, SRC-AG0290, SRC-PS0119*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.33 What a COMPLETE row contains _(CHR-433)_ {#CHR-433}

For a COMPLETE case, steps_json shall contain only VERIFICATION steps, each backed by evidence, that prove the state at audit_at.

*Parent links: SRC-AG0258, SRC-PS0091*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.34 What an INCOMPLETE row contains _(CHR-434)_ {#CHR-434}

For an INCOMPLETE case, steps_json shall contain the findings, the complete ordered remediation plan, and the verification checks that must pass after remediation.

*Parent links: SRC-AG0258, SRC-PS0091, SRC-RM0073*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.35 Findings cite evidence _(CHR-435)_ {#CHR-435}

Every FINDING step shall cite in evidence_id the participant-visible file_id, activity_id, or audit_id that proves it.

*Parent links: SRC-AG0258, SRC-AG0313, SRC-PS0127, SRC-RM0073, SRC-RM0153*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |
| issues | ISS-07 |
| note | Decision ISS-07 (you, 2026-10-24): reading confirmed. All 32 sample answers follow it (findings 41 of 41 and COMPLETE checks 34 of 34 cite evidence; future steps 118 of 118 are empty).
 |


## 4.36 COMPLETE checks cite evidence _(CHR-436)_ {#CHR-436}

Every VERIFICATION step of a COMPLETE case shall cite in evidence_id the file_id, activity_id, or audit_id of the evidence that proves the current compliant state.

*Parent links: SRC-AG0314, SRC-PS0127, SRC-RM0073, SRC-RM0153*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |
| issues | ISS-07 |
| note | Decision ISS-07 (you, 2026-10-24): reading confirmed. All 32 sample answers follow it (findings 41 of 41 and COMPLETE checks 34 of 34 cite evidence; future steps 118 of 118 are empty).
 |


## 4.37 Future steps have an empty evidence_id _(CHR-437)_ {#CHR-437}

REMEDIATION steps and post-remediation VERIFICATION steps of an INCOMPLETE case describe future work and shall use the empty string "" as evidence_id.

*Parent links: SRC-AG0258, SRC-AG0315, SRC-PS0127, SRC-RM0154*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


## 4.38 Evidence that must never be cited _(CHR-438)_ {#CHR-438}

The system shall never cite organizer-only truth, nor an evidence item captured after the case's audit_at.

*Parent links: SRC-AG0316*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | test |


## 4.39 Format reference _(CHR-439)_ {#CHR-439}

output.csv shall follow the decision and serialization format demonstrated by dataset/sample_output.csv, which is the format reference.

*Parent links: SRC-AG0195, SRC-RM0073*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | interface |
| modality | shall |
| verification | test |


# 5.0 Solution constraints {#CHR-500}

Solution constraints


## 5.1 Conform to the project contract _(CHR-501)_ {#CHR-501}

The system shall conform to the project contract (AGENTS.md section 6) so that it can be evaluated.

*Parent links: SRC-AG0084*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | inspection |


## 5.2 Runs from the terminal _(CHR-502)_ {#CHR-502}

The solution shall be runnable from the terminal.

*Parent links: SRC-AG0320*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | demonstration |


## 5.3 A clean run does everything _(CHR-503)_ {#CHR-503}

A clean run of the solution shall process all 518 cases and produce exactly one valid row per case.

*Parent links: SRC-AG0327*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | test |


## 5.4 Only participant-facing data _(CHR-504)_ {#CHR-504}

The solution shall use only the participant-facing data under dataset/ for its predictions.

*Parent links: SRC-AG0085, SRC-AG0421*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | inspection |


## 5.5 No organizer-only files _(CHR-505)_ {#CHR-505}

Organizer-only truth, golden answers, review files, generator internals, and any other organizer-only files (they live outside dataset/) shall never be used for predictions, prompt examples, hardcoded labels, or evaluation-time shortcuts.

*Parent links: SRC-AG0085, SRC-AG0206, SRC-AG0323*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | inspection |


## 5.6 No hardcoded labels or shortcuts _(CHR-506)_ {#CHR-506}

The solution shall not use hardcoded golden labels or case-family shortcuts.

*Parent links: SRC-AG0323*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | inspection |


## 5.7 Deterministic behavior _(CHR-507)_ {#CHR-507}

The solution shall keep its behavior deterministic where possible, including ordering and JSON serialization.

*Parent links: SRC-AG0324*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | test |


## 5.8 Secrets from environment variables _(CHR-508)_ {#CHR-508}

The solution shall read secrets and credentials only from environment variables; an uncommitted .env file may be used when needed.

*Parent links: SRC-AG0086, SRC-AG0325*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | inspection |


## 5.9 Never commit or submit secrets _(CHR-509)_ {#CHR-509}

Secrets (API keys, tokens, credentials) and sensitive configuration values shall never be committed or submitted: not in prompts, code, configuration, log.txt, the reports, or any other part of the submission.

*Parent links: SRC-AG0086, SRC-AG0355, SRC-PS0160, SRC-RM0114, SRC-RM0157*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | constraint |
| modality | shall |
| verification | inspection |


## 5.10 Paths relative to the repository root _(CHR-510)_ {#CHR-510}

The solution shall resolve dataset and output paths relative to the repository root so that it works on macOS, Linux, and Windows.

*Parent links: SRC-AG0404*

| Attribute | Value |
| --------- | ----- |
| party | system |
| kind | constraint |
| modality | shall |
| verification | test |


## 5.11 Free choice of technology _(CHR-511)_ {#CHR-511}

The participant may use any programming language, model, framework, IDE, AI assistant, retrieval approach, or tool, subject to the official event rules; there is no required language.

*Parent links: SRC-AG0083, SRC-AG0372, SRC-RM0127*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | constraint |
| modality | may |
| verification | n/a |


## 5.12 Python entry point _(CHR-512)_ {#CHR-512}

If the solution is written in Python, its entry point should be code/main.py, run from the repository root with: python3 code/main.py

*Parent links: SRC-AG0372, SRC-RM0026, SRC-RM0034, SRC-RM0036*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | constraint |
| modality | should |
| verification | inspection |
| issues | ISS-08 |
| note | Decision ISS-08 (you, 2026-10-24): on this machine use python as is (python3 is not set up for now); code/README.md will show both the python3 and the python command.
 |


## 5.13 Run instructions for other languages _(CHR-513)_ {#CHR-513}

If another language is used, its exact setup and run command shall be documented clearly in the submitted README.md.

*Parent links: SRC-AG0372, SRC-RM0026*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-10 |
| note | Decision ISS-10 (you, 2026-10-24): the submitted README.md is our code/README.md; the root README.md stays the organizers' original.
 |


# 6.0 Submission deliverables {#CHR-600}

Submission deliverables


## 6.1 What is submitted _(CHR-601)_ {#CHR-601}

The participant submission shall consist of: code.zip, output.csv, the chat transcript (chat_transcript), and an AI interview.

*Parent links: SRC-AG0359, SRC-AG0363, SRC-AG0364, SRC-AG0365, SRC-AG0366, SRC-PS0145, SRC-PS0146, SRC-PS0147, SRC-PS0148, SRC-PS0162, SRC-RM0122, SRC-RM0123, SRC-RM0124, SRC-RM0125*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-05 |
| note | Decision ISS-05 (you, 2026-10-24, revised): log.txt is the chat_transcript; at the end the agent trace is prepared exactly as agent_trace_instructions.md describes (agent-trace.zip); where to upload it is checked then.
 |


## 6.2 Contents of code.zip _(CHR-602)_ {#CHR-602}

code.zip shall contain the runnable solution, the prompts, the configuration, README.md, and the evaluation/ reports.

*Parent links: SRC-AG0363, SRC-PS0145, SRC-RM0122, SRC-RM0155*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.3 output.csv is submitted _(CHR-603)_ {#CHR-603}

output.csv, with one answer row for each of the 518 evaluation requests, shall be submitted.

*Parent links: SRC-AG0364, SRC-PS0146, SRC-RM0123*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.4 log.txt is the chat transcript _(CHR-604)_ {#CHR-604}

The root log.txt generated by the coding agent shall be uploaded directly as the chat_transcript submission on HackerRank; it shows how the system was developed or used.

*Parent links: SRC-AG0365, SRC-PS0147, SRC-RM0113, SRC-RM0124, SRC-RM0156*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.5 AI interview _(CHR-605)_ {#CHR-605}

The participant shall explain, live in an AI interview, the architecture, the investigation approach, the remediation planning, and the evaluation.

*Parent links: SRC-AG0366, SRC-PS0148, SRC-RM0125*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | demonstration |


## 6.6 README with setup and run instructions _(CHR-606)_ {#CHR-606}

The README.md submitted inside code.zip shall contain clear setup and run instructions.

*Parent links: SRC-AG0326, SRC-RM0127*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-10 |
| note | Decision ISS-10 (you, 2026-10-24): the root README.md stays the organizers' original; our README with setup and run instructions is code/README.md.
 |


## 6.7 Evaluation report file _(CHR-607)_ {#CHR-607}

code.zip shall include the evaluation report evaluation_report.md in the evaluation/ folder.

*Parent links: SRC-AG0331, SRC-AG0333, SRC-PS0133, SRC-RM0089, SRC-RM0091, SRC-RM0155*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-01 |
| note | Decision ISS-01 (you, 2026-10-24): option (a), code/evaluation/ only. Inside code.zip the file is code/evaluation/evaluation_report.md.
 |


## 6.8 Usage report file _(CHR-608)_ {#CHR-608}

code.zip shall include the token-usage report usage_report.md in the evaluation/ folder.

*Parent links: SRC-AG0331, SRC-AG0333, SRC-PS0152, SRC-PS0154, SRC-RM0089, SRC-RM0091, SRC-RM0155*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-01 |
| note | Decision ISS-01 (you, 2026-10-24): option (a), code/evaluation/ only. Inside code.zip the file is code/evaluation/usage_report.md.
 |


## 6.9 Where the reports are placed _(CHR-609)_ {#CHR-609}

The two reports shall be placed in code/evaluation/ (next to code/evaluation/main.py) so that they are bundled with code/; if they are placed in a top-level evaluation/ folder instead, that folder shall be added to the archive command.

*Parent links: SRC-RM0099, SRC-RM0143, SRC-RM0145*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-01 |
| note | Decision ISS-01 (you, 2026-10-24): option (a), code/evaluation/ only. No top-level evaluation/ folder.
 |


## 6.10 Report: case-level accuracy _(CHR-610)_ {#CHR-610}

evaluation_report.md shall contain the case-level deletion-status accuracy.

*Parent links: SRC-AG0338, SRC-AG0340, SRC-PS0133, SRC-PS0135, SRC-RM0096*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.11 Report: step-level and field-level accuracy _(CHR-611)_ {#CHR-611}

evaluation_report.md shall contain the step-level (row-level) and the field-level accuracy.

*Parent links: SRC-AG0338, SRC-AG0341, SRC-PS0133, SRC-PS0136, SRC-RM0096*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-04 |
| note | Decision ISS-04 (you, 2026-10-24): README's 'row' accuracy is the step-level accuracy; the report uses both names.
 |


## 6.12 Report: sequence accuracy _(CHR-612)_ {#CHR-612}

evaluation_report.md shall contain the sequence accuracy.

*Parent links: SRC-AG0338, SRC-AG0342, SRC-PS0133, SRC-PS0137, SRC-RM0096*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.13 Report: own evaluation cases _(CHR-613)_ {#CHR-613}

evaluation_report.md shall contain at least three additional evaluation cases created by the participant (team).

*Parent links: SRC-AG0338, SRC-AG0343, SRC-PS0133, SRC-PS0138, SRC-RM0096*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.14 Report: failures and improvements _(CHR-614)_ {#CHR-614}

evaluation_report.md shall describe the failures found and the improvements made.

*Parent links: SRC-AG0338, SRC-AG0344, SRC-PS0133, SRC-PS0139, SRC-RM0096*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.15 Usage report: the final full run _(CHR-615)_ {#CHR-615}

usage_report.md shall summarize the final full-dataset run that produced output.csv.

*Parent links: SRC-AG0346, SRC-PS0158, SRC-RM0097*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.16 Usage report: providers and models _(CHR-616)_ {#CHR-616}

usage_report.md shall list the model providers and the model names.

*Parent links: SRC-AG0346, SRC-AG0348, SRC-PS0158, SRC-RM0097*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.17 Usage report: model calls _(CHR-617)_ {#CHR-617}

usage_report.md shall contain the model-call counts.

*Parent links: SRC-AG0346, SRC-AG0349, SRC-PS0158, SRC-RM0097*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.18 Usage report: tokens _(CHR-618)_ {#CHR-618}

usage_report.md shall contain the input tokens and the output tokens.

*Parent links: SRC-AG0346, SRC-AG0350, SRC-PS0158, SRC-RM0097*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.19 Usage report: tokens per request _(CHR-619)_ {#CHR-619}

usage_report.md shall contain the total tokens and the average tokens per request.

*Parent links: SRC-AG0346, SRC-AG0351, SRC-PS0158, SRC-RM0097*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.20 Usage report: cost _(CHR-620)_ {#CHR-620}

usage_report.md shall contain the estimated total cost and the estimated cost per request.

*Parent links: SRC-AG0346, SRC-AG0352, SRC-PS0158, SRC-RM0097*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.21 Usage report: per-model totals _(CHR-621)_ {#CHR-621}

When several models are used, usage_report.md shall contain both per-model and overall totals, in the same file.

*Parent links: SRC-AG0346, SRC-AG0353, SRC-PS0158, SRC-RM0097*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.22 Details written in the Markdown files _(CHR-622)_ {#CHR-622}

The evaluation metrics, the custom evaluation cases, and the token and cost details shall be written directly inside the Markdown report files.

*Parent links: SRC-AG0355, SRC-RM0099*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.23 Prompts in source code or Markdown _(CHR-623)_ {#CHR-623}

Prompts shall be kept in source code or Markdown files.

*Parent links: SRC-RM0099*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.24 The code judge ignores raw data files _(CHR-624)_ {#CHR-624}

Automated code evaluation ignores raw data files (.csv, .tsv, .json, .jsonl, .sql, .log); content stored only in those formats is not visible to the code judge or the AI interviewer.

*Parent links: SRC-RM0099*

| Attribute | Value |
| --------- | ----- |
| party | organizer |
| kind | evaluation |
| modality | fact |
| verification | n/a |


## 6.25 What code.zip must not contain _(CHR-625)_ {#CHR-625}

code.zip shall not include dataset/, virtual environments (.venv, venv, node_modules), dependency or build caches (such as __pycache__), API keys, credentials, real personal data, or sensitive configuration.

*Parent links: SRC-AG0368, SRC-RM0129, SRC-RM0143, SRC-RM0146, SRC-RM0157*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.26 No nested archives _(CHR-626)_ {#CHR-626}

code.zip shall not contain nested archive files (.zip, .tar, .gz, .tgz, .7z, .rar); submissions that contain them are rejected.

*Parent links: SRC-AG0368, SRC-RM0143, SRC-RM0147*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.27 Packaging commands _(CHR-627)_ {#CHR-627}

code.zip should be created from the repository root with the provided command, which bundles README.md and code/ but not the dataset: zip -r code.zip README.md code -x (exclusions) on macOS/Linux, or Compress-Archive -Path README.md, code -DestinationPath code.zip -Force in Windows PowerShell.

*Parent links: SRC-RM0129, SRC-RM0133, SRC-RM0139*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | should |
| verification | demonstration |
| issues | ISS-10 |
| note | See ISS-10: the provided command also packs the organizers' root README.md, so code.zip would hold two READMEs (theirs at the top, ours at code/README.md). To be decided at packaging time.
 |


## 6.28 Packaging on Windows _(CHR-628)_ {#CHR-628}

On Windows, .venv shall be kept at the repository root (outside code/), and any code/__pycache__ folders shall be removed before running Compress-Archive.

*Parent links: SRC-RM0143, SRC-RM0146*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |


## 6.29 Checklist before submitting _(CHR-629)_ {#CHR-629}

Before submitting, the participant shall confirm: the output.csv header and its 518 sorted rows; valid JSON arrays with consecutive step numbers from 1; valid evidence IDs in findings and evidence in COMPLETE verification steps; an empty evidence_id in proposed steps; the required code.zip contents; the log.txt format and upload; and that no API keys, credentials, real personal data, or sensitive configuration values are included.

*Parent links: SRC-RM0149, SRC-RM0151, SRC-RM0152, SRC-RM0153, SRC-RM0154, SRC-RM0155, SRC-RM0156, SRC-RM0157*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


# 7.0 Evaluation by the organizers {#CHR-700}

Evaluation by the organizers


## 7.1 Hidden canonical answers _(CHR-701)_ {#CHR-701}

output.csv will be compared with hidden canonical answers.

*Parent links: SRC-PS0131, SRC-RM0081*

| Attribute | Value |
| --------- | ----- |
| party | organizer |
| kind | evaluation |
| modality | fact |
| verification | n/a |


## 7.2 Scored: deletion status _(CHR-702)_ {#CHR-702}

Scoring considers the correctness of deletion_status (deletion assessment accuracy).

*Parent links: SRC-PS0131, SRC-RM0081, SRC-RM0083*

| Attribute | Value |
| --------- | ----- |
| party | organizer |
| kind | evaluation |
| modality | fact |
| verification | n/a |


## 7.3 Scored: identity resolution _(CHR-703)_ {#CHR-703}

Scoring considers current and historical identity resolution.

*Parent links: SRC-PS0131, SRC-RM0081, SRC-RM0084*

| Attribute | Value |
| --------- | ----- |
| party | organizer |
| kind | evaluation |
| modality | fact |
| verification | n/a |


## 7.4 Scored: records and risks found _(CHR-704)_ {#CHR-704}

Scoring considers the discovery of remaining data (records) and recreation risks.

*Parent links: SRC-PS0131, SRC-RM0081, SRC-RM0085*

| Attribute | Value |
| --------- | ----- |
| party | organizer |
| kind | evaluation |
| modality | fact |
| verification | n/a |


## 7.5 Scored: policy decisions _(CHR-705)_ {#CHR-705}

Scoring considers correct policy application (policy decisions).

*Parent links: SRC-PS0131, SRC-RM0081, SRC-RM0086*

| Attribute | Value |
| --------- | ----- |
| party | organizer |
| kind | evaluation |
| modality | fact |
| verification | n/a |


## 7.6 Scored: evidence references _(CHR-706)_ {#CHR-706}

Scoring considers the cited evidence references.

*Parent links: SRC-PS0131, SRC-RM0081, SRC-RM0086*

| Attribute | Value |
| --------- | ----- |
| party | organizer |
| kind | evaluation |
| modality | fact |
| verification | n/a |


## 7.7 Scored: steps complete and in order _(CHR-707)_ {#CHR-707}

Scoring considers the completeness and the ordering of the remediation and verification steps in steps_json.

*Parent links: SRC-PS0131, SRC-RM0081, SRC-RM0087*

| Attribute | Value |
| --------- | ----- |
| party | organizer |
| kind | evaluation |
| modality | fact |
| verification | n/a |


## 7.8 Encouraged improvements _(CHR-708)_ {#CHR-708}

Participants are encouraged to improve retrieval, multimodal interpretation, identity and deletion-state reconstruction, remediation planning, deterministic verification, batching, caching, and token efficiency.

*Parent links: SRC-PS0162*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | evaluation |
| modality | should |
| verification | n/a |


# 8.0 Development process and chat transcript {#CHR-800}

Development process and chat transcript


## 8.1 AGENTS.md is the source of truth _(CHR-801)_ {#CHR-801}

AGENTS.md is the single source of truth for any AI coding agent working in this repository; the coding agent shall obey it exactly unless the user or the platform gives higher-priority instructions.

*Parent links: SRC-AG0005, SRC-AG0007*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.2 Read AGENTS.md first _(CHR-802)_ {#CHR-802}

At the start of each session, the coding agent shall read AGENTS.md completely before taking any action.

*Parent links: SRC-AG0007, SRC-AG0013, SRC-AG0015, SRC-AG0413, SRC-CL0001*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.3 Start the coding tool from the repository root _(CHR-803)_ {#CHR-803}

The participant shall start the AI coding tool from the repository root (or explicitly ask it to read ./AGENTS.md first), so that it reads AGENTS.md and logs every turn to the root log.txt.

*Parent links: SRC-RM0024, SRC-RM0112*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.4 The problem statement is the full specification _(CHR-804)_ {#CHR-804}

problem_statement.md is the full participant-facing specification (the complete challenge contract) and shall be read.

*Parent links: SRC-AG0041, SRC-RM0011*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.5 Minimal tool-specific configuration _(CHR-805)_ {#CHR-805}

Tool-specific configuration (for example CLAUDE.md, which only imports AGENTS.md) shall be kept minimal and point back to AGENTS.md.

*Parent links: SRC-AG0403, SRC-CL0001*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.6 Nested AGENTS.md files _(CHR-806)_ {#CHR-806}

If a nested AGENTS.md exists, the closest one governs the files inside that sub-project, but the logging rules (AGENTS.md sections 2 and 5) stay global: logging goes to the log.txt beside the top-level AGENTS.md.

*Parent links: SRC-AG0405*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.7 Do not assume bash _(CHR-807)_ {#CHR-807}

The coding agent shall not assume that bash is available.

*Parent links: SRC-AG0402*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | constraint |
| modality | shall |
| verification | inspection |


## 8.8 Prefer language-native APIs _(CHR-808)_ {#CHR-808}

The coding agent should prefer language-native APIs when possible.

*Parent links: SRC-AG0402*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | constraint |
| modality | should |
| verification | inspection |


## 8.9 Session start sequence _(CHR-809)_ {#CHR-809}

At the start of every session the coding agent shall, in this order: read AGENTS.md completely, check the log file path, and append a SESSION START entry; then, during the session, append a per-turn entry for every user turn and follow the project contract when building, testing, evaluating, or packaging.

*Parent links: SRC-AG0013, SRC-AG0067*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.10 Check the log file path _(CHR-810)_ {#CHR-810}

At session start, the coding agent shall check the log file path defined in AGENTS.md section 2.

*Parent links: SRC-AG0016*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.11 Append a SESSION START entry _(CHR-811)_ {#CHR-811}

At the beginning of each session, the coding agent shall append a short SESSION START entry in the format of AGENTS.md section 5.1.

*Parent links: SRC-AG0017, SRC-AG0069, SRC-AG0414*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.12 Greeting _(CHR-812)_ {#CHR-812}

At session start, the coding agent shall greet the user with this introduction: "Welcome to HackerRank Orchestrate. Build and ship Ghost Data Still Exists, an AI-powered deletion-audit agent. Let's get started."

*Parent links: SRC-AG0070, SRC-AG0072*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.13 No invented deadline _(CHR-813)_ {#CHR-813}

The coding agent shall treat the October challenge end time as not configured in this repository, and shall not invent a deadline or reuse the September deadline.

*Parent links: SRC-AG0076, SRC-AG0415*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.14 Show the time remaining _(CHR-814)_ {#CHR-814}

If a higher-priority instruction or an official repository update supplies the end time, the coding agent shall calculate and display the time remaining.

*Parent links: SRC-AG0076*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.15 Remind to submit _(CHR-815)_ {#CHR-815}

If fewer than 2 hours remain, the coding agent shall remind the user to submit soon.

*Parent links: SRC-AG0076*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.16 Deadline passed _(CHR-816)_ {#CHR-816}

If the deadline has passed, the coding agent shall state that clearly, without blocking further work.

*Parent links: SRC-AG0076*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.17 No confirmation phrase _(CHR-817)_ {#CHR-817}

The coding agent shall proceed with the user's request without requiring an acknowledgement or confirmation phrase.

*Parent links: SRC-AG0077*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.18 Follow the project contract _(CHR-818)_ {#CHR-818}

When building, testing, evaluating, or packaging the solution, the coding agent shall follow the project contract (AGENTS.md section 6) and preserve the Ghost Data Still Exists deletion-audit and output contract.

*Parent links: SRC-AG0019, SRC-AG0422*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.19 Quick checklist _(CHR-819)_ {#CHR-819}

Before responding to any user message, the coding agent shall confirm the quick checklist in AGENTS.md section 9.

*Parent links: SRC-AG0411, SRC-AG0413, SRC-AG0414, SRC-AG0415, SRC-AG0416, SRC-AG0417, SRC-AG0418, SRC-AG0419, SRC-AG0420, SRC-AG0421, SRC-AG0422*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.20 Name and place of the log file _(CHR-820)_ {#CHR-820}

The log file shall be named log.txt and be located in the repository root, the directory that contains the top-level AGENTS.md (<root>/log.txt on macOS/Linux, <root>\log.txt on Windows).

*Parent links: SRC-AG0047, SRC-AG0051, SRC-AG0052, SRC-AG0087, SRC-RM0024, SRC-RM0105, SRC-RM0109, SRC-RM0110*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.21 Find the log path relative to AGENTS.md _(CHR-821)_ {#CHR-821}

The log path shall be resolved relative to AGENTS.md; no folder name, user path, or platform home directory shall be hardcoded, so that the location stays correct across clones, renames, and checkouts.

*Parent links: SRC-AG0054, SRC-AG0400*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.22 Create the log if missing _(CHR-822)_ {#CHR-822}

The coding agent shall create log.txt if it is missing.

*Parent links: SRC-AG0058*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.23 Append only _(CHR-823)_ {#CHR-823}

log.txt shall only be appended to: earlier entries shall not be rewritten, reordered, or deleted.

*Parent links: SRC-AG0021, SRC-AG0059*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.24 One shared log _(CHR-824)_ {#CHR-824}

One shared log.txt is used per checkout: all agents, sub-agents, and worktrees append to the same file next to the top-level AGENTS.md, never to a private or per-worktree copy.

*Parent links: SRC-AG0021, SRC-AG0060, SRC-AG0157, SRC-AG0159*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.25 Log every turn _(CHR-825)_ {#CHR-825}

The coding agent shall log every conversation turn by appending a per-turn entry (AGENTS.md section 5.2) after every user message it responds to; logging shall never be skipped.

*Parent links: SRC-AG0018, SRC-AG0021, SRC-AG0087, SRC-AG0126, SRC-AG0416, SRC-RM0112*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.26 Format of the SESSION START entry _(CHR-826)_ {#CHR-826}

A SESSION START entry shall follow the AGENTS.md section 5.1 template: the heading "## [ISO-8601 TIMESTAMP] SESSION START", then the lines tool=, model=, Repo Root:, Branch:, Worktree:, Parent Agent:, Language: (js, ts, py, or custom:name), and Time Remaining: (Xd Yh Zm, or not configured).

*Parent links: SRC-AG0111*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.27 Format of the per-turn entry _(CHR-827)_ {#CHR-827}

A per-turn entry shall follow the AGENTS.md section 5.2 template: the heading "## [ISO-8601 TIMESTAMP] <short title, max 80 chars>", then the sections "User Prompt (verbatim, secrets redacted):", "Agent Response Summary:" (2-5 sentences: what was done, why, and any important decision), "Actions:" (one bullet per file edited, command run, or tool invoked), and "Context:" with the lines tool=, model=, branch=, repo_root=, worktree=, parent_agent=.

*Parent links: SRC-AG0128, SRC-RM0112, SRC-RM0156*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.28 The user prompt, word for word _(CHR-828)_ {#CHR-828}

A per-turn entry shall contain the exact user message, with secrets replaced by [REDACTED].

*Parent links: SRC-AG0128*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.29 The tool= line _(CHR-829)_ {#CHR-829}

Every SESSION START and per-turn entry shall contain exactly one non-empty tool= line with the exact name of the coding harness or agent that writes the entry, checked against the harness identity given by the runtime; a missing or blank value, a placeholder, a generic label such as "AI", a model name, or another harness makes the entry invalid; the tool name shall never be guessed.

*Parent links: SRC-AG0149, SRC-AG0153, SRC-AG0417, SRC-AG0419*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.30 The model= line _(CHR-830)_ {#CHR-830}

Every SESSION START and per-turn entry shall contain exactly one non-empty model= line with the exact model identifier used for that turn, taken from the runtime, session metadata, harness configuration, or another authoritative source; unknown, a model family, a generic label, an inferred name, or a placeholder is invalid; the model name shall never be guessed and does not replace tool=.

*Parent links: SRC-AG0151, SRC-AG0153, SRC-AG0418, SRC-AG0419*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.31 Re-read and correct the entry _(CHR-831)_ {#CHR-831}

Before completing a response, the coding agent shall re-read the newly appended log entry, confirm that it has exactly one populated tool= line and exactly one populated model= line with authoritative values, and correct any problem before responding.

*Parent links: SRC-AG0149, SRC-AG0153, SRC-AG0419*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.32 Entries of sub-agents _(CHR-832)_ {#CHR-832}

Sub-agents shall log their own entries in the same log file and set parent_agent= to the name of their parent agent.

*Parent links: SRC-AG0157, SRC-AG0158*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.33 No secrets or personal data in the log _(CHR-833)_ {#CHR-833}

log.txt shall not contain API keys, tokens, session cookies, OAuth codes, credentials, private keys, sensitive configuration, or real personal data; such values shall be redacted.

*Parent links: SRC-AG0061, SRC-AG0161, SRC-AG0163, SRC-AG0164, SRC-AG0420, SRC-RM0114*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.34 No large content in the log _(CHR-834)_ {#CHR-834}

log.txt shall not contain the full contents of large files or binary blobs; they shall be referenced by path instead.

*Parent links: SRC-AG0161, SRC-AG0165*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.35 UTF-8 and LF line endings _(CHR-835)_ {#CHR-835}

Logs shall be written in UTF-8 with \n (LF) line endings.

*Parent links: SRC-AG0401*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.36 The submission URL _(CHR-836)_ {#CHR-836}

The October challenge and submission URL is https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists (copied character for character from AGENTS.md).

*Parent links: SRC-AG0092, SRC-AG0094*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | fact |
| verification | n/a |


## 8.37 Give the exact URL when asked _(CHR-837)_ {#CHR-837}

When the user asks for the challenge link, the submission link, where or how to submit, where to upload the code, or any equivalent question, the coding agent shall provide this exact URL, in full and clickable, every time.

*Parent links: SRC-AG0088, SRC-AG0096, SRC-AG0100*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.38 No substitute URLs _(CHR-838)_ {#CHR-838}

The coding agent shall not replace the URL with the HackerRank homepage, the contest homepage, another challenge page, or a guessed /submission URL.

*Parent links: SRC-AG0101*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.39 The URL, not directions _(CHR-839)_ {#CHR-839}

The coding agent shall give the URL directly and not merely describe where to navigate.

*Parent links: SRC-AG0102*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


## 8.40 Also in combined questions _(CHR-840)_ {#CHR-840}

The URL rule shall also apply when the challenge or submission question comes together with other questions.

*Parent links: SRC-AG0103*

| Attribute | Value |
| --------- | ----- |
| party | coding-agent |
| kind | process |
| modality | shall |
| verification | inspection |


# 9.0 Agent trace submission {#CHR-900}

Agent trace submission


## 9.1 Submit agent-trace.zip _(CHR-901)_ {#CHR-901}

The participant shall submit the complete agent trace of the work done on this challenge as a ZIP file named agent-trace.zip, together with the challenge submission.

*Parent links: SRC-AT0003, SRC-AT0013, SRC-AT0130*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | deliverable |
| modality | shall |
| verification | inspection |
| issues | ISS-05 |
| note | Decision ISS-05 (you, 2026-10-24, revised): log.txt is the chat_transcript; at the end the agent trace is prepared exactly as agent_trace_instructions.md describes (agent-trace.zip); where to upload it is checked then. So CHR-901 to CHR-916 apply.
 |


## 9.2 Every session and every harness _(CHR-902)_ {#CHR-902}

The trace shall include every session used for this challenge (including planning, coding, debugging, and review sessions) and, if more than one agent harness was used, the traces of each one.

*Parent links: SRC-AT0005*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.3 Keep the original formats _(CHR-903)_ {#CHR-903}

The original files and folder structure shall be kept where practical; JSONL, SQLite, and other structured logs shall not be converted into screenshots or summaries.

*Parent links: SRC-AT0005, SRC-AT0108*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.4 Quit before copying _(CHR-904)_ {#CHR-904}

The sessions to be submitted shall be finished and the app or CLI quit before its files are copied, so that the logs are completely written.

*Parent links: SRC-AT0009, SRC-AT0104*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.5 Staging folder _(CHR-905)_ {#CHR-905}

A temporary folder named agent-trace shall be created somewhere easy to find; only the relevant trace files shall be copied into it, with one subfolder per tool (for example agent-trace/claude-code/ and agent-trace/codex/).

*Parent links: SRC-AT0010, SRC-AT0105*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.6 Only this challenge's sessions _(CHR-906)_ {#CHR-906}

Only the session files for this challenge shall be included, not the entire home directory or application-data folder.

*Parent links: SRC-AT0011, SRC-AT0108*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.7 Review and redact _(CHR-907)_ {#CHR-907}

The staged files shall be reviewed before sharing: secrets (API keys, tokens, passwords, cookies, private keys), personal information, and material that may not be shared shall be removed or redacted, and authentication files, settings, and credentials shall not be included.

*Parent links: SRC-AT0012, SRC-AT0109*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.8 Create the ZIP _(CHR-908)_ {#CHR-908}

The agent-trace folder shall be zipped with the operating system's built-in archive tool, from the directory that contains agent-trace/: zip -r agent-trace.zip agent-trace on macOS/Linux, or Compress-Archive -Path .\agent-trace -DestinationPath .\agent-trace.zip -Force in Windows PowerShell.

*Parent links: SRC-AT0013, SRC-AT0110, SRC-AT0116, SRC-AT0118, SRC-AT0124, SRC-AT0126*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.9 Check the ZIP _(CHR-909)_ {#CHR-909}

The ZIP shall be opened once after it is created, to confirm that it contains the intended traces and no credentials or unrelated files.

*Parent links: SRC-AT0130*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.10 Claude Code session files _(CHR-910)_ {#CHR-910}

For Claude Code, the session files of this challenge (commonly JSONL files named with a session ID) shall be copied from the project folder under ~/.claude/projects/ (macOS/Linux) or %USERPROFILE%\.claude\projects\ (Windows) into agent-trace/claude-code/; the right folder and files are found by their content and timestamps.

*Parent links: SRC-AT0019, SRC-AT0021, SRC-AT0022, SRC-AT0024*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.11 Claude Code /export _(CHR-911)_ {#CHR-911}

In each Claude Code session, /export shall be run and the readable transcript saved in agent-trace/claude-code/, in addition to the original session JSONL files when they are available.

*Parent links: SRC-AT0028, SRC-AT0030, SRC-AT0034*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.12 Claude web or desktop chat, if used _(CHR-912)_ {#CHR-912}

If Claude was used in the web app or the desktop chat for this challenge, only the relevant conversation export (Settings, Privacy, Export data) shall be included.

*Parent links: SRC-AT0036*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.13 OpenAI Codex, if used _(CHR-913)_ {#CHR-913}

If OpenAI Codex was used, the rollout files of the challenge sessions (rollout-*.jsonl in date folders under ~/.codex/sessions/, %USERPROFILE%\.codex\sessions\, or $CODEX_HOME/sessions/) shall be copied into agent-trace/codex/ (plus a reviewed session_index.jsonl only if useful), never auth.json, config.toml, credential stores, or the whole .codex directory; for hosted-only sessions, the interface's export shall be used, with a note that no local trace file exists.

*Parent links: SRC-AT0042, SRC-AT0044, SRC-AT0045, SRC-AT0047, SRC-AT0049, SRC-AT0051*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.14 Google Antigravity, if used _(CHR-914)_ {#CHR-914}

If Google Antigravity was used, the complete conversation folder(s) of this challenge under the product's brain directory (with .system_generated/logs/transcript.jsonl) shall be copied to agent-trace/antigravity/, not the entire .gemini directory; last_conversations.json is only a lookup cache, not the transcript.

*Parent links: SRC-AT0055, SRC-AT0057, SRC-AT0059, SRC-AT0060, SRC-AT0061, SRC-AT0062, SRC-AT0064, SRC-AT0066, SRC-AT0070*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.15 OpenCode, if used _(CHR-915)_ {#CHR-915}

If OpenCode was used, each challenge session shall be exported as JSON (opencode session export, optionally with --sanitize) into agent-trace/opencode/; only if the CLI is unavailable, a copy of opencode.db may be provided after quitting OpenCode and checking the copy; auth.json shall never be included, and logs or snapshots do not replace the exports.

*Parent links: SRC-AT0074, SRC-AT0076, SRC-AT0077, SRC-AT0079, SRC-AT0081, SRC-AT0085, SRC-AT0087, SRC-AT0092, SRC-AT0094, SRC-AT0098*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


## 9.16 Other harnesses, if used _(CHR-916)_ {#CHR-916}

If another agent harness or coding tool was used (for example Aider, Goose, RooCode, Cline, Devin, Factory, or JetBrains Junie), its challenge sessions shall be exported with the tool's own export feature and its raw structured trace files copied into agent-trace/<harness-name>/, keeping the original formats and subagent folders and excluding credentials and settings files.

*Parent links: SRC-AT0102, SRC-AT0104, SRC-AT0105, SRC-AT0106, SRC-AT0107, SRC-AT0108, SRC-AT0109, SRC-AT0110*

| Attribute | Value |
| --------- | ----- |
| party | participant |
| kind | process |
| modality | shall |
| verification | inspection |


