# Task 06 D6: Evidence and Traceability Matrix

This is a working draft, revision r3.1 (2026-10-10). Rows marked **r3.1** were changed for OD-21 and OD-22 (see `task06-CHANGELOG-r3-to-r3.1.md`). Rows marked **r3** were added or changed for corrections A and B (see `task06-CHANGELOG-r2-to-r3.md`). Every consequential design or analysis choice in D1–D4 is traced to its source and classified by evidence type. Rows marked **r2** were added or changed in this revision (see `task06-CHANGELOG.md`).

## Evidence types

| Code | Meaning |
|---|---|
| **EST** | Established external evidence: a published empirical or methodological source |
| **DED** | Mathematical deduction |
| **SIM** | Simulation finding (Tasks 04 and 05; simulated observers only) |
| **JDG** | Methodological judgement |
| **REG** | Regulatory or procedural source |

## Literature status

- **Task 06 reviewed no external literature on perception or statistics.**
- External sources marked EST were reviewed in Task 03. They are cited as Task 03 recorded them, with its [V] (verified) and [P] (partly verified) status. They were **not re-read** in Task 06.
- Only two external sources were checked in Task 06:
  - the NHMRC National Statement 2023 update FAQ
  - the OSF Preregistration form structure

  Both were checked for procedural facts only.

## Abbreviations

| Abbreviation | Document |
|---|---|
| T03 | `research/working/task03-adversarial-protocol-review.md` |
| T04 | `research/working/task04/task04_stage2_artefacts.zip` |
| T05R | `task05/task05-statistical-robustness-review.md` |
| T05S | `task05/task05-revised-design-specification.md` |
| CL | `task05/task05-closure-decision-record.md` |
| A1 | `task05/task05-closure-addendum-A1-near-zero.md` |
| E1, E1H2 | `task05/results/E1/E1_REPORT.md` and `task05/results/E1H2/E1H2_REPORT.md` |
| v0.1 | `research/temporal-space-v0.1.md` |

All Task 05 paths are under `research/working/`.

---

## A. Framing and claims

| # | Decision (where used) | Source | Type |
|---|---|---|---|
| A1 | Stream 1 question and the visibility, comprehension and agency distinction; study limited to a precursor of visibility (D1 §1) | v0.1 §2 and §4.15 | JDG, on canonical framing |
| A2 | Four-level separation: performance, cue weighting, mechanism, perception claims (D1 §1, D2 §3) | Task 06 brief §3; CL §6 | JDG |
| A3 | Six binding claim limits (D2 §3.3, D4 item 25) | CL §6, approved by reviewer | SIM and DED basis; reviewer decision |
| A4 | Alternatives the study cannot separate (D1 §9.2) | T05R §6 (adversarial table); CL §6 | SIM, DED |
| A5 | C reported as static-trace performance only (D1 §4, D4) | T05S S8; T03 2.3 and 2.5 | SIM (graph-reading proxies), JDG |
| A6 | No "improves" hypotheses; Task 03 H1–H5 retired (D2 §6; OD-17) | Brief §3; T03 Part 11 used latent w_on and the onset index | JDG |
| A7 **r2** | Preregistered within-condition analyses distinguished from confirmatory effectiveness claims; study is an estimation and feasibility pilot | Reviewer decision 2026-10-10; D1 §1; D2 header and §6 | Reviewer decision; JDG |

## B. Design and stimuli

