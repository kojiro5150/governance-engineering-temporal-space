"""
Task 06 thin analysis wrapper for the provisionally accepted B3-t method.

What it does (and nothing more):
  1. Verifies the frozen Task 05 modules by SHA-256 and refuses on mismatch.
  2. Applies the pre-registered participant exclusions X1-X7 WITHOUT reading
     main-trial responses (D2 section 12).
  3. Assembles per-participant arrays of the 20 main order trials and calls the
     frozen e1_methods.run_b3 UNCHANGED, once per condition, with the
     pre-registered seed (D2 section 9).
  4. Reports the numeric B3-t results (the validated outputs) and, separately,
     EXPLORATORY DESCRIPTIVE CLASSIFICATIONS from the S6 rules (D2 section 5.2),
     which are not validated mechanism identifications (r3). Q1c and Q2c
     (D2 section 6); no classification is reported when the gate fails, and
     (r3.1, OD-21) none is reported for a primary analysis with n != 12, which
     is flagged as outside the validated operating-characteristic envelope.
  4b. Runs an exploratory add-back analysis (X2/X3 exclusions) as a numerical
     sensitivity analysis only: distinct analysis ID, no classification, no Q2.
  5. Produces Level 1 descriptive proportions and DESCRIPTIVE between-condition
     comparisons (no intervals, no inferential language; D2 section 7).

It does not modify the B3-t procedure. The only computational departure it can
make is recomputing weight intervals with t(n-1) when n != 12 (the frozen code
uses the constant t(0.975, 11)); that departure is flagged in the output.
The incomplete-trial OLS sensitivity analysis was removed from the plan (r3.1, OD-22)
and is not part of this wrapper.

Status: written for Task 06 review. Not run on participant data. Tested only
with deterministic, hand-constructed fixtures (tests/test_task06_analysis.py).

Usage:
  python3 task06_analysis.py exclude --trials T.csv --sessions S.json --frozen-code DIR --out exclusions.json
  python3 task06_analysis.py analyse --trials T.csv --sessions S.json --frozen-code DIR --out results.json [--mc-diagnostic]

Input formats: see DATA_DICTIONARY below.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import platform
import sys

sys.dont_write_bytecode = True  # never write caches into the frozen Task 05 code directory

import numpy as np  # noqa: E402
import scipy  # noqa: E402
from scipy.stats import t as student_t  # noqa: E402

WRAPPER_VERSION = "task06-wrapper-r3.1"

FROZEN_SHA256 = {
    "e1_methods.py": "db99b8ba6fd85e6d7a55609cad8cf9838db32c8fadd795b85a9664723263e1c9",
    "heterogeneity_methods.py": "3cfe209ac8a9d0a435fc74bd008ae07731f0849ef3581e1324a6ad36ba758f7d",
    "ordinal_model.py": "590db5f37b028e9ae82e8069d611f347d0a3b118b61e4d24685b7dda33ceb7fe",
    "stimulus.py": "238d882ab07d1f728bbc9454a0abe35af989afd0c3ce113bf04be50ec83bb0e3",
}
PINNED_ENV = {"python": "3.13.16", "numpy": "2.5.3", "scipy": "1.18.1"}

CONDITIONS = ("A", "B", "C")
N_MAIN = 20
N_CATCH = 4
N_PLANNED = 12
SEED_PRIMARY = "task06-primary-B3t-v1"
SEED_L1_BOOT = "task06-L1-boot-v1"
SEED_MCDIAG = "task06-mcdiag-v1"
SEED_ADDBACK = "task06-addback-B3t-v1"
L1_BOOT_RESAMPLES = 2000
MC_DIAG_SEEDS = 20
RESPONSE_CODE = {"R": 0, "S": 1, "L": 2}  # y; signed score s = y - 1 (frozen convention)

DATA_DICTIONARY = {
    "trials_csv": {
        "participant_code": "pseudonymous code",
        "condition": "A | B | C",
        "block": "calibration | practice | detection | order",
        "trial_kind": "order block only: main | catch",
        "template_id": "stimulus template id (frozen stimulus.py ids; catch ids start with 'catch')",
        "d_on": "onset(R) - onset(L), seconds (+ = left began first)",
        "d_off": "offset(R) - offset(L), seconds",
        "valid": "1 if the presentation was technically valid (D1 section 6.3), else 0",
        "response": "order block: L | S | R",
    },
    "sessions_json": {
        "participant_code": "pseudonymous code",
        "condition": "A | B | C",
        "calibration_correct": "integer 0-10",
        "attention_pass": "true | false",
        "frame_prop_within_1p5": "proportion of presentation frame intervals within 1.5x nominal",
        "viewport_css_px": "integer",
        "withdrawn": "true | false",
    },
}


# ----------------------------------------------------------------- utilities --
def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def seed_for(tag):
    """Task 05 convention: first 16 hex digits of SHA-256, as an integer."""
    return int(hashlib.sha256(tag.encode()).hexdigest()[:16], 16)


def wrap180(x):
    return (x + 180.0) % 360.0 - 180.0


def load_frozen(code_dir):
    """Verify and import the frozen Task 05 modules. Refuses on any mismatch."""
    bad = {}
    for f, h in FROZEN_SHA256.items():
        p = os.path.join(code_dir, f)
        got = sha256_file(p) if os.path.isfile(p) else None
        if got != h:
            bad[f] = got
    if bad:
        raise RuntimeError(f"REFUSING: frozen Task 05 code differs or is missing: {sorted(bad)}")
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    import e1_methods  # noqa: E402
    import stimulus  # noqa: E402
    return e1_methods, stimulus


def expected_main_cells(stimulus):
    """Multiset of (d_on, d_off) in the frozen 20-trial order template."""
    cells = {}
    for t in stimulus.order_templates(2, 4):
        k = (float(t.d_on), float(t.d_off))
        cells[k] = cells.get(k, 0) + 1
    return cells


def read_trials(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["valid"] = int(r["valid"])
        for k in ("d_on", "d_off"):
            r[k] = float(r[k]) if r.get(k) not in (None, "") else None
    return rows


def read_sessions(path):
    with open(path) as f:
        return {s["participant_code"]: s for s in json.load(f)}


# ---------------------------------------------------------------- exclusions --
def apply_exclusions(sessions, trials, stimulus):
    """Rules X1-X7 (D1 section 10.1). Reads calibration, attention, frame and
    viewport summaries, catch responses, and the VALIDITY and CELL of main
    trials. It never reads main-trial responses."""
    exp = expected_main_cells(stimulus)
    by_p = {}
    for r in trials:
        if r["block"] == "order":
            by_p.setdefault(r["participant_code"], []).append(r)
    out = {}
    for code in sorted(sessions):
        s = sessions[code]
        rules = []
        if int(s["calibration_correct"]) < 9:
            rules.append("X1")
        rows = by_p.get(code, [])
        catch = [r for r in rows if r["trial_kind"] == "catch" and r["valid"] == 1]
        leader = lambda r: "L" if r["d_on"] > 0 else "R"  # noqa: E731
        catch_errors = sum(r["response"] != leader(r) for r in catch)
        if catch_errors >= 3:
            rules.append("X2")
        if not bool(s["attention_pass"]):
            rules.append("X3")
        if float(s["frame_prop_within_1p5"]) < 0.95:
            rules.append("X4")
        if int(s["viewport_css_px"]) < 900:
            rules.append("X5")
        main_valid = [r for r in rows if r["trial_kind"] == "main" and r["valid"] == 1]
        got = {}
        for r in main_valid:
            k = (r["d_on"], r["d_off"])
            got[k] = got.get(k, 0) + 1
        ids = [r["template_id"] for r in main_valid]
        complete = (got == exp) and len(ids) == len(set(ids)) == N_MAIN and len(catch) == N_CATCH
        if not complete:
            rules.append("X6")
        if bool(s["withdrawn"]):
            rules.append("X7")
        out[code] = {"condition": s["condition"], "excluded": bool(rules), "rules": rules,
                     "catch_valid": len(catch), "catch_errors": int(catch_errors), "main_valid": len(main_valid)}
    return out


# ------------------------------------------------------------ interpretation --
# r3: the S6 rules are retained unchanged for traceability, but every label they
# produce is an EXPLORATORY DESCRIPTIVE CLASSIFICATION. The validated outputs are
# the numeric B3-t estimates, intervals and the Hotelling gate (Task 05). The
# classification thresholds are not validated, and no psychological mechanism
# is identified by any output of this wrapper.
CLASSIFICATION_STATUS = "EXPLORATORY DESCRIPTIVE CLASSIFICATION: NOT A VALIDATED MECHANISM IDENTIFICATION"
CLASSIFICATION_QUALIFICATION = ("Describes where the group-average, response-scale angle interval lies relative to "
                                "provisionally specified bands (Task 05 S6, operationalised in D2 section 5.2). "
                                "The bands are not validated. It does not identify a perceptual strategy, a "
                                "psychological mechanism, or any individual's strategy, and is not confirmatory evidence.")
S6_LABELS = ("onset-dominant cue weighting", "midpoint-like cue weighting", "offset-dominant cue weighting",
             "rate or duration cue", "numeric description only", "indeterminate: interval wider than 60 deg",
             "indeterminate: contains both 0 and 45 deg", "no statement: gate failed", "no statement: interval undefined")
INTERPRETATION_STATUS = {
    "validated_statistical_procedure": "B3-t estimator, t intervals, Hotelling sensitivity gate and B3-t angle interval: "
                                       "validated by simulation only (Task 05 E1, E1-H2, A1), at n = 12, J = 20, complete "
                                       "balanced data, under the Task 05 generator family",
    "descriptive_classification_rules": "S6 bands and rule order: provisionally specified, NOT validated; exploratory and descriptive only",
    "psychological_mechanisms": "NOT IDENTIFIED by any output of this analysis",
    "between_condition_comparisons": "descriptive only; no intervals; no tests",
    "addback_analyses": "exploratory numerical sensitivity only; no classification; no Q2 conclusion",
    "primary_analysis_n_not_12": "numeric B3-t results reported; outside the validated envelope; no classification; no Q2c (OD-21)",
}


def classify_s6(em, gate_pass, lo, hi):
    """S6 rules as operationalised in D2 section 5.2 (unchanged from r2; JDG).
    Returns a raw rule outcome. Callers must wrap it with
    descriptive_classification(); it is never reported on its own."""
    if not gate_pass:
        return "no statement: gate failed"
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return "no statement: interval undefined"
    c0, c45, c90, cm45 = (em.circ_contains(lo, hi, a) for a in (0.0, 45.0, 90.0, -45.0))
    if hi - lo > 60.0:
        return "indeterminate: interval wider than 60 deg"
    if c0 and c45:
        return "indeterminate: contains both 0 and 45 deg"
    if lo >= -10.0 and hi <= 25.0:
        return "onset-dominant cue weighting"
    if c45 and not c0:
        return "midpoint-like cue weighting"
    if c90 and not c45 and not c0:
        return "offset-dominant cue weighting"
    if cm45 and not c0:
        return "rate or duration cue"
    return "numeric description only"


def descriptive_classification(em, numeric, apply_rules=True, suppress_reason=None):
    """Exploratory descriptive classification object. Always carries its status,
    the numeric estimate, interval and gate it describes, and the qualification.
    The label is withheld when the gate fails or when classification is
    suppressed (add-back analyses)."""
    obj = {"status": CLASSIFICATION_STATUS, "validated": False, "mechanism_identified": False,
           "confirmatory": False, "qualification": CLASSIFICATION_QUALIFICATION,
           "numeric_context": {"beta_mean": numeric["beta_mean"], "weight_ci_95": numeric["weight_ci_95"],
                               "angle_deg": numeric["angle_deg"], "angle_ci_B3t_95": numeric["angle_ci_B3t_95"],
                               "gate": numeric["gate"]},
           "label": None, "suppressed_reason": None}
    if not apply_rules:
        obj["suppressed_reason"] = suppress_reason or "classification not applied"
        return obj
    if not numeric["gate"]["pass"]:
        obj["suppressed_reason"] = "gate failed: no angle-based classification is reported"
        return obj
    obj["label"] = classify_s6(em, True, *numeric["angle_ci_B3t_95"])
    return obj


def q2_outcome(s6_class):
    if s6_class == "onset-dominant cue weighting":
        return "expectation met"
    if s6_class in ("midpoint-like cue weighting", "offset-dominant cue weighting", "rate or duration cue"):
        return "expectation not met"
    return "indeterminate"


def q2_object(classification):
    status = ("pre-specified descriptive question derived from the exploratory classification; "
              "not confirmatory evidence of a perceptual strategy")
    if classification["label"] is None:
        return {"issued": False, "outcome": None, "status": status,
                "reason": classification["suppressed_reason"]}
    return {"issued": True, "outcome": q2_outcome(classification["label"]), "status": status, "reason": None}


# --------------------------------------------------------------- level 1 -----
def level1(per_participant, boot_seed):
    """Descriptive proportions with participant-cluster bootstrap intervals."""
    defs = {
        "onset_only_correct_leader": lambda don, doff, r: (doff == 0 and don != 0, r == ("L" if don > 0 else "R")),
        "simultaneous_same": lambda don, doff, r: (don == 0 and doff == 0, r == "S"),
        "conflict_onset_consistent": lambda don, doff, r: (don != 0 and doff == -don, r == ("L" if don > 0 else "R")),
    }
    res = {}
    rng = np.random.default_rng(boot_seed)
    idx = rng.integers(0, len(per_participant), size=(L1_BOOT_RESAMPLES, len(per_participant)))
    for name, fn in defs.items():
        k = np.zeros(len(per_participant)); n = np.zeros(len(per_participant))
        for i, rows in enumerate(per_participant):
            for (don, doff, r) in rows:
                inc, hit = fn(don, doff, r)
                if inc:
                    n[i] += 1; k[i] += hit
        p = float(k.sum() / n.sum())
        bs = k[idx].sum(1) / n[idx].sum(1)
        res[name] = {"proportion": p, "trials": int(n.sum()),
                     "cluster_boot_95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
    return res


# ------------------------------------------------------------------ analysis --
def _numeric_b3(em, cond, rows_by_p, seed_tag):
    """Assemble arrays and run the FROZEN run_b3 unchanged. Returns
    (numeric dict, departures, l1_rows, arrays) or None if n < 3."""
    codes = sorted(rows_by_p)
    n = len(codes)
    if n < 3:
        return None
    don = np.zeros((n, N_MAIN)); doff = np.zeros((n, N_MAIN)); y = np.zeros((n, N_MAIN), dtype=int)
    l1_rows = []
    for i, code in enumerate(codes):
        rows = sorted(rows_by_p[code], key=lambda r: (r["d_on"], r["d_off"], r["template_id"]))
        don[i] = [r["d_on"] for r in rows]
        doff[i] = [r["d_off"] for r in rows]
        y[i] = [RESPONSE_CODE[r["response"]] for r in rows]
        l1_rows.append([(r["d_on"], r["d_off"], r["response"]) for r in rows])
    seed = seed_for(f"{seed_tag}|{cond}")
    b3 = em.run_b3(don, doff, y, np.random.default_rng(seed))  # FROZEN procedure, unchanged
    ci_w = b3["ci_w"]
    departures = []
    if n != N_PLANNED:
        tcrit = float(student_t.ppf(0.975, n - 1))
        ci_w = [[b3["est"][i] - tcrit * b3["se"][i], b3["est"][i] + tcrit * b3["se"][i]] for i in range(2)]
        departures.append(f"n = {n} != 12: weight intervals recomputed with t(0.975, {n - 1}); frozen code uses "
                          "t(0.975, 11). The adjusted multiplier does NOT establish validated coverage at this n.")
    lo, hi = b3["angle_ci_t"]
    numeric = {
        "seed": str(seed),
        "participant_slopes": [[float(a), float(b)] for a, b in zip(*_slopes(em, don, doff, y))],
        "beta_mean": b3["est"], "se": b3["se"], "weight_ci_95": ci_w,
        "magnitude_response_scale": float(math.hypot(*b3["est"])),
        "gate": {"p": b3["gate_p"], "pass": b3["gate_pass"]},
        "angle_deg": b3["angle"],
        "angle_ci_B3t_95": [lo, hi],
        "angle_ci_B3boot_stored_not_reported": b3["angle_ci"],
        "contains": {str(a): bool(em.circ_contains(lo, hi, a)) for a in (0.0, 45.0, 90.0)},
    }
    return numeric, departures, l1_rows, (don, doff, y)


def analyse_condition(em, cond, rows_by_p, mc_diagnostic=False):
    """PRIMARY analysis for one condition (analysis_id PRIMARY-B3T-<c>)."""
    codes = sorted(rows_by_p)
    n = len(codes)
    out = {"analysis_id": f"PRIMARY-B3T-{cond}", "analysis_role": "primary", "condition": cond, "n": n,
           "participants": codes, "departures": [], "within_validated_design": n == N_PLANNED}
    got = _numeric_b3(em, cond, rows_by_p, SEED_PRIMARY)
    if got is None:
        out["status"] = "not computable (n < 3; Hotelling F(2, n-2) undefined)"
        return out
    numeric, departures, l1_rows, (don, doff, y) = got
    out["departures"] = departures
    # OD-21 (r3.1): a primary analysis with n != 12 is outside the validated
    # operating-characteristic envelope. Numeric B3-t results are preserved;
    # the S6 classification and Q2c are suppressed.
    outside = n != N_PLANNED
    out["outside_validated_envelope"] = outside
    if outside:
        out["envelope_note"] = (f"n = {n} differs from the validated n = 12: numeric B3-t results are reported, but they "
                                "are outside the validated operating-characteristic envelope. S6 classification and "
                                "Q2c are suppressed (OD-21).")
        classification = descriptive_classification(
            em, numeric, apply_rules=False,
            suppress_reason="primary analysis with n != 12 is outside the validated operating-characteristic "
                            "envelope: classification not applied (OD-21)")
        q2 = {"issued": False, "outcome": None,
              "status": "not issued: primary analysis outside the validated envelope (OD-21)",
              "reason": "n != 12"}
    else:
        classification = descriptive_classification(em, numeric)
        q2 = q2_object(classification)
    q1 = "gate passed" if numeric["gate"]["pass"] else "gate failed: no strategy statement"
    if outside:
        q1 += " (numeric only; outside the validated envelope)"
    out.update({"status": "computed", **numeric,
                "Q1_sensitivity": q1,
                "exploratory_descriptive_classification": classification,
                "Q2_cue_weighting": q2,
                "level1": level1(l1_rows, seed_for(f"{SEED_L1_BOOT}|{cond}"))})
    if mc_diagnostic:
        ends = []
        for k in range(MC_DIAG_SEEDS):
            r = em.run_b3(don, doff, y, np.random.default_rng(seed_for(f"{SEED_MCDIAG}|{cond}|{k}")))
            ends.append(r["angle_ci_t"])
        ends = np.array(ends, dtype=float)
        sd = np.nanstd(ends, axis=0, ddof=1)
        out["exploratory_mc_endpoint_sd_deg"] = {"lower": float(sd[0]), "upper": float(sd[1]),
                                                 "flag_gt_1deg": bool(np.nanmax(sd) > 1.0)}
    return out


def analyse_addback(em, cond, rows_by_p, added, primary):
    """EXPLORATORY add-back analysis (analysis_id EXPLORATORY-ADDBACK-X2X3-<c>).
    Numerical sensitivity only: no S6 classification and no Q2 conclusion, at
    any n (the inclusion criteria differ from the validated primary analysis)."""
    n = len(rows_by_p)
    out = {"analysis_id": f"EXPLORATORY-ADDBACK-X2X3-{cond}", "analysis_role": "exploratory_addback",
           "exploratory": True, "condition": cond, "n": n, "added_participants": added,
           "sample_size_departure": n != N_PLANNED, "inclusion_criteria_differ_from_primary": True,
           "within_validated_design": False,
           "numeric_status": ("UNVALIDATED: inclusion criteria differ from the validated primary analysis"
                              + (f"; n = {n} differs from the validated n = 12" if n != N_PLANNED else "")
                              + ". Numbers are reported for sensitivity comparison only; any adjusted t multiplier "
                                "does not establish validated coverage."),
           "label": "EXPLORATORY numerical sensitivity analysis; never replaces the primary result"}
    got = _numeric_b3(em, cond, rows_by_p, SEED_ADDBACK)
    if got is None:
        out["status"] = "not computable (n < 3)"
        return out
    numeric, departures, _, _ = got
    out.update({"status": "computed", "departures": departures, **numeric,
                "exploratory_descriptive_classification": descriptive_classification(
                    em, numeric, apply_rules=False,
                    suppress_reason="add-back analysis is outside the validated design: classification not applied"),
                "Q2_cue_weighting": {"issued": False, "outcome": None,
                                     "status": "not issued for exploratory add-back analyses",
                                     "reason": "outside the validated design"}})
    if primary.get("status") == "computed":
        out["difference_from_primary"] = {
            "n": n - primary["n"],
            "beta_mean": [numeric["beta_mean"][i] - primary["beta_mean"][i] for i in range(2)],
            "angle_deg": wrap180(numeric["angle_deg"] - primary["angle_deg"]),
            "gate_pass_primary": primary["gate"]["pass"], "gate_pass_addback": numeric["gate"]["pass"],
            "note": "numerical difference only; no interval; not an inferential comparison"}
    else:
        out["difference_from_primary"] = {"note": "primary analysis not computable"}
    return out


def _slopes(em, don, doff, y):
    import heterogeneity_methods as hm  # frozen; verified by load_frozen
    return hm.b3_individual(don, doff, y)


def describe_conditions(results):
    """Descriptive between-condition comparison (reviewer decision OD-03):
    side-by-side PRIMARY estimates for every condition, plus point differences
    against A only where both gates passed. No intervals, no tests, no
    inferential language. Labels appear only inside their exploratory
    classification object."""
    table = {}
    for c in CONDITIONS:
        r = results.get(c, {})
        cls = r.get("exploratory_descriptive_classification")
        table[c] = {"analysis_id": r.get("analysis_id"), "n": r.get("n"), "status": r.get("status"),
                    "gate_pass": r.get("gate", {}).get("pass"), "angle_deg": r.get("angle_deg"),
                    "angle_ci_B3t_95": r.get("angle_ci_B3t_95"),
                    "exploratory_descriptive_classification": None if cls is None else
                    {k: cls[k] for k in ("status", "validated", "mechanism_identified", "confirmatory", "label", "suppressed_reason")}}
    diffs = {}
    for c in ("B", "C"):
        a, b = results.get("A", {}), results.get(c, {})
        if a.get("gate", {}).get("pass") and b.get("gate", {}).get("pass"):
            diffs[f"{c}-A"] = {"point_difference_deg": wrap180(b["angle_deg"] - a["angle_deg"]),
                               "note": "descriptive only; no interval; |difference| <= 3 deg not interpretable as a latent difference"}
        else:
            diffs[f"{c}-A"] = {"point_difference_deg": None, "note": "not computed: a gate failed"}
    return {"label": "DESCRIPTIVE ONLY. Not an inferential comparison. Selection by gate and exclusions applies (D2 section 10.4).",
            "table": table, "point_differences_vs_A": diffs}


def run_analysis(trials_path, sessions_path, code_dir, mc_diagnostic=False):
    em, st = load_frozen(code_dir)
    trials = read_trials(trials_path)
    sessions = read_sessions(sessions_path)
    excl = apply_exclusions(sessions, trials, st)
    rows_by_c = {c: {} for c in CONDITIONS}
    for r in trials:
        p = r["participant_code"]
        if r["block"] == "order" and r["trial_kind"] == "main" and r["valid"] == 1 and p in excl and not excl[p]["excluded"]:
            rows_by_c[sessions[p]["condition"]].setdefault(p, []).append(r)
    results = {c: analyse_condition(em, c, rows_by_c[c], mc_diagnostic) for c in CONDITIONS}
    # Exploratory add-back (D2 section 10.4): participants excluded ONLY for
    # catch errors (X2) and/or the attention check (X3), with complete order data.
    rows_sel = {c: {p: list(v) for p, v in rows_by_c[c].items()} for c in CONDITIONS}
    for r in trials:
        p = r["participant_code"]
        if (r["block"] == "order" and r["trial_kind"] == "main" and r["valid"] == 1 and p in excl
                and excl[p]["excluded"] and set(excl[p]["rules"]) <= {"X2", "X3"}):
            rows_sel[sessions[p]["condition"]].setdefault(p, []).append(r)
    addback = {}
    for c in CONDITIONS:
        added = sorted(set(rows_sel[c]) - set(rows_by_c[c]))
        if added:
            addback[c] = analyse_addback(em, c, rows_sel[c], added, results[c])
        else:
            addback[c] = {"analysis_id": f"EXPLORATORY-ADDBACK-X2X3-{c}", "analysis_role": "exploratory_addback",
                          "exploratory": True, "added_participants": [],
                          "status": "not run: no participant excluded only under X2/X3"}
    env = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}
    return {
        "wrapper_version": WRAPPER_VERSION,
        "interpretation_status": INTERPRETATION_STATUS,
        "inputs_sha256": {"trials": sha256_file(trials_path), "sessions": sha256_file(sessions_path)},
        "frozen_code_sha256": FROZEN_SHA256,
        "wrapper_sha256": sha256_file(os.path.abspath(__file__)),
        "environment": env,
        "environment_matches_pinned": env == PINNED_ENV,
        "exclusions": excl,
        "exclusion_counts_by_condition": {c: {"starters": sum(v["condition"] == c for v in excl.values()),
                                              "excluded": sum(v["condition"] == c and v["excluded"] for v in excl.values()),
                                              "by_rule": {x: sum(v["condition"] == c and x in v["rules"] for v in excl.values())
                                                          for x in ("X1", "X2", "X3", "X4", "X5", "X6", "X7")}}
                                          for c in CONDITIONS},
        "results": results,
        "descriptive_comparison": describe_conditions(results),
        "exploratory_addback_analyses": addback,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["exclude", "analyse"])
    ap.add_argument("--trials", required=True); ap.add_argument("--sessions", required=True)
    ap.add_argument("--frozen-code", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--mc-diagnostic", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "exclude":
        _, st = load_frozen(a.frozen_code)
        res = apply_exclusions(read_sessions(a.sessions), read_trials(a.trials), st)
    else:
        res = run_analysis(a.trials, a.sessions, a.frozen_code, a.mc_diagnostic)
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
