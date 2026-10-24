# Step 4: the interfaces between the components

| | |
|---|---|
| Date | 2026-10-25 |
| State | Done, waiting for your review; then the components are implemented one at a time (EXT-610) |
| Goal | Define how the components talk to each other, so that every component can be tested alone with fakes (EXT-609) |
| Not in this step | Any component's logic |

## What was made

A new component, `ARC-00_interfaces` (`code/c00_interfaces/`), listed first:

| File | Holds |
|---|---|
| `records.py` | The plain data records the components exchange: Request, IdentityRecord, IdentityChange, Activity, DeletionRule, EvidenceFile, Dataset; Observation (one record seen in one evidence item); Identity, Resource, ResourceState, Judgement, CaseVerdict; Step, CaseAnswer, CaseResult; ModelQuestion, ModelCall; Scores |
| `components.py` | The call signature of every component, and the `Components` bundle the audit pipeline receives |
| `fakes.py` | `FakeModelGateway`: answers with whatever a test tells it, and records the questions |
| `test_interfaces.py` | Proves that a fake gateway and plain functions fit every signature |

How data flows, with the signature of each component:

```text
01 input_reader        dataset_dir                                   -> Dataset
02 model_gateway       ModelQuestion                                 -> answer text (+ ModelCall records)
03 evidence_reader     evidence files, dataset_dir, gateway          -> Observations
04 request_classifier  Requests, gateway                             -> RequestDecision per case
05 identity_resolver   email, identities, identity changes, audit_at -> Identity
06 resource_finder     Identity, Request, Observations, Activities   -> Resources
07 state_reconstructor Resources, Observations, Activities, audit_at -> ResourceStates
08 policy_checker      case_id, ResourceStates, DeletionRules        -> CaseVerdict (one Judgement per resource)
09 step_planner        CaseVerdict                                   -> CaseAnswer (ordered Steps)
10 audit_pipeline      Components bundle, dataset_dir                -> output.csv + explanation per case
11 evaluator           predicted and expected CaseAnswers            -> Scores
```

Why this makes components testable alone (EXT-602): every component is a function of plain
records. A test builds the input records by hand and checks the output records; it never needs
another component. The audit pipeline gets all components as one bundle, so its test can pass
fakes. The two components that need the AI model (03 for screenshots, 04) get the gateway as a
parameter, so their tests pass `FakeModelGateway`.

Every ARC item's `interface` attribute now names its exact signature; see
[views/ARC.md](../../requirements/views/ARC.md).

## Your instructions, recorded

| ID | Says |
|---|---|
| EXT-609 | Interfaces first, so that tests can replace any component by a fake |
| EXT-610 | Components implemented one at a time, each started with your go-ahead |
| EXT-611 | The component that calls an AI model (`ARC-02_model_gateway`) is implemented last |

Planned order: 01 input_reader, 03 evidence_reader, 04 request_classifier, 05 identity_resolver,
06 resource_finder, 07 state_reconstructor, 08 policy_checker, 09 step_planner, 10 audit_pipeline,
11 evaluator, and last 02 model_gateway. Until then, 03 and 04 are tested with the fake gateway.

They link to your words after your next commit (Doorstop shows 3 expected warnings until then).

## A mistake on the way, and its repair

The first script that updated the ARC items saved them before Doorstop had loaded them (Doorstop
loads items lazily), which wrote 12 items nearly empty. `doorstop -F -W` and `srctrace.py check`
reported it at once. The 12 files were restored from your commit "Step3" with `git restore`, and the
update was run again with every item loaded first. Afterwards: `srctrace.py check` PASS, and
Doorstop shows only the 3 expected warnings.

## How to check

```powershell
python -m unittest discover -s code -t code -p "test_*.py"     # must end with OK
.venv-req\Scripts\python requirements\tools\srctrace.py check   # must end with RESULT: PASS
```
