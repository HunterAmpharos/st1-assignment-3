# Stage 6 activities and evidence

Complete this one group record. Link actual issues, diffs, tests and reviews; avoid copying entire histories. Blank fields are intentional. Duplicate rows as needed. Use synthetic data only. Every member records their own meaningful contribution. Do not invent results, reviews or Copilot use.

- Group/tutorial: Me (Hunter) and Tutorial Tuesday 5:30pm
- Members, GitHub usernames and cohorts: Just Me
- Repository URL: https://github.com/HunterAmpharos/st1-assignment-3
- Starting SHA: 44a33b08c45ec460f6ed4e1a8e625b0ee30657a5

## A Requirement to issue activities

### FR-02 Patient Search

- Title: Implement Patient Search by ID (FR-2)
- Context: Staff need to have the option to retrieve registered patients via ID. This is PatientService.find_patient
- Requirement: Given a registered patient ID, the service will return same patient object instead of a copy.

Leading and trailing spaces around the ID are ignored.

IDs are case-sensitive (for example, p1 would not be identified as P1)

An ID that is valid but not registered raises LookupError.

A blank or non-text ID raises ValueError, so “invalid” and “not found” can be told apart.

A failed lookup does not create or change any patient.
- Definition of Done: It is tested and turns out to be working succesfully. the pull requested is reviewed and merged into the main branch.
- Owner: Hunter Taylor
- Actual issue link: https://github.com/HunterAmpharos/st1-assignment-3/issues/1

### FR-06 Appointment Cancellation with FR-07 retained history

- Title: Implement Appointment Cancellation (FR-06/FR-07)
- Context: Staff need to cancel a scheduled appointment while keeping its history.
- Requirement: Staff should be able to cancel any scheduled appointments while still saving them in history. AppointmentService.cancel_appointment stub.
- Acceptance criteria: 
Cancelling a scheduled appointment sets its status to CANCELLED and returns the same appointment object.

The cancelled appointment stays in the store, with the same patient, practitioner and date/time.

Cancellation uses the domain’s own cancel() transition rather than setting the status directly.

An appointment ID that is not registered raises LookupError.

A blank or non-text ID raises ValueError.

Cancelling an appointment that can’t be cancelled (already cancelled or completed) raises ValueError and leaves its status and the stored appointments unchanged.
- Definition of Done: Tests for the success, the request is reviewed and then this request is pulled and merged with the main branch.
- Owner: Hunter Taylor
- Actual issue link: https://github.com/HunterAmpharos/st1-assignment-3/issues/2

## B Commit quality

| Original example | Strong or Weak | Reason |
|---|---|---|
| changes | weak | says nothing about what changed or why |
| final version | weak | doesn't give reviewer much to go off |
| Add patient search by ID | strong | short, specific and coherent change |
| fix stuff | weak | very vauge |
| Prevent cancellation of completed appointments | strong | stats the behaviour and what was added |

## C Over scoped PR review

A cancellation PR also renames unrelated patient fields, restructures unrelated code and adds a new dependency.

- Scope concerns: Scope was not written so this requires work
- Responsibility and architecture concerns: Renaming patient fields could touch the domain code. Cancellation should stay in service.
- Testing and review concerns: The reviewer can't match the diff to any acceptable criteria.
- Changes to remove or separate, with reasons: Remove dependency unless its justified

## D Challenge a weak Copilot review

GitHub Copilot says: "Looks good; tests pass."

- Missing evidence: It doesn’t say which requirement or criteria it checked, which tests ran, in what directory, or with what result. It cites no diff lines and doesn’t cover error paths or retained history.
- Question 1: Which requirement and acceptance criteria did you check, and how does each one map to the diff?
- Question 2: Which command ran the tests, in which directory, and what was the result? Which assertions check retained history?
- Question 3: What happens for an unknown ID, an invalid ID, and an appointment that is already cancelled or completed, and is the state changed afterwards?
- Question 4: Does cancellation use the domain’s cancel() transition, and does the service avoid bypassing domain rules or deleting anything?
- Question 5: Are there unrelated changes in the diff, and could a wrong implementation still pass these tests?

## E Team workflow agreement

| Practice | Team agreement |
|---|---|
| Branch naming | feature/shortname |
| Commit message convention | short and coherent |
| PR size | only one issue per PR |
| Another-member review requirement | nope, just me |
| Merge rule | all tests are passed first |
| Significant Copilot disclosure rule | will be disclosed every single time |

## F Issue and backlog index

Create at least two focused issues. Add a linked practitioner-lookup issue or an explicit supporting criterion with the tutor if needed to cover all three service targets.

| Issue link | Requirement | Owner | Acceptance criteria or precise link | Status |
|---|---|---|---|---|
| https://github.com/HunterAmpharos/st1-assignment-3/issues/1 | Staff need to have the option to retrieve registered patients via ID. This is PatientService.find_patient | AmpharosHunter | Given a registered patient ID, the service will return same patient object instead of a copy.

Leading and trailing spaces around the ID are ignored.

IDs are case-sensitive (for example, p1 would not be identified as P1)

An ID that is valid but not registered raises LookupError.

A blank or non-text ID raises ValueError, so “invalid” and “not found” can be told apart.

A failed lookup does not create or change any patient. | Closed, merged in PR 1 |
| https://github.com/HunterAmpharos/st1-assignment-3/issues/2 | Staff need to cancel a scheduled appointment while keeping its history. | AmpharosHunter | Cancelling a scheduled appointment sets its status to CANCELLED and returns the same appointment object.

