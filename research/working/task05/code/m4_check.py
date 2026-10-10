"""
Adversarial check added after C2 (recorded as deviation D4): is attention
failure with snapshot comparison (M2b, target 0.85 calibration) distinguishable
from an ATTENTIVE observer whose genuine strategy carries the same offset
weight (M4: onset timing with a larger detection threshold q, no
disengagement)?

M4's q is chosen by bisection so its pooled B3 strategy angle matches M2b's.
Same dataset seeds and statistics as mechanisms_C2.py.

Usage: python3 m4_check.py ../results/validationC
"""
import copy
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

import mechanisms_C2 as c2
import process_observer as po


def pooled_angle(prm, tag):
    rng = np.random.default_rng(c2.seed("cal-angle", tag))
    b_on, b_off = po.pooled_b_on(prm, c2.CAL_PARTICIPANTS, rng)
    return float(np.degrees(np.arctan2(b_off, b_on)))


def main(out):
    cal = json.load(open(os.path.join(out, "C2_calibration_target0.85.json")))
    m2b = cal["M2b"]["params"]
    target_angle = pooled_angle(m2b, "M2b")
    lo, hi = 0.1, 0.6
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        p = copy.deepcopy(po.BASE); p["q"] = mid
        if pooled_angle(p, "M4") < target_angle:
            lo = mid
        else:
            hi = mid
    m4 = copy.deepcopy(po.BASE); m4["q"] = 0.5 * (lo + hi)
    m4_angle = pooled_angle(m4, "M4")
    jobs = [(n, prm, i, i < 100) for n, prm in (("M2b", m2b), ("M4", m4)) for i in range(200)]
    with Pool(2) as p:
        rows = p.map(c2.dataset_stats, jobs, chunksize=10)
    with open(os.path.join(out, "M4_datasets_target0.85.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, default=float) + "\n")
    res = {"purpose": "attention-induced offset weight (M2b) vs genuine attentive strategy (M4) with matched angle",
           "M2b_pooled_angle": round(target_angle, 2), "M4_q": round(m4["q"], 4), "M4_pooled_angle": round(m4_angle, 2),
           "by_mechanism": {}, "auc_M2b_vs_M4": {}}
    for m in ("M2b", "M4"):
        R = [r for r in rows if r["mechanism"] == m]
        B = [r for r in R if r.get("b0_stable")]
        res["by_mechanism"][m] = {
            "b3_on_mean": round(float(np.mean([r["b3_on"] for r in R])), 4),
            "b3_angle_median": round(float(np.median([r["b3_angle"] for r in R])), 2),
            "b0_angle_median": round(float(np.median([r["b0_angle"] for r in B])), 2),
            "catch_error_rate_mean": round(float(np.mean([r["catch_error_rate"] for r in R])), 4),
            "S_rate_simultaneous_mean": round(float(np.mean([r["S_rate_simultaneous"] for r in R])), 4),
            "S_rate_all_main_mean": round(float(np.mean([r["S_rate_all_main"] for r in R])), 4)}
    A = [r for r in rows if r["mechanism"] == "M2b"]; B = [r for r in rows if r["mechanism"] == "M4"]
    for s in ("catch_error_rate", "S_rate_simultaneous", "S_rate_all_main", "b3_angle", "b3_on"):
        res["auc_M2b_vs_M4"][s] = round(c2.auc([r[s] for r in A], [r[s] for r in B]), 3)
    json.dump(res, open(os.path.join(out, "M4_check_target0.85.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
