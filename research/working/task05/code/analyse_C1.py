"""Analysis of Validation C1 (lapse-model identifiability with catch trials).
Usage: python3 analyse_C1.py IN_JSONL OUT_JSON"""
import json
import math
import sys

import numpy as np


def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(c - h, 3), round(c + h, 3)]


def main(inp, out):
    rows = [json.loads(l) for l in open(inp)]
    keys = sorted({(r["scenario"], r["K"]) for r in rows})
    res = {"n_jobs": len(rows), "cells": {}}
    for scen, K in keys:
        R = [r for r in rows if r["scenario"] == scen and r["K"] == K]
        t = R[0]["true"]
        a = 0.7 if (t["w_on"] or t["w_off"]) else None   # onset-only sensitivity scale used in Task 04 (|w_on|+|w_off|)
        cell = {"reps": len(R), "true": t,
                "catch_error_rate_mean": round(float(np.mean([r["catch_error_rate"] for r in R])), 4),
                "expected_catch_error_if_pure_lapse": round(t["lapse"] * 2 / 3, 4),
                "share_participants_with_>=1_catch_error": round(float(np.mean(
                    np.concatenate([r["catch_errors_per_participant"] for r in R]) > 0)), 4)}
        for m in ("L0", "L1", "L2", "L3"):
            S = [r for r in R if r[m]["stable"]]
            won = np.array([r[m]["w_on"] for r in S]); woff = np.array([r[m]["w_off"] for r in S])
            son = np.array([r[m]["se_w_on"] for r in S])
            k = int(np.sum(np.abs(won - t["w_on"]) <= 1.96 * son))
            d = {"stable": f"{len(S)}/{len(R)}",
                 "w_on_mean": round(float(won.mean()), 4), "w_off_mean": round(float(woff.mean()), 4),
                 "bias_w_on_over_a": round(float((won.mean() - t["w_on"]) / a), 4) if a else None,
                 "empirical_sd_w_on": round(float(won.std(ddof=1)), 4),
                 "median_se_w_on": round(float(np.median(son)), 4),
                 "coverage_w_on": round(k / len(S), 3), "coverage_w_on_wilson95": wilson(k, len(S)),
                 "angle_median_deg": round(float(np.median(np.degrees(np.arctan2(woff, won)))), 2)}
            if m in ("L1", "L2", "L3"):
                lh = np.array([r[m]["lapse_hat"] for r in R])
                d["lapse_hat_median"] = round(float(np.median(lh)), 4)
                d["lapse_hat_p10_p90"] = [round(float(np.percentile(lh, 10)), 4), round(float(np.percentile(lh, 90)), 4)]
                if m in ("L1", "L2"):
                    d["lapse_at_boundary_rate"] = round(float(np.mean([r[m]["lapse_at_boundary"] for r in R])), 3)
            cell[m] = d
        res["cells"][f"{scen} | K={K}"] = cell
    json.dump(res, open(out, "w"), indent=1)
    for k, v in res["cells"].items():
        print("\n##", k, "| catch err", v["catch_error_rate_mean"], "expected(pure lapse)", v["expected_catch_error_if_pure_lapse"],
              "| any-error participants", v["share_participants_with_>=1_catch_error"])
        for m in ("L0", "L1", "L2", "L3"):
            print("  ", m, v[m])


if __name__ == "__main__":
    main(*sys.argv[1:3])
