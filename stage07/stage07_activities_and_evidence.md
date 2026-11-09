# Stage 7 Testing and Verification Record

Group/tutorial: Solo Group Hunter Taylor (Tutorial Tuesday 5:30pm) Members/cohorts: none
Requirements baseline: SmartCare A3 Requirements Baseline 2026, revision 2.
Use the same project/. Link actual evidence; keep responses concise. Blank fields are for your group. Copy rows only as needed.

All Assignment 3 stage materials are provided from the beginning. Complete this stage only after the previous applicable stage has been integrated, verified and recorded. Use this supplied record in stage07/ in your EXISTING repository. Preserve project/, all earlier tests, records and responses. Do not download another starter or copy staff solutions.

## A Tutorial Activities

### Activity 1 Requirement to test

For each requirement, propose one positive test, one negative test and the key assertion.

| Requirement | Positive test | Negative test | Key assertion |
|---|---|---|---|
| FR-01 Register patient | registered P1 with a valid name and then lookup | regist P1 again with a different name | lookup is the original patient and the duplicate will raise a ValueError |
| FR-05 Prevent practitioner conflict | book the same practitioner at a different time | book the same practitioner at the exact same time as SCHEDULED appointment | the conflicting booking will raise a ValueError |
| FR-06 Cancel appointment | cancelling a SCHEDULED appointment | cancelling an appointment that has already been cancelled | first time the appointment is set to status CANCELLED any future attempts raise a ValueError |
| FR-07 Retain cancelled history | cancel the appointment and then look it up via ID | look up an ID that was never booked | the appointment that did exist can still be found and the other raises a ValueError |

### Activity 2 Strong or weak assertion

For each, select Strong for stated behaviour or Weak/unclear and explain why. State the behaviour and limits.

`assert True`
Judgement: Weak/unclear  Why: it does not check the result, only that the line was reached.

`assert appointment is not None`
Judgement: Weak/unclear  Why: It does show an object exists, however it could be the wrong appointment

`assert appointment.status == AppointmentStatus.CANCELLED`
Judgement: Strong for stated behaviour  Why: it checks the status that the cancellation must produce.

`assert len(results) > 0`
Judgement: Weak/unclear  Why: a non-empty list could still contain wrong records.

`assert data_store.find_appointment('A1') is appointment`
Judgement: Strong for stated behaviour  Why: it checks if the store returns the exact object.

### Activity 3 Boundary thinking

unsure.

### Activity 4 Critique GitHub Copilot tests

GitHub Copilot generates five tests, all of which pass. Two only assert that objects are not None, one asserts True, and two assume SMS notifications exist. Identify what is wrong and rewrite the test intentions.

| Candidate | What is wrong | Rewritten test intention |
|---|---|---|
| 1 | proves that an object exists. may not be the right one | register P1. check that when lookup is used it returns the same object. |
| 2 | has the same weakness | book an appointment and then check what it includes |
| 3 | this will always pass | try to cancel twice |
| 4 | notifcations are not a requriment for this task | i believe you'd reject it? |
| 5 | same thing as the last | reject |

### Tutorial exit question

Why can 100% code coverage coexist with poor software verification?
this only checks that every line ran, not that any results were actually checked.

## B Requirement to Test Traceability Matrix 

Assign TEST IDs before implementation or generation. Use canonical AC IDs with their actual meaning; quote supporting revision 2 contracts when no canonical AC is assigned. Blank-ID validation is not AC-01.2. Identify supplied versus student-authored evidence.

| Requirement | Acceptance criterion | Test ID | Test type | Test name / location | Expected behaviour | Result / observed status | Supplied or student-authored |
|---|---|---|---|---|---|---|---|
| Test ID | Requirement | AC | Positive / Negative / Boundary | Test intention | Observable result expected | Added evidence beyond supplied tests |
|---|---|---|---|---|---|---|
| T7-01 | Patient validation | n/a | Positive | valid name and ID are stored | fields = inputs | tests don't actually check patient fields directly. |
| T7-02 | Revision 2 validation | n/a | Negative / Boundary | blank, whitespace-only or any non-text ID or name | ValueError | will cover whitespace-only and none edges |
| T7-03 | Revision 2 validation | n/a | Boundary | IDs get trimmed and are case-sensitive | '' P1 '' stored as 'P1'; 'p1' stays 'p1' | trimming and case contract are pinned |
| T7-04, T7-05 | Practitioner validation | n/a | Positive / Negative | Valid fields stored: blank ID, name or specialty are rejected | Fields kept: ValueError | practitioner is not covered by supplied tests |
| T7-06 | Appointment construction | n/a | Positive | New appointment starts SCHEDULED and keeps the same participant objects | `status is SCHEDULED`; `is` identity | checks identity and not just equality |

