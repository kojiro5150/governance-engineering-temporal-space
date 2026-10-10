# Task 06 D5: Decision Register (revision 3.1)

| Field | Value |
|---|---|
| Status | Working draft for review |
| Revision | r3, 2026-10-10. r2 recorded the reviewer decision of 2026-10-10: **OD-01 to OD-20 adopted as recommended, except that OD-03 is set to descriptive-only comparisons (no V-C); OD-14 remains open**. r3 applies reviewer corrections A and B (OD-11, OD-17 and OD-19 updated) and adds two open items, OD-21 and OD-22 **r3.1 (2026-10-10, final reviewer decision): OD-21 and OD-22 approved as recommended.** Only OD-14 remains open |
| Change history | r1 options and rationale are kept in `task06_review_package_r1.zip` and summarised in `task06-CHANGELOG.md` |

## 1. Decisions

| ID | Decision | Decided (reviewer, 2026-10-10) | Where implemented | Residual risk |
|---|---|---|---|---|
| OD-01 | Response coding | Keep the frozen coding: R = −1, S = 0, L = +1. Labels are "Left began first / Same time / Right began first" | D1 §7 and §8.3; D2 §2; wrapper (unit-tested) | None identified |
| OD-02 | Study status and multiplicity | **Estimation and feasibility pilot.** Within-condition analyses are preregistered as Q1c and Q2c. They are **not confirmatory effectiveness claims**. No family claim, so no family-wise correction | D1 §1; D2 header and §6; D4 items 3, 4 and 21 | Three uncorrected per-condition outcomes. Acceptable only because no family or ranking claim is made |
| OD-03 | Between-condition comparisons | **Descriptive only.** A side-by-side table, plus point differences when both gates pass. No intervals and no tests. **V-C not performed.** This replaces the r1 recommendation (b) | D2 §7; D4 item 19; wrapper `describe_conditions` | The comparative question gets only a descriptive answer. Differences are subject to gate and exclusion selection (D2 §10.4) |
| OD-04 | Missing and invalid order trials | Re-queue once; complete cases with replacement. **r3.1:** no analysis of incomplete participants (OLS analysis removed, OD-22) | D1 §6.3 and §10; D2 §10; wrapper X6 | Selection through replacement (D2 §10.4) |
| OD-05 | Seeds, draws, environment | Fixed seed rule; 2,000 draws; pinned Python 3.13.16, numpy 2.5.3, scipy 1.18.1; container | D2 §9; wrapper | A container digest is still to be produced |
| OD-06 | Sample size | **12 completed participants per condition. V-N not performed** | D1 §2; D2 §11; D4 items 13 and 14 | Condition A may yield no strategy statement. Accepted as a pilot outcome |
| OD-07 | Setting | Supervised laboratory, only on stations that individually pass E2 | D1 §2 and §11; D3 §2 | Limits the recruitment pool. Results generalise to validated stations only |
| OD-08 | Burden threshold F3 | Median task time in A (calibration to final question) ≤ 28 min. **Provisional**: confirmed in staff dry runs, frozen before preregistration | D1 §9.1 and §13 | The figure comes from a model, not data |
| OD-09 | Frame-timing rules | X4 = F4 (at least 95% of frames within 1.5× nominal). Per-trial validity rule: any interval over 100 ms. **Provisional**: confirmed from E2 M1 on the laboratory stations | D1 §6.3 and §10.1; D3 M1-b | The value is a judgement until E2 |
| OD-10 | Change magnitude M | **Fixed before participant data collection.** 10 L* unless E2 forces a change, which is then frozen before the first participant. No tuning on participant data | D1 §3.2 and §11; D3 §6 | Possible floor or ceiling effects, detected by F5 and F6 after the fact |
| OD-11 | S6 rules, including the 60° rule | Retained for traceability as an ordered rule set. **r3 (correction A): every label is an EXPLORATORY DESCRIPTIVE CLASSIFICATION, not a validated mechanism identification.** It is reported only with the numeric estimate, interval and gate result, and never when the gate fails. Thresholds unchanged and not validated | D2 §5.2; wrapper `classify_s6` and `descriptive_classification` (unit-tested) | Asymmetric rules across labels (documented, not corrected). Fewer statements near a = 0.2 |
| OD-12 | S5 attention tolerances | Retained as a labelling screen | D2 §8.3 | Weak, with SE about 0.04 |
| OD-13 | Allocation, replacement, cap | Permuted blocks of 6; replacement by continuing the sequence; arms close at 12; cap 24 starters | D1 §6.1 and §10.4 | Calendar-time imbalance, which is reported |
| **OD-14** | **Ethics pathway, recruitment source, privacy law, reimbursement, E2 viewers** | **OPEN.** Unresolved until an eligible institution and review process are identified | D1 §11; D3 M4; D4 §0 and §8 | **Blocks preregistration, E2 M4 viewer sessions and all data collection** |
| OD-15 | Registry and timing | OSF Registries, after E2 passes and ethics approval is granted | D4 header and §0 | None |
| OD-16 | Confidence rating | Removed | D1 §5 and §8; D4 item 17 | Loses a secondary measure |
| OD-17 | Hypothesis set | Task 03 H1–H5 retired. Q1c and Q2c adopted, renamed from H1c and H2c to make their non-confirmatory status explicit. **r3:** Q2c is a descriptive question derived from the exploratory classification. It is not issued when the gate fails or for add-back analyses. **r3.1:** nor for a primary analysis with n ≠ 12 (OD-21) | D2 §6; D4 item 4 | Narrow question |
| OD-18 | E2 thresholds | D3 thresholds approved as proposals. M4 target of 5 viewers, minimum 3 | D3 | Thresholds not derived from perceptual data |
| OD-19 | Analysis code | Thin wrapper and deterministic unit tests **written** (r2). **r3:** exploratory classification objects; distinct add-back analysis IDs; classification and Q2c suppressed for add-back; 36 tests. **r3.1:** classification and Q2c also suppressed for a primary analysis with n ≠ 12 (OD-21); OLS output removed (OD-22); 41 tests. No stochastic simulation | `code/` | Not yet frozen |
| OD-20 | Placement and commit | `research/working/task06/`. Commit only after independent review | Not applicable | None |
| OD-21 (raised r3; decided r3.1) | Classification for a primary analysis with n ≠ 12 | **APPROVED (2026-10-10): suppress S6 classification and Q2c whenever the primary analysis has n ≠ 12.** Numeric B3-t results are kept; the output flags `outside_validated_envelope: true` with an explanatory note. Unit-tested at n = 11, 12 and 13, including gate-pass cases | D2 §10.3; D4 items 4, 19 and 21; wrapper `analyse_condition` | Arms that close below 12 at the cap yield numbers only, with no descriptive label |
| OD-22 (raised r3; decided r3.1) | Incomplete-trial OLS sensitivity analysis | **APPROVED (2026-10-10): removed from the initial pilot plan and from the wrapper outputs. Not implemented.** X6 exclusions appear in exclusion counts only | D2 §10.2; D4 item 23; wrapper (no output key; unit-tested) | Participants with incomplete data contribute nothing to estimates. Reinstatement would need a new specification and authorisation |

## 2. Decisions already made by the record (not reopened)

| Item | Decision | Source |
|---|---|---|
| Primary method | B3-t, provisional; exact procedure at n = 12, J = 20 | Closure record; A1 |
| Primary estimand | φ_β, response scale; gate mandatory; circular containment | Closure record §2 and §3 |
| Claim limits | Six, binding | Closure record §6 |
| Stimulus geometry, trial counts, catch trials, TPDF dither | Unchanged | Task 03; Task 04; Task 05 S4 and S10 |
| E1 verdict | REVISE, preserved | Task 05 E1 |

## 3. Items still to be done before preregistration

These are not decisions, but they must be completed first.

1. Identify the ethics pathway (OD-14).
2. Run E2 on every laboratory station.
3. Freeze M, the 100 ms rule and the 28 min threshold.
4. Freeze the wrapper hash (OD-21 and OD-22 are decided and implemented in r3.1).
5. Generate and hash-commit the allocation sequence and participant-seed list.
6. Build the container and record its digest.
