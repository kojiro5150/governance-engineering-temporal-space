# Task 06 D2: Statistical Analysis Plan (revision 3.1)

| Field | Value |
|---|---|
| Status | **Working draft for independent review.** Not preregistered |
| Revision | r3.1, 2026-10-10. Final reviewer decisions OD-21 (suppress classification and Q2c for a primary analysis with n ≠ 12) and OD-22 (incomplete-trial OLS analysis removed). Changes from r3 are in `task06-CHANGELOG-r3-to-r3.1.md`; earlier changes are in `task06-CHANGELOG-r2-to-r3.md` and `task06-CHANGELOG.md` |
| Labels | As in D1: [REC], [DED], [SIM], [JDG], [SG] |
| Baseline | `main` at `7a65782c…` |
| Analysis method | B3-t, provisionally accepted in the Task 05 closure record and Addendum A1 |
| Implementation | `code/task06_analysis.py` (§9) |

**Governing rule.** The frozen B3-t procedure is reproduced exactly (§4). Anything beyond it is an extension, marked as such and not described as validated.

**Three tiers, kept separate throughout (r3).**

| Tier | Content | Status |
|---|---|---|
| 1. Validated statistical procedure | B3-t numeric outputs: group onset and offset coefficients with t intervals, angle with B3-t circular interval, Hotelling gate | Validated by simulation only (Task 05), at n = 12, J = 20, complete balanced data. **These are the primary scientific outputs** |
| 2. Descriptive classification rules | S6 labels (§5.2) | **Exploratory descriptive classifications: not validated mechanism identifications.** Provisionally specified; thresholds not validated; retained for traceability |
| 3. Psychological mechanisms | Detection delay, midpoint timing, state or area comparison, attention | **Not identified** by any analysis in this plan |

**What this study is.** An **estimation and feasibility pilot**, with 12 completed participants per condition (OD-02, OD-06).

**What preregistration does and does not mean here.** The within-condition analyses in §6 are preregistered so that they cannot be chosen after seeing the data. They are **not confirmatory claims about the effectiveness** of any presentation condition. No analysis here tests, or can support, a claim that replay or static traces improve temporal perception (claim limit 6).

---

## 1. Scope

- **Primary analysis:** one B3-t analysis per condition (A, B, C), on the 20 main order trials of each analysable participant (D1 §10.2).
- **Not in the primary analysis:**
  - catch trials
  - detection-block trials
  - practice trials
  - invalid presentations
- **Between conditions:** comparisons are **descriptive only** (§7; OD-03).

---

## 2. Data, coding and verified conventions

| Item | Definition | Verification |
|---|---|---|
| Δon | onset(R) − onset(L), in seconds, from the schedule | `stimulus.Trial.d_on` [REC] |
| Δoff | offset(R) − offset(L), in seconds | `stimulus.Trial.d_off` [REC] |
| Response | y = 0 (Right began first), 1 (Same time), 2 (Left began first) | `ordinal_model.simulate_responses`: L when z > τ [REC]. Decided under OD-01 |
| Signed score | s = y − 1 ∈ {−1, 0, +1} | `heterogeneity_methods.b3_individual`: `score = y − 1` [REC]. Unit-tested |
| Design columns | Per participant, the 20 main trials: Δon and Δoff each sum to 0, their squares each sum to 108, and Σ Δon·Δoff = 0 | [DED]; `e1_methods.design()` |

---

## 3. Estimands

### 3.1 Primary (per condition c)

$$\varphi_{\beta,c} = \operatorname{atan2}(\beta^*_{\text{off},c},\ \beta^*_{\text{on},c})$$

β*_c is the population mean of participant-level, expected response-scale slopes of s on Δon and Δoff [REC, closure record §2].

- **Population:** eligible people who are tested in condition c **and meet the analysability criteria**. That makes the target a selected population (§10.4).
- **What kind of angle:** a population-average angle. It need not be any individual's angle.
- **When it is interpreted:** only when the gate passes (§5).
- **Scale:** response scale. In the Task 05 scenarios its relationship to latent cue weighting is a 0.46° angle deviation at most, and a mapping distortion of 2.84° at most on the frozen grid [SIM, DED]. These hold under the Task 05 generator only.

### 3.2 Secondary (descriptive)