## C Test Design

Use descriptive test names such as test_cancel_changes_status() or test_blank_patient_id_is_rejected(). Explain what new evidence each case adds.

| Test ID | Requirement | Acceptance criterion | Positive / Negative / Boundary | Test intention | Observable result expected | Added evidence beyond supplied tests |
|---|---|---|---|---|---|---|
| T7-01 | Patient validation | n/a | Positive | valid IDs and names are stored | equal inputs are required in each field | tests don't check the fields directly |

## D Arrange Act Assert Record

Arrange test data; act on one meaningful behaviour; assert the required observable outcome. Use the specific current exception with pytest.raises where needed.

| Test ID | Arrange | Act | Assert | Why meaningful / why assertion proves criterion |
|---|---|---|---|---|
| T7-02 | any bad ID values ('''', ''   '', 'None') | constructing patient | 'pytest.raises(ValueError)' | blank input is rejected by specfied document error |

## E Domain Test Evidence

Cover Patient/Practitioner construction and validation; Appointment construction, initial status, cancellation and illegal/repeated transitions. Preserve the four reference intentions described in handout Part C.

| Test ID | Behaviour | Test file/function | Result |
|---|---|---|---|
| T7-01 | patient stores the valid fields | tests/test_domain.py::test_patient_stores_valid_id_and_name | Pass |

## F Service Test Evidence

Use fresh shared SmartCareDataStore state, registered objects and completed Stage 6 services.

| Test ID | Behaviour | Requirement / criterion | Test file/function | Result |
|---|---|---|---|---|
| T7-11 | register stores patient | FR-01 / AC-01.1 | tests/test_services.py::test_register_patient_stores_the_patient | Pass |

## G Negative and Boundary Cases

Connect cases to actual contracts and verify unchanged state after rejection.

| Behaviour | Boundary/invalid input | Expected result | Test ID |
|---|---|---|---|
| patient or practitioner construction | '''', ''   '', 'None' | ValueError | T7-02, T7-05 |

## H GitHub Copilot Test Design

Select ONE real acceptance criterion. Complete human-first fields before using Copilot. Do not require an accepted generated test.

Requirement: FR-05 prevent practitioner conflict. practitioner can't be booked for 2 SCHEDULED appointments.
Acceptance criterion: “AC-04.1 (under FR-05): the same practitioner, the same exact date/time and an existing SCHEDULED appointment is a conflict and the new booking is rejected.”
Behaviour to test: booking acceptance, conflict with exact times, time/status boundry
Human-first test idea/categories: valid booking, same-time conflict
Prompt and purpose: Act as a software test-design assistant.
Requirement: FR-05 Prevent practitioner conflict. A practitioner must not be booked for two SCHEDULED appointments at the same exact date and time.

Acceptance criterion: AC-04.1 (under FR-05): the same practitioner, the same exact date/time and an existing SCHEDULED appointment is a conflict and the new booking is rejected. (AC-04.2, which is out of scope for this prompt, allows a different practitioner at the same time.)
Propose pytest test candidates covering a valid case, an invalid case and meaningful boundaries. For each
candidate, state exactly which required behaviour it is intended to verify. Do not invent behaviour not stated in the requirement or criterion. Use observable outcomes rather than private implementation
details. Use the current SmartCare public contracts and shared SmartCareDataStore. Do not introduce
SQLite, repository abstractions or unrelated features. Do not claim that a proposed test has been executed

For each significant candidate, copy this entry as needed:
- Copilot test idea/candidate: cancel an appointment, then book same practitoner
- What it claims to verify: a cancelled appointment should not block any booking already scheduled
- Requirement trace: boundary for SCHEDULED
- Assertion quality: checks the status and store appointments
- Human critique: id say its secondary to the direct conflict test
- Decision: accept
- Reason: checks the status condtion
- Final test reference if accepted/modified: proposed but not modified
- Actual verification result: it was not run

Before accepting: traces to a requirement/criterion; can fail for the right reason; assertion checks required behaviour; no invented business rule; no unnecessary private implementation dependence. Reject/modify weak assertions, invented requirements, excessive mocking, duplicates, wrong exceptions, obsolete architecture and unnecessary dependencies.

## I Weak Copilot Test Reflection

sorry, i didn't have time to finish this
Which Copilot-generated test looked convincing but was weak? not done
Why was it weak? not done
How did you strengthen it? not done
Accepted / modified / rejected test decisions and evidence: [link actual decisions in H]

## J Regression Run

Run python -m pytest from project/. Retain all accumulated tests. Record the tested SHA accurately.

| Command | Working directory | Code SHA | Passed | Failed | Failure summary | Product defect / test defect / unresolved | Evidence and interpretation |
|---|---|---|---|---|---|---|---|
| py -m pytest | project/ | c014226388d82b10d1c4f14bc2c45ab557cf4ac2 | [81] | [0] | [none] | [none observed] | all tests passed when running pytest |

Individual test runs and changed-order independence evidence:
- `py -m pytest tests/test_services.py::test_register_patient_stores_the_patient` (from project/): [1 passed]
- `py -m pytest tests/test_services.py::test_find_appointment_unknown_id_raises_lookup_error tests/test_services.py::test_register_patient_stores_the_patient` (these were run in a different order): [2 passed]
- `py -m pytest tests/test_domain.py::test_cancel_changes_scheduled_to_cancelled`: [1 passed]
Optional tutor-led demonstration notes: [optional; leave blank if not used]
A meaningful test should detect a relevant incorrect result. Students do not have to perform the demonstration or submit failure/restoration evidence for assessment. The tutor restores the example and reruns its tests. This is not a Stage 8 fault activity.

## K What the Suite Still Does Not Prove

What does your test suite still not prove?
it shows that all the scenarios that I tested behave how they should.
Coverage if used: not used
Which uncovered areas matter, and why does coverage percentage alone not establish correctness? the console recovery as well as error recovery are what matter the most.
Optional fixtures/parametrisation used and why, if any: used for one rejection rule

## L Git and Review Evidence

Use links rather than copying GitHub history. Continue the Stage 6 workflow; no commit/PR count, conflict or individual test quota is imposed.

| Issue/task | Branch | PR | Reviewer | Key feedback | Outcome |
|---|---|---|---|---|---|
|  | Add domain and service tests for Stage 7 | feature/stage7-tests | https://github.com/HunterAmpharos/st1-assignment-3/pull/6 | i did this solo | none | merged

## M Contribution Evidence

Record actual work in test design, implementation, review, traceability, diagnosis, necessary fixes and integration. Do not include confidential peer ratings.

| Member | Actual contribution | Evidence link |
|---|---|---|
| AmpharosHunter | everything during this part | https://github.com/HunterAmpharos/st1-assignment-3/pull/6 |

## N Formative Questions

1. What question does verification answer?
does the implementation meet the requirments?

2. What question does validation answer?
does the product actually meet the needs requested?

3. What is a unit test?
a test of an objects behaviour on its own

4. What is a pytest fixture?
a function that provides repeated tests

5. What is parametrisation in pytest?
running the same test function while changing the input values

6. What is regression testing?
rerunning tests after changing something

7. What does code coverage tell us, and what does it not prove?
what lines ran during the test

8. What makes an assertion weak?
it would still pass even if the behaviour was wrong

9. What is the appropriate role of GitHub Copilot as a test assistant?
it proposes ideas and suggestions like another reviewer

10. What is the Stage 7 engineering rule?
every test must provide a required behaviour

## O Stage Completion

Tested Stage 7 main SHA: 2370dadad310cc1cbba3489c197533bfe4b20ee6
Full-suite result: [81]
Unresolved defects and effect on baseline: Complete
Clean working tree and integration evidence: Not-complete
Stage 8 handover status: no stage 8 work completed
All tutorial/formative responses and traceability/Copilot decisions complete: Confirm
