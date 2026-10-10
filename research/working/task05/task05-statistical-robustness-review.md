# Research Task 05: Statistical Robustness and Experimental Design Revision

- Programme: Temporal Space in Institutional Reasoning
- Stream: 1, Human Temporal Perception
- Status: Working research document, non-canonical, provisional until reviewed
- Date: 10 October 2026
- Predecessors: Tasks 02, 03 and 04 (all unchanged by this task)
- Boundaries kept: v0.1, Tasks 02 to 04, PHDSS and JARVIS unmodified; no participant-facing application; no recruitment; nothing committed to GitHub

---

## 0. Executive assessment

**Gate recommendation: REVISE.** The experiment can measure group-level cue weighting (onset versus midpoint) robustly against sensitivity differences and random response lapses. It cannot classify individual participants, cannot tell a mixture of strategies from an intermediate strategy, and cannot separate attention-induced state comparison from a genuine cue strategy within real-time observation, except weakly at the condition level. In condition C, its cue weights measure graph-reading features rather than temporal recognition. One analysis component (interval method under participant heterogeneity) has been specified and timed but not validated, by design, pending approval.

Answer to the final decision question, in one line each:

| Claim | Supported? |
|---|---|
| Group-level onset vs midpoint discrimination, strategies homogeneous within condition | **Yes** (simulation, 500 reps) |
| Strategy estimate robust to genuine sensitivity differences and random lapses | **Yes for the strategy angle; no for sensitivity magnitude** |
| Valid intervals when participants differ in sensitivity | **Not with the current Wald method**; two candidates specified, not yet tested |
| Individual-participant strategy classification at 20 order trials | **No** (77% onset, 43% midpoint correct) |
| Mixture of strategies vs intermediate strategy | **No** |
| Attention failures vs strategy in condition A | **Only partially, at condition level**, and not when random lapses co-occur |
| Condition C cue weights as temporal recognition | **No**; they are compatible with static graph-reading proxies |

The smallest defensible revision is mostly analytic: change the primary estimand to the group-level strategy angle with a sensitivity gate, replace Wald intervals with a heterogeneity-robust method, add four pre-specified catch trials, and adopt explicit interpretation limits. Section 9 and the companion file `task05-revised-design-specification.md` give the detail.

---

## 1. Sources, provenance and workspace

### 1.1 Required sources (retrieved and verified)

| Source | Status |
|---|---|
| `research/temporal-space-v0.1.md` | Read. SHA-256 `ba56ce8e…2b543f`, unchanged since Task 04 |
| `research/working/task02-slow-change-temporal-augmentation.md` | Read. SHA-256 `2cc1b99c…bcd`, unchanged |
| `research/working/task03-adversarial-protocol-review.md` | Read. SHA-256 `96c57918…7b`, unchanged |
| `research/working/task04/task04_stage2_artefacts.zip` | Extracted to an isolated folder. SHA-256 `0e73d42d…bcd3`; contents byte-identical to the Task 04 workspace. Code, Stage 2 report and all 1,600 raw fit records inspected |

**Gap recorded.** The repository contains no `task04-prebuild-validation.md`. Task 04 produced audits and Stage 2 but never wrote its gate decisions. Section 7 closes those gates here. Task 04 itself is not modified.

### 1.2 Shared workspace finding

The working folder `/home/claude/task05` already contained material from two earlier, unreviewed Task 05 attempts (01:29–01:35 and 09:50–09:55 today), which this review did not produce:

- None of that material was used as an input.
- One earlier output was used only as an independent check: its 500-repetition core run matches all 4,000 Validation A fits in this review exactly.
- **Collision:** this review's `code/heterogeneity_methods.py` overwrote an earlier file of the same name at 10:02, before the collision was noticed. The earlier version cannot be recovered. Two earlier scripts (`runner.py`, `timing_test_b.py`) import it and will no longer behave as originally written.
- No other earlier file was modified. Details are in `logs/DEVIATIONS.md`.

### 1.3 Evidence labels

- **[SIM]** Simulation finding from code executed in this task (or Task 04 where stated). It depends on the generative assumptions.
- **[DED]** Mathematical deduction, verified numerically where stated.
- **[ASM]** Assumption, for example about observers or timing.
- **[JDG]** Methodological judgement.
- **[EMP]** Published empirical finding (cited in Tasks 02 and 03, not re-verified here).

No statement in this document is an empirical finding about human observers.

---

## 2. Model and notation used throughout

The analysis uses the **corrected** Task 04 parameterisation [DED]. Task 03's form `logit P(r ≥ k) = θ_k − η` with categories R < S < L negates the weights. Fitting one onset dataset gives w_on = −0.698 under that form against +0.698 here, with identical likelihood.

