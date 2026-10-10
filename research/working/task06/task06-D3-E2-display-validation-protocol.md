# Task 06 D3: E2 Physical-Display Validation Protocol

| Field | Value |
|---|---|
| Status | **Protocol only.** E2 is **NOT YET TESTED**. Nothing in this document has been performed, and no equipment has been bought |
| Revision | r2, 2026-10-10. E2 now validates **every actual laboratory testing station**. Thresholds approved as proposals (OD-18). The 100 ms rule is provisional. M is frozen after E2. See `task06-CHANGELOG.md` |
| Gate | E2 must pass before any participant data collection [REC, Task 05 Gate 5; closure record §9, item 1] |
| Labels | As in D1. **Thresholds marked [JDG] are proposals.** Only those marked [REC] come from the record, and even those are design choices, not validated perceptual limits |

---

## 1. What E2 must establish

1. **Timing.** Frames are delivered at the nominal rate, so analytic L*(t) reaches the screen on time. Condition B is the most demanding: s = 375 ms.
2. **Luminance.** Displayed luminance follows the intended L* within tolerance, including static levels, ramp linearity and end states.
3. **Dither.** TPDF dithering removes code-step transients without creating a visible or measurable onset cue. Undithered rendering is the comparison.
4. **Visibility.** Naive viewers cannot tell dithered static discs from undithered ones, and do not report steps or flicker in ramps.
5. **Condition C geometry.** Traces are drawn at the specified scale: 25 CSS px/s, 75 px per s-step, and fixed aspect ratio.

### Computational baseline

These come from Task 04 `render_audit.json` and the Task 05 review §7 [SIM, computational only]:

- One 8-bit code step is about 0.38–0.41 L*.
- A ramp spans 25–26 codes.
- Without dither, a step arrives every 0.34–0.60 s in A and every 0.04–0.07 s in B.
- Dithered static discs change code on 41–49% of frames, with SD about 0.5 code.
- Post-onset ÷ pre-onset frame-change variance:

| Dither | Mean ratio | 95% range |
|---|---|---|
| TPDF | 1.03 | 0.58–1.65 |
| Uniform | 0.72 | 0.42–1.10 |

E2 tests whether these hold on physical displays.

---

## 2. Test configurations

**Testing is in the laboratory (OD-07).** E2 must be run on **each actual testing station that will be used with participants** (K1-1, K1-2, …). A station means the exact computer, display, OS, GPU driver, browser version and display settings.

- **Identity.** Each station is identified by its computer and display serial numbers, which are recorded.
- **Only passing stations are used.** A station that has not passed E2 may not be used.
- **Re-validation.** Any change to a station after it passes requires E2 to be repeated for that station before further participant sessions. That includes hardware, OS or browser updates, driver changes and display settings.
- **Generality checks.** K2–K4 are optional generality checks [REC, Task 05 §7.1 minimum of three combinations]. They **do not** authorise participant testing on those configurations.
- **Three-combination minimum.** If fewer than three laboratory stations exist, the minimum is met by adding K2–K4.

| ID | Proposed example | Must record |
|---|---|---|
| K1-x (mandatory) | Each laboratory testing station | Serial numbers of computer and display; make and model; panel type; native resolution; refresh rate; OS and version; GPU and driver; browser and version; devicePixelRatio; OS colour management and HDR settings; display brightness and contrast settings; night-light and adaptive-brightness off |
| K2 (optional) | Chrome on a Windows laptop panel | As K1-x |
| K3 (optional) | Safari on a MacBook | As K1-x |
| K4 (optional) | Firefox on an external 60 Hz monitor | As K1-x |

**Conditions for every test:**

- Brightness locked.
- Display warmed up for 30 minutes or more.
- Room lighting fixed and recorded, with ambient illuminance measured at the screen.
- A fixed screen–sensor geometry, recorded.

---

## 3. Equipment

