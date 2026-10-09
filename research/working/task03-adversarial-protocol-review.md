# Research Task 03: Adversarial Protocol Review

- Programme: Temporal Space in Institutional Reasoning
- Stream: 1, Human Temporal Perception
- Subject of review: Task 02 onset-order experiment (`task02-slow-change-temporal-augmentation.md`, Part 4)
- Baseline: `research/temporal-space-v0.1.md` (immutable)
- Date: 10 October 2026
- Status: Working document. No application built. v0.1, PHDSS and JARVIS unchanged. Not a v0.2 draft.

## Summary verdict

**REVISE.** The Task 02 protocol cannot distinguish onset-based from offset-based judgement, uses an outcome measure that compares different trial subsets across conditions, and relies on a control arm (D) that does not test what it was meant to test. A revised protocol is specified below. It is close to buildable, but three desk checks must pass first (Part 10).

## Evidence labels

- **[Empirical]** Design decision supported by published experimental or methodological literature.
- **[Recommendation]** My methodological judgement, not tested in this context.
- **[V] / [P] / [U]** Bibliographic verification status, as in previous tasks.

---

## Part 1. Separating onset order from offset order

### 1.1 The defect in Task 02

Task 02 fixed both ramp durations at 15 s so that offset asynchrony equalled onset asynchrony. That does not control offset cues; it confounds them. Every correct "left first" response is equally explained by onset order, offset order, midpoint order or any mixture.

This matters empirically. Jaśkowski (1991) found that observers took offset asynchrony into account when judging onset simultaneity, despite instructions [Empirical, P]. Studies of rise time report that order judgements for gradual onsets depend on rise time [Empirical, P: Pastore 1988; Jaśkowski 1993]. Slow ramps are the extreme case: the onset is the least salient moment of the change.

### 1.2 Cue space

For linear ramps of constant magnitude, the available timing cues for each disc are its onset, its offset, its midpoint (half-amplitude time), its duration and its rate. With two discs, the relevant contrasts are:

- Δon = onset(R) − onset(L)
- Δoff = offset(R) − offset(L)

Positive values mean the left disc leads. All other timing cues are functions of these two:

- Midpoint contrast = (Δon + Δoff) / 2
- Duration contrast (L minus R) = Δon − Δoff
- Rate contrast: sign opposite to the duration contrast when magnitude is fixed

So any observer's timing strategy can be described, to a first approximation, by two weights: one on Δon and one on Δoff. A pure onset observer has weights (1, 0). A pure offset observer has (0, 1). A midpoint observer has roughly (0.5, 0.5). A "longer change started first" heuristic has (1, −1) up to scale. [Recommendation: this reduction holds for linear ramps; it would not hold for curved ramps.]

### 1.3 Orthogonal design

Vary Δon and Δoff independently over {−s, 0, +s}. The nine cells and their diagnostic value:

| Cell type | (Δon, Δoff) | Pure onset observer | Pure offset observer | Midpoint observer |
|---|---|---|---|---|
| Simultaneous | (0, 0) | Same | Same | Same |
| Congruent | (+s, +s), (−s, −s) | Correct leader | Correct leader | Correct leader |
| Onset-only | (+s, 0), (−s, 0) | Correct leader | Same | Weak lean to correct leader |
| Offset-only | (0, +s), (0, −s) | Same | "Leader" by offset | Weak lean to offset leader |
| Conflict | (+s, −s), (−s, +s) | Onset leader | Offset leader | Same |

Across a balanced allocation, Δon and Δoff are uncorrelated, so the two weights are separately estimable. [Recommendation, standard factorial logic]

**Conflict trials** are the most diagnostic. In (+s, −s), the left disc starts first and finishes last. Onset, offset and midpoint observers give three different answers.

**Onset-only and offset-only trials** test whether observers respond to one cue in the absence of the other. They are needed because conflict trials alone cannot distinguish a midpoint observer from an observer who guesses when cues disagree.

### 1.4 Constant magnitude or constant rate

Decoupling onset from offset requires the two discs to have different durations on some trials. Then either magnitude or rate must also differ.

