"""
E1 analysis. Reads targets, criteria and the decision rule ONLY from the
frozen specification; refuses to analyse a run produced under a different
specification or code.

Usage: python3 e1_analyse.py --spec ../results/E1/E1_FROZEN_SPEC.json --run-dir ../results/E1/run --out ../results/E1/E1_results.json
"""
import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

import e1_methods as em
from e1_run import load, sha


def wilson(k, n, z=1.96):
    if n == 0:
        return [float("nan"), float("nan")]
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(c - h, 4), round(c + h, 4)]


def classify_band(k, n, lo, hi):
    w = wilson(k, n); p = k / n
    if not (lo <= p <= hi):
        status = "not met (point estimate)"
    else:
        status = "met"
    if w[0] >= lo and w[1] <= hi:
        mc = "clearly inside"
    elif w[1] < lo or w[0] > hi:
        mc = "clearly outside"
    else:
        mc = "indeterminate"
    return {"k": k, "n": n, "rate": round(p, 4), "wilson95": w, "point_status": status, "mc_status": mc}


def classify_min(k, n, thr):
    w = wilson(k, n); p = k / n
    return {"k": k, "n": n, "rate": round(p, 4), "wilson95": w, "point_status": "met" if p >= thr else "not met (point estimate)",
            "mc_status": "clearly inside" if w[0] >= thr else ("clearly outside" if w[1] < thr else "indeterminate")}


def classify_max(k, n, thr):
    w = wilson(k, n); p = k / n
    return {"k": k, "n": n, "rate": round(p, 4), "wilson95": w, "point_status": "met" if p <= thr else "not met (point estimate)",
            "mc_status": "clearly inside" if w[1] <= thr else ("clearly outside" if w[0] > thr else "indeterminate")}


