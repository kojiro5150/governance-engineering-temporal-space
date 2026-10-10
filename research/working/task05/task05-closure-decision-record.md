# Task 05 closure and decision record

- **Status:** DRAFT FOR REVIEWER APPROVAL. Not canonical. Not committed.
- **Date:** 2026-10-10.
- **Scope:** closes Task 05 (statistical robustness and experimental design revision), including E1 and the E1-H2 amendment.
- **Previous reports:** none is altered. This record adds to them; it does not replace them.
- **Evidence labels:**
  - [SIM]: simulation finding.
  - [DED]: mathematical deduction.
  - [JDG]: methodological judgement.
  - [EMP]: empirical evidence. None exists; there are no participant data.

---

## 1. Decision

**B3-t is provisionally accepted as the primary group-level cue-weighting analysis method for Task 06.** This is a reviewer decision, made on 2026-10-10.

| Item | Record |
|---|---|
| Basis | The composite amended evidence: the original E1 criteria outside the fixed-composition H2 scenario, E1e, and the E1-H2 random-membership criteria. B3-t is the only variant meeting all of them at the point estimate, with none clearly outside |
| Original E1 verdict | **REVISE (no variant acceptable). Preserved unchanged** as the record of the frozen E1 run |
| Nature of acceptance | Provisional. Conditional on the claim limits in Section 6 and the outstanding items in Section 9 |
| Scope of acceptance | Group-level mean cue weighting within a condition, at 12 participants and 20 order trials per participant, on the Task 05 design |
| What it is not | Not a method for individual perceptual strategies. Not a method for distinguishing psychological mechanisms |

---

## 2. Selected estimand

**Primary estimand: the strategy angle of β*** [DED].

$$\varphi_\beta = \operatorname{atan2}(\beta^*_{\text{off}},\ \beta^*_{\text{on}})$$

β* is the population mean, over participants, of each participant's expected least-squares slopes of the signed response score on the onset and offset asynchronies:

- **Signed score:** R = −1, S = 0, L = +1.
- **Onset asynchrony:** Δon = onset(R) − onset(L).
- **Offset asynchrony:** Δoff = offset(R) − offset(L).

**Scale:** response scale. β* is a mean of probability-weighted slopes. It is not a latent perceptual weight.

**Secondary quantity:** the magnitude of (β_on, β_off). It is reported descriptively. It has no latent interpretation and must not be compared with B2, B0 or latent-model weights, or across observer models.

**Gate:** the angle is interpreted only if the sensitivity gate passes (Section 3).

**Relationship to latent cue weighting.** These statements hold under the Task 05 generators only [DED, SIM]:

- The angle of β* lies within 0.46° of the angle of the mean latent weights μ_w in every E1 scenario.
- The latent-to-response mapping compresses intermediate angles. The maximum distortion over the frozen mapping grid is 2.84°: a latent 25° maps to 22.3° at onset weight 1.07.
- β* is not the mean latent weight, and its magnitude does not estimate it.

**Interpretation rules (spec S6) are unchanged and apply to φ_β** [DED, SIM]:

| Angle | Reading |
|---|---|
| Up to about 25° | Onset-dominant. This includes onset timing with detection delay |
| About 45° | "Midpoint-like cue weighting". Never "midpoint timing" alone |
| Negative | Rate or duration cue |

**Population target.** Where participants differ in strategy, φ_β is a **population-average** angle. It need not equal any individual's angle (Section 6).

---

## 3. Inference procedure (as validated)

The procedure was validated at n = 12 participants, J = 20 order trials per participant, on the orthogonal 3 × 3 design with s = 3 s. Catch trials are excluded from the slopes. The frozen code is `heterogeneity_methods.b3_individual` and `e1_methods.run_b3`.

