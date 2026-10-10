# E1-H2 confirmatory amendment: frozen specification (human-readable)

## Status of this file

- **Authoritative version:** `E1H2_FROZEN_SPEC.json`, SHA-256 `666c0cb5326206e74bdfc94e221251d72eb945cc4ce1ef9292673cd6fa033745`, read-only.
- **When frozen:** 2026-10-10, about 11:13 AEDT, before any confirmatory dataset was generated.
- **Original E1 is unchanged and remains the record of E1:**
  - frozen spec SHA-256 `8a8533ef…`
  - results file `E1_results.json`, hash recorded in the JSON
  - REVISE verdict
- **Amendment, not pre-specification.** This specification was written after the original E1 results and the exploratory D5 run had been seen.

## Population

- **Membership:** each participant is independently onset-weighted or midpoint-weighted, with probability 0.5 each, drawn per participant per dataset.
  - Onset-weighted: w_on 0.70, w_off 0.
  - Midpoint-weighted: w_on 0.35, w_off 0.35.
- **Other parameters:** lapse 0.02, τ 1.0, bias SD 0.5.
- **Dataset size:** 12 participants × 20 order trials. 500 datasets.
- **Seeds:** SHA-256 of `task05-E1H2-confirm-v1|<rep>`.
- **Random-number order per dataset:** membership draws, then responses, then B2, then B3.

## Methods

B2, B3-boot and B3-t are run exactly as in E1. The frozen E1 code is imported unchanged, and its hashes are re-verified in this spec.

## Targets

These are the frozen E1 H2 targets. Population targets depend on the 50/50 population, not on a sample's composition. This is a deduction.

| Quantity | w_on | w_off | Angle |
|---|---|---|---|
| μ_w | 0.525 | 0.175 | 18.43° |
| θ* (B2) | 0.47845 | 0.17230 | 19.80° |
| β* (B3) | 0.17171 | 0.05878 | 18.90° |

The pre-freeze check T1 confirmed the targets:

- **θ*:** re-estimated under random membership (4 × 6,000 participants). It differed from the frozen value by −0.23 and +0.04 combined Monte Carlo SE.
- **β*:** recomputed and identical to 5 decimal places.

## Criteria

These are unchanged from E1.

| Criterion | Requirement |
|---|---|
| H1 | Weight-CI coverage of the method's own target, w_on and w_off, within [0.90, 0.98] |
| H2 | Angle coverage of the own target angle, circular containment, within [0.90, 0.98] |
| H3 | Failure rate ≤ 0.05 |
| Monte Carlo uncertainty | Wilson 95% interval, classified clearly inside, indeterminate or clearly outside |

The following are reported descriptively and do not gate any decision:

- gate behaviour: passes, and passes while excluding 0°, 45°, both or neither
- bias against the method's own target
- empirical SD against median SE
- B2 measured against μ_w
- coverage by realised composition

## Decision rule

1. **H2-population criteria:** met if H1, H2 and H3 are all met at the point estimate and none is clearly outside.
2. **Composite amended status:**
   - **What it requires:** the original E1 criteria outside the fixed-composition H2 scenario, read from the frozen E1 results by hash, plus E1e, plus the H2-population criteria.
   - **How it is reported:** separately. It never replaces the original verdict.
3. **No automatic selection:** latent-scale interpretation is not a tie-breaker.

## Disclosures

- The criteria bands were not tuned.
- The exploratory D5 run used namespace `task05-E1-posthoc-H2random-v1` and Binomial composition. It was seen before this freeze. It is not counted as confirmatory and is not pooled with this run.
- This amendment replaces only the H2 generator. B2's original E1c shortfall (35/498) stands.

## Pre-freeze runtime

- 20 complete datasets: median 0.061 s each.
- Projection for 500 datasets: 33 s single-process.
