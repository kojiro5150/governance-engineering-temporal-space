# E1 Frozen Specification (human-readable)

- Machine-readable version (authoritative): `E1_FROZEN_SPEC.json`, SHA-256 `8a8533eff182c88f5d841e5cc466d3b893b877d6d6a9d779d6e7043dce533d8f`, file mode read-only.
- Frozen 2026-10-10 at about 10:58 AEDT, before any E1 dataset was generated. The only prior runs were a 2-repetition functional smoke test in a scratch folder (checks that outputs exist and are finite; no criteria evaluated) and the pre-checks P1–P4.
- The runner refuses to start, and the analysis refuses to run, if the spec or any listed code file differs from its frozen hash.

## Design

- Scenarios (7): S01 onset moderate; S03 onset high; S04 midpoint moderate; S13 heterogeneous weights and thresholds; H2 mixture (6 onset + 6 midpoint); S12 onset with lapses 0.15; S10 guessing.
- Size: 500 repetitions each, so 3,500 datasets of 12 participants × 20 order trials.
- Seeds: SHA-256 of `task05-E1-v1|<scenario>|<rep>`.

## Method variants

| Variant | Weight CI | Gate | Angle CI |
|---|---|---|---|
| B2 | B0 estimate ± t(11) × CR1 cluster-robust SE | Robust Wald, F(2, 11) | 2,000 multivariate t(11) draws |
| B3-boot | Mean of participant slopes ± t(11) SE | Hotelling, F(2, 10) | 2,000 participant-bootstrap resamples (as originally specified) |
| B3-t (amendment AM3) | As B3-boot | As B3-boot | 2,000 multivariate t(11) draws from the participant covariance |

All angle checks use circular containment.

## Targets (estimand-specific; B2 and B3 are not numerically comparable)

- **B2 target θ*:** the pseudo-true weights of the random-intercept working model. Estimated from 4 fits × 6,000 simulated participants; Monte Carlo SE ≤ 0.0033.
- **B3 target β*:** the population mean of individual expected response-scale slopes (Monte Carlo, 400,000 draws).
- **Reference μ_w:** the mean of individual latent weights. Used only to report B2's estimand-specific bias.

| Scenario | μ_w | θ* (B2) | (θ* − μ_w) ÷ ‖μ_w‖, w_on | β* (B3) |
|---|---|---|---|---|
| S01 | (0.700, 0) | (0.676, −0.000) | −0.035 | (0.2259, 0) |
| S03 | (1.070, 0) | (1.016, 0.001) | −0.050 | (0.2861, 0) |
| S04 | (0.350, 0.350) | (0.341, 0.339) | −0.018 | (0.1176, 0.1176) |
| S13 | (0.732, 0) | (0.663, 0.001) | **−0.095** | (0.2212, 0) |
| H2 | (0.525, 0.175) | (0.478, 0.172) | −0.084 | (0.1717, 0.0588) |
| S12 | (0.700, 0) | (0.544, 0.000) | **−0.223** | (0.1959, 0) |
| S10 | (0, 0) | (0.001, −0.001) | n/a | (0, 0) |

## Criteria (judged on point estimates; Monte Carlo uncertainty classified with Wilson intervals)

- **E1a:** weight-CI coverage of the method's own target, w_on and w_off, within [0.90, 0.98] in every scenario.
- **E1a2 (AM5):** angle-interval coverage of the own target angle within [0.90, 0.98], every scenario except S10.
- **E1b:** P(gate passes and angle CI excludes 45° | S01) ≥ 0.80, and P(gate passes and angle CI excludes 0° | S04) ≥ 0.80.
- **E1c:** P(gate passes | S10) ≤ 0.07.
- **E1d:** failure rate ≤ 0.05 in every scenario.
- **E1e (AM5):** interpretation, computed from the frozen targets.
  - B2: maximum |angle(θ*) − angle(μ_w)| = 1.37° (H2). **Met.**
  - B3: maximum |angle(β*) − angle(μ_w)| = 0.46°; maximum latent-to-response distortion on the mapping grid = 2.84°. **Met.**
- **Not gating:** magnitude bias versus μ_w is reported but not a criterion.

## Decision rule

- A variant is acceptable only if all of E1a, E1a2, E1b, E1c and E1d are met at the point estimate, none is "clearly outside" its Monte Carlo interval, and E1e is met.
- If more than one variant is acceptable: **no automatic selection**. Trade-offs are reported for reviewer decision.
- Latent-scale interpretation is not a tie-breaker.

## Amendments to the Task 05 companion specification, Section 2 (made before execution, not pre-specified originally)

- **AM1:** B2 target redefined as θ*; bias against μ_w reported separately.
- **AM2:** B3's response-scale target kept separate; no cross-method numeric comparison.
- **AM3:** B3-t angle interval added after pre-check P4 showed the bootstrap interval falsely excluding the true onset angle in 7.5–9.0% of datasets at sensitivities 0.20–0.33. The specified bootstrap variant is still evaluated unchanged.
- **AM4:** circular containment; discrimination conditional on the gate; gate tests defined.
- **AM5:** criteria E1a2 and E1e added; magnitude bias made non-gating.
- **AM6:** no default preference for B2.
- **AM7:** Task 04 Stage 2 guessing-scenario angle statistics used linear containment (8 disagreements); noted only.