- Responses: R (0) < S (1) < L (2).
- η_ij = w_on·Δon_ij + w_off·Δoff_ij + u_i, with u_i ~ N(0, sd_u²).
- P(r ≤ R) = logistic(θ1 − η) and P(r ≤ S) = logistic(θ2 − η), with θ1 < θ2.
- Δon = onset(R) − onset(L) and Δoff = offset(R) − offset(L), so positive values mean the left disc leads.
- **Strategy angle** φ = atan2(w_off, w_on): 0° onset, 45° midpoint, 90° offset, −45° duration or rate heuristic.
- The Task 03 onset index is not used. It assigns 0.5 to both the midpoint (0.5, 0.5) and the duration heuristic (1, −1), and is arbitrary near zero weights (Task 04 archive, `model_checks.json`) [DED].
- Sensitivity a: the onset-only scale used in Task 04 (0.70 is moderate).

---

## 3. Validation A: core parameter recovery at 500 repetitions

### 3.1 Method

- 8 core scenarios, 20 order trials (2 per non-zero cell, 4 simultaneous), 12 participants, repetitions 0–499.
- Task 04 seeds, fitting code and criteria unchanged. The runner adds only a scenario-subset option.
- 4,000 fits, 259.8 s wall time on 2 workers, 0 errors, 8 unstable fits (0.2%).

**Reproducibility [SIM]:**
- Reps 0–99 reproduce all 800 Stage 2 fits exactly on 10 fields.
- All 4,000 fits are identical to an independent earlier execution on the same seeds.

### 3.2 Results (reps 0–499; Monte Carlo 95% Wilson intervals for coverage)

| Scenario | True (w_on, w_off) | Unstable | sd_u at 0 | Bias w_on/a | Bias w_off/a | Median SE ÷ empirical SD (w_on) | Coverage w_on | Coverage w_off |
|---|---|---|---|---|---|---|---|---|
| S01 onset moderate | (0.70, 0) | 2 | 61 | −0.021 | +0.001 | 1.07 | 0.954 [0.932, 0.969] | 0.944 [0.920, 0.961] |
| S03 onset high | (1.07, 0) | 1 | 77 | −0.027 | −0.003 | 0.92 | **0.922** [0.895, 0.942] | 0.954 [0.932, 0.969] |
| S04 midpoint moderate | (0.35, 0.35) | 0 | 33 | −0.005 | −0.008 | 0.98 | 0.938 [0.913, 0.956] | 0.932 [0.907, 0.951] |
| S06 midpoint high | (0.535, 0.535) | 2 | 46 | −0.018 | −0.011 | 0.95 | **0.920** [0.893, 0.941] | **0.926** [0.899, 0.946] |
| S07 threshold-onset q = 0.2 | (0.56, 0.14) | 0 | 40 | −0.021 | −0.010 | 1.02 | 0.952 [0.930, 0.968] | 0.946 [0.923, 0.963] |
| S08 offset moderate | (0, 0.70) | 3 | 50 | −0.000 | −0.021 | 1.03 | 0.968 [0.948, 0.980] | 0.956 [0.934, 0.971] |
| S09 duration heuristic | (0.35, −0.35) | 0 | 48 | −0.012 | +0.010 | 1.00 | 0.948 [0.925, 0.964] | 0.944 [0.920, 0.961] |
| S11 biased onset | (0.70, 0) | 0 | 2 | −0.034 | −0.003 | 0.95 | **0.924** [0.897, 0.944] | 0.950 [0.927, 0.966] |

Strategy discrimination (95% angle interval, simulation-based):

| Truth | Excludes 0° | Excludes 45° | Covers true angle | Median width |
|---|---|---|---|---|
| Onset moderate (0°) | 0.056 | **1.000** (Wilson lower bound 0.992) | 0.944 | 19.4° |
| Midpoint moderate (45°) | **1.000** (lower bound 0.992) | 0.064 | 0.936 | 24.8° |
| Threshold-onset q = 0.2 (14°) | **0.660** | 1.000 | 0.954 | 22.6° |
| Duration heuristic (−45°) | 1.000 | 1.000 | 0.960 | 24.9° |

### 3.3 Interpretation

1. **Stage 2's only criterion failure was simulation noise** [SIM]. S03 coverage was 0.899 at 100 reps and is 0.922 [0.895, 0.942] at 500.
2. **All 16 coverage point estimates (0.920–0.968) lie inside the pre-specified band [0.90, 0.98].** None is clearly below it. Five are indeterminate, because their Monte Carlo interval straddles a band edge: four at the lower edge (S03 w_on, S06 both, S11 w_on) and one at the upper edge (S08 w_on, upper bound 0.980).
3. **There is a small, consistent anti-conservative pattern** [SIM]. Where sensitivity or bias is high (S03, S06, S11), w_on coverage is 0.920–0.924, and model-based SEs are 5–8% smaller than the empirical SD (ratio 0.92–0.95). This is not a criterion failure, but it is a reason to prefer t-based or cluster-robust intervals (Section 4).
4. **Bias is negligible:** at most 3.4% of a in absolute value. Fit failure is 0.2%.
5. **Random-intercept SD at zero is common** (2–77 of 500 per scenario). It does not affect the weight estimates, but it should be reported, not treated as failure.
6. **Onset versus midpoint discrimination is unchanged and decisive.** Pure onset versus threshold-onset (q = 0.2) remains unresolved: 0.66 at 500 reps against 0.64 at 100.

