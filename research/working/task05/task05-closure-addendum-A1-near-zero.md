# Task 05 closure record: Addendum A1, B3-t near-zero sensitivity validation

- **Status:** DRAFT FOR REVIEWER APPROVAL. Not canonical. Not committed.
- **Date:** 2026-10-10.
- **What it adds to:** `task05-closure-decision-record.md`, which is unchanged (SHA-256 recorded in the A1 frozen spec and re-verified after the run).
- **What it changes:** nothing in any earlier frozen verdict.
  - The E1 verdict remains REVISE.
  - The E1-H2 results stand as reported.
- **Authority:** reviewer closure decision, item 4, which authorised one targeted validation of about 1,000 datasets.
- **Evidence labels:** [SIM] simulation, [DED] deduction, [JDG] judgement. No participant data.

---

## A1.1 Outcome

**B3-t: CONFIRMED** under the frozen A1 rule.

- All 22 criteria are met at the point estimate.
- None is clearly outside its Monte Carlo interval.
- 10 are Monte Carlo-indeterminate (Section A1.4).

The provisional acceptance of B3-t is unchanged in kind. A1 removes closure limitation 8.2: B3-t near-zero behaviour is now measured. It does not upgrade the acceptance from provisional.

---

## A1.2 Frozen design

| Item | Value |
|---|---|
| Spec | `results/NZ/NZ_FROZEN_SPEC.json`, SHA-256 `a2abb1caa66ab9e1f2b395b2e172cd6ec02d28f93965167f3dd77bb3adf32ef0`, read-only, frozen before execution |
| Generator | 12 identical participants, onset weight a, offset weight 0, lapse 0.02, 20 order trials (frozen E1 `sweep_scenario`) |
| Grid | a ∈ {0, 0.05, 0.10, 0.20, 1/3}, the P4 grid; 200 datasets each, 1,000 in total |
| Seeds | Namespace `task05-NZ-v1`; SHA-256 of `ns|a=<a>|rep` |
| Procedure | `e1_methods.run_b3`, unchanged and hash-verified; B3-t evaluated, B3-boot recorded descriptively |
| Targets | β*_on by Monte Carlo (0.0188, 0.0375, 0.0743, 0.1212 for a > 0). β*_off = 0, the target angle is 0°, and β* = (0, 0) at a = 0, all by symmetry of the zero-mean orthogonal design [DED] |
| Scope | Not extended |

**Criteria** (band [0.90, 0.98]; Wilson classification as in E1):

| Criterion | Requirement |
|---|---|
| N1 | Weight-CI coverage of β*, w_on and w_off, at every grid point |
| N2 | Angle coverage of 0° at a = 0.20 and 1/3. At a = 0.05 and 0.10 angle coverage is descriptive, because strategy is interpreted only after the gate passes and gate power there is low. **This restriction was set before execution with knowledge of P4.** It is a judgement, recorded as such |
| N3 | False strategy claim, P(gate passes and the interval excludes the true 0°), ≤ 0.07 at every a > 0 |
| N4 | Gate false-positive rate at a = 0 ≤ 0.07 |
| N5 | Failure rate ≤ 0.05 at every grid point |

**Execution:**

- 1,000 of 1,000 datasets, 0 errors, 0 duplicates.
- 2 s single process.
- 5 of 5 spot-checked datasets reproduced byte-identically.

---

## A1.3 Results (B3-t) [SIM]

| a | Gate passes | N1 w_on | N1 w_off | Angle coverage | N3 false claim | Gate and excludes 45° | Failures |
|---|---|---|---|---|---|---|---|
| 0 | **0.025** (N4) | 0.955 | 0.980 | n/a | n/a | 0.025 | 0 |
| 0.05 | 0.110 | 0.935 | 0.965 | 0.845 (descriptive) | 0.040 | 0.075 | 0 |
| 0.10 | 0.290 | 0.945 | 0.975 | 0.955 (descriptive) | 0.025 | 0.165 | 0 |
| 0.20 | 0.810 | 0.925 | 0.955 | **0.950** (N2) | 0.050 | 0.565 | 0 |
| 1/3 | 0.995 | 0.965 | 0.950 | **0.940** (N2) | 0.060 | 0.970 | 0 |

**Bias against β\*.** Every |bias| ≤ 0.0033.

- All but one are within 1.6 MC SE.
- The exception is a = 0.20, w_off: +0.0033 ± 0.0015, at 2.2 SE.

**Angle behaviour near zero.**

| a | Median CI width, all datasets | Median CI width, gate passed | Share of intervals ≥ 180° | Share of unwrapped intervals beyond ±180° | Point-angle mean resultant length |
|---|---|---|---|---|---|
| 0 | 263° | 96° | 0.770 | 0.645 | 0.06 (no direction) |
| 0.05 | 213° | 86° | 0.610 | 0.375 | 0.46 |
| 0.10 | 140° | 82° | 0.345 | 0.115 | 0.82 |
| 0.20 | 68° | 62° | 0.025 | 0.005 | 0.96 |
| 1/3 | 38° | 38° | 0 | 0 | 0.99 |

**Interval and containment checks.**

- No interval reached 360°.
- Circular and linear containment disagreed only at a = 0, on the 45° check (6 of 200). Circular containment is necessary there.
- At a = 0, 45.5% of point angles exceed |90°|. An unconditional angle at zero sensitivity is noise.

**Descriptive comparison, B3-boot** [SIM].

