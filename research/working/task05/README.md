# Task 05: statistical robustness and experimental design revision

This is a working record. It is not canonical v0.1, it does not modify Tasks 02–04, and it contains no participant data.

The reviewer approved this record for repository commit on 2026-10-10. Task 06 is not authorised by this record.

## Decision lineage

Each item below is kept as separate evidence. No later item changes an earlier frozen verdict.

| Order | Item | Outcome | Document |
|---|---|---|---|
| 1 | Task 05 review (Validations A, B, C; adversarial review; gate closure) | As reported | `task05-statistical-robustness-review.md`, `task05-revised-design-specification.md` |
| 2 | **E1** frozen heterogeneity validation (B2, B3-boot, B3-t; 3,500 datasets) | **REVISE**: no variant acceptable. **Preserved** | `results/E1/E1_FROZEN_SPEC.md`, `results/E1/E1_REPORT.md` |
| 3 | **E1-H2** confirmatory amendment, made after the results (random mixture membership; 500 datasets) | H2-population criteria met by B2 and B3-t | `results/E1H2/E1H2_FROZEN_SPEC.md`, `results/E1H2/E1H2_REPORT.md` |
| 4 | Closure decision record | B3-t **provisionally** accepted | `task05-closure-decision-record.md` |
| 5 | **Addendum A1**: B3-t near-zero sensitivity validation (1,000 datasets) | CONFIRMED; 10 Monte Carlo-indeterminate margins | `task05-closure-addendum-A1-near-zero.md` |
| 6 | Reviewer final decision | Approved for commit | This README |

## What was approved

- **Primary estimand:** the population-average, response-scale cue-weighting angle φ_β.
- **Method:** B3-t, using the exact validated complete-design procedure at n = 12 and J = 20.
- **Sensitivity gate:** mandatory.
- **Claim limits:** six, binding, set out in closure record Section 6.
- **Not supported:** claims about individual strategies, about distinguishing mechanisms, or that temporal augmentation improves human perception.

**Still outstanding:**

- E2 physical display validation (Gate 5).
- The Task 06 pre-registration items listed in closure record Section 9 and Addendum A1, Section A1.7.

## Layout

| Path | Contents |
|---|---|
| `*.md` (top level) | Review, design specification, closure record, Addendum A1, this README |
| `config.json` | Task 05 environment, inherited-code hashes, Task 05 code hashes |
| `code/` | Task 05 code. Inherited Task 04 modules are byte-identical to the Task 04 archive |
| `code/post_hoc/` | Exploratory run D5, not counted as evidence |
| `code/e1h2/` | E1-H2 amendment code |
| `code/nz/` | A1 code |
| `results/validationA/`, `validationB/`, `validationC/` | Task 05 validation outputs, including checkpointed raw batches |
| `results/adversarial_checks.json`, `results/burden_with_catch.json` | Adversarial review and burden outputs |
| `results/E1/` | Frozen spec, pre-checks, raw run batches, analysis, report, post-hoc diagnostic |
| `results/E1H2/` | Frozen spec, pre-check, raw run batches, analysis, report |
| `results/NZ/` | Frozen spec, pre-check, raw run batches, analysis |
| `logs/` | Run, analysis and pre-check logs; `DEVIATIONS.md`; checksum manifests |
| `INTEGRITY/` | Verifier script, its report for this commit, and a full SHA-256 manifest of this directory |

## Integrity

Re-run the checks from this directory:

```
python3 INTEGRITY/verify_task05_record.py . ../task04/task04_stage2_artefacts.zip "" INTEGRITY/integrity_report.json
sha256sum -c INTEGRITY/MANIFEST_SHA256.txt
```

### Base directories of the checksum manifests

These files were written from different working directories. They are kept **unaltered** because later manifests hash them. Resolve their paths as follows:

| Manifest | Base directory for its paths |
|---|---|
| `logs/TASK05_CLOSURE_SHA256SUMS.txt` | This directory |
| `logs/TASK05_ADDENDUM_A1_SHA256SUMS.txt` | This directory |
| `results/E1/E1_raw_SHA256SUMS` | `results/E1/run/` |
| `results/E1H2/E1H2_raw_SHA256SUMS` | `results/E1H2/run/` for `batch_*`, `manifest.json` and `progress.jsonl`; `results/E1H2/` for the rest |
| `results/NZ/NZ_raw_SHA256SUMS` | `results/NZ/run/` for `batch_*`, `manifest.json` and `progress.jsonl`; `results/NZ/` for the rest |
| `logs/inherited_code_sha256.txt` | `code/` |
| `logs/E1H2_original_E1_hashes_before.txt` | `code/e1h2/` |
| `logs/NZ_prior_hashes_before.txt` | `code/nz/` |
| `logs/*_FROZEN_SPEC.sha256` | Single hash of the matching frozen spec |
| `INTEGRITY/MANIFEST_SHA256.txt` | This directory |

### Known, reconciled difference

`logs/DEVIATIONS.md` is append-only. Its hash in `TASK05_CLOSURE_SHA256SUMS.txt` is that of the closure-time version. The E1-H2 and A1 entries were appended after that hash was taken. The verifier confirms that the closure-time version is an exact byte prefix of the committed file. Every other closure-manifest entry matches.

## Not included

The working folder also held files from two earlier, unreviewed Task 05 attempts. They were not inputs to this review and are not committed. `config.json` lists them under `not_part_of_this_review_left_in_workspace`, and `code/README_TASK05.md` names them. They include:

- `run_validation_a.py`, `runner.py`, `timing_test_b.py` and related scripts
- `code/t04/`
- `results/validation_a/`, `results/A_check/` and `results/A_core_J20_reps500/`

Task 04 artefacts that the review cites, such as `model_checks.json` and `render_audit.json`, are in `../task04/task04_stage2_artefacts.zip`.