1. **Gate status per condition** (Hotelling p).
2. **β*_c components and magnitude** ‖β*_c‖. Response scale, with **no latent perceptual meaning** (claim limit 4).
3. **Descriptive between-condition comparison** (§7).
4. **Level 1 observed performance**, each with a participant-cluster bootstrap interval:
   - correct-leader proportion on onset-only trials
   - "same" proportion on simultaneous trials
   - onset-consistent choice on conflict trials
   - catch error rate
5. **Detection block:** d′ and c per participant, with log-linear correction [REC, Task 03 8.1].
6. **Exclusions:** counts by rule and condition (§10.4).

### 3.3 Not estimated

| Not estimated | Claim limit |
|---|---|
| Individual strategies | 1 |
| Mechanisms | 2 |
| Mixture against intermediate strategy | 3 |
| Latent sensitivity | 4 |
| Population composition | 5 |
| Any benefit of augmentation | 6 |
| Inferential between-condition contrasts | Reviewer decision OD-03 |

---

## 4. Primary procedure: frozen B3-t, reproduced exactly

**Reference implementation.** `e1_methods.run_b3` (SHA-256 `db99b8ba…`), which calls `heterogeneity_methods.b3_individual` (SHA-256 `3cfe209a…`). Both are committed in `research/working/task05/code/`. The wrapper verifies both hashes and imports them **unchanged**. A unit test confirms that the wrapper's output equals a direct `run_b3` call.

For condition c with n analysable participants (n = 12 planned):

1. **Participant slopes.**
   - b_on,i = Σ_t s_it·Δon,t / Σ_t Δon,t²
   - b_off,i = Σ_t s_it·Δoff,t / Σ_t Δoff,t²

   This closed form equals least squares, with or without an intercept, **only** because the complete 20-trial set has zero-mean, orthogonal columns [DED]. A unit test checks the equality.
2. **Group estimate.**
   - m = mean of (b_on,i, b_off,i)
   - S = sample covariance (denominator n − 1)
   - SE = √(diag(S)/n)
3. **Weight intervals:** m ± t(0.975, n − 1)·SE. The frozen code uses the constant t(0.975, 11), which is exact only at n = 12 (§10.3).
4. **Sensitivity gate (Hotelling).**
   - T² = n·mᵀS⁻¹m
   - F = (n − 2)/(2(n − 1))·T², referred to F(2, n − 2)
   - The gate passes if p < 0.05.
   - If S is singular, the gate **fails**. This is unit-tested.
5. **Point angle:** atan2(m_off, m_on), in degrees.
6. **B3-t angle interval.**
   - Draw 2,000 values from N(0, S/n), using `method="svd"`.
   - Scale each draw by 1/√(χ²(n − 1)/(n − 1)).
   - Convert to angles, unwrapped to within ±180° of the point angle.
   - Take the 2.5th and 97.5th percentiles. The endpoints may lie outside ±180°.
7. **Random-number consumption.** `run_b3` draws 2,000 bootstrap resamples (the B3-boot interval) first, then the B3-t draws, from the same generator. The B3-boot interval is stored but **not reported** (§9.3).
8. **Containment.** A reference angle θ (0°, 45° or 90°) is "contained" if [lo, hi] contains θ + 360k for some integer k (`e1_methods.circ_contains`). This is unit-tested across the ±180° boundary.

**No modification** of steps 1–8 is permitted without a recorded amendment and re-validation.

---

## 5. Gate rules, near-zero behaviour and circular boundaries

### 5.1 Reporting

**All conditions' numbers are always reported:** m, SE, weight intervals, gate p, point angle and the B3-t interval, whatever the gate result. Reporting only gate-passing conditions would be selective reporting (§10.4).

**If the gate fails:**

- No strategy statement is made, **no angle-based classification is reported**, and the interval is labelled "not interpretable".
- Gate failure is **not** evidence of inability to perceive onset order.
- Nor is it evidence of a midpoint strategy. It means systematic cue weighting was not detected at this n.
- In A1, the ungated interval covered the true angle in only 0.845 of datasets at a = 0.05 [SIM].

### 5.2 Exploratory descriptive classification (S6 rules, retained for traceability)