1. **Participant slopes.**
   $$b_{\text{on},i} = \frac{\sum_t s_{it}\,\Delta_{\text{on},t}}{\sum_t \Delta_{\text{on},t}^2}, \qquad b_{\text{off},i} = \frac{\sum_t s_{it}\,\Delta_{\text{off},t}}{\sum_t \Delta_{\text{off},t}^2}$$
   - This closed form equals ordinary least squares only because the design columns have zero mean and are mutually orthogonal over each participant's full set of 20 trials [DED].
   - If any order trial is missing or excluded, the closed form is no longer exact. Task 06 must pre-specify how that is handled (Section 9).
2. **Group estimate:** m = the mean over participants of (b_on,i, b_off,i). S = the sample covariance of the participant slopes. SE = √(diag(S)/n).
3. **Weight intervals:** m ± t(0.975, n − 1) × SE, which is t(11) at n = 12.
4. **Sensitivity gate:** a one-sample Hotelling test of m = 0.
   - T² = n·mᵀS⁻¹m, then F = (n − 2)/(2(n − 1))·T², referred to F(2, n − 2).
   - The gate passes if p < 0.05.
   - If it fails, no strategy interpretation is made.
5. **Angle:** atan2(m_off, m_on).
6. **Angle interval (B3-t, amendment AM3):**
   - Draw 2,000 values z ~ N(0, S/n).
   - Divide each by √(χ²(n − 1)/(n − 1)). This gives multivariate t(n − 1) draws around m.
   - Convert the draws to angles and unwrap them around the point angle.
   - The interval is the 2.5th to 97.5th percentiles.
7. **Containment:** whether a reference angle (0°, 45°) lies in the interval is judged by circular containment.
8. **Discrimination claims:** a claim that the interval excludes 0° or 45° is made only when the gate passes.

**Not validated:**

- Other values of n or J.
- Unbalanced or incomplete designs.
- Any covariate adjustment.
- Between-condition contrasts of angles (Section 9).

---

## 4. Evidence

### 4.1 E1 frozen run: 3,500 datasets [SIM]

- **Run conditions:** specification SHA-256 `8a8533ef…d8f`, namespace `task05-E1-v1`, 0 errors.
- **Overall verdict:** REVISE.
- **B3-t:** missed the frozen criteria only in the fixed-composition H2 scenario.

**B3-t coverage of its own target, β\*** (band [0.90, 0.98]; 95% Wilson MC interval):

| Scenario | w_on | w_off | Angle |
|---|---|---|---|
| S01 onset moderate | 0.964 | 0.954 | 0.954 |
| S03 onset high | **0.920** (0.893–0.941) | 0.960 | 0.958 |
| S04 midpoint moderate | 0.964 | 0.954 | 0.964 |
| S13 heterogeneous weights and thresholds | **0.972** (0.954–0.983) | 0.960 | 0.956 |
| H2 fixed 6 + 6 composition | 0.986 | 0.988 | 0.996 (clearly outside) |
| S12 lapses 0.15 | 0.950 | 0.952 | 0.952 |
| S10 guessing | 0.954 | 0.944 | n/a |

Bold marks Monte Carlo-indeterminate values.

**Other B3-t results:**

- **Discrimination:** 500/500 onset datasets passed the gate and excluded 45°; 499/500 midpoint datasets passed and excluded 0°.
- **Guessing false-gate rate:** 28/500 = 0.056 (0.039–0.080). Indeterminate against the maximum of 0.07.
- **Failures:** 0.
- **Bias against β\*:** every |bias| ≤ 0.0014 on target slopes of 0.06–0.29, within about 2 MC SE.

### 4.2 E1-H2 confirmatory amendment: 500 datasets [SIM]

- **Run conditions:** specification SHA-256 `666c0cb5…3745`, frozen before execution. Namespace `task05-E1H2-confirm-v1`. Per-participant Bernoulli(0.5) strategy membership.
- **B3-t coverage of β\*:**

| | Rate | Wilson 95% | Status |
|---|---|---|---|
| w_on | 0.930 | 0.904–0.949 | Clearly inside |
| w_off | 0.922 | 0.895–0.942 | Indeterminate |
| Angle | 0.930 | 0.904–0.949 | Clearly inside |

