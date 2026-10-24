### Table of Contents

    * 1.1 Interfaces (ARC-00_interfaces)
    * 1.2 Input reader (ARC-01_input_reader)
    * 1.3 Model gateway (ARC-02_model_gateway)
    * 1.4 Evidence reader (ARC-03_evidence_reader)
    * 1.5 Request classifier (ARC-04_request_classifier)
    * 1.6 Identity resolver (ARC-05_identity_resolver)
    * 1.7 Resource finder (ARC-06_resource_finder)
    * 1.8 State reconstructor (ARC-07_state_reconstructor)
    * 1.9 Policy checker (ARC-08_policy_checker)
    * 1.10 Step planner (ARC-09_step_planner)
    * 1.11 Audit pipeline (ARC-10_audit_pipeline)
    * 1.12 Evaluator (ARC-11_evaluator)
    * 1.13 Delivery process (not code) (ARC-12_delivery_process)

## 1.1 Interfaces _(ARC-00_interfaces)_ {#ARC-00_interfaces}

The data records the components exchange (code/c00_interfaces/records.py) and the call signature of every component (code/c00_interfaces/components.py). Components depend only on these, never on each other's code; the audit pipeline receives the components as one bundle, so a test can replace any of them, and the model gateway, by a fake (code/c00_interfaces/fakes.py).

*Parent links: EXT-504, EXT-505, EXT-506, EXT-602, EXT-603, EXT-609, REV-005*

| Attribute | Value |
| --------- | ----- |
| code | code/c00_interfaces/ |
| interface | records.py and components.py |


## 1.2 Input reader _(ARC-01_input_reader)_ {#ARC-01_input_reader}

Reads the CSV files of dataset/ (requests, identities, identity history, activity, deletion rules, evidence manifest, sample requests and answers) into plain records, checks every value where it is read, and reports what it had to skip.

*Parent links: CHR-201, CHR-202, CHR-203, CHR-204, CHR-205, CHR-206, CHR-207, CHR-208, CHR-209, CHR-210, CHR-211, CHR-212, CHR-213, CHR-214, CHR-215, CHR-216, CHR-217, CHR-218, CHR-504, CHR-505, CHR-510, EXT-501, EXT-503, EXT-504, EXT-505, EXT-506, EXT-601, EXT-602, EXT-603*

| Attribute | Value |
| --------- | ----- |
| code | code/c01_input_reader/ |
| interface | DatasetReader: dataset_dir -> Dataset (all CSV records, input problems)
 |


## 1.3 Model gateway _(ARC-02_model_gateway)_ {#ARC-02_model_gateway}

The only place that calls an AI model. Provider and model are settings; adapters speak the Anthropic API and the OpenAI-compatible API over plain HTTP. Caches every answer, records calls, tokens, and cost, and checks each answer before handing it on. Reads the API key from the environment only.

*Parent links: CHR-101, CHR-508, EXT-401, EXT-402, EXT-405, EXT-502, EXT-503, EXT-504, EXT-505, EXT-506, EXT-601, EXT-602, EXT-603, EXT-611*

| Attribute | Value |
| --------- | ----- |
| code | code/c02_model_gateway/ |
| interface | ModelGateway: ask(ModelQuestion) -> answer text; calls() -> ModelCall records
 |


## 1.4 Evidence reader _(ARC-03_evidence_reader)_ {#ARC-03_evidence_reader}

Opens each file of the evidence manifest and turns its contents into observations: which resource, in which system or store, seen when, with which identifiers and which state facts. One reader per format: SQL snapshot (sqlite3), log, JSON, text, PDF (pypdf); screenshots are read through the model gateway, once, and cached.

*Parent links: CHR-218, CHR-220, CHR-221, CHR-308, CHR-310, CHR-311, EXT-405, EXT-406, EXT-501, EXT-502, EXT-503, EXT-504, EXT-505, EXT-506, EXT-601, EXT-602, EXT-603, REV-005*

| Attribute | Value |
| --------- | ----- |
| code | code/c03_evidence_reader/ |
| interface | EvidenceReader: evidence files, dataset_dir, ModelGateway -> EvidenceReading (Observations, StoreListings, input problems)
 |


