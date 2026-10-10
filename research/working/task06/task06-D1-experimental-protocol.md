# Task 06 D1: Experimental Protocol

| Field | Value |
|---|---|
| Programme | Temporal Space in Institutional Reasoning. Stream 1, Human Temporal Perception |
| Status | **Working draft for independent review.** Not canonical, not committed, not preregistered |
| Revision | r3.1, 2026-10-10. Consistency edits only, for OD-21 and OD-22 (see `task06-CHANGELOG-r3-to-r3.1.md`). r3: consistency edits for corrections A and B (see `task06-CHANGELOG-r2-to-r3.md`). r2 applied the reviewer decision of 2026-10-10 (OD-01 to OD-20 adopted; OD-14 open; see `task06-CHANGELOG.md`) |
| Proposed home | `research/working/task06/` |
| Baseline | `main` at `7a65782cff793638efd19eaa6e9833d2a33a7c69`, verified 2026-10-10 |
| Authority | Task 06 brief. Protocol development only. No build, no deployment, no recruitment, no data, no simulation |
| Companions | D2 (analysis plan), D3 (E2 display validation), D4 (preregistration draft), D5 (decision register), D6 (traceability) |

**Labels**

| Label | Meaning |
|---|---|
| [REC] | Taken from the committed record. D6 gives the source |
| [DED] | Mathematical deduction |
| [SIM] | Task 05 simulation finding |
| [JDG] | Methodological judgement made here |
| [SG] | Specification gap: the record is silent and a value is proposed here |
| **OD-xx** | Decision in the D5 register. Only OD-14 remains open in r2 |

---

## 1. Purpose and what the study can establish

**Question.** Do the three presentation conditions (A real time, B 8× replay, C static traces) produce distinguishable **group-level, response-scale cue-weighting patterns** in judgements of which of two slowly changing discs began changing first?

The study keeps four levels apart. Evidence at one level does not establish the next.

| Level | What is measured or claimed | Supported by this design? |
|---|---|---|
| 1. Observed task performance | Response proportions per cell; catch accuracy; detection d′ | Yes, descriptively |
| 2. Group-level cue weighting | Population-average response-scale angle φ_β per condition, behind a sensitivity gate | Yes, within each condition: the numeric estimates, intervals and gate are validated by simulation only (Task 05 E1, E1-H2, A1). Strategy labels are **exploratory descriptive classifications, not validated mechanism identifications** (D2 §5.2). Between conditions: descriptive only |
| 3. Candidate psychological mechanisms | Detection delay, midpoint timing, mid-ramp state comparison, area comparison, attention | **No.** Section 9 lists what is not separable |
| 4. Claims about human temporal perception or augmentation benefit | "Representation X improves perception" | **No.** Not supported by this study |

**Study type.** An estimation and feasibility pilot. Its within-condition analyses are preregistered (D2 §6). They are **not confirmatory claims about the effectiveness** of any condition, and no comparison between conditions is inferential (D2 §7).

Canonical v0.1 (Section 4.15) separates temporal visibility, comprehension and agency. At most, this study addresses an operational precursor of *visibility* for one narrow relationship: the onset order of two slow, linear lightness changes [JDG].

---

## 2. Design summary

| Element | Specification | Source |
|---|---|---|
| Design | Three independent groups, between subjects | [REC] Task 03 5.2 |
| Sample | 12 **completed (analysable)** participants per condition, 36 in total. This is an estimation and feasibility pilot, not a powered sample | [REC] Task 03 5.2; Task 05 design specification §3, item 11. Decided (OD-06) |
| Blocks | Calibration → practice → detection block (12) → order block (24 = 20 main + 4 catch) | [REC] Task 03 7.3; Task 05 S4 |
| Within-subject factors (order block) | Δon ∈ {−3, 0, +3} s crossed with Δoff ∈ {−3, 0, +3} s | [REC] Task 03 1.3 and 7.2 |
| Response | Ternary: Left began first / Same time / Right began first | [REC] Task 03 3.4 |
| Setting | Supervised laboratory sessions, only on testing stations that have individually passed E2 (D3 §2) | [JDG]. Decided (OD-07) |

---

## 3. Stimuli

