# Task 06: Readiness Assessment and Verification Report (revision 3.1, final)

| Field | Value |
|---|---|
| Status | Final Task 06 package for commit authorisation. **Not committed** |
| Not done | No preregistration. No E2. No build. No Task 07. No participant contact. No stochastic simulation |
| Revision | r3.1, 2026-10-10. Final reviewer decisions OD-21 and OD-22 only, plus the cross-document corrections they need |
| Archives | r1, r2 and r3 packages preserved unchanged (`task06_review_package_r1.zip`, `_r2.zip`, `_r3.zip`) |
| Change logs | `task06-CHANGELOG-r3-to-r3.1.md` (this revision); `task06-CHANGELOG-r2-to-r3.md`; `task06-CHANGELOG.md` (r1 to r2) |
| Destination | `research/working/task06/` (OD-20) |

---

## 1. Verification report

### Changes made

**OD-21 (approved).** The S6 descriptive classification and Q2c are suppressed whenever the **primary** analysis has n ≠ 12.

- The numeric B3-t results are kept in full.
- The output flags `outside_validated_envelope: true`, with a note saying the analysis is outside the validated operating-characteristic envelope.
- Q1c reports the gate result marked "numeric only; outside the validated envelope".
- At n = 12, behaviour is unchanged.

**OD-22 (approved).** The incomplete-trial OLS sensitivity analysis is removed:

- from the pilot plan (D2 §8.2 and §10.2; D4 items 23 and 24)
- from the wrapper output (the `not_implemented` key is gone)

It was not implemented. X6 exclusions appear in the exclusion counts only.

### Verification

| Check | Result |
|---|---|
| Deterministic tests run | **41** |
| Passed / failed | **41 / 0** (`code/TEST_RUN.log`; Python 3.13.16, numpy 2.5.3, scipy 1.18.1) |
| New tests (OD-21) | 5, in `TestEnvelopeR31`: n = 12 with the gate passing (label and Q2c present); n = 11 and n = 13 with the gate passing (label and Q2c suppressed, flag set, numerics identical to a direct frozen `run_b3` call, t(n − 1) weight intervals); n = 13 with the gate failing (suppressed); n = 12 numeric equality with frozen code |
| Changed test (OD-22) | The "OLS marked not implemented" test was replaced by one asserting that no OLS output exists |
| Code files changed | `code/task06_analysis.py`, `code/tests/test_task06_analysis.py`, `code/README.md` (and `code/TEST_RUN.log`, regenerated) |
| Primary numeric outputs unchanged? | **Yes.** On four deterministic fixtures, r3 and r3.1 are identical on every primary numeric key: slopes, coefficients, SEs, weight intervals, gate, angle, both angle intervals, containment, Level 1 and seeds. Departure flags arise in the same cases with identical wording (`supporting/verify_primary_unchanged_r3_r3.1.json`). Against r2, the numeric outputs are also identical; only the r3 wording of the departure text differs, as already recorded |
| Frozen Task 05 code hashes unchanged? | **Yes:** `e1_methods.py` `db99b8ba…`, `heterogeneity_methods.py` `3cfe209a…`, `ordinal_model.py` `590db5f3…`, `stimulus.py` `238d882a…`. The repository working tree is clean |
| Cross-document references consistent? | **Yes** (`supporting/consistency_audit.py`): no broken section references; all 22 decisions defined; OPEN only for OD-14; no stale terms; no em dashes |
| Package manifest verified? | **Yes.** The SHA-256 manifest of the r3.1 package was verified against its own contents, from the assembled folder and after re-extraction from the zip |
| D3 | Unchanged, byte-identical to r3 |

**What the tests show.** Passing tests show that the implementation is consistent with its specification. They do **not** validate psychological mechanisms, statistical operating characteristics or the classification thresholds.

**A note on the verification script.** `verify_primary_unchanged_r2_r3.py` was reused unchanged to compare r3 with r3.1. Its output field names (`r2_…`, `r3_…`) mean "earlier wrapper" and "later wrapper".

### What remains unresolved

| Item | Status |
|---|---|
| **OD-14:** ethics pathway | **OPEN.** Blocks preregistration, E2 viewer sessions and all data collection |
| E2 on every laboratory station; freezing M, the 100 ms rule and the 28 min threshold | Not started. Outside Task 06 |
| Allocation sequence and participant-seed list; container digest; freezing the wrapper hash | Not started |

### New deviations

None. No stochastic simulation was run. No approved boundary changed. No Task 02–05 file or canonical file changed.

---

## 2. Preserved boundaries (confirmed unchanged)

- **Study design:**
  - estimation and feasibility pilot
  - 12 completed participants per condition
  - 20 balanced main trials and 4 catch trials
  - stimulus geometry and the policy on M
- **Coding:** R = −1, S = 0, L = +1.
- **Primary method:**
  - the frozen B3-t estimator
  - the Hotelling gate
  - circular containment
  - fixed seeds and 2,000 draws
- **Labels:** S6 labels are exploratory descriptive classifications, not validated mechanism identifications.
- **Add-back analysis:** numerical sensitivity only.
- **Claims and comparisons:**
  - descriptive-only comparisons between conditions
  - no effectiveness claims
  - no mechanism attribution
  - no inference from the group angle to individuals
- **E2:** required on every laboratory station.
- **Still open:** OD-14.
- **Claim limits:** the six binding claim limits.

---

## 3. Departures from Task 05's validated design (r3.1 status)

| # | Departure | Status |
|---|---|---|
| P3 | OLS analysis for incomplete participants | **Removed** (OD-22) |
| P6 | Primary analysis with n ≠ 12 | t(n − 1) weight intervals flagged; **outside the validated envelope; no classification and no Q2c** (OD-21) |
| P11 | S6 bands operationalised | Exploratory descriptive classifications only (r3) |
| P12 | Add-back analysis | Numerical sensitivity only (r3) |
| P1, P2, P4, P5, P7–P10 | As in r2 | Unchanged |

---

## 4. Verdict: READY FOR COMMIT REVIEW

Both final decisions are implemented, tested and consistent across D1–D6, the code and this report. Task 06 is complete as a protocol-development task.

**This verdict does not authorise a commit.** A complete protocol is not a validated instrument: E2 has not been run, there is no build, and there are no human data.

### Proposed commit content

The `task06/` folder of `task06_review_package_r3.1.zip`, placed at `research/working/task06/`.

---

## 5. Log

| ID | Date | Entry |
|---|---|---|
| T06-L1 to L16 | 2026-10-10 | r1 to r3 entries (see r3) |
| T06-L17 | 2026-10-10 | Final reviewer decision received: OD-21 and OD-22 approved. r3 working copy archived from `task06_review_package_r3.zip` (`task06_r3_archive/`), manifest verified |
| T06-L18 | 2026-10-10 | Wrapper and tests revised. 41 of 41 pass. r3 and r3.1 primary numeric outputs are identical. Frozen hashes unchanged. Repository tree clean |
| T06-L19 | 2026-10-10 | D1, D2, D4, D5 and D6, the code README and the audit script updated. D3 unchanged. Audit passes |
| T06-L20 | 2026-10-10 | No commit, no preregistration, no E2, no build, no Task 07, no participant contact, no stochastic simulation |