## 1.5 Request classifier _(ARC-04_request_classifier)_ {#ARC-04_request_classifier}

Decides whether a request text, in any language, authorizes deletion. The text is passed to the model as data, never as instructions.

*Parent links: CHR-301, CHR-302, CHR-303, CHR-623, EXT-502, EXT-504, EXT-505, EXT-506, EXT-601, EXT-602, EXT-603*

| Attribute | Value |
| --------- | ----- |
| code | code/c04_request_classifier/ |
| interface | RequestClassifier: Requests, ModelGateway -> RequestDecision per case
 |


## 1.6 Identity resolver _(ARC-05_identity_resolver)_ {#ARC-05_identity_resolver}

Finds the subject of a request from its email (current or old) and collects all current and old identifiers: user_id, emails, phones, names, and email hashes.

*Parent links: CHR-304, CHR-305, CHR-306, EXT-504, EXT-505, EXT-506, EXT-601, EXT-602, EXT-603, REV-001, REV-002*

| Attribute | Value |
| --------- | ----- |
| code | code/c05_identity_resolver/ |
| interface | IdentityResolver: email, IdentityRecords, IdentityChanges, audit_at -> Identity or none
 |


## 1.7 Resource finder _(ARC-06_resource_finder)_ {#ARC-06_resource_finder}

Finds every record, data flow, and backup of the subject in the observations and the activity stream, through grounded links only (identifiers, hashes, resource IDs), and ignores decoys.

*Parent links: CHR-102, CHR-103, CHR-223, CHR-307, CHR-309, CHR-315, CHR-316, EXT-504, EXT-505, EXT-506, EXT-601, EXT-602, EXT-603, REV-001, REV-002*

| Attribute | Value |
| --------- | ----- |
| code | code/c06_resource_finder/ |
| interface | ResourceFinder: Identity, Request, Observations, Activities -> Resources
 |


## 1.8 State reconstructor _(ARC-07_state_reconstructor)_ {#ARC-07_state_reconstructor}

Decides the state of each resource at audit_at from the evidence captured at or before audit_at (activity results are claims), and names the evidence item that proves it.

*Parent links: CHR-208, CHR-311, CHR-312, CHR-313, CHR-314, CHR-438, EXT-504, EXT-505, EXT-506, EXT-601, EXT-602, EXT-603, REV-005*

| Attribute | Value |
| --------- | ----- |
| code | code/c07_state_reconstructor/ |
| interface | StateReconstructor: Resources, EvidenceReading, Activities, audit_at -> ResourceStates
 |


## 1.9 Policy checker _(ARC-08_policy_checker)_ {#ARC-08_policy_checker}

Maps each resource to its data category and deletion rule, and judges whether its state complies with the required treatment; decides COMPLETE or INCOMPLETE.

*Parent links: CHR-217, CHR-317, CHR-318, CHR-319, CHR-320, CHR-321, CHR-322, CHR-323, CHR-324, CHR-325, CHR-1001, CHR-1002, CHR-1003, CHR-1004, CHR-1005, CHR-1006, CHR-1007, CHR-1008, CHR-1009, CHR-1010, CHR-1011, CHR-1012, CHR-1013, CHR-1014, CHR-1015, EXT-504, EXT-505, EXT-506, EXT-601, EXT-602, EXT-603*

| Attribute | Value |
| --------- | ----- |
| code | code/c08_policy_checker/ |
| interface | PolicyChecker: case_id, ResourceStates, DeletionRules, audit_at -> CaseVerdict (Judgements)
 |


## 1.10 Step planner _(ARC-09_step_planner)_ {#ARC-09_step_planner}

Turns the policy results into the ordered steps of steps_json (findings, remediation, verification), with the evidence rules and the fixed sort order, and serializes them deterministically.

*Parent links: CHR-326, CHR-327, CHR-328, CHR-329, CHR-330, CHR-331, CHR-406, CHR-407, CHR-408, CHR-409, CHR-410, CHR-411, CHR-412, CHR-413, CHR-414, CHR-415, CHR-416, CHR-417, CHR-418, CHR-419, CHR-420, CHR-421, CHR-422, CHR-423, CHR-424, CHR-425, CHR-426, CHR-427, CHR-428, CHR-429, CHR-430, CHR-431, CHR-432, CHR-433, CHR-434, CHR-435, CHR-436, CHR-437, CHR-439, EXT-202, EXT-504, EXT-505, EXT-506, EXT-601, EXT-602, EXT-603, REV-003, REV-004*