| Option | Consequence | Assessment |
|---|---|---|
| Constant magnitude, rate varies | End states identical in magnitude; faster ramps on shorter durations | End-state frames carry no timing information. Rate may affect detection |
| Constant rate, magnitude varies | Longer ramps reach larger end states | End states leak duration, hence partial timing information; also creates salience differences |

**Decision: constant magnitude.** [Recommendation] It keeps all static end states uninformative about timing. Rate differences become a known covariate for detection; Marples et al. (2019) found no effect of change duration on gradual-change detection between 11 and 90 s, which weakly suggests rate within the planned range will not dominate [Empirical, P, incidental viewing only].

### 1.5 Instructions

Participants are asked which disc *began* changing first, with the explicit note that the discs may finish in a different order. [Recommendation] Instructions do not remove offset influence (Jaśkowski 1991), which is why the design measures it rather than relying on instructions.

---

## Part 2. Is endpoint-only condition D an adequate control?

### 2.1 What D was meant to do

Task 02 proposed D (static start and end states) to show whether condition C's advantage could be explained by detection offloading alone.

### 2.2 What D can establish

1. The level of change detection achievable with no temporal information at all.
2. That rendered end states do not leak timing information, when D order accuracy is at chance.

### 2.3 What D cannot establish

1. **That C's order advantage reflects temporal relational recognition.** C shows the full trajectory as spatial shape. D shows none of it. A C advantage over D is consistent with reading a static spatial feature (where the trace departs from flat) without any judgement that is temporal in a meaningful sense. D does not control this.
2. **That C's advantage is not memory offloading.** D has no trajectory, so it equates nothing about the memory demands of holding a trajectory. The offloading question is whether simultaneous availability of the whole history drives C's advantage. D does not address it.
3. **Anything about condition B.**
4. **Anything about onset versus offset cues.** End states contain neither.

### 2.4 Under the revised design

With constant magnitude, end states are uninformative about timing by construction. Point 2.2(2) can therefore be verified analytically from the stimulus specification and a rendering audit, without participants. D's remaining value is a detection baseline, which the calibration step already approximates.

**Decision: drop D as a separate arm.** Fold an endpoint discrimination check into calibration. [Recommendation]

### 2.5 Better offloading controls (follow-up study, not pilot)

| Control | What it changes | What it tests |
|---|---|---|
| **C-sequential** | Show the two traces one at a time with a mask between | Whether C's advantage depends on simultaneous co-presence of both histories (offloading of the comparison) |
| **C-strip** | Encode lightness as a horizontal lightness strip over time, not as line height | Whether C's advantage depends on switching from lightness to position (channel change) rather than on mapping time to space |

C-sequential is the stronger test of the offloading account. [Recommendation]

---

## Part 3. Joint analysis of detection and order

### 3.1 The selection problem

Task 02's primary measure was order accuracy conditional on both changes being reported. That selects different trial subsets in each condition.

Example: if in condition A only fast or salient ramps are detected, conditional order accuracy in A is computed on an easier subset than in C, where almost every trial passes. A difference in conditional accuracy could then arise with identical order-discrimination ability. The direction of the bias cannot be known in advance: it depends on whether the trial properties that aid detection also aid order judgement. [Recommendation, standard selection reasoning]

Unconditional success (both detected and order correct) avoids selection but mixes detection and order into one number, so it cannot locate the effect.

### 3.2 Options

| Option | How it works | Strength | Weakness |
|---|---|---|---|
| Conditional accuracy | Analyse order only where both detected | Simple | Selection bias across conditions |
| Unconditional success | Count joint correct outcomes | No selection | Cannot separate detection from order |
| Multinomial processing tree model | Model detection and order as sequential latent stages fitted to all response categories (Batchelder & Riefer, 1999) [Empirical, V] | Separates stages without selection | Needs more trials; identifiability must be checked; model-dependent |
| **Blocked design** | Separate detection block and order block; in the order block participants are told both discs change | Removes selection by design; order measured on every order trial | Changes the order construct to "recognising order of changes known to occur" |

### 3.3 Decision: blocked design

[Recommendation] Measure detection and order in separate blocks.

- **Detection block first.** Participants are told discs may change slowly or not at all. Measures noticing.
- **Order block second.** Participants are told both discs will change on every trial and asked which began first. Detection failure in this block cannot select trials out; it simply leaves the observer guessing, which the model absorbs.

