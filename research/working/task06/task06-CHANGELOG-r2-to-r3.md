# Task 06 Change Log: r2 to r3

| Field | Value |
|---|---|
| Trigger | Task 06 revision 3 instruction (independent review): targeted corrections A and B |
| r2 | Preserved unchanged in `task06_review_package_r2.zip` (working copy `task06_r2_archive/`) |
| r1 | Preserved unchanged in `task06_review_package_r1.zip` |
| r1 to r2 log | `task06-CHANGELOG.md` (kept unchanged) |

## Correction A: S6 labels are exploratory descriptive classifications

| File | Section | Precise change |
|---|---|---|
| `code/task06_analysis.py` | Interpretation | Added `CLASSIFICATION_STATUS`, `CLASSIFICATION_QUALIFICATION`, `S6_LABELS` and `INTERPRETATION_STATUS`. Added `descriptive_classification()`, which wraps the unchanged `classify_s6()` rules in an object carrying status, `validated: false`, `mechanism_identified: false`, `confirmatory: false`, a qualification and the numeric context (coefficients, intervals, angle and interval, gate). The label is withheld when the gate fails. Added `q2_object()`: Q2c is issued only when a label exists and carries a "not confirmatory evidence" status. Removed the top-level `S6_class` field. `describe_conditions()` now shows labels only inside their exploratory object. Top-level `interpretation_status` added |
| `code/tests/test_task06_analysis.py` | New `TestClassificationR3` (9 tests); 1 updated test | Gate failure (no label; numbers kept); boundary containment (exact band edges, 60° width, 45° endpoint); offset-dominant, including the documented asymmetry; ambiguous intervals; exploratory status fields; numbers alongside labels; a JSON walk proving labels never appear outside exploratory objects; Q2c qualification; OLS marked not implemented. The singular-gate test was updated to the new structure |
| D2 | Header | New three-tier table: validated procedure, descriptive classification rules, mechanisms not identified |
| D2 | §5.1 | No angle-based classification when the gate fails |
| D2 | §5.2 | Retitled. Exploratory status statement. Reporting requirements. The known asymmetry documented. Thresholds unchanged |
| D2 | §6 (Q2c) | Q2c is a descriptive question derived from the exploratory classification. Not issued when the gate fails or for add-back analyses |
| D2 | §7 | The side-by-side table lists the exploratory classification with its status |
| D2 | §9.5, §9.7 | Wrapper r3 with 36 tests; tests show implementation consistency only. The output structure is described |
| D2 | §14 | Limitation added: classification rules exploratory, unvalidated and asymmetric |
| D4 | Items 4, 19, 21; §6(f) | Q2c and S6 described as exploratory descriptive. Classification prohibited when the gate fails. Classification rules kept for traceability, not validated |
| D1 | §1 | Level 2 row: numeric outputs validated; strategy labels exploratory |
| D5 | OD-11, OD-17, OD-19 | Updated to record correction A |
| D6 | C21, C23 | Updated |

## Correction B: exploratory add-back analysis

| File | Section | Precise change |
|---|---|---|
| `code/task06_analysis.py` | Analysis | Refactored the numeric part into `_numeric_b3()`. The frozen `run_b3` call is unchanged, and so are the primary seed and inputs. `analyse_condition()` now carries `analysis_id` `PRIMARY-B3T-<c>`, `analysis_role: primary` and `within_validated_design`. New `analyse_addback()`: `analysis_id` `EXPLORATORY-ADDBACK-X2X3-<c>`, `exploratory: true`, `sample_size_departure`, `inclusion_criteria_differ_from_primary: true`, `within_validated_design: false`, and `numeric_status` stating unvalidated status and that no adjusted t multiplier establishes coverage. It reports numbers and `difference_from_primary`. The classification object is present with its label suppressed; Q2c is not issued; there are no Level 1 proportions. New seed `task06-addback-B3t-v1|<c>`. Output key renamed `exploratory_selection_sensitivity` → `exploratory_addback_analyses`. The n ≠ 12 departure text now says the adjusted multiplier does not establish validated coverage. `WRAPPER_VERSION` → `task06-wrapper-r3` |
| `code/tests/test_task06_analysis.py` | New `TestAddBackR3` (5 tests) | Distinct IDs, flags and suppression at n = 13; add-back at n = 12 still exploratory and suppressed; differences from primary; primary unaffected by add-back (equal to a direct `run_b3` call); nothing to add back. This replaces the single r2 selection-sensitivity test |
| D2 | §8.2, §9.1, §10.3, §10.4, §10.5 (new) | Add-back rules table. Separate seed. n ≠ 12 wording. OD-21 raised. §10.4 row now points to the add-back analysis in §10.5 |
| D4 | Item 24 | Add-back described as numerical sensitivity only |
| D5 | OD-21 (new, open) | Classification for a primary analysis with n ≠ 12. Not changed silently. Recommendation: suppress |
| D6 | C24, C25 | Added |

## Deferred work (instruction §7)

| Item | r3 status |
|---|---|
| Incomplete-trial OLS sensitivity analysis | **NOT IMPLEMENTED: NOT AVAILABLE FOR ANALYSIS.** Stated in D2 §8.2 and §10.2, D4 item 23 and the wrapper output (`not_implemented`); unit-tested. **Recommendation: remove it from the initial pilot plan** (D5 OD-22, open). Not implemented without authorisation |

## Other edits for consistency

| File | Change |
|---|---|
| D1 header and §11 | Revision row; 36 tests; OLS not implemented |
| D4 header and §0 | Revision row; dependency rows for OD-21 and OD-22 |
| `code/README.md` | Rewritten for r3 |
| `task06-00-readiness-assessment.md` | Rewritten for r3 |
| `supporting/consistency_audit.py` | Recognises OD-21 and OD-22; OPEN allowed for OD-14, OD-21 and OD-22 |
| `supporting/verify_primary_unchanged_r2_r3.py` (new) | Deterministic comparison of r2 and r3 primary outputs on four fixtures |

## Not changed

- **D3.** No cross-reference needed correcting.
- **Approved boundaries:**
  - pilot status
  - 12 completed participants per condition
  - 20 balanced trials and 4 catch trials
  - stimulus geometry and the policy on M
  - R = −1 / S = 0 / L = +1 coding
- **Primary method:**
  - the frozen B3-t estimator
  - the Hotelling gate
  - circular containment
  - seeds and 2,000 draws
- **Claims and comparisons:**
  - descriptive-only comparisons
  - no effectiveness claims
  - no mechanism attribution
  - E2 on every laboratory station
- **Still open:** OD-14.
- **Claim limits:** all six binding claim limits.
- **Frozen code:** the S6 thresholds and rule order; the Task 05 frozen code (hashes re-verified).
