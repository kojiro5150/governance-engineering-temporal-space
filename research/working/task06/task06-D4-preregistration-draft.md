# Task 06 D4: Preregistration Draft (revision 3.1)

| Field | Value |
|---|---|
| Status | **Draft. Not submitted.** Cannot be submitted until the dependencies in §0 are resolved |
| Revision | r3.1, 2026-10-10. OD-21 and OD-22 decided. Changes are listed in `task06-CHANGELOG-r3-to-r3.1.md` (earlier: `task06-CHANGELOG-r2-to-r3.md`) |
| Template | OSF Preregistration form (v1). Section and item titles were checked against the form's reproduction in the `preregr` R package documentation ([Form: OSF Prereg form (v1)](https://ftp.fau.de/cran/web/packages/preregr/vignettes/form_OSFprereg_v1.html)) |
| Registry | OSF Registries, after E2 and ethics approval (OD-15) |
| Governing documents | D1 (protocol) and D2 (analysis plan) govern if anything here differs from them |

## 0. Dependencies before submission

| Dependency | Status |
|---|---|
| Ethics: an eligible institution and review process identified, and approval obtained (OD-14) | **OPEN.** No eligible pathway yet identified |
| E2 passed on every laboratory testing station (D3) | Not yet tested |
| M frozen after E2 (D1 §3.2) | Pending E2 |
| Provisional thresholds confirmed and frozen: the 100 ms per-trial rule (E2 M1) and the 28 min burden threshold (staff dry runs) | Pending |
| Analysis wrapper frozen and hashed; tests pass | Wrapper (r3.1) and 41 deterministic tests written; all pass. Not frozen |
| Allocation sequence and participant-seed list generated, collision-checked and hash-committed | Not generated |
| Container image digest recorded | Not built |

---

## 1. Study information

**Item 1. Title.** "Group-level cue weighting in onset-order judgements of slow lightness changes under real-time, compressed-replay and static-trace presentation: an estimation and feasibility pilot."

**Item 2. Authors.** Sam Hayward, Governance Engineering. Other contributors are to be confirmed. A conflict-of-interest statement is in item 25.

**Item 3. Description.**

- **Task.** Participants judge which of two discs *began* changing first. Both discs undergo slow linear lightness changes, and onset and offset asynchronies are crossed orthogonally (3 × 3).
- **Conditions.** Three independent groups see the same stimulus schedules:
  - (A) in real time (24 s)
  - (B) as an 8× compressed replay (3 s)
  - (C) as static lightness-over-time traces
- **What is estimated.** For each condition, the population-average, response-scale cue-weighting angle φ_β. It is interpreted only if a sensitivity gate passes.
- **Study type.** An **estimation and feasibility pilot**.
- **Status of the within-condition analyses.** They are preregistered to prevent analytic flexibility. They are **not confirmatory claims about the effectiveness** of any presentation.
- **Between conditions.** Comparisons are descriptive only.
- **What the study cannot do.** It does not test whether any presentation improves human temporal perception, and it cannot identify individual strategies or psychological mechanisms.
- **Validation.** The B3-t analysis method has been validated by simulation only (Task 05, commit `7a65782c`).

**Item 4. Hypotheses.** The study pre-specifies two within-condition questions per condition c ∈ {A, B, C}, with fixed decision rules (D2 §6).

- **Q1c (sensitivity).** Is the population mean response-scale slope vector β*_c distinguishable from zero? Decided by a one-sample Hotelling T² gate at α = 0.05.
- **Q2c (cue weighting, only if the Q1c gate passes and n = 12; OD-21).** Is cue weighting onset-dominant? The expectation comes from Task 03, which held that observers asked about onset weight onset.
  - **Status:** a pre-specified *descriptive* question. Its outcome is read from the D2 §5.2 **exploratory descriptive classification** of the 95% B3-t interval. Those classification rules are not validated, so the outcome is **not confirmatory evidence of a perceptual strategy**.
  - **Primary outputs:** the numeric B3-t estimates, intervals and gate result. They are reported with every Q2c outcome.
  - **Mapping:**

