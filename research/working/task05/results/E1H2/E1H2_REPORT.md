# Task 05 E1-H2 confirmatory amendment: report for independent review

This is a working document. It is not canonical and has not been committed.

- **Date:** 2026-10-10.
- **Frozen amendment spec:** SHA-256 `666c0cb5…3745`, read-only.
- **Separate from the E1 report.** The original E1 specification, results, raw outputs and REVISE verdict are unchanged. Their hashes were verified after this run, in `logs/E1H2_original_E1_hashes_after_check.txt`.

## 1. What this amendment tests

**Target population.** Observers who are either onset-weighted (w_on 0.70, w_off 0) or midpoint-weighted (w_on 0.35, w_off 0.35). Each participant's membership is drawn independently with probability 0.5.

**Design.** 500 new datasets of 12 participants × 20 order trials, under namespace `task05-E1H2-confirm-v1`.

**Methods.** B2, B3-boot and B3-t, run with the frozen E1 code unchanged.

**Estimands.** These are kept separate and are not compared numerically.

| Method | Estimand | Scale | w_on | w_off | Angle |
|---|---|---|---|---|---|
| B2 | θ*, the pseudo-true weights of the random-intercept working model | Latent, working model | 0.4785 | 0.1723 | 19.80° |
| B3 | β*, the population mean of individual response-scale slopes | Response | 0.1717 | 0.0588 | 18.90° |
| Reference only | μ_w, the mean individual latent weight | Latent, individual | 0.525 | 0.175 | 18.43° |

The targets are those frozen for E1 H2. A pre-freeze check re-estimated θ* under random membership: the difference was −0.23 and +0.04 combined Monte Carlo SE. β* was identical to 5 decimal places.

**Not counted.** The exploratory D5 run, seen before this freeze, is neither counted nor pooled.

## 2. Execution

- **Completion:** 500 of 500 datasets, with 0 errors, 0 duplicates and 0 missing.
- **Runtime:** 43 s on 2 workers. The projection was 33 s single-process.
- **Composition:** realised onset counts ranged from 2 to 11 of 12. 102 datasets had 4 or fewer onset observers, 298 had 5 to 7, and 100 had 8 or more.
- **Reproducibility:** 5 randomly chosen datasets recomputed byte-identically, apart from timing.
- **Code changes after freezing:** none. During the scratch smoke test, before freezing, one import-order bug in `e1h2_analyse.py` was fixed. It is logged.

## 3. Results against the frozen criteria

Coverage is shown with 95% Wilson Monte Carlo intervals. The band is [0.90, 0.98].

| Criterion | B2 | B3-boot | B3-t |
|---|---|---|---|
| H1 w_on coverage | 0.946 (0.922–0.963), clear | 0.930 (0.904–0.949), clear | 0.930 (0.904–0.949), clear |
| H1 w_off coverage | 0.936 (0.911–0.954), clear | 0.922 (0.895–0.942), indet | 0.922 (0.895–0.942), indet |
| H2 angle coverage | 0.940 (0.916–0.958), clear | **0.882** (0.851–0.907), indet | 0.930 (0.904–0.949), clear |
| H3 failures | 1/500 | 0/500 | 0/500 |
| **H2-population criteria** | **Met** | **Not met** (angle) | **Met** |

"clear" means clearly inside the band; "indet" means indeterminate.

### Calibration

All three variants sit at or below nominal coverage. The empirical sampling SD is about 7% larger than the median SE:

| Method | Empirical SD, w_on | Median SE, w_on |
|---|---|---|
| B2 | 0.081 | 0.075 |
| B3 | 0.024 | 0.022 |

This is mild small-sample underestimation with 12 participants drawn from a bimodal population. It reverses the over-coverage seen under fixed composition in E1, as the stratification account predicted.

### Bias against each method's own target

| Method | w_on bias (MC SE) | w_off bias (MC SE) |
|---|---|---|
| B2 | +0.006 (0.004) | +0.003 (0.004) |
| B3 | −0.0007 (0.0011) | +0.0004 (0.0012) |

Both are within 2 MC SE.

### B2 measured against μ_w

This is not B2's target. B2's mean w_on is 7.3% below μ_w (relative to ‖μ_w‖). Its intervals contain μ_w's w_on in 0.912 of datasets (0.884–0.934).

### Failures

- B2 produced 1 unstable fit.
- The B2 random-intercept SD was at the boundary in 64 of 500 datasets.
- B3 had no failures.

## 4. Sensitivity-gate behaviour

Rates are per dataset, conditional on the gate passing, using circular containment.

| Event | B2 | B3-boot | B3-t |
|---|---|---|---|
| Gate passes | 499/499 | 500/500 | 500/500 |
| Passes, CI excludes 0° (pure onset) | 0.561 | 0.668 | 0.556 |
| Passes, CI excludes 45° (pure midpoint) | 0.621 | 0.752 | 0.644 |
| Passes, CI excludes **both** 0° and 45° | 0.259 | 0.426 | 0.248 |
| Passes, CI excludes **neither** | 0.076 | 0.006 | 0.048 |

The gate does what it is designed to do: there is real sensitivity, and it passes. The gate says nothing about whether a single strategy exists.

## 5. Implications for interpreting a heterogeneous group mean

The evidence type is marked on each point.