The construct change is acceptable and arguably cleaner. The central question concerns recognising a *relationship* between changes; whether people can notice that change happened at all is a separate, already well-documented limitation (Simons et al., 2000) [Empirical, V].

### 3.4 Response format for order

Use a ternary response: left began first, right began first, began at the same time. Ternary formats are recommended over binary order judgements because they separate indecision from order sensitivity, and the TOJ literature argues binary formats conflate decisional and sensory components (García-Pérez & Alcalá-Quintana, 2012) [Empirical, V]. Response errors and lapses should be modelled, because they distort fitted psychometric functions in ternary tasks [Empirical, V: García-Pérez & Alcalá-Quintana, 2012, *Frontiers in Psychology*].

### 3.5 Joint analysis that remains

- Detection block: d′ and criterion per participant.
- Order block: cue-weight model (Part 8).
- Link between them: exploratory participant-level association between detection d′ and onset weight within each condition. Underpowered at pilot size; reported descriptively only.

---

## Part 4. Comparability of conditions A, B and C

### 4.1 Intrinsic versus avoidable differences

| Difference | Intrinsic to the intervention? | Treatment |
|---|---|---|
| B compresses time (higher rate, shorter duration) | Intrinsic | None; this is the manipulation |
| C maps time to space | Intrinsic | None |
| C shows the full history simultaneously | Intrinsic to static representations | Measured as the offloading question (C-sequential follow-up) |
| C uses position rather than lightness | Intrinsic to line charts; avoidable via a strip encoding | Accept in pilot; test with C-strip later |
| C has no unfolding experience | Intrinsic | None |
| Exposure duration: A 24 s, B 3 s, C open-ended | Partly avoidable | Fix C viewing window (minimum 3 s, maximum 15 s); allow B up to two replays in the order block only; log all exposure |
| B replay reset creates a flicker-like transient | Avoidable | Grey mask of 1 s between replays; replay allowed only in the order block, where detection is not measured |
| Response timing: A and B after presentation, C during | Avoidable | C responses enabled after the 3 s minimum; RT measured from response enablement in all conditions |
| Sustained vigilance: A demands watching 24 s per trial | Intrinsic to real-time observation | Breaks every 8 trials; analyse first versus second half |
| Session length: A longest | Intrinsic | Record; report; check time-on-task effects |
| 8-bit lightness quantisation creates micro-steps at slow rates | Avoidable | Temporal dithering (Part 6); audit |
| Plot resolution limits C's temporal resolution | Avoidable | Fixed pixels per second; asynchrony s maps to at least 60 px |
| Aspect ratio affects slope judgements in C (Cleveland et al., 1988) | Avoidable | Fixed aspect ratio, reported [Empirical, V] |
| Speed and duration misperception under time-lapse (Steinhof et al., 2025) | Intrinsic to B, but irrelevant to order | Order is invariant under uniform compression [Empirical, V, plus logical argument] |
| Demand characteristics: C looks like the instrument | Partly avoidable | Between-subjects; neutral framing; no mention of hypotheses |

### 4.2 Information equivalence

All three conditions render from the same analytic stimulus function. A and B sample it per display frame (B with time scaled by the compression factor). C samples it per horizontal pixel. Differences in sampling are below the planned asynchrony by a wide margin (Part 6). [Recommendation]

### 4.3 Task demands

The judgement is nominally identical (which began first), but the operations differ: A requires noticing an onset in real time; B requires noticing it in a brief replay; C requires locating a slope change in space. These are three different tasks with one response format. That is the intervention, not a flaw, but results must be described as differences in task difficulty under different representations, not differences in a single perceptual capacity. [Recommendation]

---

## Part 5. Smallest interpretable pilot

### 5.1 Constraints

- Real-time condition A dominates session length.
- Cue-weight estimation needs all nine cells.
- Between-subjects conditions prevent carry-over.

### 5.2 Design