| Classification of the interval | Q2c outcome |
|---|---|
| Onset-dominant (within −10° to 25°) | Expectation met |
| Midpoint-like, offset-dominant, or rate or duration | Expectation not met |
| Gate failed, interval wider than 60°, contains both 0° and 45°, or numeric description only | Indeterminate |

There are no hypotheses about differences between conditions, and no claim of effectiveness.

---

## 2. Design plan

**Item 5. Study type.** Experiment. Presentation condition is randomised between subjects; asynchrony is manipulated within subjects.

**Item 6. Blinding.**

- Participants are not told the hypotheses or the other conditions.
- Session staff see the allocation only at session start.
- Exclusions are applied by script without reading main-trial responses. This is unit-tested (D2 §12).

**Item 7. Additional blinding.** The allocation sequence is concealed and hash-committed.

**Item 8. Study design.**

- **Between subjects:** condition A, B or C.
- **Within subjects:** 20 main order trials over 9 (Δon, Δoff) cells, s = 3 s, direction balanced.
- **Other trials:** 4 catch trials (Δ = ±8 s, congruent); 12 detection trials; 10 calibration trials; 3 practice trials.
- **Response:** ternary only. No confidence rating.
- **Setting:** supervised laboratory, only on testing stations that have individually passed E2.
- **Full specification:** D1 §3–§5.

**Item 9. Randomisation.**

- **Conditions:** permuted blocks of 6, from a seeded PRNG, hash-committed.
- **Trial order:** per participant, from the seeded mulberry32 stream.
- **Catch trials:** one per quarter of the order block (D1 §6).

---

## 3. Sampling plan

**Item 10. Existing data.** Registration before any data is created.

**Item 11. Explanation of existing data.** Only simulated data exist (Tasks 04 and 05).

**Item 12. Data collection procedures.**

- **Setting:** supervised laboratory sessions on E2-validated stations.
- **Recruitment source and institution:** **OPEN** (OD-14).
- **Eligibility:**
  - aged 18 or over
  - normal or corrected-to-normal vision
  - no history of photosensitive epilepsy
  - able to give informed consent
- **Reimbursement:** to be decided with the ethics pathway.

**Item 13. Sample size.**

- 12 completed (analysable) participants per condition, 36 in total.
- Cap of 24 starters per condition.

**Item 14. Sample size rationale.**

- **Basis:** a feasibility rule of thumb for pilots (Julious, 2005, cited in Task 03). **Not a power calculation.**
- **Simulated operating characteristics of B3-t at n = 12, J = 20** (Task 05; D2 §11):

| Onset weight a | Gate pass rate |
|---|---|
| 0 | 0.025 |
| 0.20 | 0.81 |
| 1/3 | ≥ 0.995 |

- **Other simulated results:** false strategy claims ≤ 0.06.
- **Unknown for humans:** sensitivity in each condition, the width of the "same" band, heterogeneity and lapses.
- **Condition A risk:** condition A may yield no strategy statement. That is accepted as a pilot outcome.

**Item 15. Stopping rule.**

- Each arm stops at 12 analysable participants or 24 starters.
- No outcome-dependent stopping and no interim analyses.
- Technical and safety pauses as in D1 §10.4.

---

## 4. Variables

**Item 16. Manipulated variables.**

- Condition (A, B, C).
- Δon ∈ {−3, 0, +3} s and Δoff ∈ {−3, 0, +3} s.
- Direction (lighter or darker), balanced.

**Item 17. Measured variables.**

- Order response (left began first / same time / right began first), coded y ∈ {0, 1, 2} = {R, S, L}.
- Response time from enablement.
- Catch responses.
- Detection responses: per disc, changed yes/no.
- Calibration accuracy.
- Process measures: replays in B, exposure in C, frame timing, visibility events, station ID.
- Attention check; free-text strategy report.

**Item 18. Indices.**

