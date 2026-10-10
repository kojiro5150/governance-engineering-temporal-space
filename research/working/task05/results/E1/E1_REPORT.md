# Task 05 E1: heterogeneity validation, execution report

Working document. Not canonical. Not committed.
Date: 2026-10-10. Frozen specification SHA-256 `8a8533ef…d8f` (read-only; unchanged after the run).

## 1. Verdict under the frozen decision rule

**No variant is acceptable. The frozen rule returns REVISE.**

| Variant | All criteria met at point estimate | Any criterion clearly outside | Indeterminate | Acceptable |
|---|---|---|---|---|
| B2 (B0 + CR1, t(11)) | No | Yes | 3 | No |
| B3-boot (as originally specified) | No | No | 11 | No |
| B3-t (amendment AM3) | No | Yes | 5 | No |

The failures that drive the verdict:

- **All three variants** over-cover in H2, the 6 onset + 6 midpoint mixture.
  - Weights: B2 0.984 and 0.994; B3 0.986 and 0.988.
  - Angle: B2 1.000; B3-boot 0.986; B3-t 0.996.
- **B2 only** misses E1c, the guessing false-gate rate: 35/498 = 0.0703 against a maximum of 0.07. The Wilson interval is 0.051 to 0.096, so this is indeterminate. It is one dataset over the limit.

Section 5 diagnoses the H2 failure post hoc, using an exploratory check that was not pre-specified. The diagnosis does not change the verdict.

## 2. Execution record

- **Jobs:** 3,500 of 3,500 completed: 7 scenarios × 500 repetitions, each dataset 12 participants × 20 order trials. There were 0 runtime errors, 0 duplicates and 0 missing jobs.
- **Runtime:** 286 s on 2 workers, mean 0.161 s per job.
  - Pre-check P3 projected 224 s single-core, which implies about 0.064 s per job.
  - The 2.6× gap per job is recorded in `DEVIATIONS.md`.
  - The probable cause is contention between the worker processes. This is not verified.
- **Code integrity:** all 6 frozen code files and the spec were hash-identical before and after the run (`logs/E1_posthash_check.log`).
- **Reproducibility:** 6 randomly chosen jobs were recomputed from their seeds and were byte-identical apart from timing.
- **Raw outputs:** 70 atomic batch files, the manifest and the progress log are preserved, with SHA-256 sums in `E1_raw_SHA256SUMS`.

## 3. Results by criterion

Monte Carlo uncertainty is shown as 95% Wilson intervals. "clear" means clearly inside the band and "indet" means indeterminate (see the frozen spec). n = 500 per scenario, less any failures.

### E1a and E1a2: coverage of each method's own target

The two methods have different targets:

- **B2** targets θ*, the pseudo-true working-model weights (latent scale).
- **B3** targets β*, the mean response-scale slope.

The rates below are therefore coverage rates of different quantities. The coefficients themselves are not compared across methods.

| Scenario | B2 w_on | B2 w_off | B2 angle | B3 w_on | B3 w_off | B3-boot angle | B3-t angle |
|---|---|---|---|---|---|---|---|
| S01 onset moderate | 0.962 | 0.966 | 0.964 | 0.964 | 0.954 | 0.920 indet | 0.954 |
| S03 onset high | 0.950 | 0.954 | 0.954 | 0.920 indet | 0.960 | 0.916 indet | 0.958 |
| S04 midpoint moderate | 0.966 | 0.952 | 0.966 | 0.964 | 0.954 | 0.924 indet | 0.964 |
| S13 heterogeneous | 0.976 indet | 0.952 | 0.952 | 0.972 indet | 0.960 | 0.920 indet | 0.956 |
| **H2 mixture** | **0.984** indet | **0.994** out | **1.000** out | **0.986** indet | **0.988** indet | **0.986** indet | **0.996** out |
| S12 lapses 0.15 | 0.944 | 0.960 | 0.958 | 0.950 | 0.952 | 0.922 indet | 0.952 |
| S10 guessing | 0.958 | 0.950 | n/a | 0.954 | 0.944 | n/a | n/a |

Bold marks a miss at the point estimate. "out" means clearly outside the band. B3-boot and B3-t share the same weight intervals.

The B3 bootstrap angle interval under-covers consistently, at 0.916 to 0.924. That is inside the band but at its lower edge in every scenario, which matches pre-check P4. The B3-t interval brings angle coverage to 0.952 to 0.964 outside H2.

### E1b: discrimination, gate-conditional, circular containment

