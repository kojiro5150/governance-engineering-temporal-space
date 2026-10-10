"""
Validation C2: can catch trials (and other indicators) distinguish
  M1  independent random response lapses,
  M2a sustained-attention failures with deferred timing,
  M2b sustained-attention failures with snapshot (state) comparison on re-engagement,
  M3  genuinely low temporal-order sensitivity (larger timing noise),
when all four are CALIBRATED to the same loss of main-trial onset sensitivity?

All mechanisms are built on the same onset-timing observer M0 (process_observer.py).
Calibration target: pooled B3 onset slope = 0.60 x that of M0 (pre-specified).

Usage: python3 mechanisms_C2.py --datasets 200 --b0-datasets 100 --out ../results/validationC
"""
import argparse
import copy
import hashlib
import json
import os
import time
from multiprocessing import Pool

import numpy as np

import process_observer as po
import ordinal_model as om
import heterogeneity_methods as hm

NS = "task05-C2-v1"
TARGET_RATIO = 0.60          # pre-specified; 0.85 added as deviation D3 (see logs/DEVIATIONS.md)
CAL_PARTICIPANTS = 1500


def seed(*p):
    return int(hashlib.sha256("|".join([NS, *map(str, p)]).encode()).hexdigest()[:16], 16)


def b_on_for(prm, tag):
    rng = np.random.default_rng(seed("cal", tag))
    return po.pooled_b_on(prm, CAL_PARTICIPANTS, rng)[0]


def bisect(make, lo, hi, target, tag, increasing, iters=14):
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        v = b_on_for(make(mid), tag)
        if (v < target) == increasing:
            lo = mid
        else:
            hi = mid
    x = 0.5 * (lo + hi)
    return x, b_on_for(make(x), tag)


def calibrate(ratio=TARGET_RATIO):
    m0 = copy.deepcopy(po.BASE)
    b0 = b_on_for(m0, "M0")
    target = ratio * b0
    out = {"M0": {"params": m0, "b_on": b0}, "target_ratio": ratio, "target_b_on": target}
    def mk(**kw):
        def f(x):
            p = copy.deepcopy(po.BASE)
            for k, v in kw.items():
                p[k] = v(x) if callable(v) else v
            return p
        return f
    lam, v = bisect(mk(lam=lambda x: x), 0.0, 0.9, target, "M1", increasing=False)
    out["M1"] = {"params": mk(lam=lambda x: x)(lam), "b_on": v, "calibrated": {"lam": lam}}
    for name, pol in (("M2a", "timing"), ("M2b", "snapshot")):
        E, v = bisect(mk(E=lambda x: x, policy=pol), 0.5, 200.0, target, name, increasing=True)
        p = mk(E=lambda x: x, policy=pol)(E)
        out[name] = {"params": p, "b_on": v,
                     "calibrated": {"E_mean_engaged_s": E, "D_mean_disengaged_s": p["D"],
                                    "stationary_disengaged_fraction": p["D"] / (E + p["D"])}}
    sig, v = bisect(mk(sigma=lambda x: x), 1.2, 15.0, target, "M3", increasing=False)
    out["M3"] = {"params": mk(sigma=lambda x: x)(sig), "b_on": v, "calibrated": {"sigma_s": sig}}
    return out


def dataset_stats(args):
    name, prm, d_i, do_b0 = args
    rng = np.random.default_rng(seed("data", name, d_i))
    d = po.simulate_dataset(prm, rng)
    don, doff, y, yc, cd = d["don"], d["doff"], d["y"], d["yc"], d["catch_don"]
    b_on, b_off = po.b3_slopes(don, doff, y)
    o3 = hm.b3(don, doff, y, rng)
    sim = (don == 0) & (doff == 0)
    correct_c = yc == np.where(cd > 0, 2, 0)
    out = {"mechanism": name, "dataset": d_i,
           "b3_on": float(b_on.mean()), "b3_off": float(b_off.mean()),
           "b3_angle": float(np.degrees(np.arctan2(b_off.mean(), b_on.mean()))),
           "b3_angle_ci": list(o3["angle_ci"]),
           "catch_error_rate": float(1 - correct_c.mean()),
           "catch_errors_per_participant": (4 - correct_c.sum(1)).tolist(),
           "S_rate_simultaneous": float((y[sim] == 1).mean()),
           "S_rate_all_main": float((y == 1).mean())}
    if do_b0:
        f = om.fit(don, doff, y)
        lo, hi = hm.angle_ci_from_cov(np.array([f["w_on"], f["w_off"]]), np.array(f["cov_w"]), rng)
        out.update({"b0_w_on": f["w_on"], "b0_w_off": f["w_off"], "b0_stable": f["stable"],
                    "b0_angle": float(np.degrees(np.arctan2(f["w_off"], f["w_on"]))), "b0_angle_ci": [lo, hi]})
    return out


