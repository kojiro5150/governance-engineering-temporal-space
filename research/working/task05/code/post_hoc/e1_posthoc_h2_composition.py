"""
POST-HOC, EXPLORATORY (not part of the frozen E1 specification; does not alter
the E1 verdict). Tests one explanation for the H2 over-coverage: the frozen
generator fixes the mixture composition at exactly 6 onset + 6 midpoint in
every dataset, whereas the participant-level SEs of B2 and B3 estimate
sampling variance for participants drawn at random from a 50/50 population,
which includes variation in composition.

Here n_onset ~ Binomial(12, 0.5) per dataset. The population targets are the
frozen H2 targets (theta*, beta* were computed at a 50/50 split).
Frozen code imported unchanged.

Usage: python3 e1_posthoc_h2_composition.py SPEC OUT_JSONL [--reps 500]
"""
import argparse, hashlib, json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import e1_methods as em
from e1_run import clean

NS = "task05-E1-posthoc-H2random-v1"

def main(a):
    spec = json.load(open(a.spec))
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)["rep"] for l in open(a.out)}
    with open(a.out, "a") as f:
        for rep in range(a.reps):
            if rep in done:
                continue
            s = int(hashlib.sha256(f"{NS}|{rep}".encode()).hexdigest()[:16], 16)
            rng = np.random.default_rng(s)
            k = int(rng.binomial(12, 0.5))
            groups = [g for g in [(k, 0.70, 0.0), (12 - k, 0.35, 0.35)] if g[0] > 0]
            don, doff, y = em.generate(dict(groups=groups, lapse=0.02), rng)
            row = {"rep": rep, "seed": str(s), "n_onset": k,
                   "B2": em.run_b2(don, doff, y, rng), "B3": em.run_b3(don, doff, y, rng)}
            f.write(json.dumps(clean(row)) + "\n"); f.flush(); os.fsync(f.fileno())

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("out"); ap.add_argument("--reps", type=int, default=500)
    main(ap.parse_args())