| Item | Purpose | Requirement |
|---|---|---|
| Photometer or colorimeter with a luminance reading (cd/m²) | Absolute and relative luminance | Calibration certificate or date recorded. Model to be decided, **not purchased under Task 06** |
| Photodiode with oscilloscope or data logger (≥ 1 kHz) | Frame-level luminance time series | Preferred for M3. Optional if a camera is used |
| Phone or camera in manual exposure, 120–240 fps | Fallback for temporal artefacts | **Not radiometric.** Valid for relative and temporal checks only, never for absolute luminance [REC, Task 05 §7.1 fallback] |
| Test build | Renders the stimuli | Same rendering code as the study build. Must log `requestAnimationFrame` timestamps |

---

## 4. Measurements

### M1. Frame timing (per configuration, per condition A, B and C)

**Procedure:**

- Run each condition's stimulus loop for 2 minutes, logging every `requestAnimationFrame` timestamp [REC, Task 05 §7.1].
- Repeat with the browser in its normal study state: fullscreen, no other tabs.

**Outputs:** nominal interval; median interval; 95th and 99th percentile intervals; maximum interval; proportion of intervals within 1.5× nominal; count over 100 ms.

**Acceptance:**

- **M1-a** [REC, Task 03 F4]: at least 95% of intervals within 1.5× nominal.
- **M1-b** [JDG]: no interval over 100 ms in 2 minutes. **Provisional.** The M1 distribution on each laboratory station is used to confirm or revise the per-trial invalidity threshold in D1 §6.3. A revision must lie well above the station's 99th percentile frame interval [JDG]. The final value is frozen before preregistration.
- **M1-c** [JDG]: if photodiode timing is available, photodiode and log timing agree to within 1 frame.

### M2. Static luminance and transfer function (per configuration)

**Procedure:**

- Full-field patches at 9 sRGB code values spanning the L* range used: L* = 35 (background), 45, 50, 55 (L0), 60, 65, 70 (fixation) and the two end states L0 ± 10.
- Then the disc itself at L0, L0 − 10 and L0 + 10 on the background, measured at the disc centre.

**Outputs:** measured luminance, converted to L* relative to the measured white.

**Acceptance** [JDG]:

- **M2-a:** end-state contrast |L*(L0 ± 10) − L*(L0)| is within ±1 L* of 10, on the darkening and lightening sides alike.
- **M2-b:** monotonic across all measured codes.

**If M2 fails:** apply a per-display correction (LUT) and re-measure. A LUT is a rendering change, so the stimulus audit must be re-run.

### M3. Ramp luminance time series: TPDF against no dither (per configuration, A and B)

**Procedure:**

- Render single-disc ramps in each direction:
  - 9 s and 15 s durations in A
  - the compressed equivalents in B
- Render each with TPDF and with no dither.
- Record with a photodiode at ≥ 1 kHz (preferred) or a camera at 120–240 fps.
- Repeat with static discs (no ramp) for 30 s in each dither mode.

**Analyses:**

- **(i) Linearity:** fit a line to the ramp in L* and report the residual RMS.
- **(ii) Step periodicity:** the power spectrum of the detrended ramp segment, at the expected code-step rate and its harmonics.
- **(iii) Onset stationarity:** the ratio of frame-to-frame luminance-change variance in a 1 s window after onset to the 1 s window before it, as in the computational audit.

**Acceptance:**

- **M3-a** [REC, Task 05 S10, restated for physical data]: with TPDF, no periodic component at the code-step rate. Proposed operationalisation [JDG]: spectral power at the step frequency is no more than 3× the median power in a ±20% band around it. The undithered recording must show the peak, as a positive control.
- **M3-b** [REC, S10; range JDG]: with TPDF, the post ÷ pre variance ratio falls within the computational 95% range of 0.58–1.65, averaged over at least 10 onsets per configuration.
- **M3-c** [JDG]: ramp linearity residual RMS ≤ 0.5 L*.

**Camera fallback:** M3-a and M3-b are assessed on relative pixel intensity from frames that are not saturated. M3-c is not assessed.

### M4. Blinded visibility assessment (each laboratory station K1-x)

[REC, Task 05 §7.1 outline; details JDG]

**Viewers:**