- **Gate:** 500/500 passed.
- **Failures:** 0.
- **Calibration:** empirical SD exceeded the median SE by about 7%. Coverage sits below nominal but inside the band.

### 4.3 Supporting Task 05 evidence (context; not B3-t-specific)

| Finding | Evidence | Source |
|---|---|---|
| Strategy angle robust to random lapses | Under B0 | Validation C1 [SIM] |
| Angle robust to observer-model misspecification | Within 1°, under B0 | Section 6 of the robustness review [SIM] |
| Onset and midpoint discriminated in homogeneous groups | Under B0 | Validation A [SIM] |
| Mixtures not identifiable from the group mean | | Validation B [SIM]; E1-H2 Section 5 [DED, SIM] |

These analyses used B0 or B2 fits, not B3-t. Their transfer to B3-t is argued from the shared angle estimand and the E1 S12 and H2 results. It was not tested directly [JDG].

---

## 5. Provenance of B3-t

Recorded in order so the selection path is visible.

1. **Task 05 companion specification, Section 2.** It specified B2 and B3, with B3 using a 2,000-resample participant-bootstrap angle interval. Its decision rule was "if both pass, choose B2".
2. **Reviewer conditional approval of E1.** The reviewer required estimand audits and no automatic B2 preference.
3. **Amendments made before freezing, after pre-checks** (AM1–AM7, recorded in the E1 frozen spec). Among them:
   - **AM6** removed the B2 default.
   - **AM3** added B3-t. Pre-check P4 showed the bootstrap interval falsely excluding the true onset angle in 7.5% to 9.0% of datasets at onset weight 0.20–0.33.
4. **E1 frozen run.** No variant was acceptable, so the verdict was REVISE. The H2 over-coverage was diagnosed by an exploratory run (deviation D5). That run is not counted.
5. **E1-H2 amendment.** It was approved, specified and frozen **after** the E1 results were seen. It replaced only the H2 generator, ran on new seeds, and used unchanged criteria bands.
6. **Reviewer decision.** B3-t provisionally accepted on the composite.

**Implication** [JDG]:

- B3-t was not an originally specified method.
- It was introduced in response to an observed weakness.
- It was accepted through a composite that includes a post-results amendment.

New seeds and frozen criteria at each stage limit, but do not remove, the risk that selection was shaped by the results. Section 9 item 2 is the most direct remaining test.

---

## 6. Claim limits (binding for Task 06 unless revised by the reviewer)

B3-t supports **only** statements of this form:

> "In this condition, the population-average response-scale cue weighting has angle φ_β, interval [·, ·], given a passed sensitivity gate."

It does **not** support:

1. **Individual perceptual strategies.** Validation B found individual classification inadequate at 20 trials: 0.774 for onset and 0.429 for midpoint, with about 52 trials needed (spec S7). Individual B3 slopes may be shown descriptively only.
2. **Distinguishing psychological mechanisms.** In particular:
   - onset timing with detection delay versus offset use, for angles up to about 25°
   - midpoint timing versus a mid-ramp state comparison, versus area comparison in condition C, all at about 45°
   - attention failure versus strategy change in condition A
   - graph reading versus temporal recognition in condition C
3. **Mixture versus homogeneous intermediate strategy.** These are not identifiable from the group mean [DED]. In E1-H2, the interval excluded both strategies actually present in about a quarter of datasets.
4. **Magnitude as perceptual sensitivity**, or magnitude comparisons with latent-model estimates.
5. **Representative composition.** A single sample's angle depends on its realised composition. Conditional coverage fell to 0.84–0.85 in unbalanced E1-H2 samples [SIM].
6. **Any claim about human perception**, or that temporal augmentation improves it. No participant evidence exists.

---

## 7. Remaining Monte Carlo-indeterminate margins (B3-t)