**Conclusion:** the additional repetitions do not materially change the Stage 2 conclusions. They remove the apparent coverage failure and reveal mild under-coverage at high sensitivity.

---

## 4. Validation B: participant heterogeneity

### 4.1 Approaches specified (before any timing)

| | **B0 Baseline** | **B1 Random slopes** | **B2 Cluster-robust** | **B3 Two-stage summary** | **B4 Participant bootstrap** |
|---|---|---|---|---|---|
| Model | Ternary cumulative logit, random intercepts, marginal ML | B0 plus independent normal random slopes on w_on, w_off; 3-D Gauss–Hermite (7³ nodes) | B0 point estimates | Per participant: least-squares slopes of signed score (R = −1, S = 0, L = +1) on Δon, Δoff (closed form; design orthogonal); then group mean | B0 refitted on participant-resampled data |
| Estimand | Fixed weights of the working model; under unmodelled heterogeneity, an attenuated population-averaged weight | Mean individual latent weights | As B0 | Population mean of individual response-scale cue slopes (not latent weights) | As B0 |
| Key assumptions | Correct model; homogeneous weights | Normal slope distribution; correct link | Independence across participants; enough clusters for the sandwich | Participants independent; the linear score summarises responses | Participants exchangeable; enough clusters |
| Identifiability at 12 × 20 | Weights yes; sd_u often at 0 | Weights yes; **slope SDs weakly identified** | As B0 | Always computable; 20 trials per participant give noisy individual slopes | Resamples can duplicate participants; occasional failed refits |
| Interval | Wald, z = 1.96 | Wald, z = 1.96 | Sandwich H⁻¹MH⁻¹, CR1 factor G/(G−1), t(11) | Mean ± t(11)·SD/√12; angle by participant bootstrap | Percentile |
| Convergence / overfitting risk | Low | Moderate: variance components at bound; 7 parameters on 240 responses | Low; sandwich unstable with very few clusters | None (no iterative fitting) | Low per fit, but many fits |
| Condition comparison | Difference in weights, Wald | Difference in weights, Wald | Difference with robust SEs (Welch-type df) | Difference of group means, Welch t on participant summaries; angle by bootstrap | Bootstrap of the difference |
| Cost per dataset (measured) | 0.053–0.055 s, shared with B2 | 0.78–1.04 s | Included in B0 time | 0.0006 s | 5.1 s per 100 resamples |

B5 (a Bayesian hierarchical model with weakly informative priors, as Task 03 proposed) is specified only. No sampler is installed here and it was not timed.

### 4.2 Small timing and feasibility test (executed; NOT a coverage study)

Setup: 20 datasets per scenario (B1 on 10; B4 on 2 datasets × 100 resamples), 45.0 s in total. Counts below have a Monte Carlo SE of about 0.05–0.07, so they are **indicative only**.

| Scenario | B0 covers w_on | B2 | B3 | B1 | B4 | Notes |
|---|---|---|---|---|---|---|
| H0 homogeneous onset | 19/20 | 19/20 | 18/20 | 9/10 | n/a | B1 slope SDs at lower bound in 6/10 |
| H1 heterogeneous weights and thresholds (Task 04 S13 generator) | **16/20** | 18/20 | 19/20 | 9/10 | 2/2 | B1 recovers slope SD 0.22 for w_on (generator implies ≈ 0.22) but puts w_off slope SD at bound 7/10 |
| H2 mixture: 6 onset + 6 midpoint | 20/20 | 20/20 | 20/20 | 9/10 | n/a | See 4.4 |

One defect was found and corrected during this test: the B3 "truth" function had P(L) wrong, which made the truth zero. The fixed value matches an independent closed form (0.2259 against 0.2258). The first run is superseded and kept (`logs/DEVIATIONS.md`, D1).

### 4.3 Projected cost of a full heterogeneity validation (measured rates)

For 500 reps × 7 scenarios = 3,500 datasets:
- B0 + B2: about 3.2 CPU-minutes.
- B3: under 5 seconds.
- B1: about 50–60 CPU-minutes.
- B4 at 1,000 resamples: about 50 CPU-hours, which is **impractical**. B4 is therefore not recommended as the validated method.

### 4.4 Individual-level identifiability (executed, closed form, 20,000 simulated participants per cell) [SIM]

Classification of each participant's strategy from their own trials, by B3 angle with a guessing-based evidence floor:

| Order trials | Onset moderate: classified onset | Midpoint moderate: classified midpoint (unclassifiable) | Onset low | Midpoint low |
|---|---|---|---|---|
| 20 (specified) | 0.774 | **0.429** (0.386) | 0.227 | 0.089 |
| 28 | 0.894 | 0.615 (0.205) | 0.347 | 0.153 |
| 36 | 0.949 | 0.759 (0.095) | 0.440 | 0.209 |
| 52 | 0.985 | 0.884 (0.017) | 0.630 | 0.338 |
| 68 | 0.995 | 0.939 (0.002) | 0.761 | 0.439 |