**Status (r3): EXPLORATORY DESCRIPTIVE CLASSIFICATIONS: NOT VALIDATED MECHANISM IDENTIFICATIONS.** The labels below must not be used as confirmatory evidence of a perceptual strategy.

- The Task 05 validation of B3-t covers the estimator, intervals and gate. **It does not validate these classification boundaries.**
- The deterministic unit tests establish that the rules are implemented as written. They do not establish that the rules are scientifically valid.
- The thresholds and rule order are unchanged from r2, for traceability. No threshold has been added or changed.

**Reporting requirements:**

- A label is reported only when the gate passes **and** the primary analysis has n = 12 (OD-21, §10.3). It is never reported for add-back analyses (§10.5).
- Every label is reported inside an object that carries:
  - the exploratory status, with `validated: false`, `mechanism_identified: false` and `confirmatory: false`
  - the numeric estimate, the weight intervals, the angle and its B3-t interval, and the gate result
  - an explicit qualification
- A label never appears on its own.
- A unit test walks the full results output to confirm this.

[REC, Task 05 S6. Operationalisation JDG, r2. Implemented in `classify_s6` and `descriptive_classification`; unit-tested.]

The rules are applied in order; the first that matches decides.

| Order | Condition on [lo, hi] | Classification |
|---|---|---|
| 1 | Gate failed | No statement |
| 2 | hi − lo > 60° | Indeterminate |
| 3 | Contains both 0° and 45° | Indeterminate |
| 4 | lo ≥ −10° and hi ≤ 25° | Onset-dominant cue weighting |
| 5 | Contains 45°, excludes 0° | Midpoint-like cue weighting |
| 6 | Contains 90°, excludes 45° and 0° | Offset-dominant cue weighting |
| 7 | Contains −45°, excludes 0° | Rate or duration cue |
| 8 | Otherwise | Numeric description only |

**Permitted wording** is unchanged from S6:

- "Onset-dominant" is compatible with onset timing plus detection delay. Do not write "uses offset information".
- For a midpoint-like result, do not write "judges midpoints".

**The 60° rule (OD-11)** is retained. It only reduces claims. It was not part of E1 or A1.

**Rule 6 is a judgement.** Task 05 S6 says only "about 90°". The containment rule here is my judgement, and the S6 band edges (−10° and 25°) are applied exactly as written.

**Known asymmetry (r3, retained and not corrected).**

- Rule 4 confines onset-dominant intervals to a 35° band.
- Rules 5–7 rest on containment, subject only to the general 60° cap. An interval such as [61°, 119°] is labelled offset-dominant.
- The rule set therefore does not treat the strategy labels symmetrically.
- Correcting this would mean inventing thresholds. Instead the asymmetry is documented, and it is one reason the labels are exploratory.

### 5.3 Near zero sensitivity

From A1 [SIM]:

| a | 0.05 | 0.10 | 0.20 |
|---|---|---|---|
| Gate pass rate | 0.11 | 0.29 | 0.81 |

B3-t false strategy claims were 0.025 to 0.060 across a = 0.05 to 1/3.

### 5.4 Circular boundaries

- Intervals are reported as unwrapped endpoints, with the point angle in (−180°, 180°].
- Containment is always circular. At a = 0, linear containment would have changed 6 of 200 results on the 45° check [SIM, A1].

---

## 6. Pre-specified within-condition questions (not effectiveness claims)

These replace Task 03 H1–H5 (OD-17). For each c ∈ {A, B, C} separately:

**Q1c (sensitivity).** Is β*_c distinguishable from zero?

- Decided by the Hotelling gate at α = 0.05.
- Operating characteristics [SIM]:
  - false positives 0.025 at a = 0 (A1) and 0.056 in S10 (E1)
  - power 0.81 at a = 0.20, and at least 0.995 at a ≥ 1/3

**Q2c (cue weighting, conditional on Q1c).** Is the group cue weighting onset-dominant?

- The expectation comes from Task 03 H4: observers asked about onset weight onset.
- **Status (r3).** Q2c is a pre-specified *descriptive* question. Its outcome is derived from the exploratory classification (§5.2), so it inherits that status. It is **not confirmatory evidence of a perceptual strategy**.
- **When it is not issued:**
  - when the gate fails
  - for exploratory add-back analyses (§10.5)
  - for a primary analysis with n ≠ 12 (§10.3; OD-21)
