# Task 06 Change Log: r1 to r2

| Field | Value |
|---|---|
| Trigger | Reviewer decision, 2026-10-10: protocol revision authorised |
| r1 | Preserved unchanged in `task06_review_package_r1.zip` (and the working copy `task06_r1_archive/`) |
| r2 | This package |

The changes do **not** touch the stimulus geometry, trial counts, catch trials, the B3-t steps, the Hotelling gate, circular containment, the six claim limits, or any Task 02–05 or canonical file.

## Reviewer decision applied

| Item | Applied as |
|---|---|
| OD-01 to OD-20 | Adopted as recommended. OD-14 remains open |
| OD-03 | Set to descriptive-only comparisons by the reviewer. This replaces the r1 recommendation (b), inferential contrasts after V-C |
| V-C, V-N | Not performed |
| Wrapper and tests | Authorised. Written |

## Changes by document

| Doc | Section | Change | Reason |
|---|---|---|---|
| D1 | Header | Revision row added; legend changed so that OD-xx means "decision in D5" | r2 |
| D1 | §1 | Study type stated: estimation and feasibility pilot; preregistered within-condition analyses are not confirmatory effectiveness claims; Level 2 row notes comparisons are descriptive only | Reviewer: distinguish preregistered analyses from effectiveness claims |
| D1 | §2 | Sample decided: 12 completed per condition. Setting: laboratory, E2-passing stations only | OD-06, OD-07 |
| D1 | §3.2 | M fixed before participant data collection. An E2-forced change is frozen before the first participant. Task 03 tuning allowance withdrawn | Reviewer: fix M; OD-10 |
| D1 | §5 | Device-check note changed to station ID. Confidence rating removed from step 8 | OD-07, OD-16 |
| D1 | §6.1, §6.3 | Marked decided. The 100 ms rule is **provisional**, confirmed from E2 M1 and frozen before preregistration | Reviewer: 100 ms provisional; OD-09 |
| D1 | §8 | Confidence field removed. OD-01 decided | OD-16, OD-01 |
| D1 | §9.1 | F3 revised to task time in A ≤ 28 min, **provisional** | Reviewer: 28 min provisional; OD-08 |
| D1 | §10.1 | X4 and X6 decided. X6 now also covers fewer than 4 valid catch trials, matching the wrapper | OD-04, OD-09; consistency with code |
| D1 | §10.3 (new) | Selection effects of exclusion and replacement, pointing to D2 §10.4. Stopping renumbered to §10.4 | Reviewer: selection bias |
| D1 | §11 | E2 on every station, with re-validation after change. Ethics pathway OPEN (OD-14). Wrapper and tests exist. M frozen. Provisional thresholds confirmed and frozen. Items renumbered | Reviewer: E2 on actual hardware; fix M; ethics unresolved |
| D1 | §13 | F3 row revised and marked provisional | OD-08 |
| D2 | Whole | **Rewritten as r2.** Pilot status and the "not effectiveness claims" statement in the header. Descriptive-only comparisons (§7). Q1c/Q2c, renamed from H1c/H2c (§6). S6 operationalised as an ordered rule set (§5.2). All numbers reported whatever the gate (§5.1). Selection-bias register (§10.4). Sample size decided, no V-N (§11). Wrapper and tests referenced (§9.5). Provisional thresholds named (§12). Confidence-related analyses removed. Holm alternative removed. Contrast inference and V-C removed | Reviewer decisions; OD-02, OD-03, OD-06, OD-11, OD-16, OD-17 |
| D3 | Header | Revision row | r2 |
| D3 | §2 | E2 on every actual laboratory station (K1-x), identified by serial number. Re-validation after any change. K2–K4 optional, not authorising | Reviewer: E2 on actual hardware |
| D3 | M1-b | 100 ms rule provisional; confirmed or revised from each station's M1 distribution | Reviewer: 100 ms provisional |
| D3 | M4 | Heading per station. Viewers: minimum 3, target 5, with a scaled failure margin | OD-18 |
| D3 | §6 | Decision rows per station. New row: freeze M, rendering and the 100 ms rule after E2. Online-testing paragraph replaced by a scope-of-validity statement | Reviewer: fix M; OD-07 |
| D4 | Whole | **Rewritten as r2.** Dependencies table updated (ethics OPEN; E2 per station; M; provisional thresholds; wrapper). Pilot title and description. Q1c/Q2c. Descriptive comparisons. Confidence removed. Ethics section states the pathway is unresolved | Reviewer decisions |
| D5 | Whole | **Rewritten as a decision record.** Decision, implementation location and residual risk for each OD. OD-14 open. Pre-preregistration task list | Reviewer decisions |
| D6 | Rows | A7, B23, B24, C21, C22, C23, E6 and F6 added. B22, C9, C11, D6 and D8 revised. C10 reference corrected | Traceability of r2 changes |
| 00 | Whole | **Rewritten as r2.** Requirement-to-implementation table. Updated departures (P11, P12). Code summary. Audit results. Remaining blockers. Verdict | r2 |
| code | New | `task06_analysis.py`, `tests/test_task06_analysis.py` (23 deterministic tests), `TEST_RUN.log`, `README.md` | OD-19, authorised |
| supporting | New | `consistency_audit.py` | Audit |

## Not changed

- Stimulus specification, trial counts, catch trials and TPDF dither.
- B3-t steps 1–8, the 2,000 draws and the seed rules.
- Claim limits.
- Interpretation bands (only operationalised).
- E2 measurements M1–M5 and their thresholds, other than the station scope and the provisional marking of the 100 ms figure.
- `supporting/model_response_probabilities.*` (r1).