def auc(a, b):
    """P(stat from b > stat from a) + 0.5 P(tie): separability of two samples."""
    a = np.asarray(a); b = np.asarray(b)
    gt = (b[:, None] > a[None, :]).mean(); eq = (b[:, None] == a[None, :]).mean()
    return float(gt + 0.5 * eq)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", type=int, default=200)
    ap.add_argument("--b0-datasets", type=int, default=100)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default="../results/validationC")
    ap.add_argument("--target", type=float, default=TARGET_RATIO)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    t0 = time.time()
    cal = calibrate(args.target)
    suf = f"_target{args.target:.2f}"
    t_cal = time.time() - t0
    json.dump(cal, open(os.path.join(args.out, f"C2_calibration{suf}.json"), "w"), indent=1, default=float)
    print("calibration", round(t_cal, 1), "s", json.dumps({k: (v["calibrated"] if isinstance(v, dict) and "calibrated" in v else v)
                                                          for k, v in cal.items() if k != "M0"}, default=float), flush=True)
    jobs = [(name, cal[name]["params"], i, i < args.b0_datasets)
            for name in ("M0", "M1", "M2a", "M2b", "M3") for i in range(args.datasets)]
    rows = []
    with Pool(args.workers) as p, open(os.path.join(args.out, f"C2_datasets{suf}.jsonl"), "w") as f:
        for r in p.imap(dataset_stats, jobs, chunksize=10):
            rows.append(r); f.write(json.dumps(r, default=float) + "\n")
    t_all = time.time() - t0
    mech = ("M0", "M1", "M2a", "M2b", "M3")
    summ = {"target_ratio": args.target, "calibration_reached": {m: round(cal[m]["b_on"] / cal["target_b_on"], 3) for m in ("M1", "M2a", "M2b", "M3")},
            "seconds_total": round(t_all, 1), "seconds_calibration": round(t_cal, 1),
            "datasets_per_mechanism": args.datasets, "b0_datasets_per_mechanism": args.b0_datasets,
            "by_mechanism": {}, "auc_pairs": {}}
    for m in mech:
        R = [r for r in rows if r["mechanism"] == m]
        B = [r for r in R if "b0_angle" in r and r["b0_stable"]]
        pp = np.concatenate([r["catch_errors_per_participant"] for r in R])
        summ["by_mechanism"][m] = {
            "b3_on_mean": round(float(np.mean([r["b3_on"] for r in R])), 4),
            "b3_off_mean": round(float(np.mean([r["b3_off"] for r in R])), 4),
            "b3_angle_median": round(float(np.median([r["b3_angle"] for r in R])), 2),
            "b3_angle_ci_excludes_0": round(float(np.mean([(r["b3_angle_ci"][0] > 0) or (r["b3_angle_ci"][1] < 0) for r in R])), 3),
            "b3_angle_ci_excludes_45": round(float(np.mean([(r["b3_angle_ci"][0] > 45) or (r["b3_angle_ci"][1] < 45) for r in R])), 3),
            "b0_angle_median": round(float(np.median([r["b0_angle"] for r in B])), 2) if B else None,
            "b0_angle_ci_excludes_0": round(float(np.mean([(r["b0_angle_ci"][0] > 0) or (r["b0_angle_ci"][1] < 0) for r in B])), 3) if B else None,
            "b0_angle_ci_excludes_45": round(float(np.mean([(r["b0_angle_ci"][0] > 45) or (r["b0_angle_ci"][1] < 45) for r in B])), 3) if B else None,
            "b0_w_on_mean": round(float(np.mean([r["b0_w_on"] for r in B])), 4) if B else None,
            "b0_w_off_mean": round(float(np.mean([r["b0_w_off"] for r in B])), 4) if B else None,
            "catch_error_rate_mean": round(float(np.mean([r["catch_error_rate"] for r in R])), 4),
            "catch_error_rate_p5_p95": [round(float(np.percentile([r["catch_error_rate"] for r in R], q)), 4) for q in (5, 95)],
            "participants_with_any_catch_error": round(float(np.mean(pp > 0)), 4),
            "S_rate_simultaneous_mean": round(float(np.mean([r["S_rate_simultaneous"] for r in R])), 4),
            "S_rate_all_main_mean": round(float(np.mean([r["S_rate_all_main"] for r in R])), 4),
        }
    stats = ("catch_error_rate", "S_rate_simultaneous", "S_rate_all_main", "b3_angle", "b3_on")
    for i, a in enumerate(("M1", "M2a", "M2b", "M3")):
        for b in ("M1", "M2a", "M2b", "M3")[i + 1:]:
            Ra = [r for r in rows if r["mechanism"] == a]; Rb = [r for r in rows if r["mechanism"] == b]
            d = {s: round(auc([r[s] for r in Ra], [r[s] for r in Rb]), 3) for s in stats}
            Ba = [r["b0_angle"] for r in Ra if "b0_angle" in r and r["b0_stable"]]
            Bb = [r["b0_angle"] for r in Rb if "b0_angle" in r and r["b0_stable"]]
            d["b0_angle"] = round(auc(Ba, Bb), 3)
            pa = np.concatenate([r["catch_errors_per_participant"] for r in Ra])
            pb = np.concatenate([r["catch_errors_per_participant"] for r in Rb])
            d["catch_errors_single_participant"] = round(auc(pa, pb), 3)
            summ["auc_pairs"][f"{a} vs {b}"] = d
    json.dump(summ, open(os.path.join(args.out, f"C2_summary{suf}.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
