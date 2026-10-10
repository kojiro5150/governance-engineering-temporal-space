"""
Parameter-recovery simulation (Task 04, section 2).

Simulates one experimental condition (N participants x J order trials) many
times for each observer scenario and trial allocation, fits the corrected
ternary cumulative-logit model with participant random intercepts, and scores
recovery against PRE-SPECIFIED criteria (below). The criteria were written
before any simulation was run and must not be edited after seeing results;
any change must be recorded as a deviation in the Task 04 document.

Usage:
  python3 simulate_recovery.py --reps 1000 --workers 2 --out ../results/recovery
Outputs:
  <out>_fits.csv      one row per fit (for independent re-analysis)
  <out>_summary.json  scenario x allocation summaries and criterion results
"""
import argparse
import csv
import hashlib
import json
import time
from multiprocessing import Pool

import numpy as np

import stimulus as st
from ordinal_model import fit, simulate_responses

# ---------------------------------------------------------------------------
# PRE-SPECIFIED RECOVERY CRITERIA (fixed before running; do not edit)
# ---------------------------------------------------------------------------
CRITERIA = {
    "RC1_bias": "|mean(w_hat) - w_true| <= 0.10 * a for w_on and w_off, in every CORE scenario",
    "RC2_coverage": "95% Wald CI coverage for w_on and w_off within [0.90, 0.98], in every CORE scenario",
    "RC3_stability": "unstable-fit rate <= 0.05 in every scenario",
    "RC4_onset_vs_midpoint": ("P(angle CI excludes 45 deg | onset truth, moderate) >= 0.80 AND "
                              "P(angle CI excludes 0 deg | midpoint truth, moderate) >= 0.80"),
    "RC5_null_false_interpretation": "P(joint Wald test of (w_on, w_off) = 0 rejects at 0.05 | guessing) <= 0.07",
    "decision_rule": ("An allocation PASSES recovery only if RC1-RC5 all hold. The smallest passing "
                      "allocation within the 30-minute condition-A burden limit is recommended. "
                      "Low-sensitivity, lapse-heavy and heterogeneity scenarios are reported but are "
                      "not pass/fail criteria."),
}
TAU = 1.0
A_LOW, A_MOD, A_HIGH = 1 / 3, 0.70, 1.07   # onset-only P(correct leader) ~ 0.50, 0.75, 0.90
N_PARTICIPANTS = 12
ALLOCATIONS = {"J20 (k=2)": (2, 4), "J28 (k=3)": (3, 4), "J36 (k=4)": (4, 4)}

# name: (w_on, w_off, kwargs for simulate_responses, a, role)
SCENARIOS = {
    "S01 onset moderate":        (A_MOD, 0.0, {}, A_MOD, "core"),
    "S02 onset low":             (A_LOW, 0.0, {}, A_LOW, "report"),
    "S03 onset high":            (A_HIGH, 0.0, {}, A_HIGH, "core"),
    "S04 midpoint moderate":     (A_MOD / 2, A_MOD / 2, {}, A_MOD, "core"),
    "S05 midpoint low":          (A_LOW / 2, A_LOW / 2, {}, A_LOW, "report"),
    "S06 midpoint high":         (A_HIGH / 2, A_HIGH / 2, {}, A_HIGH, "core"),
    "S07 threshold-onset q=0.2": (0.8 * A_MOD, 0.2 * A_MOD, {}, A_MOD, "core"),
    "S08 offset moderate":       (0.0, A_MOD, {}, A_MOD, "core"),
    "S09 duration heuristic":    (A_MOD / 2, -A_MOD / 2, {}, A_MOD, "core"),
    "S10 guessing":              (0.0, 0.0, {}, A_MOD, "null"),
    "S11 biased onset":          (A_MOD, 0.0, {"bias_mean": 1.0, "bias_sd": 1.0}, A_MOD, "core"),
    "S12 lapse-heavy onset":     (A_MOD, 0.0, {"lapse": 0.15}, A_MOD, "report"),
    "S13 heterogeneous onset":   (A_MOD, 0.0, {"w_het_sd": 0.3, "tau_het_sd": 0.3}, A_MOD, "report"),
}
LAPSE_MODEL_SCENARIOS = {"S01 onset moderate", "S10 guessing", "S12 lapse-heavy onset"}
MASTER = "task04-recovery-v1"  # seed namespace unchanged by the v2 fitting deviation
N_ANGLE_DRAWS = 2000


def rep_seed(scen, alloc, rep):
    h = hashlib.sha256(f"{MASTER}|{scen}|{alloc}|{rep}".encode()).hexdigest()
    return int(h[:16], 16)


def angle_ci(w_on, w_off, cov, rng):
    try:
        draws = rng.multivariate_normal([w_on, w_off], cov, size=N_ANGLE_DRAWS, method="svd")
    except Exception:
        return np.nan, np.nan
    ang = np.degrees(np.arctan2(draws[:, 1], draws[:, 0]))
    centre = np.degrees(np.arctan2(w_off, w_on))
    # unwrap relative to the point estimate so intervals near +/-180 behave
    ang = (ang - centre + 180.0) % 360.0 - 180.0 + centre
    return float(np.percentile(ang, 2.5)), float(np.percentile(ang, 97.5))