- Outcome mapping from the §5.2 classification:

| §5.2 classification | Q2c outcome |
|---|---|
| Onset-dominant | **Expectation met** |
| Midpoint-like, offset-dominant, or rate or duration | **Expectation not met** |
| Anything else, or gate failed | **Indeterminate** |

**Multiplicity (OD-02).**

- Each condition's outcome is reported on its own.
- **No family-level claim** is made, such as "at least one condition…", so no family-wise correction is applied.
- No ranking or "best condition" statement is made.

**What these outcomes are not.** They are not tests of whether any condition is better, more accurate or more perceptive than another. An "expectation met" outcome in B or C says nothing about effectiveness relative to A.

---

## 7. Between-condition comparisons: descriptive only (OD-03)

Reviewer decision: no inferential contrasts and no V-C validation at this stage. Implemented in `describe_conditions` and unit-tested.

1. **Side-by-side table** for A, B and C:
   - n
   - gate status
   - point angle
   - B3-t interval
   - the exploratory descriptive classification, with its status (§5.2)
   - Level 1 proportions
   - attention indicators (§8.3)
2. **Point differences of angle** (B − A, C − A, wrapped to ±180°), computed only when both gates pass.
   - **No interval and no test**, and therefore no "significant", "greater" or "improved".
   - Otherwise reported as "not computed".
3. **Labels.** Every comparison is labelled "descriptive only" and given its S5 attention label.

**Interpretation limits.** These apply even to descriptive differences.

- **Scale artefact.**
  - Response-scale compression of intermediate angles depends on sensitivity, by up to 2.84° under the generator [DED].
  - A |difference| of about 3° or less is not read as a latent difference.
- **Gate selection.** A difference exists only when both gates pass (§10.4).
- **Condition C** is graph reading (S8). C − A is not a comparison of two perceptual states.
- **Composition.** In unbalanced samples, conditional coverage fell to 0.84–0.85 [SIM, E1-H2]. The differences between independent groups of 12 partly reflect who was sampled.
- **Non-overlap of intervals** is not used as a test, in either direction.

