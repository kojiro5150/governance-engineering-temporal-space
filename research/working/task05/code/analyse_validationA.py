"""
Validation A analysis: core scenarios, J = 20, reps 0-499.

1. Verifies that reps 0-99 reproduce the archived Task 04 Stage 2 fits exactly.
2. Reports bias, variability, coverage with Monte Carlo uncertainty (Wilson
   95% intervals), fit failures, boundary estimates and strategy
   discrimination, for reps 0-99 and 0-499 side by side.
3. Classifies each pre-specified criterion as clearly met / clearly not met /
   indeterminate given Monte Carlo uncertainty.

Usage: python3 analyse_validationA.py RUN_DIR STAGE2_FITS_CSV OUT_JSON
"""
import csv
import json
import math
import sys

import numpy as np

KEYS_EXACT = ["w_on", "w_off", "se_w_on", "se_w_off", "theta1", "theta2", "sd_u", "angle_lo", "angle_hi", "stable"]
A_OF = {"S01 onset moderate": 0.7, "S03 onset high": 1.07, "S04 midpoint moderate": 0.7,
        "S06 midpoint high": 1.07, "S07 threshold-onset q=0.2": 0.7, "S08 offset moderate": 0.7,
        "S09 duration heuristic": 0.7, "S11 biased onset": 0.7}


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(c - h, 4), round(c + h, 4))


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def classify(lo, hi, band_lo, band_hi):
    if lo >= band_lo and hi <= band_hi:
        return "clearly met"
    if hi < band_lo or lo > band_hi:
        return "clearly not met"
    return "indeterminate (MC interval straddles boundary)"


def summarise(R, scen):
    S = [r for r in R if r["stable"] == "True"]
    n, ns = len(R), len(S)
    a = A_OF[scen]
    ton, toff = f(R[0]["w_on_true"]), f(R[0]["w_off_true"])
    won = np.array([f(r["w_on"]) for r in S]); woff = np.array([f(r["w_off"]) for r in S])
    son = np.array([f(r["se_w_on"]) for r in S]); soff = np.array([f(r["se_w_off"]) for r in S])
    lo = np.array([f(r["angle_lo"]) for r in S]); hi = np.array([f(r["angle_hi"]) for r in S])
    k_on = int(np.sum(np.abs(won - ton) <= 1.96 * son)); k_off = int(np.sum(np.abs(woff - toff) <= 1.96 * soff))
    true_ang = math.degrees(math.atan2(toff, ton))
    ex0 = int(np.sum((lo > 0) | (hi < 0))); ex45 = int(np.sum((lo > 45) | (hi < 45)))
    cov_truth = int(np.sum((lo <= true_ang) & (hi >= true_ang)))
    bias_on = won.mean() - ton; bias_off = woff.mean() - toff
    mcse_on = won.std(ddof=1) / math.sqrt(ns); mcse_off = woff.std(ddof=1) / math.sqrt(ns)
    return {
        "reps": n, "stable": ns, "unstable": n - ns, "unstable_rate_wilson95": wilson(n - ns, n),
        "sd_u_at_boundary": int(sum(r["sd_u_at_boundary"] == "True" for r in R)),
        "true": [ton, toff], "a": a,
        "bias_w_on_over_a": round(bias_on / a, 4), "bias_w_on_over_a_mc95": [round((bias_on - 1.96 * mcse_on) / a, 4), round((bias_on + 1.96 * mcse_on) / a, 4)],
        "bias_w_off_over_a": round(bias_off / a, 4), "bias_w_off_over_a_mc95": [round((bias_off - 1.96 * mcse_off) / a, 4), round((bias_off + 1.96 * mcse_off) / a, 4)],
        "empirical_sd_w_on": round(float(won.std(ddof=1)), 4), "median_se_w_on": round(float(np.median(son)), 4),
        "se_ratio_on(median_se/empirical_sd)": round(float(np.median(son) / won.std(ddof=1)), 3),
        "empirical_sd_w_off": round(float(woff.std(ddof=1)), 4), "median_se_w_off": round(float(np.median(soff)), 4),
        "se_ratio_off": round(float(np.median(soff) / woff.std(ddof=1)), 3),
        "coverage_w_on": round(k_on / ns, 4), "coverage_w_on_wilson95": wilson(k_on, ns),
        "coverage_w_off": round(k_off / ns, 4), "coverage_w_off_wilson95": wilson(k_off, ns),
        "angle_true_deg": round(true_ang, 2),
        "angle_ci_covers_truth": round(cov_truth / ns, 4), "angle_ci_covers_truth_wilson95": wilson(cov_truth, ns),
        "angle_ci_excludes_0": round(ex0 / ns, 4), "angle_ci_excludes_0_wilson95": wilson(ex0, ns),
        "angle_ci_excludes_45": round(ex45 / ns, 4), "angle_ci_excludes_45_wilson95": wilson(ex45, ns),
        "median_angle_ci_width": round(float(np.median(hi - lo)), 2),
    }