def one_job(args):
    scen, alloc, rep, lapse_model = args
    w_on_t, w_off_t, kw, a, role = SCENARIOS[scen]
    k, m = ALLOCATIONS[alloc]
    tm = st.order_templates(k, m)
    don = np.tile([t.d_on for t in tm], (N_PARTICIPANTS, 1))
    doff = np.tile([t.d_off for t in tm], (N_PARTICIPANTS, 1))
    rng = np.random.default_rng(rep_seed(scen, alloc, rep))
    kw2 = {"tau": TAU, "lapse": 0.02, "bias_sd": 0.5}
    kw2.update(kw)
    y = simulate_responses(rng, don, doff, w_on_t, w_off_t, **kw2)
    f = fit(don, doff, y, lapse=lapse_model)
    cov = np.array(f["cov_w"])
    lo, hi = (angle_ci(f["w_on"], f["w_off"], cov, rng) if f["stable"] else (np.nan, np.nan))
    try:
        wald = float(np.array([f["w_on"], f["w_off"]]) @ np.linalg.solve(cov, [f["w_on"], f["w_off"]]))
    except Exception:
        wald = np.nan
    denom = abs(f["w_on"]) + abs(f["w_off"])
    return {"scenario": scen, "allocation": alloc, "rep": rep, "lapse_model": lapse_model,
            "w_on_true": w_on_t, "w_off_true": w_off_t, "a": a, "role": role,
            "w_on": f["w_on"], "w_off": f["w_off"], "se_w_on": f["se_w_on"], "se_w_off": f["se_w_off"],
            "theta1": f["theta1"], "theta2": f["theta2"], "sd_u": f["sd_u"], "lapse_hat": f["lapse"],
            "converged": f["converged"], "stable": f["stable"], "sd_u_at_boundary": f["sd_u_at_boundary"],
            "lapse_at_boundary": f["lapse_at_boundary"], "w_at_bound": f["w_at_bound"],
            "other_param_at_bound": f["other_param_at_bound"],
            "angle_lo": lo, "angle_hi": hi,
            "angle_hat": float(np.degrees(np.arctan2(f["w_off"], f["w_on"]))),
            "wald_chi2": wald, "OI_task03": (f["w_on"] / denom) if denom > 0 else np.nan,
            "resp_share_S": float(np.mean(y == 1))}


def summarise(rows):
    out = {}
    keys = sorted({(r["scenario"], r["allocation"], r["lapse_model"]) for r in rows})
    for key in keys:
        R = [r for r in rows if (r["scenario"], r["allocation"], r["lapse_model"]) == key]
        S = [r for r in R if r["stable"]]
        n, ns = len(R), len(S)
        d = {"reps": n, "stable": ns, "unstable_rate": round(1 - ns / n, 4),
             "sd_u_boundary_rate": round(float(np.mean([r["sd_u_at_boundary"] for r in R])), 4)}
        if ns:
            a = R[0]["a"]
            won = np.array([r["w_on"] for r in S]); woff = np.array([r["w_off"] for r in S])
            son = np.array([r["se_w_on"] for r in S]); soff = np.array([r["se_w_off"] for r in S])
            ton, toff = R[0]["w_on_true"], R[0]["w_off_true"]
            cov_on = np.mean(np.abs(won - ton) <= 1.96 * son)
            cov_off = np.mean(np.abs(woff - toff) <= 1.96 * soff)
            true_ang = np.degrees(np.arctan2(toff, ton)) if (ton or toff) else np.nan
            lo = np.array([r["angle_lo"] for r in S]); hi = np.array([r["angle_hi"] for r in S])
            wald = np.array([r["wald_chi2"] for r in S])
            oi = np.array([r["OI_task03"] for r in S])
            d.update({
                "w_on_true": round(ton, 4), "w_off_true": round(toff, 4), "a": round(a, 4),
                "w_on_mean": round(float(won.mean()), 4), "w_off_mean": round(float(woff.mean()), 4),
                "bias_w_on": round(float(won.mean() - ton), 4), "bias_w_off": round(float(woff.mean() - toff), 4),
                "bias_w_on_over_a": round(float((won.mean() - ton) / a), 4),
                "bias_w_off_over_a": round(float((woff.mean() - toff) / a), 4),
                "rmse_w_on": round(float(np.sqrt(np.mean((won - ton) ** 2))), 4),
                "rmse_w_off": round(float(np.sqrt(np.mean((woff - toff) ** 2))), 4),
                "empirical_sd_w_on": round(float(won.std(ddof=1)), 4),
                "median_se_w_on": round(float(np.median(son)), 4),
                "median_se_w_off": round(float(np.median(soff)), 4),
                "coverage_w_on": round(float(cov_on), 4), "coverage_w_off": round(float(cov_off), 4),
                "mc_se_coverage": round(float(np.sqrt(0.95 * 0.05 / ns)), 4),
                "true_angle_deg": None if np.isnan(true_ang) else round(float(true_ang), 2),
                "p_angle_ci_covers_truth": (None if np.isnan(true_ang) else
                                            round(float(np.mean((lo <= true_ang) & (hi >= true_ang))), 4)),
                "p_angle_ci_excludes_0": round(float(np.mean((lo > 0) | (hi < 0))), 4),
                "p_angle_ci_excludes_45": round(float(np.mean((lo > 45) | (hi < 45))), 4),
                "p_angle_ci_excludes_-45": round(float(np.mean((lo > -45) | (hi < -45))), 4),
                "median_angle_ci_width": round(float(np.median(hi - lo)), 2),
                "p_wald_reject_0.05": round(float(np.mean(wald > 5.991)), 4),
                "OI_task03_mean": round(float(np.nanmean(oi)), 4),
                "OI_task03_p5_p95": [round(float(np.nanpercentile(oi, 5)), 4),
                                     round(float(np.nanpercentile(oi, 95)), 4)],
                "between_condition_SE_diff_w_on(approx sqrt2*median_se)": round(float(np.sqrt(2) * np.median(son)), 4),
                "mean_share_S_responses": round(float(np.mean([r["resp_share_S"] for r in S])), 4),
                "lapse_hat_median": round(float(np.median([r["lapse_hat"] for r in S])), 4),
            })
        out[" | ".join([key[0], key[1], "lapse-model" if key[2] else "standard-model"])] = d
    return out