**Consequence:**
- At 20 trials, individual strategy classification is not reliable. A mixture of onset and midpoint observers (H2) produces a group angle that B0 reports with confidence as intermediate: B0's interval excluded 0° in 17/20 datasets and 45° in 20/20. B2 and B3 intervals are wider (median 38.4° and 32.2°, against 23.7° for B0), so they make that claim less often.
- The group estimand is therefore **mean cue weighting**, not "the strategy participants used".
- Roughly 52 order trials would be needed for about 88% correct classification of moderate midpoint observers. Under the inherited burden model that is far beyond 30 minutes in condition A (Section 5.4).

### 4.5 Status

- B0 Wald intervals under heterogeneity: **REVISE** (Stage 2: 0.83 coverage; feasibility 16/20).
- B2 and B3: **NOT YET TESTED**. Both are cheap, so a full validation costs minutes.
- B1: possible but slow, with weakly identified variance components.
- B4: not practical to validate.
- **Approval is requested for the validation in Section 11, E1.**

---

## 5. Validation C: lapses, attention and catch trials

### 5.1 Pre-specified catch trials

Specified in `code/catch_trials.py` before any catch-trial simulation was run:

- **Count and placement:** K = 4 per participant, in the order block, one at a random position in each quarter.
- **Cells:** (Δon, Δoff) = (+8, +8) twice and (−8, −8) twice. These are congruent, so onset, offset and midpoint cues all agree.
- **Ramps:** 6 s for both discs, non-overlapping, with a 2 s gap. Same magnitude and trial length (24 s) as main trials. Directions are balanced and crossed with leader side.
- **Timing check** over 2,000 schedules: earliest onset 1.5 s, latest offset 18.5 s, minimum gap 2.0 s [SIM].
- **Use:** excluded from the cue-weight model. Used only to estimate a response-lapse rate and as an exclusion indicator.
- **Burden** (inherited Task 04 model, unchanged assumptions) [ASM]: condition A median 23.0 → 25.4 minutes (90th percentile 26.2); B 12.9 → 14.1; C 14.2 → 15.5. With K = 8, A rises to 27.3 minutes.

### 5.2 Mechanisms distinguished

1. **Independent random response lapses (M1):** a uniform random response with probability λ.
2. **Sustained-attention failures (M2)**, in which a detection falling within a disengaged episode is deferred to re-engagement:
   - **M2a** keeps the deferred timing.
   - **M2b** compares the discs' current states (snapshot) when both detections were deferred to the same re-engagement.
3. **Genuinely low temporal-order sensitivity (M3):** larger timing noise.

All are built on one onset-timing process observer M0 (detection threshold q = 0.1, timing noise σ = 1.2 s, decision band ±1 s, λ = 0.02) [ASM].

### 5.3 C1: is an explicit lapse model identifiable? [SIM]

Setup: linear-weight generator; 100 reps per cell; 3,200 fits; 378 s.

Four fits on each dataset:
- **L0:** standard model.
- **L1:** lapse model, main trials only.
- **L2:** lapse model with catch trials in the likelihood.
- **L3:** two-step, with λ̂ = 1.5 × catch error rate, then fixed.

| Truth | K | Model | Stable | Bias w_on/a | Empirical SD ÷ median SE | Coverage w_on | Angle (median) |
|---|---|---|---|---|---|---|---|
| Onset, λ = 0.15 | 4 | L0 | 100 | **−0.206** | 0.066 / 0.066 | **0.43** | −0.25° |
| | 4 | L1 | 97 | +0.032 | 0.213 / 0.193 | 0.84 | −0.44° |
| | 4 | L2 | 92 | −0.000 | 0.156 / 0.136 | 0.88 | −0.42° |
| | 4 | L3 | 99 | +0.086 | **0.224 / 0.101** | 0.94 | +0.37° |
| | 8 | L2 | **23** | +0.082 | 0.145 / 0.133 | 0.96 | −1.54° |
| | 8 | L3 | 97 | +0.045 | 0.126 / 0.102 | 0.93 | −0.32° |
| Onset, λ = 0.02 | 4 | L2 | 69 | +0.029 | | 0.93 | |
| | 8 | L2 | **11** | +0.041 | | 0.91 | |
| | 4 | L3 | 100 | +0.048 | 0.098 / 0.080 | 0.92 | |
| Midpoint, λ = 0.15 | 4 | L0 | 98 | −0.087 | | 0.81 | **45.4°** |

Findings:

1. **Lapses attenuate sensitivity magnitude but leave the strategy angle intact** (onset −0.25° and midpoint 45.4° at λ = 0.15).
2. **L1 is not identifiable at 20 trials.** Its SEs are about three times L0's, and λ̂ sits at the lower bound in 32% of fits even when λ = 0.15.
3. **L2 has a degenerate second optimum.** An almost deterministic observer (w at the bound of 10) with 25–35% lapses absorbs every error. More catch trials make this worse (11–53% stable at K = 8, against 69–100% at K = 4).
4. **L3 recovers magnitude approximately** at the group level, with small upward bias where catch errors include non-lapse errors (S01: catch error 0.0225 against 0.0133 expected from lapses alone). Its SEs ignore uncertainty in λ̂ and can be half the empirical SD (K = 4).
5. **Per participant, catch trials are too few.** With λ = 0.15, only 39% (K = 4) or 61% (K = 8) of participants make any catch error. Guessing observers make 72% catch errors.

### 5.4 C2: can catch trials distinguish the mechanisms? [SIM]

Setup:
- Each mechanism is calibrated so that the pooled onset slope falls to a fixed fraction of M0's.
- Pre-specified target 0.60: it required implausible parameters (41% random lapses; 57% of time disengaged), and M2b could not reach it even at 92% disengagement.
- A second target of 0.85 was added after seeing this (deviation D3). Both are reported; the table shows 0.85.
- 200 datasets per mechanism; B0 fitted on 100.

Calibrated parameters at 0.85: M1 λ = 0.154; M2a 21% disengaged; M2b 37% disengaged; M3 σ = 2.05 s.

| Mechanism | B0 angle (median) | Angle CI excludes 0° | Catch error rate | Participants with ≥ 1 catch error | "Same" rate, main trials |
|---|---|---|---|---|---|
| M0 reference | 6.2° | 0.34 | 0.013 | 0.05 | 0.268 |
| M1 random lapses | 3.9° | 0.19 | **0.106** | 0.36 | 0.276 |
| M2a attention, deferred timing | 5.3° | 0.25 | 0.075 | 0.27 | **0.384** |
| M2b attention, snapshot | **13.4°** | **0.83** | 0.058 | 0.22 | 0.254 |
| M3 low sensitivity | 4.3° | 0.18 | 0.012 | 0.05 | 0.251 |
| M4 attentive, q = 0.20 (matched angle, exploratory D4) | 14.2° | n/a | 0.013 | n/a | 0.291 |

Separability (the probability that a statistic orders two datasets correctly; 0.5 means no separation):

| Pair | Catch error | "Same" rate | Strategy angle | Catch errors, single participant |
|---|---|---|---|---|
| M1 vs M3 | **0.99** | 0.74 | 0.52 | 0.66 |
| M2a vs M3 | 0.96 | **1.00** | 0.50 | 0.61 |
| M2b vs M3 | 0.90 | 0.53 | **0.92** | 0.58 |
| M1 vs M2a | 0.70 | **1.00** | 0.53 | 0.55 |
| M1 vs M2b | 0.81 | 0.71 | 0.92 | 0.57 |
| M2b vs M4 (genuine strategy) | **0.90** | 0.82 | 0.53 | n/a |

Findings:

1. **At the condition level, catch trials separate random lapses from low sensitivity** (separability 0.99), and the "same" rate separates deferred-attention failures from both.
2. **At the participant level, nothing separates the mechanisms** (0.55–0.66).
3. **Attention failure with snapshot comparison (M2b) is a real confound for strategy.** It shifts the angle from 6° to 13°, and the interval excludes pure onset in 83% of datasets, against 18–34% for the other mechanisms. An attentive observer with a genuine detection threshold q = 0.20 has the same angle. The two differ mainly in catch error rate (5.8% against 1.3%, separability 0.90).
4. **That separation fails when random lapses are also present**, because lapses raise catch errors without moving the angle. The mechanisms therefore cannot be distinguished reliably as a set. This is stated as a limitation, not resolved by catch trials.

### 5.5 Status

- Strategy angle robust to lapses: **PASS** [SIM].
- Explicit lapse model: **STOP** at this allocation (L1 not identifiable; L2 degenerate).
- Catch-anchored magnitude correction (L3): usable only as a sensitivity analysis.
- Catch trials as a condition-level lapse versus low-sensitivity indicator: **PASS**.
- Attention-failure attribution: **REVISE**. The design defence is described in 9.2.

---

## 6. Adversarial scientific review

Results in `results/adversarial_checks.json`, produced by fitting B0 to 400 simulated participants per rule [SIM, DED].