The cancelled appointment stays in the store, with the same patient, practitioner and date/time.

Cancellation uses the domain’s own cancel() transition rather than setting the status directly.

An appointment ID that is not registered raises LookupError.

A blank or non-text ID raises ValueError.

Cancelling an appointment that can’t be cancelled (already cancelled or completed) raises ValueError and leaves its status and the stored appointments unchanged. | Closed, merged in PR 2 |

## G Pull request evidence

Ran out of time and could not complete

## H Copilot collaboration record

Record meaningful required use, not every trivial completion. Repeat per significant interaction.

- Member and task: AmpharosHunter. I implemented lookup and cancellation methods. I also wrote tests that corresponded to these methods.
- Prompt/purpose and relevant issue/diff:Prompt provided by instructions on Canvas with diff of services.py and test_services.py
- Summary of output: Added patient and practitioner lookup methods that return registered records and report missing records, plus appointment cancellation that changes a scheduled appointment to cancelled, rejects repeated cancellation, and retains the appointment for later lookup. Added tests for these behaviors and relevant ID validation.
- Human check against actual code, requirements and tests: I confirmed the implementation and tests cover patient lookup (FR-02), cancellation and repeated-cancellation rejection (FR-06), and the retrieval of cancelled appointments (FR-07).
- Decision: [Accept]
- Reason: Matched the acceptance criteria.
- Verification/evidence: py -m pytest in project/, success

## I Human versus Copilot review comparison

- Human reviewer noticed before consulting Copilot: No issues
- Copilot noticed: The tests cover the stated requirements: known and unknown patient lookup, cancellation and any repeated cancellation rejection. Copilot also suggested an optional test that could be added for cancelling an appointment that does not have the status: SCHEDULED.
- Overlap: None.
- What did the human reviewer notice that Copilot did not: I reported nothing.
- What did Copilot identify that the human reviewer initially missed: An additonal test that can verify if an appointment is in a non_SCHEDULED state. Not neccessary for the assingment.
- Unsupported or incorrect Copilot suggestion: Copilot was concerned about the has_practitioner_conflict(). I decided this was unsupported.
- Human judgement accepted, modified or rejected, and why: I rejected the suggestion. The optional test suggestion could be considered for future iterations of this project if it is required.
- Which evidence justified merge approval: py -m pytest run from project/ succeeded.

## J Contributions

Repeat per member. Include only categories that describe actual work; write not applicable where appropriate. Pairing or mentoring can be supported by a short corroborated note.

- Member: Hunter Taylor (AmpharosHunter)
- Implementation: ID lookup and appointment cancellation. check Github PRs.
- Testing: Created tests for previous functions. check commited Github work.
- Review: Content was reviewed while writing and further review was not performed due to lack of time.
- Issue refinement: No major issues were present during this stage.
- Design and responsibility discussion: It's just me.
- Debugging or integration: No debugging was preformed at this stage.
- Documentation or team support: All the documentation can be found throughout this document. Team is still me.

## K Exit question

Why is a high commit count not necessarily evidence of strong contribution?

Having a high commit count only shows how often someone has saved their work, not how helpful that work actually is. Some commits that may just be cosmetic or reformatting can count towards the commit count and inflate the number more than other members. A precice code review that actually implements the changes, catches bugs and is a worthwhile design decision contributes way more to a project. Contribution is also not only about commit count.

## L Stage 6 formative questions

1. What is version control?

Recording all the changes that are made to the code and why they were made. Allows people to compare versions and also work on seperate branches.

2. Why is a feature branch useful?

It keeps one focused feature away from the main branch so that it can be tested thoroughly before it makes its way into the main branch.

3. What makes a commit a good engineering commit?

It contains one good coherent change.

4. What is a pull request?

A request to merge one branch into another.

5. What is the purpose of code review?

Usually when working in a team you can catch issues that the author may have missed.

6. What does a Git diff show?

The exact lines that were added and changed.

7. What is a Definition of Done?

Once the agreed checklist has been completed and the work has been completed. Once the PR is mergered and the issue is closed that is when it is "Done".

8. What is the appropriate role of GitHub Copilot in pull-request review?

It works the same as a seperate reader who can anaylse your code and provide feedback.

9. Why should individual contribution not be judged only by commit count?

Commits measure activity not good work.

10. What is the Stage 6 engineering rule?

...

## M Completion and handover

- Starting SHA: 03ab87e3e58dafd687b52d75b0e05cd3054f32b9
- Final Stage 6 code SHA: 7643dbd8e55d44fcd06b4f7c1e2c2942a6e14307
- Test command: py -m pytest
- Working directory: project/
- Observed result: [32]
- PR and another-member reviewer: no other members
- Unresolved issue or none: none
- Stage 7 handover status: [ready for tutor checkpoint / unresolved work]
- Final submitted SHA if later than tested SHA: only the Stage 6 markdown record changed

- [x] Three Stage 6 service targets completed and checked.
- [x] Original supplied tests retained and passing.
- [x] At least two focused issues link requirements and acceptance criteria.
- [ ] Feature work reviewed by another member using the actual diff.
- [ ] Human-first review and required Copilot comparison recorded.
- [ ] Feedback resolved and approval recorded before merge.
- [x] Everyone pulled main and integrated checks passed.
- [x] Required activities, quiz responses and contribution notes completed.
- [x] Only synthetic data included; confidential peer material kept out.
- [x] Tutor can trace a requirement through issue, code, tests, PR and checkpoint.

Do not write a file's own future commit SHA into that file. Record the tested code SHA first, then commit the evidence; explain the difference when submitting.