These carry over unchanged from Task 03 Part 6, with the Task 04 implementation and Task 05 corrections S10 and S11. The frozen generator `stimulus.py` (SHA-256 `238d882a…`) is the reference. Any participant-facing build must reproduce its schedules bit for bit.

### 3.1 Display

| Element | Specification |
|---|---|
| Background | CIELAB L* = 35, neutral grey |
| Fixation | L* = 70, diameter 6 CSS px |
| Discs | Diameter 12% of the smaller viewport dimension (minimum 100 CSS px); centred at 25% and 75% of viewport width; vertically centred |
| Viewport | Minimum 900 CSS px wide |

### 3.2 Constants

| Constant | Value |
|---|---|
| T (trial duration) | 24 s |
| D0 (base ramp duration) | 12 s |
| s (asynchrony step) | 3 s |
| L0 (start lightness) | 55 |
| M (change magnitude) | 10 L* |
| B compression factor | 8 |

**M is fixed before participant data collection (OD-10).**

- M = 10 L* unless E2 forces a rendering change (D3 §6).
- Any such change is made, re-audited, recorded as an amendment and frozen **before the first participant**.
- There is no tuning of M on participant data at any point. Task 03's allowance to adjust M during piloting is withdrawn.

### 3.3 Order trials

From cell (Δon, Δoff):

- dur_L = D0 + (Δon − Δoff)/2 and dur_R = D0 − (Δon − Δoff)/2
- m_on ~ U[3, 6] s
- onset_L = m_on − Δon/2 and onset_R = m_on + Δon/2

**Sign convention** [REC; verified against `stimulus.py`]:

- Δon = onset(R) − onset(L). Positive means the left disc began first.
- Δoff = offset(R) − offset(L).

Onsets fall within [1.5, 7.5] s and the latest offset is 19.5 s [DED, Task 05 S11]. Lightness follows L(t) = L0 + dir·M·clamp((t − onset)/dur, 0, 1), with direction shared by both discs within a trial.

### 3.4 Detection trials

The 12 templates are as implemented in Task 04 `detection_templates()`:

| Type | Count |
|---|---|
| No change | 4 |
| Left only (9 s +, 15 s −) | 2 |
| Right only (9 s −, 15 s +) | 2 |
| Both, simultaneous, 12 s | 4 |

Onset ~ U[3, 9] s. This resolves the Task 03 6.3 versus 7.1 duration ambiguity [REC, Task 04 SPEC-GAP].

### 3.5 Catch trials

Four per participant [REC, Task 05 S4]:

- **Cells:** (+8, +8) twice and (−8, −8) twice.
- **Ramps:** 6 s each, with a 2 s gap between them and no overlap.
- **Directions:** balanced, and crossed with leader side.
- **Timing:** m ~ U[5.5, 8.5] s.
- **Placement:** one at a random position within each quarter of the 24-trial order block.
- **Analysis:** excluded from the cue-weight analysis.

### 3.6 Rendering

[REC, Task 03 6.4 and Task 05 S10]

- L*(t) is computed analytically on every animation frame from `performance.now()`. In B, t_real = 8 × t_display.
- L* is converted to relative luminance, then to sRGB.
- **Triangular (TPDF) temporal dither** is applied before 8-bit quantisation. It replaces Task 03's uniform dither.
- Every frame timestamp is logged.
- Visibility of the dither and of code steps is **not yet tested** (E2, D3).

### 3.7 Condition C plot

[REC, Task 03 6.5]

| Element | Specification |
|---|---|
| Layout | Two stacked panels, top labelled Left and bottom labelled Right |
| Time axis | Shared, 0–24 s at 25 CSS px/s (600 px) |
| Panels | 120 px high each; y-range L0 ± (M + 2); identical in both panels |
| Line | 2 px wide; one computed point per horizontal pixel |
| Gridlines | Every 4 s |
| Omitted | No onset or offset markers; no numeric y-axis |

### 3.8 Random number generation

[REC, Task 03 6.2; Task 04]

- **Generator:** mulberry32, bit-exact with `stimulus.Mulberry32`.
- **Trial seed:** (participantSeed × 1000 + trialIndex) mod 2³².
- **Shuffle streams:** indices 900 (detection) and 901 (order).
- **Catch positions:** drawn from the seeded PRNG.

**Seed collisions [SG]** (Task 03 is silent; the reduction to 32 bits makes collisions possible):

