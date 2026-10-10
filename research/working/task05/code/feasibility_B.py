"""
Validation B: small timing and feasibility test (NOT a coverage study).

Runs each candidate method on a small number of simulated datasets to measure
cost, convergence and boundary behaviour. Coverage counts are recorded but are
indicative only (Monte Carlo SE about 0.05-0.07 at these sizes).

Usage:
  python3 feasibility_B.py --reps 20 --reps-b1 10 --boot-datasets 2 --out ../results/validationB
"""
import argparse
import hashlib
import json
import os
import time

import numpy as np

import stimulus as st
import ordinal_model as om
import heterogeneity_methods as hm

N = 12
NS = "task05-B-feasibility-v1"


def seed(*parts):
    return int(hashlib.sha256("|".join([NS, *map(str, parts)]).encode()).hexdigest()[:16], 16)


def design():
    tm = st.order_templates(2, 4)
    return (np.tile([t.d_on for t in tm], (N, 1)), np.tile([t.d_off for t in tm], (N, 1)))


def generate(scen, rng):
    don, doff = design()
    base = dict(tau=1.0, lapse=0.02, bias_sd=0.5)
    if scen == "H0 homogeneous onset":
        y = om.simulate_responses(rng, don, doff, 0.7, 0.0, **base)
    elif scen == "H1 heterogeneous onset (S13 generator)":
        y = om.simulate_responses(rng, don, doff, 0.7, 0.0, w_het_sd=0.3, tau_het_sd=0.3, **base)
    elif scen == "H2 strategy mixture 6 onset + 6 midpoint":
        y1 = om.simulate_responses(rng, don[:6], doff[:6], 0.7, 0.0, **base)
        y2 = om.simulate_responses(rng, don[6:], doff[6:], 0.35, 0.35, **base)
        y = np.vstack([y1, y2])
    else:
        raise ValueError(scen)
    return don, doff, y


LATENT_TRUTH = {"H0 homogeneous onset": (0.7, 0.0),
                "H1 heterogeneous onset (S13 generator)": (0.7, 0.0),
                "H2 strategy mixture 6 onset + 6 midpoint": (0.525, 0.175)}   # mean of individual weights


def b3_truth(scen, n_mc=200000, rng=None):
    """Population mean of individual expected response-scale slopes, by Monte
    Carlo over the generator's participant-level draws (deduction + MC)."""
    rng = rng or np.random.default_rng(seed("b3truth", scen))
    tm = st.order_templates(2, 4)
    d_on = np.array([t.d_on for t in tm]); d_off = np.array([t.d_off for t in tm])
    def slopes(w_on, w_off, beta, gw, gt, lapse=0.02):
        eta = gw[:, None] * (w_on * d_on + w_off * d_off)[None, :] + beta[:, None]
        tau = gt[:, None]
        pR = 1 / (1 + np.exp(tau + eta)); pL = 1 / (1 + np.exp(tau - eta))   # P(z > tau); fixed 2026-10-10 (see log)
        s = (1 - lapse) * (pL - pR)
        return (s * d_on).sum(1) / (d_on ** 2).sum(), (s * d_off).sum(1) / (d_off ** 2).sum()
    beta = rng.normal(0, 0.5, n_mc)
    one = np.ones(n_mc)
    if scen == "H0 homogeneous onset":
        a, b = slopes(0.7, 0.0, beta, one, one)
    elif scen.startswith("H1"):
        gw = np.exp(rng.normal(0, 0.3, n_mc)); gt = np.exp(rng.normal(0, 0.3, n_mc))
        a, b = slopes(0.7, 0.0, beta, gw, gt)
    else:
        a1, b1 = slopes(0.7, 0.0, beta, one, one)
        a2, b2 = slopes(0.35, 0.35, beta, one, one)
        a, b = 0.5 * (a1 + a2), 0.5 * (b1 + b2)
    return float(a.mean()), float(b.mean())