- Three naive viewers: not involved in the research, no knowledge of the hypotheses, eligible under D1.
- Viewers are **not** study participants, and their data are not study data.
- Ethics coverage for this step is **OPEN, OD-14**. It may need approval or a determination of exemption.

**Clips:**

- 20 short clips, 6 s each, shown in a randomised order generated from seed `task06-E2-visibility-v1`.

| Clip type | Count |
|---|---|
| Static disc, TPDF | 5 |
| Static disc, no dither | 5 |
| Ramp onset, TPDF (A timing) | 5 |
| Ramp onset, no dither (A timing) | 5 |

**Question after each clip:** "Did anything flicker, shimmer or jump in steps?" (yes/no).

**Acceptance** [JDG]:

- **M4-a:** static TPDF discs are not reported as flickering more often than static undithered discs. Across all viewers there are 15 TPDF and 15 undithered static presentations. The rule fails if TPDF "yes" exceeds undithered "yes" by 4 or more.
- **M4-b:** ramp-onset TPDF clips draw no more "yes" responses than static TPDF clips, by the same margin.
- **M4-c:** undithered ramp onsets are reported. This is a sensitivity check of the procedure; if viewers report nothing anywhere, M4 is inconclusive.

**Power warning.** With 3 viewers and 5 clips per type, M4 can detect only gross visibility. Passing M4 is weak evidence of invisibility.

**Viewer numbers (OD-18).** The minimum is 3 viewers, from the record. **The target is 5.** With 5 viewers there are 25 presentations per type, and the M4-a and M4-b failure margin becomes 6 or more [JDG]. The number of viewers is fixed before M4 begins.

### M5. Condition C geometry (per configuration)

**Procedure:** capture screenshots at native resolution.

**Acceptance** [REC, Task 03 6.5 specification; tolerance JDG]:

- **M5-a:** the time axis measures 600 CSS px ± 1 px.
- **M5-b:** a 3 s interval spans 75 CSS px ± 1 px.
- **M5-c:** panel heights are equal.
- **M5-d:** the line is continuous, with no gaps.
- **M5-e:** devicePixelRatio scaling preserves these figures in device pixels.

---

## 5. Logging and reproducibility

**For each configuration, keep an E2 record containing:**

- Hardware, software and settings (§2), with photographs of the settings screens.
- Raw files:
  - frame-time logs
  - photometer readings with timestamps
  - photodiode or camera recordings
  - visibility responses
  - screenshots
- Analysis scripts, with hashes.
- Operator, date, room illuminance.
- Any deviation.

**Analysis rules:**

- Analysis scripts are written and hashed before the measurements.
- Thresholds are fixed in this protocol (after reviewer approval) **before** measurement.
- Thresholds are not changed after measurement. If one proves unworkable, the change is recorded as an E2 amendment and the affected measurements are repeated.

---

## 6. Decision rules

| Outcome | Decision |
|---|---|
| All of M1–M5 pass on a laboratory station K1-x | **E2 PASS for that station.** Participants may be tested only on passing stations |
| M1 fails | That station may not be used. Change hardware or browser and repeat E2 |
| M2 fails | Apply a LUT correction, re-run the stimulus audit, repeat M2 and M3 |
| M3-a or M3-b fails (dither leaves a step pattern or an onset cue) | **Rendering redesign trigger.** Options: dither amplitude, spatio-temporal dither, a 10-bit display path, or a change to M. Any of these is a design change: re-audit and record it as an amendment. A change to M would also bear on feasibility criteria F5–F7 |
| M4 fails (dither visible) | **Rendering redesign trigger**, as above |
| M5 fails | Fix the layout code and repeat M5 |
| Any redesign | Re-run the computational render audit, then E2 from M1 on every station |
| E2 complete | **Freeze M** (D1 §3.2), the rendering code and the provisional 100 ms rule before preregistration. No later change without an amendment and repeat of E2 |

**E2 failure is a rendering problem, not a statistical one.** It does not reopen B3-t [REC, Task 05 §7.1, point 5].

**Scope of validity.** E2 validates only the stations tested. Study results apply only to presentation on E2-passing laboratory stations. Online testing on participants' own devices is not part of this study (OD-07), because E2 could not validate those displays.