| # | Decision | Source | Type |
|---|---|---|---|
| B1 | Orthogonal 3 × 3 Δon × Δoff design; 20 order trials | T03 1.3 and 7.2; T04 `stimulus.py` | DED (factorial logic), JDG |
| B2 | Measure offset influence rather than rely on instructions | T03 1.1, citing Jaśkowski (1991) [P] | EST (via T03) |
| B3 | Constant magnitude | T03 1.4; weak support from Marples et al. (2019) [P] | JDG, EST (weak, via T03) |
| B4 | Ternary response format | T03 3.4, citing García-Pérez & Alcalá-Quintana (2012) [V] | EST (via T03) |
| B5 | Blocked design, detection before order | T03 3.3 | JDG |
| B6 | Between subjects, 3 conditions | T03 5.2 and 4.1 | JDG |
| B7 | Stimulus constants (T, D0, s, L0, M, ×8) | T03 6.3 and 6.6; T04 `stimulus.py` | JDG (provisional in T03) |
| B8 | Latest order offset 19.5 s; onsets in [1.5, 7.5] s | T05S S11 | DED |
| B9 | Sign convention Δon = onset(R) − onset(L); y = 2 is L; s = y − 1 | T04/T05 `stimulus.py`, `ordinal_model.py`, `heterogeneity_methods.py`; verified in Task 06 | DED (code inspection) |
| B10 | Four catch trials, specification and placement | T05S S4; T05 `catch_trials.py` | JDG, informed by SIM |
| B11 | TPDF dither replaces uniform | T05S S10; T04 `render_audit.json` | SIM (computational only) |
| B12 | Condition C plot geometry; fixed aspect ratio | T03 6.5, citing Cleveland et al. (1988) [V] | EST (via T03), JDG |
| B13 | B replay rules and 1 s mask | T03 4.1 and 6.6 | JDG |
| B14 | Order invariant under uniform compression | T03 4.1, citing Steinhof et al. (2025) [V], plus a logical argument | EST (via T03), DED |
| B15 | Detection templates and pairing | T04 `detection_templates()` SPEC-GAP | JDG |
| B16 | Seeded mulberry32; trial-seed rule; collision check | T03 6.2; T04 audit; D1 §3.8 (new check) | JDG |
| B17 | Inter-trial 1 s fixation and 1 s blank; per-disc yes/no detection response; re-queue stream | D1 §4, §5 and §6.3 [SG] | JDG (new) |
| B18 | Re-queue of invalid trials (OD-04) | D1 §6.3 | JDG (new); DED (keeps closed form exact) |
| B19 | Neutral instructions; no hypothesis disclosure | T03 1.5 and 4.1 | JDG |
| B20 | Allocation in permuted blocks, cap and replacement (OD-13) | D1 §6.1 | JDG (new) |
| B21 | Lab setting (OD-07) | D1 §2; D3 §6 | JDG (new) |
| B22 **r2** | M fixed before participant data collection: 10 L* unless E2 forces a change, then frozen before the first participant (OD-10) | T03 6.3 conflicts with preregistration; reviewer decision | JDG; reviewer decision |
| B23 **r2** | 100 ms per-trial rule and 28 min burden threshold are provisional, confirmed from E2 M1 and staff dry runs, then frozen (OD-08, OD-09) | Reviewer decision; D1 §6.3 and §13 | JDG (values not evidence-based) |
| B24 **r2** | Confidence rating removed (OD-16) | Burden; T03 8.1 | JDG |

## C. Analysis

| # | Decision | Source | Type |
|---|---|---|---|
| C1 | B3-t as primary method, provisional | CL §1 and §3; A1; reviewer decisions | SIM; reviewer decision |
| C2 | Primary estimand φ_β, response scale, gate mandatory | CL §2 | DED, SIM |
| C3 | Closed form valid only on the complete balanced set; OLS with intercept equal there | CL §3; D2 §4 | DED |
| C4 | Hotelling gate F(2, n − 2), α = 0.05; singular S means fail | E1 frozen code `run_b3` | DED (standard test), SIM (operating characteristics) |
| C5 | B3-t interval: 2,000 multivariate t(n − 1) draws, percentile, unwrapped | E1 AM3; `e1_methods.run_b3` | SIM (E1, E1H2, A1) |
| C6 | Circular containment | E1 AM4; A1 (6 linear disagreements at a = 0) | SIM, DED |
| C7 | Gate-failure prohibition; ungated interval invalid | A1 §A1.5, point 1 (ungated coverage 0.845 at a = 0.05) | SIM |
| C8 | S6 interpretation table, including the 60° rule | T05S S6; CL §2 | DED, SIM, JDG (60° rule) |
| C9 **r2** | Pre-specified within-condition questions Q1c and Q2c, which replace H1c and H2c; outcomes "expectation met / not met / indeterminate" (OD-17) | T03 H4, restated; reviewer decision | JDG |
| C10 | No family-wise correction; no family claim; no ranking (OD-02) | D2 §6 | JDG; reviewer decision |
| C11 **r2** | Between-condition comparisons descriptive only: side-by-side table and point differences without intervals (OD-03) | Reviewer decision; D2 §7 | Reviewer decision; DED (no validated contrast) |
| C12 | Contrast scale-artefact limit of about 3° | CL §2 (mapping distortion 2.84°) | DED under generator |
| C13 | Composition affects contrasts and angles | E1H2 §5 | SIM |
| C14 | S5 attention labelling rule and tolerances | T05S S5 | JDG, informed by SIM |
| C15 | Magnitudes are response-scale with no latent meaning | CL §6, claim limit 4 | SIM |
| C16 | Individual angles descriptive only | T05S S7; Validation B (0.77 and 0.43) | SIM |
| C17 | Catch-anchored lapse correction exploratory only | T05S S9 | SIM |
| C18 | Seeds, 2,000 draws, pinned environment, tolerances | D2 §9; T05 `config.json` versions | JDG |
| C19 **r3.1** | Complete cases with replacement; no analysis of incomplete participants (OLS sensitivity analysis removed, OD-22) | D2 §10.1 and §10.2; reviewer decision | DED, JDG; reviewer decision |
| C20 | T11 fixed in frozen code, so exact only at n = 12 | `e1_methods.run_b3` and `heterogeneity_methods.T11` | DED (code inspection) |
| C21 **r2, r3** | S6 operationalised as an ordered rule set: band edges −10° and 25° applied exactly; the offset rule is my judgement. **r3:** every label is an exploratory descriptive classification, not a validated mechanism identification. Reported only with the numeric context, never when the gate fails. The asymmetry across labels is documented | D2 §5.2; `classify_s6`, `descriptive_classification`; unit-tested | JDG. **Not validated:** unit tests show implementation consistency only |
| C22 **r2** | Selection-bias register: replacement, differential exclusion, X6, re-queue, gate, arm timing, recruitment. All numbers reported whatever the gate; exploratory add-back of X2/X3 exclusions | D2 §10.4; Task 05 S4 exclusion operating characteristics | JDG; SIM (exclusion rates in simulated observers only) |
| C23 **r2, r3, r3.1** | Thin wrapper verifies frozen hashes and calls `run_b3` unchanged. 41 deterministic unit tests (r3.1), no stochastic simulation. r2, r3 and r3.1 primary numeric outputs are identical on all fixtures (`supporting/verify_primary_unchanged_r2_r3.json`, `supporting/verify_primary_unchanged_r3_r3.1.json`) | `code/task06_analysis.py`; `code/tests/`; `code/TEST_RUN.log` | DED (tests check identities and equality with frozen code) |
| C24 **r3** | Add-back analysis: distinct ID and seed; always exploratory, including at n = 12; numbers marked unvalidated; differences from primary; no classification and no Q2c | D2 §10.5; reviewer correction B | Reviewer decision; JDG |
| C25 **r3.1** | Classification and Q2c suppressed for a primary analysis with n ≠ 12, numeric results kept and flagged outside the validated envelope (OD-21, approved); incomplete-trial OLS analysis removed (OD-22, approved) | D2 §10.2 and §10.3; D5; Task 05 validation envelope n = 12, J = 20 | Reviewer decision; SIM (envelope); DED (tests at n = 11, 12, 13) |