def covers(lo, hi, truth):
    return [bool(lo[i] <= truth[i] <= hi[i]) for i in range(2)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--reps-b1", type=int, default=10)
    ap.add_argument("--boot-datasets", type=int, default=2)
    ap.add_argument("--boot-n", type=int, default=100)
    ap.add_argument("--out", default="../results/validationB")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    rows = []
    t_all = time.time()
    for scen in LATENT_TRUTH:
        tl = LATENT_TRUTH[scen]
        tb3 = b3_truth(scen)
        for rep in range(args.reps):
            rng = np.random.default_rng(seed(scen, rep))
            don, doff, y = generate(scen, rng)
            r = {"scenario": scen, "rep": rep, "seed": str(seed(scen, rep))}
            t0 = time.perf_counter(); o = hm.b0_b2(don, doff, y); t_b02 = time.perf_counter() - t0
            for m in ("B0", "B2"):
                lo, hi = hm.wald_ci(o[m])
                alo, ahi = hm.angle_ci_from_cov(o[m]["est"], o[m]["cov"], rng,
                                                crit_df=(11 if m == "B2" else None))
                r[m] = {"ok": bool(o[m]["ok"]), "est": o[m]["est"].tolist(), "se": o[m]["se"].tolist(),
                        "covers_latent_truth": covers(lo, hi, tl), "angle_ci": [alo, ahi]}
            r["B0B2_seconds"] = round(t_b02, 4)
            r["sd_u_boundary"] = bool(o["sd_u_boundary"])
            t0 = time.perf_counter(); o3 = hm.b3(don, doff, y, rng); t_b3 = time.perf_counter() - t0
            lo, hi = hm.wald_ci(o3)
            r["B3"] = {"ok": o3["ok"], "est": o3["est"].tolist(), "se": o3["se"].tolist(),
                       "covers_b3_truth": covers(lo, hi, tb3), "angle_ci": list(o3["angle_ci"]),
                       "individual_angle_deg": np.degrees(np.arctan2(o3["b_off_i"], o3["b_on_i"])).round(1).tolist()}
            r["B3_seconds"] = round(t_b3, 4)
            if rep < args.reps_b1:
                t0 = time.perf_counter(); o1 = hm.b1(don, doff, y); t_b1 = time.perf_counter() - t0
                lo, hi = hm.wald_ci(o1)
                alo, ahi = hm.angle_ci_from_cov(o1["est"], o1["cov"], rng)
                r["B1"] = {"ok": o1["ok"], "converged": o1["converged"], "est": o1["est"].tolist(),
                           "se": o1["se"].tolist(), "covers_latent_truth": covers(lo, hi, tl),
                           "angle_ci": [alo, ahi], "sd_slopes": o1["sd_slopes"],
                           "slope_sd_at_lower_bound": o1["slope_sd_at_lower_bound"]}
                r["B1_seconds"] = round(t_b1, 3)
            if scen.startswith("H1") and rep < args.boot_datasets:
                t0 = time.perf_counter(); o4 = hm.b4(don, doff, y, rng, n_boot=args.boot_n); t_b4 = time.perf_counter() - t0
                r["B4"] = {"ci_lo": o4["ci_lo"].tolist(), "ci_hi": o4["ci_hi"].tolist(),
                           "covers_latent_truth": covers(o4["ci_lo"], o4["ci_hi"], tl),
                           "boot_failures": o4["boot_failures"], "n_boot": o4["n_boot"]}
                r["B4_seconds"] = round(t_b4, 2)
            rows.append(r)
            with open(os.path.join(args.out, "feasibility_rows.jsonl"), "a") as f:
                f.write(json.dumps(r, default=float) + "\n")
        print(scen, "done", round(time.time() - t_all, 1), "s", flush=True)

    summ = {"note": "Feasibility only. Coverage counts are indicative, not evidence.",
            "args": vars(args), "total_seconds": round(time.time() - t_all, 1), "by_scenario": {}}
    for scen in LATENT_TRUTH:
        R = [r for r in rows if r["scenario"] == scen]
        d = {"latent_truth": LATENT_TRUTH[scen], "b3_truth_response_scale": b3_truth(scen),
             "n": len(R), "sd_u_boundary_rate": float(np.mean([r["sd_u_boundary"] for r in R]))}
        for m in ("B0", "B2", "B3", "B1"):
            M = [r for r in R if m in r]
            if not M:
                continue
            key = "covers_b3_truth" if m == "B3" else "covers_latent_truth"
            ok = [r for r in M if r[m]["ok"]]
            d[m] = {"n": len(M), "ok": len(ok),
                    "covers_w_on": f'{sum(r[m][key][0] for r in ok)}/{len(ok)}',
                    "covers_w_off": f'{sum(r[m][key][1] for r in ok)}/{len(ok)}',
                    "mean_est": np.mean([r[m]["est"] for r in ok], axis=0).round(4).tolist() if ok else None,
                    "median_se": np.median([r[m]["se"] for r in ok], axis=0).round(4).tolist() if ok else None,
                    "median_angle_ci_width": round(float(np.median([r[m]["angle_ci"][1] - r[m]["angle_ci"][0]
                                                                    for r in ok])), 2) if ok else None,
                    "angle_ci_excludes_0": f'{sum((r[m]["angle_ci"][0] > 0) or (r[m]["angle_ci"][1] < 0) for r in ok)}/{len(ok)}',
                    "angle_ci_excludes_45": f'{sum((r[m]["angle_ci"][0] > 45) or (r[m]["angle_ci"][1] < 45) for r in ok)}/{len(ok)}'}
            if m == "B1":
                d[m]["slope_sd_on_at_bound"] = f'{sum(r["B1"]["slope_sd_at_lower_bound"][0] for r in M)}/{len(M)}'
                d[m]["slope_sd_off_at_bound"] = f'{sum(r["B1"]["slope_sd_at_lower_bound"][1] for r in M)}/{len(M)}'
                d[m]["median_sd_slopes"] = np.median([r["B1"]["sd_slopes"] for r in M], axis=0).round(4).tolist()
        d["seconds_per_dataset_median"] = {
            "B0+B2": float(np.median([r["B0B2_seconds"] for r in R])),
            "B3": float(np.median([r["B3_seconds"] for r in R])),
            "B1": float(np.median([r["B1_seconds"] for r in R if "B1_seconds" in r])) if any("B1_seconds" in r for r in R) else None,
            "B4": float(np.median([r["B4_seconds"] for r in R if "B4_seconds" in r])) if any("B4_seconds" in r for r in R) else None}
        B4 = [r for r in R if "B4" in r]
        if B4:
            d["B4"] = [{"ci_lo": r["B4"]["ci_lo"], "ci_hi": r["B4"]["ci_hi"], "boot_failures": r["B4"]["boot_failures"],
                        "n_boot": r["B4"]["n_boot"], "covers": r["B4"]["covers_latent_truth"]} for r in B4]
        if scen.startswith("H2"):
            ia = np.array([r["B3"]["individual_angle_deg"] for r in R])
            d["H2_individual_B3_angles_median_onset_participants"] = float(np.median(ia[:, :6]))
            d["H2_individual_B3_angles_median_midpoint_participants"] = float(np.median(ia[:, 6:]))
        summ["by_scenario"][scen] = d
    with open(os.path.join(args.out, "feasibility_summary.json"), "w") as f:
        json.dump(summ, f, indent=1, default=float)
    print(json.dumps(summ, indent=1, default=float))


if __name__ == "__main__":
    main()