- Participant seeds are generated in advance as a list, using the allocation procedure in 6.1.
- The list is accepted only if no trial seed collides across all planned participants, replacements included.
- The collision check is part of the pre-data audit (Section 11).

---

## 4. Conditions

| | A Real time | B Replay (8×) | C Static traces |
|---|---|---|---|
| Presentation | 24 s animation | 3 s animation. s becomes 375 ms; ramps last 1.1–1.9 s | Two lightness-over-time traces |
| Detection block | Single play | Single play, no replay | Traces visible; response enabled after 3 s; removed at 15 s |
| Order block | Single play | Single play plus up to 2 replays on request, each preceded by a 1 s mask | As detection block |
| Response enabled | After presentation ends | After presentation ends, or after the last replay | After 3 s |
| Response time measured from | Response enablement | Response enablement | Response enablement |
| Process measures | Frame log | Frame log; replay count | Exposure time |
| Construct caution | Real-time noticing of slow onsets | Order under uniform compression | **Graph reading.** Not validated as temporal recognition (Section 9) |

**Inter-trial structure [SG]** (Task 03 specifies none):

- 1.0 s fixation before each trial.
- 1.0 s blank after each response.

These values are added to the burden model, which already assumes about 1 s per trial.

---

## 5. Participant journey

| Step | Content | Notes |
|---|---|---|
| 0 | Information statement and written consent, before the task software starts | Ethics-approved documents (D4 §8) |
| 1 | Eligibility confirmation and minimal demographics: age band, normal or corrected vision, no history of photosensitive epilepsy | [SG] Minimal data set |
| 2 | Device check: viewport ≥ 900 CSS px, refresh-rate estimate, browser and display identifiers logged | Laboratory station ID recorded; only E2-passing stations are used (OD-07) |
| 3 | General and condition-specific instructions (Section 7) | |
| 4 | **Calibration:** 10 static endpoint discriminations (start against end lightness, side by side). Pass at 9/10 or better | Failure ends the session, with full reimbursement. Counted in F2 |
| 5 | **Practice:** 3 trials with abrupt changes (2 s ramps; 0.25 s in B), in the participant's condition. Feedback on response format only | [REC] Task 03 7.3 |
| 6 | **Detection block:** 12 trials, randomised order, break after trial 6. Response: left disc changed (yes/no), then right disc changed (yes/no) | [SG] Per-disc yes/no format. Task 03 defines hits and false alarms per disc but not the response screen |
| 7 | Order-block instructions | Section 7 |
| 8 | **Order block:** 24 trials (20 main and 4 catch), randomised, breaks after trials 8 and 16. Ternary response only | Confidence rating removed (OD-16) |
| 9 | Attention check question; strategy question ("What did you look for to decide which disc began first?") | [REC] Task 03 7.3 |
| 10 | Debrief | D4 §8 |

Breaks are self-paced up to 60 s, with a continue button. **Order-block re-queue** is described in 6.3.

---

## 6. Allocation, randomisation and sequencing

### 6.1 Condition allocation [JDG; decided, OD-13]

- **Unit:** each new participant who passes eligibility.
- **Method:** permuted blocks of 6 (two per condition).
- **Sequence generation:** a seeded PRNG generates the sequence before the first session, using seed `sha256("task06-allocation-v1")` truncated as in D2 §9.
- **Concealment:** the sequence's SHA-256 is recorded in the preregistration as a commitment. The sequence is concealed from the session runner until each allocation.
- **Replacements:** a participant excluded under §10 is not reassigned. Allocation simply continues down the sequence.
- **Closing an arm:** once an arm reaches 12 analysable participants, it is closed and later allocations to it are skipped. This brings a small calendar-time imbalance across arms, which is recorded (D2 §12).
- **Cap:** 24 starters per arm (§10.4).

### 6.2 Trial order

- Detection and order blocks are each shuffled per participant from the seeded PRNG.
- One catch trial is placed at a random position within each quarter of the order block (positions 1–6, 7–12, 13–18, 19–24).
- Lightening and darkening are balanced within each cell, as in the Task 03 7.2 allocation.

### 6.3 Technically invalid order trials: re-queue [JDG; decided, OD-04]

**What makes a trial invalid**, judged by the software without reference to the response:

