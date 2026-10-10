"""
E1-H2 analysis. Reads targets, criteria and the original E1 results ONLY via
the frozen E1-H2 spec; refuses on spec/code/E1-results hash mismatch, on
duplicates and on an incomplete run.
Usage: python3 e1h2_analyse.py --spec SPEC --run-dir DIR --out OUT_JSON
"""
import argparse, json, os, sys
import numpy as np
import e1h2_common  # noqa: F401  (sets sys.path to code/)
import e1_methods as em
from e1_run import load
from e1_analyse import wilson, classify_band, classify_max
from e1h2_run import sha, verify, CODE_ROOT

METHODS = {"B2": ("B2", "angle_ci", "theta_star", "angle_theta_star"),
           "B3-boot": ("B3", "angle_ci", "beta_star", "angle_beta_star"),
           "B3-t": ("B3", "angle_ci_t", "beta_star", "angle_beta_star")}
H2_E1 = "H2 mixture 6 onset + 6 midpoint"


def rate(k, n):
    return {"k": int(k), "n": int(n), "rate": round(k / n, 4) if n else None, "wilson95": wilson(k, n)}


def main(a):
    spec = json.load(open(a.spec))
    man = json.load(open(os.path.join(a.run_dir, "manifest.json")))
    if man["frozen_spec_sha256"] != sha(a.spec):
        sys.exit("REFUSING: run not produced under this frozen spec")
    if verify(spec):
        sys.exit(f"REFUSING: code differs from frozen spec: {verify(spec)}")
    e1p = os.path.join(CODE_ROOT, spec["original_E1"]["results_path_rel_code"])
    if sha(e1p) != spec["original_E1"]["results_sha256"]:
        sys.exit("REFUSING: original E1 results file differs from the hash frozen in this spec")
    rows, dups = load(a.run_dir)
    if dups:
        sys.exit("REFUSING: duplicates")
    if {r["job_id"] for r in rows} != {f"H2random|rep{r}" for r in range(spec["reps"])}:
        sys.exit("REFUSING: run incomplete or has unexpected jobs")
    T = spec["targets"]; C = spec["criteria"]; band = C["coverage_band"]
    mu = np.array(T["mu_w"])
    E1 = json.load(open(e1p))
    res = {"n_rows": len(rows), "errors": sum(r["status"] == "error" for r in rows),
           "n_onset_distribution": np.bincount([r["n_onset"] for r in rows if r["status"] == "ok"], minlength=13).tolist(),
           "by_method": {}}
    for m, (key, ck, tk, ak) in METHODS.items():
        n_all = len(rows)
        ok = [r for r in rows if r["status"] == "ok" and r[key]["ok"]]; n = len(ok)
        tgt = np.array(T[tk]); tang = T[ak]
        est = np.array([r[key]["est"] for r in ok])
        con = sum(r[key]["ci_w"][0][0] <= tgt[0] <= r[key]["ci_w"][0][1] for r in ok)
        coff = sum(r[key]["ci_w"][1][0] <= tgt[1] <= r[key]["ci_w"][1][1] for r in ok)
        cang = sum(em.circ_contains(*r[key][ck], tang) for r in ok)
        gp = [r for r in ok if r[key]["gate_pass"]]
        ex0 = [not em.circ_contains(*r[key][ck], 0.0) for r in gp]
        ex45 = [not em.circ_contains(*r[key][ck], 45.0) for r in gp]
        crit = {"H1_w_on": classify_band(con, n, *band), "H1_w_off": classify_band(coff, n, *band),
                "H2_angle": classify_band(cang, n, *band),
                "H3_failures": classify_max(n_all - n, n_all, C["failure_max"])}
        point = all(v["point_status"] == "met" for v in crit.values())
        out = any(v["mc_status"] == "clearly outside" for v in crit.values())
        d = {"criteria": crit, "H_criteria_met_point": point, "H_any_clearly_outside": out,
             "H_n_indeterminate": sum(v["mc_status"] == "indeterminate" for v in crit.values()),
             "H2_population_criteria_met": bool(point and not out),
             "target": tgt.tolist(), "target_angle": tang,
             "mean_est": est.mean(0).round(5).tolist(),
             "bias_vs_own_target": (est.mean(0) - tgt).round(5).tolist(),
             "bias_mc_se": (est.std(0, ddof=1) / np.sqrt(n)).round(5).tolist(),
             "empirical_sd": est.std(0, ddof=1).round(5).tolist(),
             "median_se": np.median([r[key]["se"] for r in ok], 0).round(5).tolist(),
             "mean_angle_est": round(float(np.mean([r[key]["angle"] for r in ok])), 3),
             "sd_angle_est": round(float(np.std([r[key]["angle"] for r in ok], ddof=1)), 3),
             "median_angle_ci_width": round(float(np.median([r[key][ck][1] - r[key][ck][0] for r in ok])), 2),
             "gate": {"pass": rate(len(gp), n),
                      "pass_and_excl_0": rate(sum(ex0), n), "pass_and_excl_45": rate(sum(ex45), n),
                      "pass_and_excl_both_0_and_45": rate(sum(x and y for x, y in zip(ex0, ex45)), n),
                      "pass_and_excl_neither": rate(sum((not x) and (not y) for x, y in zip(ex0, ex45)), n)}}
        if key == "B2":
            d["bias_vs_mu_w"] = (est.mean(0) - mu).round(5).tolist()
            d["relative_bias_vs_mu_w_norm"] = ((est.mean(0) - mu) / np.hypot(*mu)).round(4).tolist()
            d["coverage_of_mu_w"] = {"w_on": rate(sum(r[key]["ci_w"][0][0] <= mu[0] <= r[key]["ci_w"][0][1] for r in ok), n),
                                     "w_off": rate(sum(r[key]["ci_w"][1][0] <= mu[1] <= r[key]["ci_w"][1][1] for r in ok), n)}
        # informational: coverage by realised composition
        strata = {}
        for lab, lo, hi in C["composition_strata"]:
            S = [r for r in ok if lo <= r["n_onset"] <= hi]
            if S:
                strata[lab] = {"n": len(S),
                               "cov_w_on": round(np.mean([r[key]["ci_w"][0][0] <= tgt[0] <= r[key]["ci_w"][0][1] for r in S]), 4),
                               "cov_w_off": round(np.mean([r[key]["ci_w"][1][0] <= tgt[1] <= r[key]["ci_w"][1][1] for r in S]), 4),
                               "cov_angle": round(np.mean([em.circ_contains(*r[key][ck], tang) for r in S]), 4),
                               "mean_angle": round(float(np.mean([r[key]["angle"] for r in S])), 2)}
        d["informational_by_composition"] = strata
        # pre-specified composite: original E1 non-H2 criteria + this amendment's H2 criteria
        oc = E1["by_method"][m]["criteria"]
        flat = []
        for s, v in oc["E1a_weight_coverage"].items():
            if s != H2_E1: flat += [v["w_on"], v["w_off"]]
        flat += [v for s, v in oc["E1a2_angle_coverage"].items() if s != H2_E1]
        flat += [oc["E1b_onset_excl45"], oc["E1b_midpoint_excl0"], oc["E1c_guessing_gate"]]
        flat += [v for s, v in oc["E1d_failures"].items() if s != H2_E1]
        orig_ok_point = all(x["point_status"] == "met" for x in flat)
        orig_out = any(x["mc_status"] == "clearly outside" for x in flat)
        orig_fail = [x for x in flat if x["point_status"] != "met" or x["mc_status"] == "clearly outside"]
        d["composite_amended_status"] = {
            "original_E1_non_H2_criteria_met_point": orig_ok_point, "original_E1_non_H2_any_clearly_outside": orig_out,
            "original_E1_non_H2_shortfalls": orig_fail,
            "E1e_met": oc["E1e_interpretation"]["met"],
            "meets_all_with_amended_H2": bool(orig_ok_point and not orig_out and oc["E1e_interpretation"]["met"]
                                              and d["H2_population_criteria_met"])}
        res["by_method"][m] = d
    res["original_E1_verdict_unchanged"] = {"acceptable_methods": E1["acceptable_methods"], "verdict": "REVISE"}
    res["decision_rule"] = spec["decision_rule"]
    res["variants_meeting_all_with_amended_H2"] = [m for m, v in res["by_method"].items()
                                                   if v["composite_amended_status"]["meets_all_with_amended_H2"]]
    j = lambda o: o.item() if hasattr(o, "item") else str(o)
    json.dump(res, open(a.out, "w"), indent=1, default=j)
    print(json.dumps({m: {"H2_met": v["H2_population_criteria_met"], **{k: x["rate"] for k, x in v["criteria"].items()},
                          "composite": v["composite_amended_status"]["meets_all_with_amended_H2"]}
                      for m, v in res["by_method"].items()}, indent=1, default=j))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True); ap.add_argument("--run-dir", required=True); ap.add_argument("--out", required=True)
    main(ap.parse_args())
