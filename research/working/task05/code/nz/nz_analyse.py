"""
NZ analysis against the frozen NZ spec. Refuses on spec/code mismatch,
duplicates or incomplete run.
Usage: python3 nz_analyse.py --spec SPEC --run-dir DIR --out OUT_JSON
"""
import argparse, json, os, sys
import numpy as np
import nz_common as c
import e1_methods as em
from e1_run import load
from e1_analyse import wilson, classify_band, classify_max
from nz_run import sha, verify

VARIANTS = {"B3-t": "angle_ci_t", "B3-boot (descriptive)": "angle_ci"}


def rate(k, n):
    return {"k": int(k), "n": int(n), "rate": round(k / n, 4) if n else None, "wilson95": wilson(k, n)}


def main(a):
    spec = json.load(open(a.spec))
    if json.load(open(os.path.join(a.run_dir, "manifest.json")))["frozen_spec_sha256"] != sha(a.spec):
        sys.exit("REFUSING: run not produced under this spec")
    if verify(spec):
        sys.exit(f"REFUSING: code differs: {verify(spec)}")
    rows, dups = load(a.run_dir)
    if dups:
        sys.exit("REFUSING: duplicates")
    exp = {f"{c.label(g)}|rep{r}" for g in spec["grid"] for r in range(spec["reps_per_grid"])}
    if {x["job_id"] for x in rows} != exp:
        sys.exit("REFUSING: incomplete")
    C = spec["criteria"]; T = spec["targets"]
    res = {"n_rows": len(rows), "errors": sum(x["status"] == "error" for x in rows), "by_variant": {}}
    for v, ck in VARIANTS.items():
        per, crit = {}, {}
        for g in spec["grid"]:
            lab = c.label(g); tg = np.array(T[lab]["beta_star"]); tang = T[lab]["angle"]
            R = [x for x in rows if x["grid"] == lab]; n_all = len(R)
            ok = [x for x in R if x["status"] == "ok" and x["B3"]["ok"]]; n = len(ok)
            B = [x["B3"] for x in ok]
            gp = [b for b in B if b["gate_pass"]]
            lo = np.array([b[ck][0] for b in B]); hi = np.array([b[ck][1] for b in B]); w = hi - lo
            con = sum(b["ci_w"][0][0] <= tg[0] <= b["ci_w"][0][1] for b in B)
            coff = sum(b["ci_w"][1][0] <= tg[1] <= b["ci_w"][1][1] for b in B)
            exc0 = [not em.circ_contains(*b[ck], 0.0) for b in gp]
            exc45 = [not em.circ_contains(*b[ck], 45.0) for b in gp]
            lin0 = sum((b[ck][0] <= 0.0 <= b[ck][1]) != em.circ_contains(*b[ck], 0.0) for b in B)
            lin45 = sum((b[ck][0] <= 45.0 <= b[ck][1]) != em.circ_contains(*b[ck], 45.0) for b in B)
            ang = np.radians([b["angle"] for b in B])
            cm = np.degrees(np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())); Rbar = float(np.hypot(np.sin(ang).mean(), np.cos(ang).mean()))
            d = {"n": n_all, "failures": n_all - n, "target_beta_star": tg.tolist(), "target_angle": tang,
                 "weight_cov_w_on": classify_band(con, n, *C["coverage_band"]), "weight_cov_w_off": classify_band(coff, n, *C["coverage_band"]),
                 "gate_pass": rate(len(gp), n),
                 "gate_and_excl_0": rate(sum(exc0), n), "gate_and_excl_45": rate(sum(exc45), n),
                 "mean_est": np.mean([b["est"] for b in B], 0).round(5).tolist(),
                 "bias_vs_beta_star": (np.mean([b["est"] for b in B], 0) - tg).round(5).tolist(),
                 "bias_mc_se": (np.std([b["est"] for b in B], 0, ddof=1) / np.sqrt(n)).round(5).tolist(),
                 "angle_point": {"circular_mean_deg": round(float(cm), 2), "mean_resultant_length": round(Rbar, 3),
                                 "share_abs_angle_gt_90": round(float(np.mean(np.abs(np.degrees(ang)) > 90)), 4)},
                 "angle_ci_width": {"median_all": round(float(np.median(w)), 1),
                                    "median_gate_passed": round(float(np.median([b[ck][1] - b[ck][0] for b in gp])), 1) if gp else None,
                                    "share_ge_180": round(float(np.mean(w >= 180)), 4), "share_ge_360": round(float(np.mean(w >= 360)), 4)},
                 "wrapping": {"share_interval_beyond_pm180": round(float(np.mean((lo < -180) | (hi > 180))), 4),
                              "circular_vs_linear_disagree_0": int(lin0), "circular_vs_linear_disagree_45": int(lin45)}}
            if tang is not None:
                cang = sum(em.circ_contains(*b[ck], tang) for b in B)
                d["angle_cov"] = classify_band(cang, n, *C["coverage_band"])
            per[lab] = d
            if v == "B3-t":
                crit[f"N1 {lab} w_on"] = d["weight_cov_w_on"]; crit[f"N1 {lab} w_off"] = d["weight_cov_w_off"]
                if g in C["N2_grid"]:
                    crit[f"N2 {lab} angle"] = d["angle_cov"]
                if g > 0:
                    crit[f"N3 {lab} false strategy claim"] = classify_max(sum(exc0), n, C["N3_max"])
                else:
                    crit["N4 a=0 gate false positive"] = classify_max(len(gp), n, C["N4_max"])
                crit[f"N5 {lab} failures"] = classify_max(n_all - n, n_all, C["N5_max"])
        out = {"per_grid": per}
        if crit:
            pt = all(x["point_status"] == "met" for x in crit.values()); co = any(x["mc_status"] == "clearly outside" for x in crit.values())
            out.update({"criteria": crit, "all_met_point": pt, "any_clearly_outside": co,
                        "n_indeterminate": sum(x["mc_status"] == "indeterminate" for x in crit.values()),
                        "NZ_outcome": "CONFIRMED" if (pt and not co) else "NOT CONFIRMED"})
        res["by_variant"][v] = out
    res["decision_rule"] = spec["decision_rule"]
    j = lambda o: o.item() if hasattr(o, "item") else str(o)
    json.dump(res, open(a.out, "w"), indent=1, default=j)
    b = res["by_variant"]["B3-t"]
    print(json.dumps({"outcome": b["NZ_outcome"], "indeterminate": b["n_indeterminate"],
                      "criteria": {k: (x["rate"], x["wilson95"], x["point_status"], x["mc_status"]) for k, x in b["criteria"].items()}}, indent=1, default=j))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--spec", required=True); ap.add_argument("--run-dir", required=True); ap.add_argument("--out", required=True)
    main(ap.parse_args())
