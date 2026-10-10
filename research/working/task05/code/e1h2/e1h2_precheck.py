"""
Pre-freeze checks for E1-H2 (run BEFORE the specification is frozen):
  T1 target cross-check: theta* re-estimated under random membership
     (4 seeds x 6,000 participants, membership Bernoulli(0.5) per participant)
     compared with the frozen E1 H2 theta* (fixed 50/50, also 4 x 6,000).
     beta* and mu_w are deterministic functions of the 50/50 population and
     are identical by construction (deduction); beta* re-estimated as a check.
  T2 runtime benchmark: 20 complete datasets (generation + B2 + B3).
Usage: python3 e1h2_precheck.py E1_FROZEN_SPEC OUT_JSON
"""
import hashlib, json, sys, time
import numpy as np
import e1h2_common as c
import e1_methods as em
import ordinal_model as om

NS = "task05-E1H2-precheck-v1"

def seed(tag, i):
    return int(hashlib.sha256(f"{NS}|{tag}|{i}".encode()).hexdigest()[:16], 16)

def main(spec_path, out):
    E1 = json.load(open(spec_path))["targets"]["H2 mixture 6 onset + 6 midpoint"]
    vals = []
    t0 = time.time()
    for i in range(4):
        rng = np.random.default_rng(seed("theta", i))
        m = rng.random(6000) < c.P_ONSET; k = int(m.sum())
        don, doff, y = em.generate(dict(groups=[(k, *c.ONSET), (6000 - k, *c.MIDPOINT)], lapse=c.LAPSE), rng)
        f = om.fit(don, doff, y); vals.append([f["w_on"], f["w_off"], k])
    vals = np.array(vals)
    th = vals[:, :2].mean(0); th_se = vals[:, :2].std(0, ddof=1) / 2
    t_theta = time.time() - t0
    b, bse = em.beta_star(c.population_spec(), np.random.default_rng(seed("beta", 0)))
    # T2 benchmark
    times = []
    for i in range(20):
        t = time.perf_counter(); rng = np.random.default_rng(seed("bench", i))
        don, doff, y, k = c.generate(rng); em.run_b2(don, doff, y, rng); em.run_b3(don, doff, y, rng)
        times.append(time.perf_counter() - t)
    r = {"T1_theta_star_random_membership": th.round(5).tolist(), "T1_theta_star_mc_se": th_se.round(5).tolist(),
         "T1_fits": vals.tolist(), "T1_seconds": round(t_theta, 1),
         "frozen_E1_H2_theta_star": E1["theta_star"], "frozen_E1_H2_theta_star_mc_se": E1["theta_star_mc_se"],
         "theta_diff_over_combined_se": ((th - np.array(E1["theta_star"])) / np.hypot(th_se, np.array(E1["theta_star_mc_se"]))).round(2).tolist(),
         "T1_beta_star_recomputed": b.round(5).tolist(), "T1_beta_star_mc_se": bse.round(6).tolist(),
         "frozen_E1_H2_beta_star": E1["beta_star"],
         "T2_complete_dataset_seconds": {"median": round(float(np.median(times)), 4), "max": round(max(times), 4),
                                        "projection_500_single_process_s": round(500 * float(np.mean(times)), 1)}}
    json.dump(r, open(out, "w"), indent=1); print(json.dumps(r, indent=1))

if __name__ == "__main__":
    main(*sys.argv[1:])