- **Signed score:** s = y − 1.
- **Participant slopes** on the complete 20-trial set:
  - b_on = Σ s·Δon / Σ Δon²
  - b_off = Σ s·Δoff / Σ Δoff²
- **Detection:** d′ and c, with log-linear correction.
- **Catch error rate.**
- **Level 1 proportions:**
  - correct leader on onset-only trials
  - "same" on simultaneous trials
  - onset-consistent choice on conflict trials

---

## 5. Analysis plan

**Item 19. Statistical models.**

- **Primary, per condition:** B3-t, reproduced exactly from the frozen Task 05 code (`e1_methods.run_b3`, SHA-256 `db99b8ba…`), through the wrapper `task06_analysis.py`, whose hash is to be recorded:
  - group mean and covariance of participant slopes
  - t(n − 1) weight intervals
  - Hotelling gate F(2, n − 2)
  - point angle atan2(m_off, m_on)
  - B3-t angle interval from 2,000 multivariate t(n − 1) draws, 2.5th to 97.5th percentiles
  - circular containment
  - **reported separately as exploratory:** the S6 descriptive classification (D2 §5.2). It is marked "exploratory descriptive classification: not a validated mechanism identification", is withheld when the gate fails or the primary analysis has n ≠ 12 (OD-21), and is always accompanied by the numeric estimate, interval and gate result
- **Secondary (descriptive):**
  - magnitudes, response-scale only
  - Level 1 proportions, with participant-cluster bootstrap intervals
  - d′ and c
  - first-half against second-half point estimates
  - descriptive individual angles
  - attention indicators and S5 labels
  - exclusions by rule and condition
- **Between conditions: descriptive only.** A side-by-side table, plus point differences of angle (B − A, C − A) when both gates pass. There are no intervals and no tests. Differences of 3° or less are not read as latent differences.

**Item 20. Transformations.**

- Angles are in degrees, with point angles in (−180°, 180°].
- Interval endpoints are unwrapped around the point angle.

**Item 21. Inference criteria.**

- Q1c: gate p < 0.05.
- Q2c: the D2 §5.2 exploratory classification rules. These are descriptive, not an inference criterion for any perceptual strategy.
- Each condition is reported separately. There is no family claim and therefore no family-wise correction. No condition is ranked.
- Strategy statements, and any angle-based classification, are prohibited when the gate fails. Classification and Q2c are also suppressed for a primary analysis with n ≠ 12, whose numeric results are reported and flagged as outside the validated envelope (OD-21; D2 §10.3).
- **All numbers are reported for every condition, whatever the gate result.**

**Item 22. Data exclusion.**

| Rule | Exclude when |
|---|---|
| X1 | Calibration below 9/10 |
| X2 | 3 or more catch trials wrong |
| X3 | Failed attention check |
| X4 | Fewer than 95% of frames within 1.5× nominal |
| X5 | Viewport below 900 CSS px |
| X6 | Any missing main order trial after one re-queue, or fewer than 4 valid catch trials |
| X7 | Withdrawal |

- **How applied:** by script, before outcomes are computed, without reading main responses.
- **Replacement:** excluded participants are replaced.
- **Selection risks:** listed and reported as in D2 §10.4.

**Item 23. Missing data.**

- **Design:** technically invalid trials are re-queued once. The per-trial rule (a frame interval over 100 ms, or a loss of visibility or focus) is **provisional** until E2.
- **Analysis:** complete cases only, with replacement.
- **Incomplete participants:** no analysis. Participants excluded under X6 appear in the exclusion counts only. The previously proposed OLS sensitivity analysis is removed from the plan (OD-22).

**Item 24. Exploratory analysis.**

- strategy-report coding
- association between d′ and slopes
- catch-anchored lapse-corrected magnitude
- Monte Carlo endpoint stability over 20 auxiliary seeds
- add-back numerical sensitivity: participants excluded only under X2 or X3 added back
  - separate analysis ID
  - reported numbers, marked unvalidated, plus differences from the primary analysis
  - no classification and no Q2c
  - exploratory even when n = 12 (D2 §10.5)

