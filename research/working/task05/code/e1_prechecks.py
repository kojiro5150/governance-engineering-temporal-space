"""
E1 pre-execution checks (corrections 1-4 of the conditional approval).

  P1  B2 estimand audit: pseudo-true theta* (working-model KL projection) per
      scenario from 4 independent fits of 6,000 simulated participants;
      compared with mean individual latent weights mu_w.
  P2  B3 targets: beta* (response-scale) per scenario, plus the latent-to-
      response angle mapping for homogeneous observers (for interpretation).
  P3  Benchmark of the COMPLETE B2 and B3 procedures (incl. 2,000 draws or
      bootstrap resamples per dataset) on 200 datasets.
  P4  Near-zero sensitivity sweep: gates, interval widths, circular vs
      linear containment, false strategy claims; and re-check of archived
      Task 04/05 angle statistics under circular containment.

Usage: python3 e1_prechecks.py OUT_DIR
"""
import csv
import hashlib
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

import e1_methods as em

NS = "task05-E1-precheck-v1"


def seed(*p):
    return int(hashlib.sha256("|".join([NS, *map(str, p)]).encode()).hexdigest()[:16], 16)


def _theta_job(args):
    name, k = args
    spec = em.SCENARIOS[name]
    rng = np.random.default_rng(seed("theta*", name, k))
    don, doff, y = em.generate(spec, rng, n_scale=500)
    f = em.om.fit(don, doff, y)
    return name, k, [f["w_on"], f["w_off"]], bool(f["stable"])


def p1_p2(out):
    jobs = [(n, k) for n in em.SCENARIOS for k in range(4)]
    t0 = time.time()
    with Pool(2) as p:
        res = p.map(_theta_job, jobs)
    t_theta = time.time() - t0
    targets = {}
    for n, spec in em.SCENARIOS.items():
        v = np.array([r[2] for r in res if r[0] == n])
        th, th_se = v.mean(0), v.std(0, ddof=1) / 2.0
        mu = em.mu_w(spec)
        b, b_se = em.beta_star(spec, np.random.default_rng(seed("beta*", n)))
        norm_mu = float(np.hypot(*mu))
        targets[n] = {
            "mu_w": mu.round(5).tolist(), "angle_mu_w": round(em.angle(mu), 3) if norm_mu > 0 else None,
            "theta_star": th.round(5).tolist(), "theta_star_mc_se": th_se.round(5).tolist(),
            "theta_star_replicates": v.round(5).tolist(),
            "theta_star_all_fits_stable": all(r[3] for r in res if r[0] == n),
            "angle_theta_star": round(em.angle(th), 3) if norm_mu > 0 else None,
            "theta_star_minus_mu_w_relative_to_norm_mu": ((th - mu) / norm_mu).round(4).tolist() if norm_mu > 0 else None,
            "beta_star": b.round(6).tolist(), "beta_star_mc_se": b_se.round(7).tolist(),
            "angle_beta_star": round(em.angle(b), 3) if norm_mu > 0 else None}
    # latent -> response-scale angle mapping for homogeneous observers, two sensitivities
    mapping = {}
    for a in (0.35, 0.70, 1.07):
        rows = []
        for phi in (0, 5, 10, 14.04, 20, 25, 30, 35, 40, 45, 60, 75, 90, -20, -45):
            r = np.radians(phi)
            spec = dict(groups=[(12, a * np.cos(r) / (abs(np.cos(r)) + abs(np.sin(r))),
                                 a * np.sin(r) / (abs(np.cos(r)) + abs(np.sin(r))))], lapse=0.02)
            b, _ = em.beta_star(spec, np.random.default_rng(seed("map", a, phi)), n_mc=200_000)
            rows.append({"latent_angle": phi, "response_angle": round(em.angle(b), 2)})
        mapping[f"a={a} (|w_on|+|w_off|)"] = rows
    json.dump({"seconds_theta_star": round(t_theta, 1), "targets": targets, "latent_to_response_angle": mapping},
              open(os.path.join(out, "P1_P2_targets.json"), "w"), indent=1)
    return targets


def p3(out, n=200):
    spec = em.SCENARIOS["S13 heterogeneous weights+thresholds"]
    t2, t3 = [], []
    for i in range(n):
        rng = np.random.default_rng(seed("bench", i))
        don, doff, y = em.generate(spec, rng)
        t = time.perf_counter(); em.run_b2(don, doff, y, rng); t2.append(time.perf_counter() - t)
        t = time.perf_counter(); em.run_b3(don, doff, y, rng); t3.append(time.perf_counter() - t)
    r = {"datasets": n, "scenario": "S13", "draws_or_resamples_per_dataset": em.N_DRAWS,
         "B2_complete_seconds": {"median": round(float(np.median(t2)), 4), "p95": round(float(np.percentile(t2, 95)), 4), "total": round(float(np.sum(t2)), 1)},
         "B3_complete_seconds": {"median": round(float(np.median(t3)), 5), "p95": round(float(np.percentile(t3, 95)), 5), "total": round(float(np.sum(t3)), 2)},
         "projection_3500_datasets_single_core_s": round(3500 * (float(np.mean(t2)) + float(np.mean(t3))), 0)}
    json.dump(r, open(os.path.join(out, "P3_benchmark.json"), "w"), indent=1)
    return r


