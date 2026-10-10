# Task 05 Companion: Revised Experimental Design Specification

- Status: Proposal for review. Non-canonical. It does not modify Task 03; it lists changes to carry into Task 06 (specification and pre-registration) if approved.
- Basis: `task05-statistical-robustness-review.md` (evidence labels as defined there)
- Date: 10 October 2026

Everything not listed here stays as specified in Task 03 Parts 6–9, with the Task 04 corrections.

---

## 1. Specification changes

### S1. Likelihood and sign convention [DED]

Categories are ordered R < S < L. With η_ij = w_on·Δon_ij + w_off·Δoff_ij + u_i:

- P(r ≤ R) = logistic(θ1 − η)
- P(r ≤ S) = logistic(θ2 − η), with θ1 < θ2

Δon = onset(R) − onset(L) and Δoff = offset(R) − offset(L). This replaces the Task 03 Part 8.2 formula, which negates the weights.

### S2. Primary estimand [SIM]

For each condition, the **group-level strategy angle** φ = atan2(w_off, w_on), in degrees.

- **Sensitivity gate:** φ is interpreted only if the joint test of w_on = w_off = 0 rejects at α = 0.05, using the method chosen in S3.
- **Secondary:** sensitivity magnitude ‖w‖, labelled lapse-confounded (S9).
- **Removed:** the Task 03 onset index.

### S3. Inference method [SIM; pending E1]

One method is chosen after E1, pre-registered, and used for everything:

- **B2:** B0 point estimates with participant-cluster-robust sandwich variance (CR1 factor 12/11), t(11) critical values. Angle interval from multivariate t(11) draws.
- **B3:** per-participant least-squares slopes of the signed score (R = −1, S = 0, L = +1); group mean with t(11) intervals; angle interval by participant bootstrap (2,000 resamples).

The Task 03 Bayesian proposal is dropped for the pilot. It was not timed or validated.

### S4. Catch trials [JDG, informed by SIM]

- **Specification:** K = 4 per participant, inside the order block, one per quarter. Cells (+8, +8) twice and (−8, −8) twice. 6 s non-overlapping ramps with a 2 s gap. Magnitude M = 10 L*. Directions balanced and crossed with leader side. Mean onset m ~ U[5.5, 8.5] s; first onset in [1.5, 4.5] s; last offset in [15.5, 18.5] s; T = 24 s.
- **Order block length:** 24 trials (20 main + 4 catch). Breaks after trials 8 and 16.
- **Excluded from the cue-weight model.**
- **Participant exclusion:** 3 or more of 4 catch trials wrong. Simulated operating characteristics [SIM; `results/validationC/exclusion_rule_operating_characteristics.json`]:

| Simulated participant type | Proportion excluded |
|---|---|
| Guessing (no order sensitivity) | 0.68 |
| Onset observer, random lapses 0.02 | 0.000 |
| Onset observer, random lapses 0.15 | 0.006 |
| Midpoint observer, random lapses 0.15 | 0.003 |
| Low temporal sensitivity (process M3, either calibration) | ≤ 0.0004 |
| Attention failures (process M2a / M2b, 0.85 calibration) | 0.004 / 0.0004 |

The rule removes most non-performing participants without removing genuinely low-sensitivity ones. It assumes attentive participants are close to ceiling on catch trials [ASM; untested in humans].

### S5. Attention indicators and reporting rule [SIM, JDG]

For each condition, report:
- catch error rate,
- "same" response rate on main trials,
- main-trial performance in the first vs second half of the order block.

**Rule:** an A-versus-B or A-versus-C difference in φ is labelled **"attention-inclusive"** unless both of the following hold:
- A's catch error rate is within 0.05 of the comparison condition's, and
- A's "same" rate is within 0.10 of it.

Otherwise it is labelled **"possibly attentional"**.

**Power note:** with 48 catch trials per condition, the SE of a catch-error difference is about 0.04 (computed for 0.06 against 0.013). The rule is a screen, not a test.

### S6. Interpretation rules [DED, SIM]

| Estimated φ (with interval) | Permitted description | Not permitted |
|---|---|---|
| Interval within about −10° to 25° | Onset-dominant cue weighting; compatible with onset timing plus detection delay | "Uses offset information" |
| Interval containing 45° and excluding 0° | Midpoint-like cue weighting | "Judges midpoints", "uses timing of midpoints" (state comparison and, in C, area comparison produce the same signature) |
| About 90° | Offset-dominant cue weighting | |
| Negative, towards −45° | Rate or duration cue | |
| Interval wider than 60° or gate fails | No strategy statement | Any strategy label |

All statements are group-level. Strategy labels describe cue weighting, not mechanism.

### S7. No individual classification [SIM]