def evaluate(summary):
    res = {}
    for alloc in ALLOCATIONS:
        def g(s):
            return summary.get(f"{s} | {alloc} | standard-model", {})
        core = [s for s, v in SCENARIOS.items() if v[4] == "core"]
        rc1 = {s: (abs(g(s)["bias_w_on_over_a"]) <= 0.10 and abs(g(s)["bias_w_off_over_a"]) <= 0.10) for s in core}
        rc2 = {s: (0.90 <= g(s)["coverage_w_on"] <= 0.98 and 0.90 <= g(s)["coverage_w_off"] <= 0.98) for s in core}
        rc3 = {s: g(s)["unstable_rate"] <= 0.05 for s in SCENARIOS}
        rc4 = {"onset_excludes_45": g("S01 onset moderate")["p_angle_ci_excludes_45"],
               "midpoint_excludes_0": g("S04 midpoint moderate")["p_angle_ci_excludes_0"]}
        rc4_pass = rc4["onset_excludes_45"] >= 0.80 and rc4["midpoint_excludes_0"] >= 0.80
        rc5 = g("S10 guessing")["p_wald_reject_0.05"]
        res[alloc] = {"RC1_pass": all(rc1.values()), "RC1_detail": rc1,
                      "RC2_pass": all(rc2.values()), "RC2_detail": rc2,
                      "RC3_pass": all(rc3.values()), "RC3_detail": rc3,
                      "RC4_pass": rc4_pass, "RC4_detail": rc4,
                      "RC5_pass": rc5 <= 0.07, "RC5_detail": rc5}
        res[alloc]["ALL_PASS"] = all(res[alloc][k] for k in
                                     ["RC1_pass", "RC2_pass", "RC3_pass", "RC4_pass", "RC5_pass"])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default="../results/recovery")
    args = ap.parse_args()
    jobs = []
    for alloc in ALLOCATIONS:
        for scen in SCENARIOS:
            for rep in range(args.reps):
                jobs.append((scen, alloc, rep, False))
                if scen in LAPSE_MODEL_SCENARIOS:
                    jobs.append((scen, alloc, rep, True))
    t0 = time.time()
    with Pool(args.workers) as p:
        rows = p.map(one_job, jobs, chunksize=50)
    with open(args.out + "_fits.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    summary = summarise(rows)
    result = {"criteria": CRITERIA, "reps_per_cell": args.reps, "n_participants": N_PARTICIPANTS,
              "tau": TAU, "sensitivity_levels": {"low": A_LOW, "moderate": A_MOD, "high": A_HIGH},
              "allocations": {k: {"reps_per_nonzero_cell": v[0], "simultaneous": v[1],
                                  "J": 8 * v[0] + v[1]} for k, v in ALLOCATIONS.items()},
              "baseline_generation": {"lapse": 0.02, "bias_sd": 0.5, "tau": TAU},
              "n_fits": len(rows), "runtime_s": round(time.time() - t0, 1),
              "evaluation": evaluate(summary), "summary": summary}
    with open(args.out + "_summary.json", "w") as f:
        json.dump(result, f, indent=1)
    print(json.dumps(result["evaluation"], indent=1))
    print("fits:", len(rows), "runtime s:", result["runtime_s"])


if __name__ == "__main__":
    main()