def main(run_dir, stage2_csv, out):
    rows = list(csv.DictReader(open(f"{run_dir}/fits.csv")))
    s2 = {r["job_id"]: r for r in csv.DictReader(open(stage2_csv))}
    # 1. exact reproduction of Stage 2 for reps 0-99
    compared, mismatches = 0, []
    for r in rows:
        if r["job_id"] in s2:
            compared += 1
            for k in KEYS_EXACT:
                if r[k] != s2[r["job_id"]][k]:
                    mismatches.append((r["job_id"], k, r[k], s2[r["job_id"]][k]))
    res = {"reproduction_of_stage2": {"fits_compared": compared, "fields_compared": KEYS_EXACT,
                                      "mismatches": len(mismatches), "examples": mismatches[:5]},
           "n_fits": len(rows), "by_scenario": {}}
    for scen in A_OF:
        R = [r for r in rows if r["scenario"] == scen]
        R100 = [r for r in R if int(r["rep"]) < 100]
        res["by_scenario"][scen] = {"reps_0_99": summarise(R100, scen), "reps_0_499": summarise(R, scen)}
    # 3. criteria with MC uncertainty (reps 0-499)
    crit = {}
    for scen, d in res["by_scenario"].items():
        x = d["reps_0_499"]
        crit[scen] = {
            "RC1_bias_w_on": classify(*x["bias_w_on_over_a_mc95"], -0.10, 0.10),
            "RC1_bias_w_off": classify(*x["bias_w_off_over_a_mc95"], -0.10, 0.10),
            "RC2_coverage_w_on": classify(*x["coverage_w_on_wilson95"], 0.90, 0.98),
            "RC2_coverage_w_off": classify(*x["coverage_w_off_wilson95"], 0.90, 0.98),
            "RC3_unstable": classify(*x["unstable_rate_wilson95"], 0.0, 0.05),
        }
    x1 = res["by_scenario"]["S01 onset moderate"]["reps_0_499"]
    x4 = res["by_scenario"]["S04 midpoint moderate"]["reps_0_499"]
    crit["RC4_onset_excludes_45"] = classify(*x1["angle_ci_excludes_45_wilson95"], 0.80, 1.0)
    crit["RC4_midpoint_excludes_0"] = classify(*x4["angle_ci_excludes_0_wilson95"], 0.80, 1.0)
    res["criteria_with_mc_uncertainty"] = crit
    with open(out, "w") as fo:
        json.dump(res, fo, indent=1)
    print(json.dumps(res["reproduction_of_stage2"], indent=1))
    hdr = ["unstable", "sd_u_at_boundary", "bias_w_on_over_a", "bias_w_off_over_a", "se_ratio_on(median_se/empirical_sd)",
           "coverage_w_on", "coverage_w_on_wilson95", "coverage_w_off", "coverage_w_off_wilson95",
           "angle_ci_excludes_0", "angle_ci_excludes_45", "angle_ci_covers_truth", "median_angle_ci_width"]
    for scen, d in res["by_scenario"].items():
        print("\n##", scen)
        for part in ("reps_0_99", "reps_0_499"):
            print(" ", part, {h: d[part][h] for h in hdr})
    print("\nCRITERIA:", json.dumps(crit, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