- (i) Any frame interval during the presentation exceeds 100 ms. [JDG] **This threshold is provisional.** It is not justified by the record. It is confirmed or revised from E2 measurement M1 on the actual laboratory hardware, and frozen before preregistration (OD-09).
- (ii) The tab or window lost visibility or focus during presentation.
- (iii) A technical error occurred.

**What happens:**

- An invalid main or catch trial is re-queued once, at the end of the order block, with the same template and a fresh m_on drawn from a reserved stream (trial index 950 + k) [SG].
- A trial invalid twice is recorded as **missing**.
- The response to an invalid presentation is logged but never analysed.

**Why.** It keeps the complete, balanced, orthogonal 20-trial set that the validated B3-t closed form needs (D2 §4), without changing the estimator.

**Costs.** It shifts the position of re-queued trials and adds time. Both are logged.

**Detection block.** Invalid detection trials are handled the same way.

---

## 7. Instructions (draft wording; final wording requires ethics approval)

The wording is neutral. It does not mention hypotheses, onset or offset strategies, or what to look for in condition C [REC, Task 03 4.1 demand characteristics].

**General.** "You will see two discs. On some trials one or both discs will slowly become lighter or darker. Please keep your eyes on the screen for the whole trial."

**Condition B addition.** "Each trial shows 24 seconds of change played 8 times faster, so it lasts 3 seconds. In the second part you may replay a trial up to twice."

**Condition C addition.** "Each trial shows two lines. Each line shows how the lightness of one disc changed over 24 seconds. Time runs from left to right. The top line is the left disc; the bottom line is the right disc."

**Detection block.** "Some discs will change and some will not. After each trial, tell us whether the left disc changed and whether the right disc changed."

**Order block.** "In every trial in this part, **both** discs will change. They may begin and finish at different times, and the disc that finishes first is not always the one that began first. Your task is to decide which disc **began** changing first. If they seemed to begin at the same time, choose *Same time*."

**Response buttons.** These are on-screen and in a fixed spatial order: **[Left began first] [Same time] [Right began first]**.

**Feedback.** None during the detection and order blocks.

---

## 8. Response capture and data recorded

### 8.1 Trial-level record [JDG]

| Field group | Fields |
|---|---|
| Identity | Participant code (pseudonymous); condition; participantSeed |
| Trial | Block; position; template ID; trial seed; Δon; Δoff; direction; m_on; onset and duration per disc |
| Response | Response (L/S/R, or per-disc yes/no in detection); response time |
| Process | Replay count (B); exposure (C) |
| Validity | Validity flags and reason; re-queue flag |
| Frame summary | Count; median, 95th percentile and maximum interval; intervals over 1.5× nominal; intervals over 100 ms |
| Visibility | Visibility or focus events |

### 8.2 Session-level record

- Timestamps, total duration and break durations.
- Calibration score.
- Device: browser, OS, viewport, devicePixelRatio, refresh estimate, display identifier.
- Attention check and free-text strategy answer.

### 8.3 Coding for analysis

- **Order response:** y ∈ {0, 1, 2} = {R, S, L}.
- **Signed score:** s = y − 1, so Right began first = −1, Same time = 0, Left began first = +1.

The frozen implementation (`ordinal_model.simulate_responses`, `heterogeneity_methods.b3_individual`) codes responses this way [REC]. The brief's labels ("Earlier = −1, Later = +1") do not match the response wording. The left/right coding is retained (decided, OD-01).

---

## 9. Learning, fatigue, attention, order effects and burden

| Threat | Control in design | Measurement and reporting |
|---|---|---|
| Condition order and carry-over | Between subjects | Not applicable |
| Learning within blocks | No feedback; practice uses abrupt ramps only; randomised trial order | Order-block first versus second half: cell proportions and φ_β, descriptive only (D2 §8) |
| Fatigue and vigilance (largest in A) | Breaks after trials 8 and 16; 24 s trials are the same in every block | Time on task; second-half catch errors; "same" rate by half [REC, Task 05 S5] |
| Attention failure | Catch trials; attention check | Catch error rate per condition; S5 labelling of any between-condition statement |
| Block order (detection before order) | Fixed for every participant. Detection must precede order, because the order block tells participants that both discs change | Not separable; a design constant |
| Replay use (B) | At most 2 replays per trial | Replay counts; descriptive |
| Exposure (C) | 3–15 s window | Exposure distribution; descriptive |
| Catch-trial burden | Four 24 s trials | Modelled cost of about +2.4 min in A [REC, Task 05] |