- Three between-subjects conditions: A, B, C.
- 12 participants per condition (36 completing). Julious (2005) recommends 12 per group for pilots where no prior information exists, based on feasibility and precision of mean and variance [Empirical, V]. This is a feasibility rationale, not a power calculation.
- Shorter real-time trials than Task 02: 24 s instead of 30 s.
- 12 detection trials plus 20 order trials.
- Estimated condition A session: about 21 minutes.

### 5.3 What is dropped and why

| Dropped | Reason |
|---|---|
| Condition D as an arm | Uninformative under constant magnitude (Part 2) |
| Multiple asynchrony levels | One step size suffices for cue weights; thresholds deferred |
| Multiple compression factors | Non-monotonic compression prediction deferred to R2 follow-up |
| Implicit-influence measures | Out of scope |

---

## Part 6. Revised protocol: stimulus-generation specification

### 6.1 Display

- Background: CIELAB L* = 35, neutral grey.
- Fixation: central dot, L* = 70, diameter 6 CSS px.
- Discs: diameter 12% of the smaller viewport dimension (minimum 100 CSS px), centred at 25% and 75% of viewport width, vertically centred.
- Minimum viewport width 900 CSS px (needed for condition C).

### 6.2 Random number generation

- Seeded PRNG (for example, mulberry32) with seed = participantSeed × 1000 + trialIndex.
- participantSeed generated at entry and stored with all data.
- All trial parameters drawn from the PRNG; no use of unseeded randomness.

### 6.3 Trial parameters

Constants:

- Real trial duration T = 24 s.
- Base duration D0 = 12 s.
- Step size s = 3 s.
- Start lightness L0 = 55.
- Change magnitude M = 10 L* units (provisional; adjusted once in piloting so that the calibration pass rate meets F2).

For each order trial, from its cell (Δon, Δoff):

- dur_L = D0 + (Δon − Δoff) / 2
- dur_R = D0 − (Δon − Δoff) / 2
- Mean onset m_on drawn uniformly from [3, 6] s.
- onset_L = m_on − Δon / 2; onset_R = m_on + Δon / 2
- offset_L = onset_L + dur_L; offset_R = onset_R + dur_R

Check: offset_R − offset_L = Δon + (dur_R − dur_L) = Δoff. Durations take values in {9, 10.5, 12, 13.5, 15} s. Earliest onset 1.5 s; latest offset 22.5 s; both within T.

Lightness for disc i at real time t:

L_i(t) = L0 + dir × M × clamp((t − onset_i) / dur_i, 0, 1)

- dir ∈ {+1, −1}, the same for both discs within a trial, balanced across trials (so lightening and darkening are equally represented and never compared against each other within a trial).

For detection trials:

- No-change disc: L(t) = L0 throughout.
- Changing disc: onset drawn from [3, 9] s; duration from {9, 12, 15} s, balanced; same formula.

### 6.4 Rendering

- Compute L_i(t) analytically on every animation frame from `performance.now()` relative to trial start. Condition B uses t_real = 8 × t_display.
- Convert L* to relative luminance, then to sRGB using the standard transfer function.
- Apply temporal dithering before quantising to 8 bits: add a uniform random offset in [−0.5, 0.5) of one code value per frame per disc. This keeps the expected displayed value continuous and prevents discrete steps acting as transients. [Recommendation; the risk it addresses is real, its sufficiency on each display is untested]
- Log every frame timestamp.

### 6.5 Condition C rendering

- Two panels stacked vertically, top labelled Left, bottom labelled Right, each with a small disc icon.
- Shared time axis 0 to 24 s at 25 CSS px per second (600 px). Step size s maps to 75 px; half-step contrasts to 37.5 px.
- Panel height 120 px each; y-range L0 − M − 2 to L0 + M + 2; identical in both panels; fixed aspect ratio.
- Line width 2 px; one computed point per horizontal pixel from the same analytic function.
- Light vertical gridlines every 4 s; no onset or offset markers; no numeric y-axis.
- Visible from trial start; responses enabled after 3 s; display removed at 15 s if no response, then response required.

### 6.6 Condition B specifics

- Compression factor 8: 24 s becomes 3 s; s becomes 375 ms; ramps last 1.1 to 1.9 s.
- Detection block: single play, no replay.
- Order block: single play plus up to two replays on request, each preceded by a 1 s mask (discs absent, background only).