- The false strategy claim rate was 0.085 at a = 0.20 and 0.090 at a = 1/3, both above the N3 limit.
- Angle coverage was 0.915 and 0.910.
- This replicates P4 on new seeds and supports the reason for amendment AM3.

---

## A1.4 Monte Carlo-indeterminate margins added by A1 (B3-t)

| Criterion | Rate | Wilson 95% | Note |
|---|---|---|---|
| N3 false claim, a = 1/3 | 0.060 | 0.035–0.102 | Nominal joint rate is about 0.05 |
| N3 false claim, a = 0.20 | 0.050 | 0.027–0.090 | |
| N3 false claim, a = 0.05 | 0.040 | 0.020–0.077 | |
| N2 angle coverage, a = 1/3 | 0.940 | 0.898–0.965 | |
| N1 w_on, a = 0.20 | 0.925 | 0.880–0.954 | |
| N1 w_on, a = 0.05 | 0.935 | 0.892–0.962 | |
| N1 w_on, a = 1/3 | 0.965 | 0.930–0.983 | |
| N1 w_off, a = 0 | 0.980 | 0.950–0.992 | At the band edge |
| N1 w_off, a = 0.05 | 0.965 | 0.930–0.983 | |
| N1 w_off, a = 0.10 | 0.975 | 0.943–0.989 | |

Indeterminacy here mainly reflects 200 datasets per grid point. That count was the authorised scope.

---

## A1.5 Implications

1. **The sensitivity gate is necessary, not ornamental** [SIM, JDG].
   - At a = 0.05 the unconditional B3-t angle interval covers the true angle in only 0.845 of datasets.
   - With the gate applied, the false strategy claim rate is 0.040.
   - The angle interval must never be reported as a strategy statement without a passed gate. This tightens claim limit 6 in practice and should be written into the Task 06 analysis plan.
2. **Low-sensitivity groups yield few strategy statements, and that is correct behaviour** [SIM].
   - At a = 0.10 the gate passes in 29% of datasets, and the interval then excludes 45° in 0.165 of all datasets.
   - Below a ≈ 0.2, failing to distinguish onset from midpoint is expected and is not evidence of a midpoint strategy.
3. **Near-zero false claims sit near nominal** [SIM]. The B3-t false claim rate was 0.025–0.060 across the grid. Its upper Monte Carlo bound reaches 0.102 at a = 1/3. A larger run could settle this. It is not proposed (Section A1.7).
4. **Circular containment is required at zero sensitivity** [SIM]: there were 6 linear/circular disagreements at a = 0.

---

## A1.6 Changes to the closure record (by reference; the original text is not edited)

| Closure section | Was | Now (A1) |
|---|---|---|
| 8, limitation 2 | B3-t near-zero behaviour inferred, not measured | **Measured.** B3-t CONFIRMED under the frozen A1 rule |
| 9, item 2 | Recommended, not run | **Completed (A1)** |
| 7, indeterminate margins | Four listed | Four, plus ten from A1 (Section A1.4) |
| 3, step 8 | Discrimination claims only when the gate passes | Unchanged. A1 shows the requirement is load-bearing. Task 06 should state that ungated angle intervals are not reported as strategy evidence |
| 1, decision | Provisional acceptance | Unchanged |

All other sections of the closure record stand.

---

## A1.7 Recommendation [JDG]

- **No further simulation is proposed.** Narrowing the indeterminate A1 margins would need about 4–8 times the datasets, and the decision would not change.
- **Outstanding before any participant data:** E2 physical display validation, plus Task 06 items 9.3–9.6 (missing-trial handling, analysis seed, any between-condition contrast, and the re-validation trigger).

---

## A1.8 Items for approval

1. Accept A1 and its CONFIRMED outcome for B3-t, with the margins in Section A1.4.
2. Accept the A1 changes to the closure record (Section A1.6), recorded by reference.
3. Repository placement under `research/working/task05/`. A layout is proposed below; nothing has been committed.

**Proposed layout**

| Path | Content |
|---|---|
| `research/working/task05/` | The Task 05 review, design specification, closure record and Addendum A1 |
| `research/working/task05/E1/` | E1 frozen spec and report |
| `research/working/task05/E1H2/` | E1-H2 frozen spec and report |
| `research/working/task05/NZ/` | A1 frozen spec |
| `research/working/task05/task05_artefacts.zip` | Code, raw outputs, logs and hash manifests, as for Task 04 |

---

## A1.9 Files

| Content | Path (in `task05/`) |
|---|---|
| Frozen spec | `results/NZ/NZ_FROZEN_SPEC.json` |
| Pre-check | `results/NZ/precheck/precheck.json`; `logs/NZ_precheck.log` |
| Raw outputs | `results/NZ/run/` (20 batch files, manifest, progress) |
| Hashes | `results/NZ/NZ_raw_SHA256SUMS` |
| Analysis | `results/NZ/NZ_results.json`; `logs/NZ_analyse.log` |
| Run log | `logs/NZ_run.log` |
| Code | `code/nz/` |
| Prior-file integrity | `logs/NZ_prior_hashes_before.txt`, verified OK after the run |
| Deviations | `logs/DEVIATIONS.md`, NZ entry |
| Hash manifest | `logs/TASK05_ADDENDUM_A1_SHA256SUMS.txt` |

Task 06 has not been started. No canonical document has been modified, and nothing has been committed.