def lin_contains(lo, hi, th):
    return bool(np.isfinite(lo) and np.isfinite(hi) and lo <= th <= hi)


def _sweep_job(args):
    a, rep = args
    spec = em.sweep_scenario(a)
    rng = np.random.default_rng(seed("sweep", a, rep))
    don, doff, y = em.generate(spec, rng)
    r = {"a": a, "rep": rep}
    for name, fn in (("B2", em.run_b2), ("B3", em.run_b3)):
        o = fn(don, doff, y, rng)
        lo, hi = o["angle_ci"]
        r[name] = {"ok": o["ok"], "gate_pass": o["gate_pass"], "angle": o["angle"], "angle_ci": [lo, hi],
                   "width": (hi - lo) if np.isfinite(lo) else None,
                   "circ_contains_0": em.circ_contains(lo, hi, 0.0), "lin_contains_0": lin_contains(lo, hi, 0.0),
                   "circ_contains_45": em.circ_contains(lo, hi, 45.0), "lin_contains_45": lin_contains(lo, hi, 45.0)}
    return r


def p4(out, reps=200):
    grid = (0.0, 0.05, 0.10, 0.20, 1 / 3)
    with Pool(2) as p:
        rows = p.map(_sweep_job, [(a, r) for a in grid for r in range(reps)], chunksize=20)
    with open(os.path.join(out, "P4_sweep_rows.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, default=float) + "\n")
    summ = {}
    for a in grid:
        R = [r for r in rows if r["a"] == a]
        d = {}
        for m in ("B2", "B3"):
            M = [r[m] for r in R if r[m]["ok"]]
            g = [x for x in M if x["gate_pass"]]
            d[m] = {"ok": len(M), "gate_pass_rate": round(len(g) / len(M), 4),
                    "median_angle_ci_width_all": round(float(np.median([x["width"] for x in M])), 1),
                    "median_angle_ci_width_gate_passed": round(float(np.median([x["width"] for x in g])), 1) if g else None,
                    "share_width_ge_180": round(float(np.mean([x["width"] >= 180 for x in M])), 3),
                    "share_width_ge_360": round(float(np.mean([x["width"] >= 360 for x in M])), 3),
                    "circular_vs_linear_disagree_on_0": int(sum(x["circ_contains_0"] != x["lin_contains_0"] for x in M)),
                    "circular_vs_linear_disagree_on_45": int(sum(x["circ_contains_45"] != x["lin_contains_45"] for x in M)),
                    "false_claim_rate": round(sum((not x["circ_contains_0"]) for x in g) / len(M), 4) if a > 0 else round(len(g) / len(M), 4),
                    "claim_midpoint_excluded_given_gate": round(sum((not x["circ_contains_45"]) for x in g) / len(M), 4)}
        summ[f"a={a:.3f}"] = d
    # archived statistics re-checked under circular containment
    arch = {}
    paths = {"Task05 Validation A (500 reps)": "../results/validationA/J20_core_reps500/fits.csv",
             "Task04 Stage 2 (100 reps)": "/tmp/claude-0/-home-claude/569ec786-da3a-5a21-98ca-7bc559b81a24/scratchpad/task04_archive_extract/task04/results/stage2/J20_reps100/fits.csv"}
    for lab, pth in paths.items():
        if not os.path.exists(pth):
            arch[lab] = "not available"; continue
        rows2 = [r for r in csv.DictReader(open(pth)) if r.get("stable") == "True"]
        dis = {}
        for r in rows2:
            lo, hi = float(r["angle_lo"]), float(r["angle_hi"])
            for th in (0.0, 45.0, -45.0):
                if em.circ_contains(lo, hi, th) != lin_contains(lo, hi, th):
                    key = f'{r["scenario"]} | {r.get("lapse_model","False")} | {th:+.0f}'
                    dis[key] = dis.get(key, 0) + 1
        arch[lab] = {"stable_fits_checked": len(rows2), "disagreements": dis}
    res = {"reps_per_grid_point": reps, "grid_onset_weight": list(grid), "summary": summ,
           "archived_angle_statistics_recheck": arch}
    json.dump(res, open(os.path.join(out, "P4_near_zero.json"), "w"), indent=1)
    return res


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    tg = p1_p2(out); print("P1/P2 done", round(time.time() - t0, 1), "s", flush=True)
    b = p3(out); print("P3 done", round(time.time() - t0, 1), "s", json.dumps(b), flush=True)
    s = p4(out); print("P4 done", round(time.time() - t0, 1), "s", flush=True)
