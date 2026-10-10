# Task 06 Change Log: r3 to r3.1 (final)

| Field | Value |
|---|---|
| Trigger | Final reviewer decision, 2026-10-10: OD-21 and OD-22 approved |
| r3 | Preserved unchanged in `task06_review_package_r3.zip` (working copy `task06_r3_archive/`) |
| Scope | These two decisions and the cross-document corrections they need. Nothing else |

## OD-21: suppress classification and Q2c for a primary analysis with n ≠ 12

| File | Precise change |
|---|---|
| `code/task06_analysis.py` | In `analyse_condition`, when n ≠ 12: `outside_validated_envelope: true` and an `envelope_note`. The classification object is built with its rules not applied, the label withheld and the reason given (OD-21). Q2c gets `issued: false`. Q1c gets the suffix "(numeric only; outside the validated envelope)". At n = 12, `outside_validated_envelope: false`, with behaviour unchanged. Numeric results unchanged. `INTERPRETATION_STATUS` gains `primary_analysis_n_not_12`. Docstring updated. `WRAPPER_VERSION` → `task06-wrapper-r3.1` |
| `code/tests/test_task06_analysis.py` | New `TestEnvelopeR31` (5 tests): n = 12 with the gate passing; n = 11 and n = 13 with the gate passing (suppression, flag, numerics equal to frozen `run_b3`, t(n − 1) intervals); n = 13 with the gate failing; n = 12 numeric equality. New helper `_direct` |
| D2 | Header (r3.1). §5.2: a label requires a passing gate **and** n = 12. §6: Q2c is not issued for a primary analysis with n ≠ 12. §9.7: output fields. §10.3: the open question replaced by the approved rule |
| D4 | Header (r3.1). §0: the OD-21/OD-22 dependency row removed. Item 4: Q2c needs n = 12. Item 19: classification withheld at n ≠ 12. Item 21: suppression rule stated |
| D5 | Header (r3.1). OD-17 note. OD-19 note. OD-21 recorded as APPROVED |
| D6 | Header (r3.1). C25 revised |

## OD-22: remove the incomplete-trial OLS sensitivity analysis

| File | Precise change |
|---|---|
| `code/task06_analysis.py` | `not_implemented` output key removed. Docstring notes the removal. No OLS code existed or was added |
| `code/tests/test_task06_analysis.py` | `test_ols_analysis_marked_not_implemented` replaced by `test_ols_analysis_removed_from_outputs`, which asserts no `not_implemented` key and no "OLS" anywhere in the output |
| D2 | §8.2 bullet removed. §9.7 `not_implemented` line removed. §10.2 rewritten as "Incomplete participants: no analysis (OD-22)" |
| D4 | Item 23: no analysis of incomplete participants. Item 24: OLS bullet removed |
| D5 | OD-04 wording. OD-19 residual-risk note. OD-22 recorded as APPROVED. §3 item 4 |
| D6 | C19 revised |
| D1 | §11, item 5: OLS line removed |

## Other cross-document corrections

| File | Change |
|---|---|
| D1 | Revision row. §11: wrapper r3.1, 41 tests |
| D6 | C23: 41 tests; r3 to r3.1 comparison added |
| `code/README.md` | r3.1; OD-21 behaviour; OLS removal; 41 tests |
| `supporting/consistency_audit.py` | OPEN now allowed for OD-14 only. The D5 decision-row pattern accepts the new row format |
| `supporting/verify_primary_unchanged_r3_r3.1.json` (new) | Output of the existing comparison script, run with the r3 wrapper against r3.1 |
| `task06-00-readiness-assessment.md` | Rewritten as the r3.1 verification report |

## Not changed

- D3.
- The S6 thresholds and rule order.
- The add-back rules.
- The primary B3-t procedure, seeds and draws.
- Every approved boundary.
- The six claim limits.
- OD-14, which remains open.
- The Task 05 frozen code.