### 6.7 Stimulus audit (before any participant)

A script generates the full trial set for 100 simulated participants and verifies:

1. Within each order block, correlation between Δon and Δoff is zero.
2. All end states of changing discs are equal in magnitude within each trial.
3. All onsets and offsets fall within [1.5, 22.5] s.
4. Duration and direction balance across cells.
5. Rendered sRGB sequences under dithering have no single-frame step larger than one code value.

---

## Part 7. Balanced trial allocation

### 7.1 Detection block (12 trials, all conditions)

| Trial type | Count | Balance |
|---|---|---|
| No change | 4 | Direction irrelevant |
| Left only | 2 | Durations 9 and 15 s; directions +/− |
| Right only | 2 | Durations 9 and 15 s; directions +/− |
| Both change, simultaneous, D0 = 12 s | 4 | Directions 2+, 2− |

### 7.2 Order block (20 trials, all conditions)

| Cell | (Δon, Δoff) in s | Count | Direction balance |
|---|---|---|---|
| Simultaneous | (0, 0) | 4 | 2+, 2− |
| Congruent | (+3, +3), (−3, −3) | 2 each | 1+, 1− per cell |
| Onset-only | (+3, 0), (−3, 0) | 2 each | 1+, 1− per cell |
| Offset-only | (0, +3), (0, −3) | 2 each | 1+, 1− per cell |
| Conflict | (+3, −3), (−3, +3) | 2 each | 1+, 1− per cell |

Left-leading and right-leading cells are mirror pairs, so leader side is balanced by construction.

### 7.3 Sequence

1. Device check (viewport, frame rate estimate).
2. Instructions.
3. Calibration: 10 static endpoint discriminations (start versus end lightness, side by side); pass at 9 of 10.
4. Practice: 3 trials with abrupt changes (2 s ramps) covering the response format, with feedback on format only.
5. Detection block: 12 trials, randomised order, break after trial 6.
6. Instructions for order block (both discs will change; judge which *began* first; finishing order may differ).
7. Order block: 20 trials, randomised order, breaks after trials 7 and 14.
8. Attention check question and brief strategy question ("What did you look for?").
9. Data download.

Condition assignment is randomised at entry and logged. Trial order within blocks is randomised per participant from the seeded PRNG.

---

## Part 8. Outcome definitions and analysis plan

### 8.1 Outcome definitions

**Detection block**
- Hit: changing disc reported as changed.
- False alarm: unchanged disc reported as changed.
- d′ and criterion c per participant, log-linear correction for extreme rates.

**Order block**
- Response r ∈ {L, S, R} (left first, same time, right first).
- Onset weight w_on and offset weight w_off from the model below.
- Onset index OI = w_on / (|w_on| + |w_off|): 1 for pure onset, 0.5 for midpoint, 0 for pure offset.
- Diagnostic proportions: correct leader on onset-only trials; "same" on offset-only trials; onset-consistent choice on conflict trials; "same" on simultaneous trials.
- Confidence (1 to 3) and RT from response enablement.

**Process measures**
- Exposure time (C), replays (B), frame timing, time-on-task.

### 8.2 Primary model

Cumulative-logit (ordinal) model with response categories ordered R < S < L:

logit P(r ≥ k) = θ_k,condition − (w_on,condition × Δon + w_off,condition × Δoff) − u_participant

- Two thresholds per condition capture bias and the width of the "same" band.
- Participant random intercepts only; random slopes are not estimable at pilot size.
- Optional lapse mixture to absorb response errors (García-Pérez & Alcalá-Quintana, 2012) [Empirical, V].
- Fitted in a Bayesian framework with weakly informative priors for stability at small N. [Recommendation]

### 8.3 Secondary analyses

- Detection d′ and c by condition (descriptive with bootstrap intervals).
- Time-on-task: order performance in first versus second half of the block.
- Confidence–accuracy relation by condition.
- Strategy reports coded for onset, offset, midpoint, duration and other cues.

### 8.4 What the pilot will and will not claim

- Will report: estimates and intervals for w_on, w_off, OI and d′ by condition; feasibility outcomes.
- Will not report: significance tests of condition effects, threshold estimates, or claims of perceptual change.