**Future work.** An inferential comparison would need a validated contrast procedure (r1's V-C proposal, not performed) and probably a larger sample.

---

## 8. Secondary and exploratory analyses

### 8.1 Secondary (pre-specified, descriptive)

1. β*_c, ‖β*_c‖ and gate p per condition, labelled response-scale.
2. Level 1 proportions per condition, with participant-cluster bootstrap intervals (2,000 resamples; seed in §9).
3. Detection d′ and c per condition: mean, SD and bootstrap interval.
4. **Learning and fatigue.**
   - Level 1 proportions, and B3 point estimates, for the first and second halves of the order block.
   - Point estimates only. The closed form is invalid on the unbalanced halves [DED].
5. **Descriptive individual B3 angles:** a histogram per condition, with the statement that 20 trials do not support classifying individuals [REC, S7].
6. Process measures: replay counts (B) and exposure (C).
7. Feasibility criteria F1–F8 (D1 §13).
8. Exclusion counts by rule and condition (§10.4).

### 8.2 Exploratory (labelled, never confirmatory)

- Coding of the strategy reports.
- Participant-level association between d′ and b_on, within condition.
- Catch-anchored lapse-corrected magnitude [REC, S9]. Its SEs understate uncertainty.
- Monte Carlo endpoint stability: 20 auxiliary seeds; flag if any endpoint SD exceeds 1° (§9.4).
- **Add-back numerical sensitivity (§10.5):** B3-t with participants excluded only under X2 or X3 added back. Numbers and differences from the primary analysis only. No classification and no Q2c. Implemented.

### 8.3 Attention reporting rule

[REC, Task 05 S5; tolerances retained, OD-12]

**Indicators**, for each condition:

- catch error rate
- main-trial "same" rate
- first-half against second-half performance

**Labelling.** Any descriptive statement comparing A with B or C is labelled **"attention-inclusive"** unless both of these hold:

- A's catch error rate is within 0.05 of the comparison condition's.
- A's "same" rate is within 0.10 of it.

Otherwise the statement is labelled **"possibly attentional"**.

---

## 9. Reproducibility (OD-05)

### 9.1 Seeds

All seeds use `int(sha256(tag).hexdigest()[:16], 16)`.

| Purpose | Tag |
|---|---|
| Primary analysis, per condition c | `task06-primary-B3t-v1|{c}` |
| Level 1 bootstrap | `task06-L1-boot-v1|{c}` |
| Monte Carlo diagnostic | `task06-mcdiag-v1|{c}|{k}` |
| Exploratory add-back (r3) | `task06-addback-B3t-v1|{c}` |
| Allocation | `task06-allocation-v1` |

The seeds are fixed in the preregistration. **No re-running with other seeds** to obtain a preferred result.

### 9.2 Draws

2,000 B3-t draws, the validated number.

### 9.3 Reported interval

Only B3-t is reported. B3-boot is stored, and choosing between them after seeing the data is prohibited.

### 9.4 Monte Carlo endpoint diagnostic (exploratory)

Optional flag `--mc-diagnostic`. It never changes the primary result.

### 9.5 Software and code

- **Pinned environment:** Python 3.13.16, numpy 2.5.3, scipy 1.18.1, matching Task 05 `config.json`. The wrapper records the environment and whether it matches.
- **Container:** a lock file and container digest are to be recorded in the preregistration.
- **Wrapper:** `code/task06_analysis.py` (revision 3.1), with 41 deterministic unit tests in `code/tests/`. All pass (`code/TEST_RUN.log`).
- **What the tests show:** implementation consistency only. They are not validation of operating characteristics or of the classification rules.
- **Freezing:** the wrapper is to be frozen and hashed in the preregistration after approval.

### 9.6 Tolerances

| Check | Tolerance |
|---|---|
| Re-run in the pinned environment | Identical results, apart from input hashes. Unit-tested for input-order invariance |
| Cross-environment: slopes and covariance | Relative difference ≤ 1e-12 |
| Cross-environment: gate p | Absolute difference ≤ 1e-10 |
| Cross-environment: angle endpoints | Reported, not required to match |

### 9.7 Outputs

**Results JSON** (`json.dump`, sorted keys) contains:

- input hashes, frozen-code hashes, wrapper hash and environment
- exclusions by participant and by rule and condition
- `interpretation_status`: the three tiers above
- per-condition **primary** results (`analysis_id` `PRIMARY-B3T-<c>`):
  - n, seed, participant slopes, m, SE, weight intervals, gate, angle, the B3-t interval, the stored B3-boot interval, containment flags
  - `within_validated_design`, `outside_validated_envelope` (with `envelope_note` when n ≠ 12), departures
  - Q1c
  - the `exploratory_descriptive_classification` object (§5.2)
  - the Q2c object
  - Level 1 proportions
- the descriptive comparison, with labels only inside their exploratory objects
- `exploratory_addback_analyses` (`analysis_id` `EXPLORATORY-ADDBACK-X2X3-<c>`; §10.5)

---

## 10. Missing data, exclusions and selection

### 10.1 Primary

**Complete cases with replacement (OD-04).** Invalid trials are re-queued once (D1 §6.3), so missing main trials should be rare. A participant with any missing main order trial, or fewer than 4 valid catch trials, is excluded (X6) and replaced.

This keeps the closed form exact [DED]. There is no imputation.

### 10.2 Incomplete participants: no analysis (OD-22, r3.1)

**Removed from the initial pilot plan (OD-22, approved 2026-10-10).** The per-participant OLS sensitivity analysis for incomplete participants, specified in r2 and marked not implemented in r3, is removed. It is not implemented and does not appear in the wrapper output.

- Participants excluded under X6 are reported in the exclusion counts only (§10.4). Their data enter no estimate.
- Reasons for removal: re-queue makes X6 rare; the analysis was unvalidated; it would have added a second estimator with untested behaviour.
- Any future reinstatement would need a new specification, implementation, unit tests and authorisation, recorded as an amendment.

### 10.3 n ≠ 12

If an arm closes at its cap with fewer than 12 analysable participants:

- The wrapper recomputes the weight intervals with t(0.975, n − 1) and flags a **departure**. This is unit-tested at n = 11.
- The gate and the B3-t draws already use n.
- Not validated at n ≠ 12. **The adjusted multiplier does not establish validated coverage** (r3 wording, also in the output's departure flag).
- The output marks `within_validated_design: false`.
- When n < 3, the condition is "not computable" (F8 fails).
- **Classification and Q2c suppressed (OD-21, approved 2026-10-10).** Whenever the primary analysis has n ≠ 12 (11 or fewer at the arm cap, or more than 12):
  - The numeric B3-t results are reported in full: coefficients, SEs, weight intervals, gate, angle and B3-t interval, containment flags, Level 1 proportions.
  - The output sets `outside_validated_envelope: true` and gives an `envelope_note` stating that the analysis lies outside the validated operating-characteristic envelope.
  - The exploratory classification object is present with its label withheld and the reason given. Q2c is not issued. Q1c reports the gate result marked "numeric only; outside the validated envelope".
  - Unit-tested at n = 11, 12 and 13, including gate-pass cases.

### 10.4 Selection-bias risks (new in r2)

| Source | Mechanism | Likely direction | Mitigation and reporting |
|---|---|---|---|
| **Replacement of excluded participants** | The analysed sample is restricted to people who pass calibration, catch, attention and timing checks, then topped up to 12. The estimand describes this **selected** population, not all eligible people | Towards higher sensitivity and attentiveness. In simulation, X2 removed 68% of guessing participants and almost no low-sensitivity ones [SIM, Task 05 S4]. Real exclusion behaviour is unknown | Report starters, completers and exclusions by rule and condition. State the analysed population explicitly. Run the exploratory add-back numerical sensitivity analysis (X2/X3 exclusions added back; no classification, no Q2c; §10.5) |
| **Differential exclusion between conditions** | A's 24 s trials may produce more catch and attention failures. The surviving A sample is then more selected than B or C | Comparisons partly reflect different selection, which would inflate A's apparent sensitivity relative to B and C | Exclusion rates by condition are an attention indicator in their own right. Descriptive comparisons carry the S5 label. A large imbalance (more than 2 more X2/X3 exclusions in one arm than another) is flagged [JDG threshold] |
| **Complete-case rule (X6)** | Participants with technical failures are dropped | Depends on whether failures correlate with participant traits (for example, tab switching, which correlates with inattention) | Re-queue limits X6. Visibility and focus events are reported by condition |
| **Re-queue** | Re-queued trials move to the end of the block, after fatigue and learning | Small. Possibly attenuates sensitivity in A | Report re-queue counts and positions by condition |
| **Sensitivity gate** | Interpretation is conditioned on p < 0.05. Estimates from gate-passing conditions are a selected subset (winner's-curse direction: magnitude overstated when power is low) | Magnitude overstated and angle precision overstated near the gate threshold. A1 shows false *strategy claims* stay at 0.025–0.06, but did not assess conditional bias of magnitudes | Report every condition's numbers whatever the gate (§5.1). Never pool or rank gate-passing conditions. Descriptive differences exist only when both gates pass, and say so. Magnitudes are never interpreted (claim limit 4) |
| **Arm closure at different times** | Arms reach 12 at different calendar times | Possible drift in staff, season or recruitment | Report session dates by arm |
| **Recruitment source** | Whoever volunteers for a lab study | Unknown. Limits generalisation | State the source (OD-14 pending). Claim limit 5 |

**The gate and the exclusions together** define *which* population and *which* conditions receive interpretation. The report states this beside every angle.

### 10.5 Exploratory add-back analysis (r3)

**Purpose.** A numerical sensitivity analysis of how much the X2/X3 exclusions change the estimates. Participants excluded **only** under X2 and/or X3 are added back, and only if their order-block data are complete.

| Rule | Implementation |
|---|---|
| Distinct identity | `analysis_id` `EXPLORATORY-ADDBACK-X2X3-<c>`; `analysis_role: exploratory_addback`; `exploratory: true`; separate seed (§9.1); stored separately from the primary results |
| Always exploratory | `within_validated_design: false` and `inclusion_criteria_differ_from_primary: true` **even when n = 12**, because inclusion differs from the validated primary analysis |
| Sample-size departure | `sample_size_departure: true` whenever n ≠ 12. `numeric_status` states that the numbers are unvalidated and that any adjusted t multiplier does not establish validated coverage |
| Reported | n; coefficient estimates, SEs and intervals; gate p; angle and interval, all marked unvalidated; `difference_from_primary` (n, coefficients, angle; no interval, not inferential) |
| Not reported | **No S6 classification** (object present with label withheld and reason given). **No Q2c conclusion** (`issued: false`). No Level 1 proportions |
| Never replaces the primary result | Primary outputs are computed independently. A unit test confirms they are unaffected by the presence of add-back participants |

All rules are unit-tested (D2 §9.5). No stochastic validation was performed.

---

## 11. Sample size (OD-06, decided)

**Decision:** 12 completed (analysable) participants per condition. Estimation and feasibility pilot. **V-N not performed.**

### 11.1 Demonstrated

[SIM, Task 05; n = 12, J = 20, frozen generator]

- **Coverage** of the own target: 0.92–0.98 in every validated scenario outside fixed-composition H2.
- **Discrimination** at a = 0.7 and at (0.35, 0.35): at least 0.998.
- **Gate pass rate by onset weight:**

| a | 0 | 0.05 | 0.10 | 0.20 | 1/3 |
|---|---|---|---|---|---|
| Gate pass rate | 0.025 | 0.11 | 0.29 | 0.81 | 0.995 |

- **False strategy claims:** at most 0.06.

### 11.2 Deduced bridge to observables

[DED, deterministic quadrature; `supporting/model_response_probabilities.json`]

| a | 0 | 0.20 | 1/3 | 0.70 |
|---|---|---|---|---|
| Correct-leader proportion on onset-only trials | 0.28 | 0.41 | 0.50 | 0.73 |

These figures assume τ = 1, bias SD 0.5 and lapse 0.02.

### 11.3 Assumed and untested about humans

- sensitivity in each condition
- τ and bias spread
- heterogeneity and lapse rates
- attention dynamics
- catch-trial ceiling

### 11.4 Consequence [JDG]

- Q1c and Q2c are adequately supported only where group sensitivity is a ≳ 0.2.
- **Condition A is the binding risk.** If A falls below that, A yields "no statement", and the descriptive comparison against A is "not computed".
- This is an accepted outcome for a pilot, and is itself feasibility information.
- Julious (2005) supports 12 per group as a pilot rule of thumb, not as a power calculation [REC via Task 03; not re-reviewed].

---

## 12. Analysis sequencing, blinding and data-quality checks

1. **Exclusions** are applied by `task06_analysis.py exclude`.
   - It reads calibration, attention, frame and viewport summaries, catch responses, and the validity and cell of main trials.
   - It **never reads main-trial responses**. This is unit-tested.
2. **Running data-quality checks**, reported in aggregate only:
   - completion
   - calibration exclusions
   - timing failures
   - re-queue rates
   - task time against the **provisional** 28-minute threshold
   - frame intervals against the **provisional** 100 ms rule

   These checks may trigger the D1 §10.4 pause. They may not change the analysis.
3. **Data lock** when all arms close (hash recorded). Then a single run of `task06_analysis.py analyse` in the pinned environment.
4. **No interim look** at slopes, angles or comparisons.

---

## 13. Deviations and amendments

- **Before data collection:** amendments to the preregistration, time-stamped with a rationale. This includes any E2-driven change to M or rendering, frozen before the first participant.
- **After data:** deviations reported alongside the preregistered analysis, which is always reported.
- **Fixed after data access:** the primary estimand, method, seeds, draw count and S6 operationalisation.
- **Log fields:** ID, date, rule, reason, whether data had been seen, and effect.

---

## 14. Limitations

- **One generator family.** All operating characteristics are simulation findings under one generator family. B3-t was not evaluated under the process-observer, attention or detection-delay generators [REC].
- **Unresolved Monte Carlo margins:** ten from A1 and four from the closure record [REC].
- **Response-scale estimand.** Magnitudes have no latent meaning, and the mapping distortion is at most 2.84° under the generator.
- **Group-level only.** Mixtures cannot be identified, and the sample's composition shifts the angle.
- **Selection:** by exclusions, replacement and the gate (§10.4).
- **Classification rules** are exploratory, not validated, and asymmetric across labels (§5.2).
- **Condition C** indexes graph reading.
- **No inferential between-condition comparison** is made.
- **E2 hardware only.** Results apply only to the lab hardware validated in E2 (D3).