| Variant | S01: gate and excludes 45° | S04: gate and excludes 0° |
|---|---|---|
| B2 | 499/499 | 499/500 |
| B3-boot | 500/500 | 500/500 |
| B3-t | 500/500 | 499/500 |

All variants are clearly above 0.80.

H2 has no single true strategy, so its discrimination is informational only:

| Variant | H2: gate and excludes 45° | H2: gate and excludes 0° |
|---|---|---|
| B2 | 0.698 | 0.586 |
| B3-boot | 0.842 | 0.742 |
| B3-t | 0.740 | 0.576 |

### E1c: guessing false-gate rate (S10; maximum 0.07)

| Variant | Gate passes | Rate | Wilson 95% |
|---|---|---|---|
| B2 (robust Wald, F(2, 11)) | 35/498 | 0.0703 | 0.051 to 0.096 |
| B3 (Hotelling, F(2, 10)) | 28/500 | 0.056 | 0.039 to 0.080 |

The nominal level is 0.05. B2's gate is liberal at 7%, consistent with known small-cluster liberality of CR1 Wald tests. The single-run evidence is indeterminate.

### E1d: failures (maximum 0.05)

- **B2:** 6 of 3,500 fits flagged unstable (S01 1, S03 1, S12 2, S10 2), at most 0.4% in any scenario.
- **B3:** no failures.
- **B2 boundary estimates:** separately, B2's random-intercept SD was estimated at the boundary in 395 of 3,500 datasets (11%). These fits still produced valid robust SEs and are not failures under the frozen definition.

### E1e: interpretation (from frozen targets)

This criterion is met for both methods. It was computed before execution, so it is a deduction from the targets, not a simulation result of E1.

## 4. Estimand-specific bias

### B2 relative to its own target θ*

Values are mean estimate − θ*, with Monte Carlo SE.

| Scenario | w_on | w_off |
|---|---|---|
| S01 | +0.012 (0.003) | +0.003 (0.003) |
| S03 | +0.015 (0.005) | −0.008 (0.003) |
| S04 | −0.001 (0.003) | +0.003 (0.003) |
| S13 | +0.007 (0.004) | −0.003 (0.003) |
| H2 | +0.008 (0.003) | +0.002 (0.002) |
| S12 | +0.006 (0.003) | −0.005 (0.003) |

There is a small upward finite-sample bias in w_on, about 1.5 to 1.8% of θ* in S01 and S03 (3 to 4 MC SE). This is consistent with ML small-sample inflation in logistic models. Coverage is unaffected.

### B2 relative to the mean latent weight μ_w

This is the reference quantity B2 is often assumed to estimate. It is not B2's target.

| Scenario | Relative bias, w_on | B2 CI coverage of μ_w, w_on |
|---|---|---|
| S01 | −1.7% | 0.940 |
| S03 | −3.6% | 0.922 |
| S04 | −2.0% | 0.966 |
| S13 | −8.6% | 0.900 |
| H2 | −7.0% | 0.984 |
| S12 | **−21.4%** | **0.476** |

Relative bias is (mean estimate − μ_w) ÷ ‖μ_w‖.

Under lapses, B2's intervals are calibrated for θ* and miss the mean latent weight in more than half of datasets. Correct cluster-robust coverage of θ* does not make B2 a magnitude estimator of μ_w. The angle survives: mean B2 angle in H2 was 19.7°, against 19.8° for θ* and 18.4° for μ_w.

### B3 relative to its own target β*

Every |bias| was at most 0.0014 on a slope scale of about 0.1 to 0.3, within about 2 MC SE everywhere. B3's magnitude is a response-scale quantity. It is not comparable to B2's or to μ_w.

## 5. Post-hoc diagnosis of the H2 failure (exploratory, not pre-specified)

### The hypothesis (deduction)

The frozen generator fixes H2's composition at exactly 6 onset and 6 midpoint participants in every dataset. Both methods' participant-level SEs estimate sampling variance for participants drawn independently from a 50/50 population. That variance includes variation in composition. Fixing the composition removes that component from the true sampling variance, so the SEs are conservative and the intervals over-cover. This is stratified sampling analysed as if it were simple random sampling.

The run supports the hypothesis:

| Method | Empirical SD of the estimate, w_on | Median SE, w_on |
|---|---|---|
| B2 | 0.058 | 0.076 |
| B3 | 0.016 | 0.023 |

### The test