---

## 6. Other

**Item 25. Other.**

### (a) Claim limits

These six limits are binding and carried from the Task 05 closure record §6. This study will not claim:

1. identification of individual perceptual strategies
2. identification or separation of psychological mechanisms from the group angle
3. discrimination of mixtures from homogeneous intermediate strategies
4. latent perceptual meaning for B3-t magnitudes
5. that sample composition represents the population
6. any empirical benefit of temporal augmentation

### (b) Explanations the study cannot separate

- onset timing with detection delay versus offset use
- midpoint timing versus mid-ramp state comparison
- midpoint timing versus area comparison (C)
- attention failure versus strategy change
- graph reading versus temporal recognition (C)

### (c) Condition C

C is reported as "recognition of onset order from a static trace display".

### (d) Feasibility criteria

F1–F8 as in D1 §13. F3 is task time ≤ 28 min in A, **provisional**.

### (e) Reproducibility

- Seeds: `task06-primary-B3t-v1|{A,B,C}` and the related seeds in D2 §9.
- 2,000 draws.
- Pinned environment: Python 3.13.16, numpy 2.5.3, scipy 1.18.1, with the container digest.
- Hashes are checked at run time for the frozen code and the wrapper.
- The data lock is recorded by hash.

### (f) Deviations

- Before data: time-stamped amendments.
- After data: deviations reported alongside the preregistered analysis.
- Fixed after data access: the primary estimand, method, seeds, draws and the exploratory classification rules, which are kept for traceability and not validated.

### (g) Conflict of interest

The author leads Governance Engineering, the organisation conducting this research programme. Disclosure wording is to be finalised.

---

## 7. Data and code sharing (proposed)

- **Data:** de-identified trial-level data and session summaries after the analysis lock. Free-text strategy reports are reviewed for identifying content first.
- **Code:** the analysis wrapper with its tests, plus the frozen Task 05 modules, with hashes.
- **E2 records:** included.
- **Consent:** sharing wording must be in the consent form and approved by the reviewing body.

---

## 8. Ethics, consent, privacy and withdrawal (OD-14: OPEN)

**The ethics pathway is unresolved.** No eligible institution or review process has been identified. This draft does not assume one, and it does not assume the study is exempt. Recruitment, the E2 visibility viewers (D3 M4) and data collection all wait on it.

### Framework

Australian human research is governed by the NHMRC *National Statement on Ethical Conduct in Human Research*. Its 2023 update took effect on 1 January 2024. It assesses risk on a continuum and makes review processes an institutional responsibility ([NHMRC FAQ](https://nhmrc.gov.au/research-policy/ethics/national-statement-ethical-conduct-human-research/2023-update-faqs)).

**Which body reviews the study, and at what risk level, is for the eligible institution and its review process to determine.**

### Consent

The written information statement covers:

- purpose, without hypotheses
- procedures and duration: about 35 minutes in A, including consent. This is an estimate.
- risks: visual fatigue, and possible flicker sensitivity from low-amplitude luminance noise (E2 pending)
- voluntariness and withdrawal
- data handling and sharing
- contacts and complaints

Consent is recorded before the task starts.

### Eligibility and safety

- People with photosensitive epilepsy are excluded as a precaution.
- Any discomfort ends the session.

### Withdrawal

- During the session: at any time, without giving a reason and without loss of reimbursement.
- After the session: until the analysis lock date, using the participant code.
- After the lock: de-identified data cannot be singled out. The consent form states this.

### Privacy

- **Minimal data:** age band, vision status, task data, device and station data. No names in the task data.
- Consent records are stored separately from the task data.
- Storage is secure, with access limited to named researchers.
- **Applicable privacy law:** for example the *Privacy Act 1988* (Cth) and the Australian Privacy Principles, where they apply. Applicability has **not been assessed** and must be confirmed through the eligible institution.
- **Retention:** as that institution requires.

### Debrief

After the session, a short explanation of the aim and the other conditions, with a contact for questions.