| Attribute | Value |
| --------- | ----- |
| code | code/c09_step_planner/ |
| interface | StepPlanner: CaseVerdict -> CaseAnswer (ordered Steps) |


## 1.11 Audit pipeline _(ARC-10_audit_pipeline)_ {#ARC-10_audit_pipeline}

The entry point code/main.py. Runs the components for every case, writes output.csv at the repository root (one row per case, number order) and a readable explanation of every step beside it.

*Parent links: CHR-101, CHR-219, CHR-222, CHR-401, CHR-402, CHR-403, CHR-404, CHR-405, CHR-501, CHR-502, CHR-503, CHR-506, CHR-507, CHR-510, CHR-512, EXT-203, EXT-401, EXT-402, EXT-404, EXT-501, EXT-504, EXT-505, EXT-506, EXT-601, EXT-602, EXT-603*

| Attribute | Value |
| --------- | ----- |
| code | code/c10_audit_pipeline/ |
| interface | Components bundle, dataset_dir -> output.csv and a CaseResult (answer, explanation) per case
 |


## 1.12 Evaluator _(ARC-11_evaluator)_ {#ARC-11_evaluator}

Scores output against the sample answers the way the organizers score (status, steps, fields, sequence), runs our own evaluation cases, and computes the numbers of evaluation_report.md and usage_report.md from recorded data.

*Parent links: CHR-213, CHR-607, CHR-608, CHR-609, CHR-610, CHR-611, CHR-612, CHR-613, CHR-614, CHR-615, CHR-616, CHR-617, CHR-618, CHR-619, CHR-620, CHR-621, CHR-622, CHR-624, CHR-701, CHR-702, CHR-703, CHR-704, CHR-705, CHR-706, CHR-707, CHR-708, EXT-201, EXT-403, EXT-504, EXT-505, EXT-506, EXT-601, EXT-602, EXT-603*

| Attribute | Value |
| --------- | ----- |
| code | code/c11_evaluator/ |
| interface | Evaluator: predicted and expected CaseAnswers -> Scores |


## 1.13 Delivery process (not code) _(ARC-12_delivery_process)_ {#ARC-12_delivery_process}

How the work is done and delivered: the coding agent's rules and log.txt, the requirements and their traceability tools, the README, packaging of code.zip, the submission, and the agent trace. Checked by inspection, not by program tests.

*Parent links: CHR-509, CHR-511, CHR-513, CHR-601, CHR-602, CHR-603, CHR-604, CHR-605, CHR-606, CHR-609, CHR-623, CHR-625, CHR-626, CHR-627, CHR-628, CHR-629, CHR-801, CHR-802, CHR-803, CHR-804, CHR-805, CHR-806, CHR-807, CHR-808, CHR-809, CHR-810, CHR-811, CHR-812, CHR-813, CHR-814, CHR-815, CHR-816, CHR-817, CHR-818, CHR-819, CHR-820, CHR-821, CHR-822, CHR-823, CHR-824, CHR-825, CHR-826, CHR-827, CHR-828, CHR-829, CHR-830, CHR-831, CHR-832, CHR-833, CHR-834, CHR-835, CHR-836, CHR-837, CHR-838, CHR-839, CHR-840, CHR-901, CHR-902, CHR-903, CHR-904, CHR-905, CHR-906, CHR-907, CHR-908, CHR-909, CHR-910, CHR-911, CHR-912, CHR-913, CHR-914, CHR-915, CHR-916, EXT-101, EXT-102, EXT-103, EXT-104, EXT-105, EXT-106, EXT-107, EXT-108, EXT-109, EXT-110, EXT-111, EXT-204, EXT-205, EXT-206, EXT-301, EXT-302, EXT-601, EXT-602, EXT-603, EXT-604, EXT-605, EXT-606, EXT-607, EXT-608, EXT-610, EXT-611*

| Attribute | Value |
| --------- | ----- |
| code | - |
| interface | - |