## D. Sample size and feasibility

| # | Decision | Source | Type |
|---|---|---|---|
| D1 | 12 per condition as a feasibility baseline | T03 5.2, citing Julious (2005) [V] | EST (via T03; rule of thumb), JDG |
| D2 | Gate power and false-claim rates by a | A1 §A1.3 | SIM |
| D3 | Coverage and discrimination at n = 12, J = 20 | E1, E1H2, CL §4 | SIM |
| D4 | a mapped to observable proportions (0.28, 0.41, 0.50, 0.73) | `supporting/model_response_probabilities.json` | DED (deterministic quadrature of the frozen generator; human parameters assumed) |
| D5 | Condition A is the binding risk | T03 H1 expectation combined with D2 above | JDG |
| D6 **r2** | V-C and V-N **not performed** (reviewer decision). Contrast inference is deferred to any future study | Reviewer decision 2026-10-10 | Reviewer decision |
| D7 | Feasibility criteria F1–F8 | T03 Part 9; F8 redefined per T05S §3, item 9 | JDG |
| D8 **r2** | Burden: 25.4 min modelled; F3 revised to task time ≤ 28 min, provisional (OD-08) | T05 `results/burden_with_catch.json`; T04 `burden.py` assumptions | SIM (assumption-driven model); JDG |

## E. Display validation (D3)

| # | Decision | Source | Type |
|---|---|---|---|
| E1 | Three or more configurations; M1–M4 outline | T05R §7.1 | JDG |
| E2 | M1-a frame criterion (≥ 95% within 1.5×) | T03 F4 | JDG (inherited) |
| E3 | M3 step periodicity and onset stationarity; variance-ratio range 0.58–1.65 | T05S S10; T04 `render_audit.json` | SIM (computational range); JDG (physical use) |
| E4 | M1-b, M2, M3-c, M4 and M5 tolerances | D3 | JDG (new; not validated) |
| E5 | E2 failure triggers a rendering, not statistical, revision | T05R §7.1, point 5 | JDG |
| E6 **r2** | E2 on every actual laboratory station; re-validation after any change; K2–K4 optional and not authorising | Reviewer decision; D3 §2 | JDG; reviewer decision |

## F. Governance

| # | Decision | Source | Type |
|---|---|---|---|
| F1 | Ethics review required; risk on a continuum; institutional responsibility | [NHMRC 2023 update FAQ](https://nhmrc.gov.au/research-policy/ethics/national-statement-ethical-conduct-human-research/2023-update-faqs), checked in Task 06 | REG |
| F2 | Preregistration structure (OSF Prereg v1, 25 items) | [preregr: OSF Prereg form (v1)](https://ftp.fau.de/cran/web/packages/preregr/vignettes/form_OSFprereg_v1.html), checked in Task 06 | REG |
| F3 | Privacy law applicability | Not assessed. Needs specialist confirmation (OD-14, **open**) | None |
| F6 **r2** | Ethics pathway unresolved until an eligible institution and review process are identified | Reviewer decision; D4 §8 | Reviewer decision |
| F4 | Pre-registration items list | T05S §3 | JDG |
| F5 | Deviations and amendment rules | Task 05 practice (frozen specs, amendments recorded separately); D2 §13 | JDG |