Individual B3 angles are reported descriptively (histogram, per condition) with the explicit statement that 20 trials do not support classifying individuals. The simulated rates were 0.77 correct for onset and 0.43 correct for midpoint, with 0.39 unclassifiable. Mixture versus intermediate strategy is declared unidentifiable.

### S8. Condition C claims [SIM]

Condition C results are described as **"recognition of onset order from a static trace display"**. They are not evidence of temporal relationship recognition until C-sequential and C-strip controls (Task 03 Part 2.5) have been run in a later study.

### S9. Lapses [SIM]

- No explicit lapse parameter in the primary model.
- A catch-anchored correction (λ̂ = 1.5 × catch error rate, fixed in the lapse model) is reported as a labelled sensitivity analysis for magnitude only. Its SEs understate uncertainty.

### S10. Rendering [SIM, computational only]

- Triangular (TPDF) temporal dither replaces Task 03's uniform dither. Simulated post-onset ÷ pre-onset frame-change variance ratio: 1.03 against 0.72 for uniform.
- Task 03 audit criterion 6.7(5) is replaced by:
  - (a) no undithered code step pattern in rendered ramps, and
  - (b) frame-change variance stationary across onset within the computational range.
- Visibility remains subject to the physical-display check (E2).

### S11. Timing statement [DED]

The latest order-block offset is 19.5 s (Task 03 stated 22.5 s). T stays 24 s, so exposure is equal across main, catch and detection trials. Detection-block ramps can end at 24.0 s, so their end state may not be displayed for any interval. That is noted, not changed.

### Burden (model-based) [ASM]

Medians: condition A 25.4 minutes (90th percentile 26.2); B 14.1; C 15.5. These figures use the inherited Task 04 assumptions and must be measured in Task 07.

---

## 2. E1: heterogeneity validation (requires approval before running)

**Purpose:** choose between B2 and B3 (S3), or reject both.

**Scenarios** (20 order trials, 12 participants, Task 04 generator conventions):
- S01 onset moderate
- S03 onset high
- S04 midpoint moderate
- S13 heterogeneous weights and thresholds
- H2 mixture (6 onset + 6 midpoint)
- S12 onset with lapses 0.15
- S10 guessing

**Scale:** 500 repetitions each, 3,500 datasets. New seed namespace `task05-E1-v1`. Checkpointed with `simulate_recovery_v3.py`-style batching.

**Measured cost:** B0 + B2 at about 0.055 s per dataset; B3 at under 0.001 s. About 3–4 CPU-minutes in total, so under 5 minutes of wall time on 2 cores. B1, if requested, adds about 30 minutes of wall time.

**Pre-specified criteria:**

| ID | Criterion |
|---|---|
| E1-a | Coverage of each method's own estimand in [0.90, 0.98], every scenario. B2 estimand: B0 weights in the homogeneous scenarios; mean of individual latent weights in S13 and H2. B3 estimand: population mean of individual expected response-scale slopes (computed by the Monte Carlo truth function, corrected version) |
| E1-b | Onset vs midpoint: P(angle interval excludes 45° given onset truth) ≥ 0.80 and P(excludes 0° given midpoint truth) ≥ 0.80 |
| E1-c | Guessing: sensitivity gate rejects in at most 0.07 of datasets |
| E1-d | Fit or estimation failure at most 0.05 in every scenario |

**Monte Carlo uncertainty:** criteria are judged on point estimates; Wilson intervals are reported. Results within an interval that straddles a boundary are labelled indeterminate rather than failed.

**Decision rule:** choose the method that meets all criteria. If both do, choose B2 (latent-scale estimand, comparable with Tasks 03–05). If neither does, REVISE the analysis plan before Task 06.

---

## 3. Items requiring pre-registration (Task 06)

1. Hypotheses, stated as group-level cue-weighting contrasts between conditions. No individual-level hypotheses.
2. Stimulus specification: Task 03 Part 6 with S10 and S11; the catch-trial specification S4; seed scheme and PRNG.
3. Trial allocation: 12 detection trials; 24 order trials (20 + 4 catch); positions and randomisation.
4. Primary estimand, sensitivity gate and the interpretation table (S2, S6).
5. Inference method chosen after E1 (S3), with software versions and the fitting settings (bounds, quadrature nodes, boundary handling).
6. Exclusion rules: calibration below 9/10; catch errors ≥ 3/4; failed attention check; frame-timing failure (Task 03 F4); viewport below 900 CSS px.
7. Attention reporting rule and tolerances (S5).
8. Secondary analyses: magnitude; catch-anchored sensitivity analysis (S9); detection-block d′; descriptive individual angles (S7).
9. Feasibility criteria (Task 03 Part 9), with F8 redefined on the chosen method's intervals.
10. Claim limits: S7 and S8 verbatim.
11. Sample size: 12 per condition as a feasibility rule of thumb (Julious 2005), not powered for inference.
12. Deviations procedure and data-sharing format.