### 8.5 Pre-registration

Register the stimulus specification, trial allocation, model, exclusion rules and feasibility criteria before data collection. [Recommendation]

---

## Part 9. Feasibility criteria

Pilot succeeds as a feasibility study if all of the following hold. These are criteria for proceeding to a confirmatory study, not evidence about the hypotheses.

| ID | Criterion | Threshold |
|---|---|---|
| F1 | Completion | ≥ 80% of starters complete |
| F2 | Calibration | ≤ 15% of starters excluded at calibration |
| F3 | Burden | Median condition A session ≤ 25 minutes |
| F4 | Timing | ≥ 95% of frames within 1.5× nominal interval in included sessions |
| F5 | Not at ceiling | Condition A correct leader on onset-only trials < 90% |
| F6 | Not at floor everywhere | At least one condition with correct leader on onset-only trials > 60% (chance about 33%) |
| F7 | Scale use | "Same" chosen on ≥ 30% of simultaneous trials in at least one condition |
| F8 | Estimability | Model converges; posterior interval for group w_on in each condition excludes implausibly wide ranges set in the parameter-recovery simulation |

Exclusion rules: calibration below 9 of 10; failed attention check; more than 10% dropped frames; viewport below 900 CSS px.

---

## Part 10. Gates before BUILD

1. **Stimulus audit** (Part 6.7) passes, including dithering behaviour on at least three common display and browser combinations.
2. **Parameter-recovery simulation.** Simulate onset, offset, midpoint, guessing and biased observers with the planned trial counts and N = 12 per condition. Fit the primary model. Confirm that OI separates onset from midpoint observers at group level and that w_on is recovered without systematic bias. If not, increase order trials (for example, to 3 per non-zero cell) and recompute burden.
3. **Pre-registration** of the items in 8.5.

These are desk tasks. None requires building the participant-facing application.

---

## Part 11. Falsification table

| Hypothesis | Finding that would weaken it | Finding that would substantially falsify it |
|---|---|---|
| H1. Onset order of slow changes is difficult to recognise unaided (A) | A onset-only accuracy high but conflict trials offset-driven | A onset-only accuracy ≥ 85% with OI near 1: informed observers recognise slow onset order unaided |
| H2. Compressed replay (B) improves onset-order recognition | B improves w_off but not w_on (offset-based gain); gain concentrated in threshold shifts | w_on in B no greater than in A |
| H3. Static representation (C) improves onset-order recognition | C gain present but OI lower than in A (judging by a different cue) | w_on in C no greater than in A |
| H3b. C's gain reflects relational exposure beyond offloading (follow-up) | C-sequential retains part of the gain | C-sequential eliminates the gain entirely |
| H4. Observers judge by onset when asked about onset | OI between 0.5 and 0.8 (mixed cues) | OI ≤ 0.5 in all conditions: judgements are midpoint- or offset-based, so the task does not measure onset recognition |
| H5. Gains reflect sensitivity, not bias | Thresholds shift across conditions with modest weight change | Condition differences appear only in thresholds or confidence, with equal weights |
| H6. Detection and order are separable limitations | d′ and w_on strongly associated within conditions | Order gains fully tracked by detection gains (follow-up power required) |
| Programme premise: an instrument exposes a relationship not recognisable unaided | Gains small relative to between-participant variance | H1 falsified, or H2 and H3 both falsified |

---

## Part 12. Literature-supported decisions versus recommendations

