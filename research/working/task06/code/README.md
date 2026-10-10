# Task 06 analysis wrapper (revision 3.1)

- `task06_analysis.py`: thin wrapper around the frozen Task 05 B3-t procedure (`e1_methods.run_b3`, unchanged).
  - Verifies the frozen module hashes.
  - Applies exclusions X1-X7 without reading main-trial responses.
  - Runs B3-t per condition with the pre-registered seeds (`analysis_id` `PRIMARY-B3T-<c>`).
  - Reports the numeric results as the primary output.
  - Reports S6 strategy labels only inside an `exploratory_descriptive_classification` object marked "EXPLORATORY DESCRIPTIVE CLASSIFICATION: NOT A VALIDATED MECHANISM IDENTIFICATION", with the numeric context; no label when the gate fails.
  - Q1c and the Q2c object (descriptive; not issued when the gate fails).
  - Primary analysis with n != 12 (OD-21, r3.1): numeric results reported and flagged `outside_validated_envelope`; S6 classification and Q2c suppressed.
  - Level 1 proportions and descriptive between-condition comparisons.
  - Exploratory add-back analysis of X2/X3 exclusions (`analysis_id` `EXPLORATORY-ADDBACK-X2X3-<c>`): numbers marked unvalidated and differences from the primary; never classified, never a Q2c conclusion, exploratory even at n = 12.
- `tests/test_task06_analysis.py`: 41 deterministic unit tests on hand-constructed fixtures. No stochastic simulation. The tests establish implementation consistency only, not statistical operating characteristics or the validity of the classification rules.
- `TEST_RUN.log`: result of the r3.1 test run (Python 3.13.16, numpy 2.5.3, scipy 1.18.1).

Run the tests from this directory:

    TASK05_CODE=<path to research/working/task05/code> python3 -m unittest -v tests/test_task06_analysis.py

The incomplete-trial OLS sensitivity analysis was removed from the plan (OD-22, r3.1) and is not part of the wrapper.

Not run on participant data. Status: for Task 06 review; to be frozen (hash recorded in the preregistration) only after approval.