| Possible confusion | Evidence | Status |
|---|---|---|
| **Detection delays read as offset reasoning** | Onset timing with a detection threshold q gives an offset weight of exactly q, deduced as (1 − q, q): fitted angles 2.5°, 6.7°, 14.9° and 23.8° for q = 0.05, 0.1, 0.2 and 0.3, against deduced 3.0°, 6.3°, 14.0° and 23.2°. Pure onset versus q = 0.2 is separated in only 66% of datasets (Section 3) | **Controlled by interpretation rule:** angles up to about 25° are compatible with onset timing plus detection delay and must not be described as offset use |
| **Model misspecification read as perceptual limitation** | A process observer (Gaussian timing, threshold decision) fitted by the logit model recovers its decision geometry within 1°. Magnitudes are not on a common scale across observer models | **Controlled for the angle; unresolved for magnitude.** Do not compare latent "sensitivity" across representations as if it were a perceptual quantity |
| **Attention differences read as temporal-recognition differences** | Section 5.4: snapshot comparison after disengagement moves the angle; deliberate snapshots at 1, 3, 6, 9 and 12 s after the mean onset give angles of 5.7°, 18.0°, **44.3°**, 72.2° and 87.3° | **Unresolved within condition A.** A 45° result is equally compatible with midpoint timing and with a mid-ramp state comparison |
| **Participant heterogeneity read as measurement precision** | B0 coverage 0.83 under heterogeneity (Task 04 Stage 2); B0 reports a confident intermediate angle for a 6 + 6 mixture (Section 4.4) | **Measured; method revision pending (E1).** Mixtures are not identifiable at 20 trials |
| **Static visual reference read as enhanced temporal perception (condition C)** | Graph-reading proxies reproduce every signature: locating each trace's kink gives 0° (onset); "which trace reaches the top first" gives 90°; comparing heights at plot position x = 8 s gives 22°, at x = 12 s gives 59°; comparing area under the traces gives **45°** | **Unresolved.** C's cue weights index graph reading. They cannot show temporal recognition without C-sequential or C-strip controls (Task 03 Part 2.5) |
| Duration or rate cue | Inherent to constant magnitude: in non-zero-onset trials, the onset leader is never the faster ramp (correlation 0.82, Task 04 audit) | **Controlled:** the design separates it (−45°, discriminated in 100% of datasets, Section 3) |
| Lightness quantisation | Section 7, Gate 3 | Computational REVISE; physical NOT YET TESTED |

**No result in this task shows that any representation improves human temporal perception.** Every finding concerns what the measurement method could or could not distinguish, under stated generative assumptions.

---

## 7. Closing the Task 04 gates

| Gate | Decision | Evidence | Residual limitation | Required action |
|---|---|---|---|---|
| **1. Mathematical and statistical validity** | **PASS with corrections** | Task 04 `model_checks.json` (executed): (a) Task 03 sign convention negates weights (−0.698 against +0.698, same likelihood); (b) onset index fails (midpoint and duration heuristic both 0.5); (c) stimulus identities hold exactly; latest order-block offset is **19.5 s**, not Task 03's stated 22.5 s; (d) threshold observer implies weights (1 − q, q) exactly (maximum deviation 8.9e-16) | Corrections must be adopted in the Task 06 specification | Adopt corrected likelihood and angle with sensitivity gate (spec items S1, S2) |
| **2. Parameter recovery** | **PASS (homogeneous); REVISE (heterogeneous); NOT YET TESTED (replacement method)** | Section 3 (4,000 fits, independently reproduced); Stage 2 S13; Section 4 | Mild under-coverage (about 0.92) at high sensitivity; individual-level recovery inadequate | Run E1, then choose B2 or B3 |
| **3. Stimulus generation and computational rendering** | **Stimulus PASS; rendering REVISE** | Task 04 stimulus audit: 200 + 200 schedules, all checks passed, no seed collisions; catch spec checked here. Rendering (Task 04 `render_audit.json`): one 8-bit code step ≈ 0.38–0.41 L*; a ramp spans 25–26 codes. Without dithering, steps arrive every 0.34–0.60 s in A and every 0.04–0.07 s in B. **Task 03's uniform dither changes noise statistics at ramp onset:** post-onset ÷ pre-onset frame-change variance has mean 0.72 (95% range 0.42–1.10), a possible onset cue. Triangular (TPDF) dither: 1.03 (0.58–1.65). Dithered static discs change code on 41–49% of frames (SD about 0.5 code). Task 03's audit criterion "no step larger than one code value under dithering" cannot be met by any dither (2-code steps occur) | Computational only; visibility of dither noise and steps is unknown | Replace uniform with TPDF dither; restate criterion 6.7(5) as a noise-stationarity check (spec S10) |
| **4. Participant burden** | **PASS (model-based)** | Inherited assumptions: A 23.0 min median at 20 order trials; **25.4 min with 4 catch trials**; 27.3 min at 28 trials; 32.1 min at 36 | Response, instruction and break times are assumptions, not measurements; individual-level aims (about 52 trials) are not feasible | Measure real timings in Task 07 |
| **5. Physical display validation** | **NOT YET TESTED** | None | Unknown | Procedure in 7.1 |

### 7.1 Minimal physical-display validation procedure (specified; not executed)