| Design decision | Basis | Source status |
|---|---|---|
| Measure offset influence rather than rely on instructions | Empirical: offset asynchrony affects onset judgements (Jaśkowski 1991) | [P] |
| Expect gradual onsets to degrade order judgement | Empirical: rise-time dependence of order thresholds (Pastore 1988; Jaśkowski 1993) | [P], millisecond scales only |
| Expect gradual changes to escape detection under intentional viewing | Empirical (Simons et al. 2000) | [V] |
| Ternary response format | Empirical and methodological (García-Pérez & Alcalá-Quintana 2012) | [V] |
| Model response errors | Empirical (García-Pérez & Alcalá-Quintana 2012, *Frontiers*) | [V] |
| MPT as alternative joint model | Methodological (Batchelder & Riefer 1999) | [V] |
| Measure order, not rate or duration, under compression | Empirical speed and duration biases under time-lapse (Steinhof et al. 2025) plus invariance argument | [V] |
| Fix aspect ratio in C | Empirical (Cleveland, McGill & McGill 1988) | [V] |
| 12 per condition | Methodological rule of thumb (Julious 2005) | [V] |
| Orthogonal Δon × Δoff design and cue-weight model | Recommendation | Standard factorial logic, untested here |
| Constant magnitude | Recommendation | Weak support from Marples et al. on rate insensitivity [P] |
| Blocked detection and order | Recommendation | |
| Dropping D; C-sequential as offloading control | Recommendation | |
| Temporal dithering | Recommendation | Sufficiency untested |
| Compression factor 8, step 3 s, M = 10 L* | Recommendation | Provisional; tuned in pilot |

---

## Part 13. Recommendation

**REVISE.**

Justification by methodological readiness:

1. **The Task 02 protocol is not buildable as specified.** Its onset and offset cues are confounded, its primary measure compares selected subsets, and its main control (D) does not test offloading. Building it would produce data that cannot answer the question it was designed for.
2. **The revised protocol resolves the three structural defects** through the orthogonal cue design, the blocked detection and order design, and the replacement of D.
3. **Three items remain unverified and each could force redesign.** Whether the cue-weight model is recoverable at the planned trial count; whether dithering removes quantisation transients on ordinary displays; and whether the provisional parameters (s, M, compression factor) avoid floor and ceiling. The first two are checkable without participants.

Move to **BUILD** when the three gates in Part 10 pass. If parameter recovery fails at any burden under 30 minutes for condition A, move to **STOP** for this design and reconsider the candidate relationship.

---

## References

| Status | Reference |
|---|---|
| [V] | Alcalá-Quintana, R., & García-Pérez, M. A. (2013). Fitting model-based psychometric functions to simultaneity and temporal-order judgment data: MATLAB and R routines. *Behavior Research Methods*. doi:10.3758/s13428-013-0325-2 |
| [V] | Batchelder, W. H., & Riefer, D. M. (1999). Theoretical and empirical review of multinomial process tree modeling. *Psychonomic Bulletin & Review*, 6, 57–86. |
| [V] | Cleveland, W. S., McGill, M. E., & McGill, R. (1988). The shape parameter of a two-variable graph. *JASA*, 83, 289–300. |
| [V] | García-Pérez, M. A., & Alcalá-Quintana, R. (2012). Response errors explain the failure of independent-channels models of perception of temporal order. *Frontiers in Psychology*, 3. doi:10.3389/fpsyg.2012.00094 |
| [V] | García-Pérez, M. A., & Alcalá-Quintana, R. (2012). On the discrepant results in synchrony judgment and temporal-order judgment tasks: A quantitative model. *Psychonomic Bulletin & Review*. |
| [P] | Jaśkowski, P. (1991). Perceived onset simultaneity of stimuli with unequal durations. *Perception*, 20, 715–726. |
| [P] | Jaśkowski, P. (1993). Temporal-order judgment and reaction time to stimuli of different rise times. *Perception*, 22. |
| [V] | Julious, S. A. (2005). Sample size of 12 per group rule of thumb for a pilot study. *Pharmaceutical Statistics*, 4(4), 287–291. doi:10.1002/pst.185 |
| [P] | Marples, D., Carter, P., Gledhill, D., & Goodson, S. (2019). Broad environmental change blindness in virtual environments and video games. *Videogame Sciences and Arts*. |
| [P] | Pastore, R. E., et al. (1988). *Perception & Psychophysics*, 44, 257–271. |
| [V] | Simons, D. J., Franconeri, S. L., & Reimer, R. L. (2000). *Perception*, 29(10), 1143–1154. |
| [V] | Steinhof, V., Schroeger, A., Liepelt, R., & Sperl, L. (2025). *Cognitive Research: Principles and Implications*, 10(1), 36. |
| [P] | Ulrich, R. (1987). Threshold models of temporal-order judgments evaluated by a ternary response task. *Perception & Psychophysics*, 42, 224–239. |