1. **The group-mean angle describes no observer** *(simulation finding and deduction).* The estimated angle averages 19.5° (B3) to 20.2° (B2). Every simulated observer uses either 0° or 45°. In about a quarter of datasets (B2 0.259, B3-t 0.248), a method with correct coverage of its own target reports an angle interval that excludes both strategies actually present. The inference is correct about the population mean and wrong if read as a typical observer's strategy.
2. **Group-mean data cannot distinguish a mixture from a homogeneous intermediate strategy** *(deduction).* A 50/50 mixture of 0° and 45° observers and a population of identical observers at about 19° produce the same population-mean target. Distinguishing them needs individual-level estimates or a mixture model. Validation B found individual classification at J = 20 to be weak: 0.774 for onset and 0.429 for midpoint. Neither route is validated at this design size.
3. **The estimate tracks the realised sample composition** *(simulation finding, informational stratum analysis).*
   - The SD of the angle across datasets is 9.4°.
   - The mean estimated angle is about 30° when 4 or fewer of 12 are onset observers, and 9° to 10° when 8 or more are.
   - Coverage of the population target is correct unconditionally. Conditional on an unbalanced sample it falls to 0.76–0.88 for the angle, depending on method and direction of imbalance.
   - A single study's group mean is therefore an estimate of the population mix. It can sit far from it when the sample is unbalanced.
4. **Magnitude remains estimand-specific** *(simulation finding).*
   - B2's weights are attenuated relative to μ_w by 7% here and by up to 21% in E1.
   - B3's weights are on the response scale.
   - Neither should be reported as the mean individual latent weight.
5. **Reporting consequence** *(methodological judgement).* If a participant study pools a population that may be heterogeneous, the strategy angle should be reported as a population-average angle. Any claim about individual strategy needs separate, validated individual-level evidence.

## 6. Composite amended status (pre-specified; reported separately from the original verdict)

The composite requires a variant to meet the original E1 criteria outside the fixed-composition H2 scenario, plus E1e, plus the H2-population criteria above.

| Variant | H2-population criteria | Original E1 shortfalls outside H2 | Composite |
|---|---|---|---|
| B2 | Met | E1c guessing false-gate rate 35/498 = 0.0703 against a maximum of 0.07 (indeterminate) | Not met |
| B3-boot | Not met (angle 0.882) | None at the point estimate. Angle coverage was 0.916–0.924 in E1 (indeterminate). | Not met |
| B3-t | Met | None | Met |

B3-t is the only variant that meets the composite. Under the frozen rule this is reported, not acted on. **No method is selected.**

Trade-offs for the reviewer:

- **B3-t's provenance.**
  - B3-t was added as amendment AM3 after a pre-check showed the bootstrap interval's weakness. It was not originally specified.
  - E1 and this amendment test it on new seeds, so the tests are out of sample. But the variant was chosen with knowledge of the problem it fixes.
- **B3-t's margins.**
  - It has four indeterminate margins. Three are from E1 outside H2: w_on 0.920 in S03, w_on 0.972 in S13, and the guessing false-gate rate 0.056 (Wilson 0.039–0.080). The fourth is w_off 0.922 here.
  - All are inside the band at the point estimate, and none is clearly outside.
- **B3's estimand.**
  - It is response-scale and model-light.
  - Its angle tracked μ_w's angle to within 0.46° in all E1 scenarios.
  - It compresses intermediate angles by up to 2.84° on the frozen grid.
  - Its magnitude has no latent interpretation.
- **B2.**
  - B2 meets every H2-population criterion and is clearly inside on all of them.
  - Its remaining shortfall is a guessing-gate rate one dataset over the limit. That is indeterminate, with Wilson interval 0.051–0.096.
  - Resolving it needs either a larger frozen run of the guessing scenario or a small-sample gate correction, which would be a new method.
  - Its latent scale belongs to the working model, not to individuals, and is not a tie-breaker.
- **Decision not made here.** Whether the composite result warrants adopting B3-t, or whether B2's gate deserves a confirmatory test first, is a reviewer decision.

## 7. Evidence status

| Type | Content |
|---|---|
| Simulation findings | Sections 2 to 4, and the numerical parts of 5 and 6 |
| Mathematical deductions | Invariance of the targets to sampling composition; non-identifiability of a mixture from the group mean |
| Methodological judgement | Reporting consequence (5.5); trade-offs (6) |
| Empirical evidence | None. Nothing here bears on human perception or on temporal augmentation. |

## 8. Files

| Content | Location |
|---|---|
| Frozen spec | `results/E1H2/E1H2_FROZEN_SPEC.json` and `E1H2_FROZEN_SPEC.md` |
| Pre-freeze checks | `results/E1H2/precheck/precheck.json`; `logs/E1H2_precheck.log` |
| Raw outputs | `results/E1H2/run/` (10 batch files, manifest, progress); hashes in `results/E1H2/E1H2_raw_SHA256SUMS` |
| Analysis | `results/E1H2/E1H2_results.json`; `logs/E1H2_analyse.log` |
| Run log | `logs/E1H2_run.log` |
| Code | `code/e1h2/` |
| Deviations | `logs/DEVIATIONS.md` (E1-H2 entry) |
| Original E1 integrity check | `logs/E1H2_original_E1_hashes_before.txt` and `logs/E1H2_original_E1_hashes_after_check.txt` |

The amendment is complete. Task 06 has not been started, nothing has been committed, and no canonical document has been changed.