### 9.1 Session length

These figures are model-based [REC, Task 05 `burden_with_catch.json`].

| Condition | Median | 90th percentile |
|---|---|---|
| A | 25.4 min | 26.2 min |
| B | 14.1 min | 15.0 min |
| C | 15.5 min | 16.4 min |

The burden model leaves out several things:

- consent, eligibility, debrief
- the inter-trial structure in Section 4
- re-queued trials

The modelled 25.4 min exceeded Task 03's F3 threshold (median A ≤ 25 min). F3 is revised to **median task time in A ≤ 28 min**, measured from calibration to the final question (OD-08). **This threshold is provisional.** It rests on a model, not data, and is checked in staff dry runs before preregistration and measured in the pilot.

### 9.2 What the design can and cannot separate

[REC, Task 05 review §6 and closure record §6]

| Alternative explanations | Separable here? | What would be required |
|---|---|---|
| Onset timing with detection delay vs genuine offset use | **No** for angles up to about 25° | Independent detection-latency measurement (for example, reaction time to single-ramp onset) in the same participants. Not in this study |
| Midpoint timing vs mid-ramp state comparison | **No.** Both give about 45° | Manipulations that dissociate them, such as ramps of unequal magnitude or curved ramps. These would break the constant-magnitude design |
| Midpoint timing vs area comparison of static traces (C) | **No** | C-strip or C-sequential controls [REC, Task 03 2.5] |
| Attention failure vs strategy change | **Partly.** Condition-level screen only (catch errors and "same" rate; S5) | An attention-specific manipulation; considered and not recommended in Task 05 |
| Graph reading vs temporal recognition (C) | **No** | C-sequential and C-strip controls in a follow-up study |
| Heterogeneous mixture vs homogeneous intermediate strategy | **No** [DED] | About 52 or more order trials per participant for individual classification [SIM]; not feasible in A within 30 minutes |
| Rate or duration heuristic vs onset | **Yes.** The design separates the −45° signature [SIM] | Not applicable |
| Onset-dominant vs midpoint-like, at group level and adequate sensitivity | **Yes**, behind the gate [SIM] | Not applicable |

---

## 10. Exclusions, replacement and stopping

### 10.1 Participant-level exclusion

Each rule is applied before the outcome is analysed. Excluded participants are replaced (§6.1).

| ID | Rule | Source |
|---|---|---|
| X1 | Calibration below 9/10. The session ends | [REC] Task 03 9 |
| X2 | 3 or more of the 4 catch trials wrong | [REC] Task 05 S4 |
| X3 | Failed attention check | [REC] Task 03 9 |
| X4 | Fewer than 95% of presentation frame intervals within 1.5× nominal, across the session | [REC] Task 03 F4. This replaces the inconsistent Task 03 "more than 10% dropped frames". Decided (OD-09) |
| X5 | Viewport below 900 CSS px | [REC] Task 03 9 |
| X6 | Any **missing** main order trial after re-queue (§6.3), or fewer than 4 valid catch trials. The participant is excluded from the primary analysis | [JDG] Decided (OD-04) |
| X7 | Withdrawal | Ethics |

Exclusion decisions are logged with the rule ID. They are made by a script that does not compute φ_β (D2 §12).

### 10.2 Analysable participant

An analysable participant:

- passed X1–X5 and X7
- has all 20 main order trials valid
- has all 4 catch trials presented, including re-queues

### 10.3 Selection effects of exclusion and replacement

The analysed sample is a **selected** population: people who pass calibration, catch, attention and timing checks, topped up to 12 per arm. Exclusion rates may differ between conditions. D2 §10.4 sets out each selection risk and how it is reported. Starters, completers and exclusions by rule and condition are always reported.

### 10.4 Stopping

No stopping rule depends on the outcome, and there is no interim analysis of φ_β or of any contrast.