1. **Setup:** three browser–display combinations at minimum, for example Chrome on a Windows laptop panel, Safari on a MacBook, and Firefox on an external 60 Hz monitor. Record the device-pixel ratio, refresh rate and any OS colour-management setting.
2. **Frame timing:** run each condition's stimulus loop for 2 minutes with `requestAnimationFrame` logging. Pass if at least 95% of frame intervals fall within 1.5× nominal (Task 03 F4).
3. **Luminance:** with a photometer if available, otherwise a phone camera in manual exposure mode at 120–240 fps, record (a) static undithered and dithered discs, and (b) ramp onsets, for TPDF dither and none.
   - Pass: no periodic component at the code-step rate in the ramp segments, and no change in frame-to-frame variance at onset beyond the computational range.
4. **Visibility:** three blinded viewers who know nothing of the hypothesis. 20 short clips mixing static dithered discs, static undithered discs and ramp onsets. Ask "did anything flicker or step?"
   - Pass: dithered and undithered static discs are not reported differently above chance.
5. **Record and decide:** record everything as Task 07 evidence. Any failure triggers a rendering revision, not a statistical one.

---

## 8. Decision table (Task 05)

| # | Criterion | Decision | Basis |
|---|---|---|---|
| 1 | Group-level onset vs midpoint discrimination (homogeneous) | **PASS** | [SIM] 500 reps: both directions 1.000 |
| 2 | Weight bias (homogeneous) | **PASS** | [SIM] at most 3.4% of a |
| 3 | Interval coverage, B0 Wald (homogeneous), pre-specified band [0.90, 0.98] | **PASS** (5 of 16 Monte Carlo-indeterminate; about 0.92 at high sensitivity) | [SIM] |
| 4 | Interval validity under heterogeneity, B0 | **REVISE** | [SIM] 0.83 (Stage 2), 16/20 |
| 5 | Heterogeneity-robust interval method (B2 or B3) | **NOT YET TESTED** | Specified and timed only |
| 6 | Individual participant strategy classification at 20 trials | **STOP** for this design | [SIM] 0.77 / 0.43; about 52 trials needed |
| 7 | Mixture vs intermediate strategy | **STOP** (not identifiable) | [SIM] Section 4.4 |
| 8 | Strategy angle robust to random lapses | **PASS** | [SIM] C1 |
| 9 | Sensitivity magnitude robust to lapses | **REVISE** (secondary, with L3 sensitivity analysis only) | [SIM] −21% bias |
| 10 | Explicit lapse model identifiable at 20 (+4/8) trials | **STOP** | [SIM] L1 imprecise; L2 degenerate |
| 11 | Catch trials: lapse vs low sensitivity, condition level | **PASS** | [SIM] separability 0.99 |
| 12 | Catch trials: any mechanism, participant level | **STOP** | [SIM] 0.55–0.66 |
| 13 | Attention failure vs genuine strategy (condition A) | **REVISE** (partial: condition-level catch error 0.90 only without concurrent lapses) | [SIM] Section 5.4 |
| 14 | Detection delay vs offset reasoning | **PASS with interpretation rule** | [DED, SIM] |
| 15 | Angle robust to observer-model misspecification | **PASS** (within 1°) | [SIM] |
| 16 | Condition C cue weights as temporal recognition | **REVISE** (claims restricted; controls needed later) | [SIM] proxies |
| 17 | Participant burden with 4 catch trials | **PASS (model-based)** | [ASM] 25.4 min |
| 18 | Physical display | **NOT YET TESTED** | None |
| 19 | Pre-registration | **NOT YET TESTED** (Task 06) | n/a |

---

## 9. Revised design (summary; full specification in the companion file)

### 9.1 Changes

| ID | Change | Basis |
|---|---|---|
| S1 | Corrected likelihood and sign convention (Section 2) | [DED] Task 04 |
| S2 | **Primary estimand:** group-level strategy angle φ per condition, interpreted only if a sensitivity gate passes (joint test of w_on = w_off = 0 rejects at 0.05). Magnitude is secondary | [SIM] C1 and C2: angle robust, magnitude not |
| S3 | **Inference:** B2 (cluster-robust, t(11)) or B3 (two-stage), chosen after E1. Not B0 Wald | [SIM] Section 4 |
| S4 | **Four catch trials** per participant, as specified in 5.1. Exclusion if 3 or more of 4 are wrong | [JDG], informed by C1; see the companion file for operating characteristics |
| S5 | Condition-level attention indicators reported alongside every condition contrast: catch error rate, "same" rate, first vs second half of block | [SIM] C2 |
| S6 | **Interpretation rules:** angle ≤ about 25° = onset-dominant (includes detection delay); about 45° = "midpoint-like cue weighting" (midpoint timing, mid-ramp state comparison, or area comparison in C), never "midpoint timing" alone; negative angles = rate or duration cue | [DED, SIM] Section 6 |
| S7 | **No individual classification.** Individual B3 angles are reported descriptively only; claims stay at group mean cue weighting | [SIM] 4.4 |
| S8 | **Condition C claims restricted** to graph-reading performance until C-sequential or C-strip controls exist | [SIM] Section 6 |
| S9 | Explicit lapse model removed; catch-anchored magnitude correction (L3) is a labelled sensitivity analysis | [SIM] C1 |
| S10 | TPDF dither replaces uniform dither; audit criterion restated | [SIM] Task 04 rendering |
| S11 | Corrected timing statement (latest offset 19.5 s) | [DED] |