- **Code:** `code/post_hoc/e1_posthoc_h2_composition.py`, written after seeing the results and recorded as D5.
- **Design:** 500 datasets with the onset count drawn from Binomial(12, 0.5), a new seed namespace, frozen code imported unchanged, and the frozen H2 targets.
- **Runtime:** measured at 20 repetitions before running about 50 s.

| Variant | w_on | w_off | Angle |
|---|---|---|---|
| B2 | 0.950 | 0.952 | 0.952 |
| B3-boot | 0.936 | 0.952 | 0.924 |
| B3-t | 0.936 | 0.952 | 0.950 |

With random composition, empirical SDs match the SEs: B2 0.079 against 0.076, and B3 0.024 against 0.023.

### Reading

The H2 failure comes from a mismatch between the generator and the target population. It is common to all three variants and is not specific to any method. This is a simulation finding from one exploratory run. It does not rescue any variant under the frozen rule, and it was not pre-specified.

## 6. Scientific interpretation of each estimand (methodological judgement)

**B2.** The estimand is θ*, the KL projection of a heterogeneous or lapsing population onto a random-intercept model with common slopes.

- Its angle tracked the angle of μ_w to within 1.4° in every scenario.
- Its magnitude is attenuated by lapses and slope heterogeneity, by up to 22% here. It should not be reported as the mean latent weight.
- It keeps the latent scale only in the sense of the working model's scale, not the individual scale.

**B3.** The estimand is β*, the mean of individual response-scale slopes of the signed score.

- Its magnitude has no latent interpretation.
- Its angle tracked the angle of μ_w to within 0.46° in these scenarios. The mapping distortion on the frozen grid was at most 2.84°, with compression of intermediate angles.
- It is model-light and does not depend on the ordinal link.

**What each estimand supports.** Both are defensible for the primary quantity, the strategy angle, on this evidence. Neither is defensible as an estimator of mean latent weight magnitude.

## 7. What would change the verdict (for reviewer decision; not acted on)

1. **H2 generator.**
   - The reviewer would need to decide whether H2 should represent random sampling from a mixed population.
   - If it should, the clean route is a fresh frozen confirmatory run of H2 only, with random composition and a new namespace, recorded as a post-results amendment.
   - Reinterpreting the existing run is not a substitute.
2. **If H2 were resolved,** the outcome on this run's other scenarios would be:
   - **B3-t** meets every other criterion at the point estimate, with none clearly outside.
     - B3-t was itself added before execution (AM3) after a pre-check showed the problem it fixes.
     - E1 is therefore an out-of-sample test of B3-t, with new seeds, but not of an originally specified method.
   - **B3-boot** meets the other criteria at the point estimate, with angle coverage at 0.916 to 0.924 in every scenario.
   - **B2** still misses E1c by one dataset (indeterminate). Its gate would need either a larger confirmatory run or a small-sample correction such as CR2 with Bell-McCaffrey degrees of freedom. That would be a new method, not a reinterpretation.
3. **No method is selected here.** The latent-scale interpretation of B2 is not used as a tie-breaker. As section 6 shows, B2's latent scale is the working model's, not the participants'.

## 8. Evidence status

| Type | Content |
|---|---|
| Simulation findings | Coverage, bias, gate rates and failures in sections 3 to 5 (E1 frozen run; H2 post-hoc run labelled exploratory) |
| Mathematical deductions | The stratification account of H2 over-coverage; E1e angle deviations from the frozen targets |
| Methodological judgement | Estimand interpretation (section 6); the options in section 7 |
| Empirical evidence | None. No participant data exist. Nothing here bears on whether temporal augmentation improves human perception. |

## 9. Files

| Content | Location |
|---|---|
| Frozen spec | `results/E1/E1_FROZEN_SPEC.json` and `E1_FROZEN_SPEC.md` |
| Raw outputs | `results/E1/run/` (70 batch files, `manifest.json`, `progress.jsonl`); hashes in `results/E1/E1_raw_SHA256SUMS` |
| Analysis | `results/E1/E1_results.json`; `logs/E1_analyse.log` |
| Run log | `logs/E1_run.log` |
| Integrity check | `logs/E1_posthash_check.log` |
| Pre-checks | `results/E1/prechecks/` |
| Post-hoc diagnostic | `results/E1/post_hoc/` (jsonl and summary); code in `code/post_hoc/` |
| Deviations | `logs/DEVIATIONS.md`, entries D5 and the E1 execution note |

E1 is complete. Task 06 has not been started. No canonical document has been modified, and nothing has been committed.