- **Arm complete:** 12 analysable participants.
- **Arm cap:** 24 starters. At the cap the arm closes with whatever analysable participants it has. That is reported as a feasibility failure (F1 and F2), not filled further.
- **Technical pause:** if more than 20% of the last 10 sessions fail X4, recruitment pauses for review [JDG].
- **Safety pause:** any adverse event, such as discomfort or a suspected photosensitive reaction, pauses the study pending review. The flicker-like risk of dither noise is low but untested (E2).

---

## 11. Pre-data checks

These are required before the first participant.

1. **E2 passes on every laboratory testing station that will be used** (D3 §2). This is mandatory.
   - A station that has not individually passed E2 may not be used.
   - Any change to a station's hardware, OS, browser, driver or display settings after E2 requires E2 to be repeated for that station.
2. **Stimulus audit** is re-run on the build's actual schedule output for the full pre-generated participant-seed list. It covers Task 03 6.7(1)–(4) [REC] and the Task 05 S10 replacement for 6.7(5), and also:
   - bit-exact agreement with `stimulus.py`
   - no trial-seed collisions
   - catch positions one per quarter
3. **An eligible ethics pathway is identified and approval is in hand** (D4 §8). This is **OPEN (OD-14)**: no eligible institution or review process has yet been identified.
4. **Preregistration** is submitted and time-stamped (D4).
5. **The analysis code is frozen and hashed** (D2 §9).
   - Its deterministic unit tests must pass.
   - The wrapper (r3.1) and its 41 deterministic tests exist in `code/`. They are not yet frozen.
6. **M is frozen** (§3.2), after E2.
7. **The provisional thresholds are confirmed or revised and then frozen:** the 100 ms per-trial rule (from E2 M1) and the 28 min burden threshold (from staff dry runs).
8. **Dry runs:** at least 2 complete sessions per condition by staff, on the study hardware. These data are discarded and logged.

---

## 12. Implementation requirements for a future build (not authorised here)

- **Rendering:** analytic per frame as in §3.6, with no pre-rendered video.
- **Schedules:** generated client side from the seeds, or supplied from the audited list; bit-exact with `stimulus.py`.
- **Logging:** frame intervals for every presentation. Data is written to local secure storage after each trial.
- **Response controls:** disabled until enablement. The participant cannot proceed without responding.
- **Run order:** the build has no condition-switching controls visible to participants. The study runner cannot change the trial order.
- **Data format:** one CSV per participant at trial level, plus a session JSON. Field definitions follow §8, and a data dictionary is versioned with the build.
- **Build identity:** the build hash is recorded in every session file.

---

## 13. Feasibility criteria

These are carried from Task 03 Part 9 and revised as marked. They are criteria for proceeding, not evidence about hypotheses.

| ID | Criterion | Status |
|---|---|---|
| F1 | At least 80% of starters complete | Unchanged |
| F2 | At most 15% of starters excluded at calibration | Unchanged |
| F3 | Median condition A task time (calibration to final question) ≤ 28 min | Revised (OD-08). **Provisional** |
| F4 | At least 95% of frames within 1.5× nominal in included sessions | Unchanged. It is also exclusion rule X4 |
| F5 | Condition A correct-leader proportion on onset-only trials < 0.90 | Unchanged |
| F6 | Correct-leader proportion on onset-only trials > 0.60 in at least one condition | Unchanged |
| F7 | "Same" chosen on at least 30% of simultaneous trials in at least one condition | Unchanged |
| F8 | B3-t computable in each condition, with the participant slope covariance non-singular | Redefined from Task 03's posterior-interval wording [REC, Task 05 design specification §3, item 9] |

**Reading F5–F7 against the frozen generator** [DED, deterministic quadrature; `supporting/model_response_probabilities.json`]. These figures assume τ = 1, bias SD 0.5 and lapse 0.02, which are assumptions about humans.

| Onset weight a | Correct-leader proportion on onset-only trials |
|---|---|
| 0 | 0.28 |
| 0.20 | 0.41 |
| 1/3 | 0.50 |
| 0.70 | 0.73 |
| 1.07 | 0.88 |

The model's simultaneous-trial "same" rate is 0.44.

- **F6:** "> 0.60" corresponds to roughly a ≥ 0.5.
- **F5:** "< 0.90" corresponds to roughly a < 1.1.
- **Gate-power reference:** the B3-t sensitivity gate passed in 81% of datasets at a = 0.20 [SIM, A1].