| Criterion | Rate | Wilson 95% | Band or limit |
|---|---|---|---|
| E1 S03 weight coverage, w_on | 0.920 | 0.893–0.941 | [0.90, 0.98] |
| E1 S13 weight coverage, w_on | 0.972 | 0.954–0.983 | [0.90, 0.98] |
| E1 S10 guessing false-gate rate | 0.056 | 0.039–0.080 | ≤ 0.07 |
| E1-H2 weight coverage, w_off | 0.922 | 0.895–0.942 | [0.90, 0.98] |

**Pattern** [SIM]: coverage tends to sit below nominal, at 0.92–0.93, at high sensitivity (S03) and in a random-membership mixture. All four margins are inside the band at the point estimate.

---

## 8. Limitations

1. **Simulated observers only.** The generators are the corrected ternary cumulative logit with lapses, heterogeneity and mixture variants. B3-t was not evaluated under:
   - the Validation C process observer
   - attention mechanisms M2a and M2b
   - the detection-delay rule
2. **B3-t behaviour near zero sensitivity is only partly tested.** Pre-check P4 (onset weight 0–0.33) ran before AM3 and evaluated the bootstrap interval, not B3-t. B3-t's performance in the regime that motivated it, onset weight about 0.20–0.33, is inferred from shared construction with B2. It was not measured. S10 (zero sensitivity) and S04 (onset weight 0.35, offset 0.35) are the nearest tested points.
3. **Fixed design.** Validated only at n = 12 and J = 20, with a complete, balanced, orthogonal design.
4. **Interval endpoints are Monte Carlo.** With 2,000 draws, endpoint variability was not quantified. A fixed analysis seed is needed for reproducibility.
5. **Single criterion band**, [0.90, 0.98], throughout.
6. **Gate behaviour.** The gate tests sensitivity, not strategy homogeneity. It passes in mixtures.
7. **Burden and timing** remain model-based (Gate 4).

---

## 9. Outstanding items

| # | Item | Status | Required before |
|---|---|---|---|
| 1 | **E2: physical display validation** (robustness review Section 7.1): frame timing on three or more browser–display combinations; luminance recording of static and dithered discs and ramp onsets, TPDF against none; blinded visibility check with three naive viewers | **NOT YET TESTED** (Gate 5) | Any participant data collection. A failure triggers a rendering revision, not a statistical one |
| 2 | B3-t near-zero sensitivity check: repeat P4 with B3-t, onset weight 0–0.33, about 1,000 datasets, under one minute measured cost | Recommended, **not run**. Needs approval | Freezing Task 06's analysis plan |
| 3 | Missing or excluded order-trial handling: replace the closed form with per-participant OLS on (Δon, Δoff), or a pre-specified exclusion rule | Not specified | Task 06 pre-registration |
| 4 | Fixed analysis seed and draw count for the B3-t angle interval | Not specified | Task 06 pre-registration |
| 5 | Between-condition contrasts (A against B, A against C) of φ_β, including "attention-inclusive difference" labelling (spec 9.2) | Not validated | Task 06 must specify, and may require a targeted check |
| 6 | Re-validation trigger: any change to n, J or design geometry requires re-validation | Rule stated here | Task 06 |
| 7 | Real participant timing and burden | Model-based only | Task 07 |
| 8 | Condition C controls (C-sequential and C-strip) | Deferred | Any temporal-recognition claim for condition C |

---

## 10. Gate and decision-table updates

Each update states the old status and the new one. The originals remain in the robustness review.

| Gate or item | Was | Now |
|---|---|---|
| Gate 2: parameter recovery, heterogeneous | REVISE; replacement method NOT YET TESTED | **PASS, provisional**, for the group-level angle under B3-t (Sections 4 and 7). E1 frozen verdict REVISE preserved |
| Decision table item 4: interval validity under heterogeneity, B0 | REVISE | Unchanged. B0 is not used |
| Decision table item 5: heterogeneity-robust method | NOT YET TESTED | **PASS, provisional (B3-t)** |
| Spec S3: inference choice | "B2 or B3, chosen after E1"; default B2 | **B3-t**. The B2 default was withdrawn (AM6) |
| Gate 5 / item 18: physical display | NOT YET TESTED | **NOT YET TESTED** |
| Item 19: pre-registration | NOT YET TESTED | Task 06 |

