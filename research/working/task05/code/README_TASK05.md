# Task 05 reproducible artefacts

Supports `research/working/task05-statistical-robustness-review.md`. Nothing here is participant-facing.

## Environment

Python 3.13.16, numpy 2.5.3, scipy 1.18.1, 2 CPU cores. Run every command from this `code/` directory.

## Provenance

- `stimulus.py`, `ordinal_model.py`, `simulate_recovery.py`, `simulate_recovery_v2.py` and `burden.py` are byte-identical copies of the Task 04 archive (`research/working/task04/task04_stage2_artefacts.zip`). Their hashes are in `../logs/inherited_code_sha256.txt` and `../config.json`. They were not modified.
- Files written by this review: `simulate_recovery_v3.py`, `analyse_validationA.py`, `heterogeneity_methods.py`, `feasibility_B.py`, `individual_identifiability.py`, `catch_trials.py`, `lapse_catch.py`, `analyse_C1.py`, `process_observer.py`, `mechanisms_C2.py`, `m4_check.py` and `adversarial_checks.py`.
- Not part of this review: `run_validation_a.py`, `timing_test_b.py`, `simulate_lapses_c.py`, `evaluate_a.py`, `runner.py`, `attention_sim.py`, `aggregate_A.py`, `t04/` and `t04_SHA256SUMS`. These are left over from two earlier, unreviewed Task 05 attempts in the same folder. None of this review's results depend on them. See `../logs/DEVIATIONS.md`, which also records the `heterogeneity_methods.py` name collision.

## Commands (in execution order)

| Step | Command | Measured wall time |
|---|---|---|
| Validation A | `python3 simulate_recovery_v3.py run --run-dir ../results/validationA/J20_core_reps500 --reps 500 --allocations "J20 (k=2)" --workers 2 --batch-size 50 --no-lapse-refits --scenarios "S01 onset moderate" "S03 onset high" "S04 midpoint moderate" "S06 midpoint high" "S07 threshold-onset q=0.2" "S08 offset moderate" "S09 duration heuristic" "S11 biased onset"` then `aggregate --run-dir ...` | 259.8 s |
| A analysis | `python3 analyse_validationA.py ../results/validationA/J20_core_reps500 <Task04 stage2 fits.csv> ../results/validationA/validationA_analysis.json` | < 5 s |
| B feasibility | `python3 feasibility_B.py --reps 20 --reps-b1 10 --boot-datasets 2 --boot-n 100 --out ../results/validationB` | 45.0 s |
| B individual | `python3 individual_identifiability.py ../results/validationB/individual_identifiability.json` | 2.1 s |
| C1 | `python3 lapse_catch.py --reps 100 --workers 2 --out ../results/validationC/lapse_catch.jsonl` then `python3 analyse_C1.py ../results/validationC/lapse_catch.jsonl ../results/validationC/C1_analysis.json` | 378.4 s |
| C2 | `python3 mechanisms_C2.py --datasets 200 --b0-datasets 100 --target 0.60 --out ../results/validationC` (repeat with `--target 0.85`) | 81.8 s, 74.2 s |
| M4 | `python3 m4_check.py ../results/validationC` | 27.5 s |
| Adversarial | `python3 adversarial_checks.py ../results/adversarial_checks.json` | 23.6 s |

## Reproducibility guarantees

- Validation A uses the Task 04 seed namespace unchanged. Reps 0–99 reproduce all 800 Stage 2 fits exactly, and all 4,000 fits match an independent earlier execution exactly.
- The other runs use their own SHA-256 seed namespaces (listed in `config.json`). The Validation A and C1 runners checkpoint as they go, and rerunning skips work already completed.
- Deviations from pre-specification are listed with timestamps in `../logs/DEVIATIONS.md`.

## What these artefacts do not show

- Anything about human observers. Every observer is simulated, and the process observer's parameters are assumptions.
- Anything about physical displays.
- Coverage of the heterogeneity methods B1–B4. The feasibility test is too small to estimate it, by design.
