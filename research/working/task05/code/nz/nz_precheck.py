"""
Pre-freeze: beta* targets per grid point (deterministic MC, fixed seed) and
runtime benchmark (20 complete datasets per grid point, B3 only).
Usage: python3 nz_precheck.py OUT_JSON
"""
import hashlib, json, sys, time
import numpy as np
import nz_common as c
import e1_methods as em

NS = "task05-NZ-precheck-v1"
sd = lambda t: int(hashlib.sha256(f"{NS}|{t}".encode()).hexdigest()[:16], 16)

out = {"targets": {}, "benchmark": {}}
for a in c.GRID:
    b, se = em.beta_star(c.scenario(a), np.random.default_rng(sd(f"beta|{a}")))
    out["targets"][c.label(a)] = {"a": a, "beta_star": b.tolist(), "beta_star_mc_se": se.tolist(),
                                  "angle_beta_star": em.angle(b) if a > 0 else None,
                                  "angle_note": "a=0: beta*=(0,0) exactly (zero-mean design columns; deduction); angle undefined" if a == 0 else "latent angle 0 deg; response-scale angle 0 deg (w_off=0 => beta*_off=0 by symmetry)"}
    t = []
    for i in range(20):
        t0 = time.perf_counter(); rng = np.random.default_rng(sd(f"bench|{a}|{i}"))
        don, doff, y = em.generate(c.scenario(a), rng); em.run_b3(don, doff, y, rng); t.append(time.perf_counter() - t0)
    out["benchmark"][c.label(a)] = {"median_s": round(float(np.median(t)), 5), "max_s": round(max(t), 5)}
out["projection_1000_single_process_s"] = round(200 * sum(v["median_s"] for v in out["benchmark"].values()), 1)
json.dump(out, open(sys.argv[1], "w"), indent=1); print(json.dumps(out, indent=1))