def main(a):
    spec = json.load(open(a.spec))
    man = json.load(open(os.path.join(a.run_dir, "manifest.json")))
    if man["frozen_spec_sha256"] != sha(a.spec):
        sys.exit("REFUSING: run was not produced under this frozen spec")
    rows, dups = load(a.run_dir)
    if dups:
        sys.exit(f"REFUSING: {len(dups)} duplicate job_ids")
    exp = {f"{s}|rep{r}" for s in spec["scenarios"] for r in range(spec["reps"])}
    if {r["job_id"] for r in rows} != exp:
        sys.exit("REFUSING: run incomplete or has unexpected jobs")
    T = spec["targets"]; C = spec["criteria"]
    methods = {"B2": ("B2", "angle_ci", "theta_star", "angle_theta_star"),
               "B3-boot": ("B3", "angle_ci", "beta_star", "angle_beta_star"),
               "B3-t": ("B3", "angle_ci_t", "beta_star", "angle_beta_star")}
    res = {"n_rows": len(rows), "errors": sum(r["status"] == "error" for r in rows), "by_method": {}}
    for mname, (key, ci_key, tgt_key, ang_key) in methods.items():
        per = {}
        for scen in spec["scenarios"]:
            R = [r for r in rows if r["scenario"] == scen and r["status"] == "ok"]
            n_all = len([r for r in rows if r["scenario"] == scen])
            ok = [r for r in R if r[key]["ok"]]
            fail = n_all - len(ok)
            tgt = np.array(T[scen][tgt_key]); tang = T[scen][ang_key]; mu = np.array(T[scen]["mu_w"])
            est = np.array([r[key]["est"] for r in ok])
            cw = [[r[key]["ci_w"][i][0] <= tgt[i] <= r[key]["ci_w"][i][1] for i in range(2)] for r in ok]
            d = {"n": n_all, "failures": fail, "failure_rate": round(fail / n_all, 4),
                 "target": tgt.round(5).tolist(), "target_angle": tang,
                 "mean_est": est.mean(0).round(5).tolist(),
                 "bias_vs_own_target": (est.mean(0) - tgt).round(5).tolist(),
                 "bias_vs_own_target_mc_se": (est.std(0, ddof=1) / np.sqrt(len(est))).round(5).tolist(),
                 "empirical_sd": est.std(0, ddof=1).round(5).tolist(),
                 "median_se": np.median([r[key]["se"] for r in ok], axis=0).round(5).tolist(),
                 "coverage_w_on": classify_band(sum(c[0] for c in cw), len(ok), *C["E1a_band"]),
                 "coverage_w_off": classify_band(sum(c[1] for c in cw), len(ok), *C["E1a_band"]),
                 "gate_pass_rate": round(float(np.mean([r[key]["gate_pass"] for r in ok])), 4)}
            if key == "B2":
                d["bias_vs_mu_w"] = (est.mean(0) - mu).round(5).tolist()
                d["relative_bias_vs_mu_w_norm"] = ((est.mean(0) - mu) / np.hypot(*mu)).round(4).tolist() if np.hypot(*mu) > 0 else None
                d["coverage_of_mu_w_on_(informational)"] = round(float(np.mean([r[key]["ci_w"][0][0] <= mu[0] <= r[key]["ci_w"][0][1] for r in ok])), 4)
            if tang is not None:
                cov_a = sum(em.circ_contains(*r[key][ci_key], tang) for r in ok)
                d["angle_coverage"] = classify_band(cov_a, len(ok), *C["E1a2_band"])
                d["median_angle_ci_width"] = round(float(np.median([r[key][ci_key][1] - r[key][ci_key][0] for r in ok])), 2)
                d["mean_angle_est"] = round(float(np.mean([r[key]["angle"] for r in ok])), 3)
            gp = [r for r in ok if r[key]["gate_pass"]]
            d["P(gate & excl 45)"] = round(sum(not em.circ_contains(*r[key][ci_key], 45.0) for r in gp) / len(ok), 4)
            d["P(gate & excl 0)"] = round(sum(not em.circ_contains(*r[key][ci_key], 0.0) for r in gp) / len(ok), 4)
            d["_counts"] = {"ok": len(ok), "gate_excl45": sum(not em.circ_contains(*r[key][ci_key], 45.0) for r in gp),
                            "gate_excl0": sum(not em.circ_contains(*r[key][ci_key], 0.0) for r in gp),
                            "gate_pass": len(gp)}
            per[scen] = d
        # criteria
        crit = {}
        crit["E1a_weight_coverage"] = {s: {"w_on": per[s]["coverage_w_on"], "w_off": per[s]["coverage_w_off"]} for s in spec["scenarios"]}
        crit["E1a2_angle_coverage"] = {s: per[s]["angle_coverage"] for s in spec["scenarios"] if "angle_coverage" in per[s]}
        s1, s4, s10 = C["E1b_onset_scenario"], C["E1b_midpoint_scenario"], C["E1c_guessing_scenario"]
        crit["E1b_onset_excl45"] = classify_min(per[s1]["_counts"]["gate_excl45"], per[s1]["_counts"]["ok"], C["E1b_min"])
        crit["E1b_midpoint_excl0"] = classify_min(per[s4]["_counts"]["gate_excl0"], per[s4]["_counts"]["ok"], C["E1b_min"])
        crit["E1c_guessing_gate"] = classify_max(per[s10]["_counts"]["gate_pass"], per[s10]["_counts"]["ok"], C["E1c_max"])
        crit["E1d_failures"] = {s: classify_max(per[s]["failures"], per[s]["n"], C["E1d_max"]) for s in spec["scenarios"]}
        crit["E1e_interpretation"] = spec["E1e_results"]["B2" if key == "B2" else "B3"]
        flat = []
        for s, v in crit["E1a_weight_coverage"].items():
            flat += [v["w_on"], v["w_off"]]
        flat += list(crit["E1a2_angle_coverage"].values())
        flat += [crit["E1b_onset_excl45"], crit["E1b_midpoint_excl0"], crit["E1c_guessing_gate"]]
        flat += list(crit["E1d_failures"].values())
        point_all = all(x["point_status"] == "met" for x in flat) and crit["E1e_interpretation"]["met"]
        any_clear_out = any(x["mc_status"] == "clearly outside" for x in flat)
        indet = sum(x["mc_status"] == "indeterminate" for x in flat)
        res["by_method"][mname] = {"per_scenario": per, "criteria": crit,
                                   "all_criteria_met_point": point_all, "any_clearly_outside": any_clear_out,
                                   "n_indeterminate": indet,
                                   "acceptable_under_frozen_rule": bool(point_all and not any_clear_out)}
    acc = [m for m, v in res["by_method"].items() if v["acceptable_under_frozen_rule"]]
    res["frozen_decision_rule"] = spec["decision_rule"]
    res["acceptable_methods"] = acc
    json.dump(res, open(a.out, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(json.dumps({"acceptable_methods": acc,
                      **{m: {"all_point": v["all_criteria_met_point"], "clear_out": v["any_clearly_outside"],
                             "indeterminate": v["n_indeterminate"]} for m, v in res["by_method"].items()}}, indent=1,
                     default=lambda o: o.item() if hasattr(o, "item") else str(o)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True); ap.add_argument("--run-dir", required=True); ap.add_argument("--out", required=True)
    main(ap.parse_args())