### 9.2 Defence against attention confounding (smallest defensible option)

Catch trials cannot attribute attention failures reliably (5.4). The defensible response is an analysis and reporting rule, not a new instrument:

- Contrasts between A and B, or A and C, in strategy angle are reported as **"attention-inclusive differences"** unless A's catch error and "same" rate are within pre-specified tolerances of the comparison condition.
- If they are not, the contrast is labelled "possibly attentional".
- This accepts, explicitly, that real-time observation combines attentional and temporal limits. That is consistent with the bottleneck taxonomy in the Stream 1 literature scan.

An attention-specific probe (for example, slow transient "bump" trials) was considered. It is not recommended, because in the process model its discriminating power would follow from how the model was built rather than from any evidence [JDG].

---

## 10. Answer to the final decision question

> Can the proposed experiment reliably distinguish temporal-recognition strategies without confounding them with participant sensitivity, lapses or sustained-attention failures?

**Partly.**

**Supported, under these conditions** [SIM]:
- Strategies are assessed at the **group level**, as mean cue weighting.
- Strategies are reasonably homogeneous within a condition.
- The **angle**, not magnitude, is the estimand.
- The sensitivity gate passes.
- Intervals come from a heterogeneity-robust method that still needs validating (E1).

Under these conditions, onset-weighted and midpoint-weighted cue use are distinguished decisively, and the distinction is robust to genuine sensitivity differences and random lapses.

**Not supported:**
- Individual-level strategy claims.
- Separating mixtures from intermediate strategies.
- Attributing angle shifts in condition A to strategy rather than attention when lapses also vary.
- Reading condition C cue weights as temporal recognition.

**Smallest scientifically defensible revision:** S1–S11. These are analytic changes, four catch trials (about +2.4 minutes in A) and explicit claim limits. **No increase in order-trial count** is recommended. More trials would help individual classification only at about 52 trials, which is not feasible in condition A within 30 minutes.

---

## 11. Minimum further evidence before Task 06

**E1 (requires approval). Heterogeneity validation of B2 and B3** at 20 order trials and 12 participants. The full specification is in the companion file.
- Scope: 500 reps × 7 scenarios (S01, S03, S04, S13 heterogeneity, the H2 mixture, S12 with λ = 0.15, and S10 guessing) = 3,500 datasets.
- Measured cost: about 3–4 CPU-minutes, so under 5 minutes of wall time. B1 can be added at about 30 minutes of wall time on 2 cores.
- Pre-specified criteria:
  - Coverage of each method's own estimand in [0.90, 0.98] in all scenarios.
  - Onset vs midpoint discrimination ≥ 0.80.
  - Guessing false-gate rate ≤ 0.07.
- Decision rule: choose the method passing all criteria; if both pass, choose B2 (latent-scale estimand); if neither passes, return to REVISE.

**E2. Physical display validation** (7.1). Not computational.

**E3. Pre-registration** in Task 06. Items listed in the companion file.

Not needed: larger allocations, more Validation A repetitions, or a full B4 bootstrap validation.

---

## 12. Deviations and limitations

**Deviations** (`logs/DEVIATIONS.md`):
- **D1:** B3 truth bug fixed; first feasibility run superseded and kept.
- **D3:** a second C2 calibration target (0.85) added after the pre-specified 0.60 proved implausible.
- **D4:** the M4 check was exploratory, added after seeing C2.
- **Workspace:** the file-name collision described in 1.2.

**Limitations:**
- All observers are simulated. The process observer, catch-trial accuracy and burden timings are assumptions.
- Heterogeneity methods were not validated (by instruction).
- C2 compares mechanisms at matched loss of onset slope. Other matching choices could change separability.
- The C1 linear generator extrapolates to catch trials at Δ = 8 s.
- Every coverage criterion uses a single band, [0.90, 0.98].

---

## 13. Reproducibility and file inventory

- `config.json`: commands, seed namespaces, code hashes and measured wall times.
- `code/README_TASK05.md`: how to run each step.
- `results/validationA/`: checkpointed run (80 batches), `fits.csv`, `summary.json`, `validationA_analysis.json`.
- `results/validationB/`: feasibility rows and summary (current and superseded), `individual_identifiability.json`.
- `results/validationC/`: `lapse_catch.jsonl` (800 jobs), `C1_analysis.json`, C2 calibration, datasets and summaries for both targets, M4 check.
- `results/adversarial_checks.json` and `results/burden_with_catch.json`.
- `logs/`: run logs, `DEVIATIONS.md`, `inherited_code_sha256.txt`.

Total measured compute for this task: about 16 minutes of wall time on 2 cores. No single run exceeded 6.5 minutes.