All other gates and items (1, 3, 4, 6–17) are unchanged.

---

## 11. Deviations and amendments (consolidated)

| ID | What | When | Effect |
|---|---|---|---|
| D1 | `feasibility_B.b3_truth` sign error fixed; first run superseded and kept | Validation B | None on conclusions |
| D3 | Second C2 calibration target, 0.85, added after the pre-specified 0.60 proved implausible | Validation C | Both reported |
| D4 | M4 check added after seeing C2 | Validation C | Exploratory |
| Workspace | Earlier attempt's `heterogeneity_methods.py` overwritten; unrecoverable | Validation B | Recorded; earlier files not used |
| AM1–AM7 | Estimand separation, B3-t, circular containment, criteria E1a2 and E1e, no B2 default, linear-containment note | Before E1 freeze | Recorded in the E1 frozen spec |
| D5 | Exploratory H2 random-composition run after seeing E1 | After E1 | Not counted; not pooled |
| E1 runtime | 286 s actual against 224 s projected | E1 | None |
| E1-H2 | Post-results amendment; new frozen spec; import-order fix in scratch before freezing | After E1 | Basis of the composite |
| Decision | B3-t provisionally accepted on the composite | Reviewer, 2026-10-10 | This record |

The full log is in `logs/DEVIATIONS.md`.

---

## 12. Recommendation on further simulation [JDG]

Concur with the reviewer's recommendation to stop the simulation cycle.

- **Diminishing returns.** Further optimisation against simulated observers would mostly test assumptions built into the generators, not anything about people.
- **Exceptions:** two narrow checks, each tied to a decision Task 06 must freeze.
  - Item 9.2 (B3-t near zero), because B3-t was introduced to fix exactly that regime and has not been measured there.
  - Item 9.5, only if Task 06 pre-registers a between-condition angle contrast.
  - Both are small and should run only with explicit approval.
- **Next major value:** E2 physical display validation and a pre-registered protocol, followed in due course by participant data.

---

## 13. Canonical record

- **No change to canonical v0.1 is made or required by this record.**
- **On approval,** the recommended placement is `research/working/task05/`, holding the Task 05 reports, E1 and E1-H2 reports and frozen specs, and this record. Raw outputs would be kept as an archive alongside, as for Task 04.
- **Not yet committed.** Placement and commit await approval.

---

## 14. Items for approval

1. Selected estimand and inference procedure (Sections 2 and 3) as the Task 06 primary analysis.
2. Claim limits (Section 6) as binding for Task 06.
3. Gate updates (Section 10).
4. Whether to run item 9.2 before Task 06's analysis plan is frozen.
5. Repository placement and commit (Section 13).

---

## 15. Files

| Content | Path (in `task05/`) |
|---|---|
| Robustness review | `task05-statistical-robustness-review.md` |
| Design specification | `task05-revised-design-specification.md` |
| E1 frozen spec | `results/E1/E1_FROZEN_SPEC.json` and `.md` |
| E1 report | `results/E1/E1_REPORT.md` |
| E1 results | `results/E1/E1_results.json` |
| E1 raw outputs | `results/E1/run/` |
| E1-H2 frozen spec | `results/E1H2/E1H2_FROZEN_SPEC.json` and `.md` |
| E1-H2 report | `results/E1H2/E1H2_REPORT.md` |
| E1-H2 results | `results/E1H2/E1H2_results.json` |
| E1-H2 raw outputs | `results/E1H2/run/` |
| Deviations log | `logs/DEVIATIONS.md` |
| Hash manifest | `logs/TASK05_CLOSURE_SHA256SUMS.txt`: SHA-256 of every file referenced here, taken when this record was prepared |
