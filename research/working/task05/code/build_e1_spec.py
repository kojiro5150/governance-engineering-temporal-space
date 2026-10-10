"""
Build the frozen E1 specification from the pre-check outputs.

Usage: python3 build_e1_spec.py PRECHECK_DIR OUT_JSON [--reps N]
(--reps other than 500 is for smoke tests only and writes a non-frozen spec.)
"""
import argparse
import hashlib
import json
import os
import time

import numpy as np

import e1_methods as em

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = ["e1_methods.py", "e1_run.py", "e1_analyse.py", "heterogeneity_methods.py", "ordinal_model.py", "stimulus.py"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main(a):
    P = json.load(open(os.path.join(a.precheck, "P1_P2_targets.json")))
    tg = P["targets"]
    # E1-e interpretation results (deterministic from frozen targets and mapping)
    b2_dev = {s: abs(v["angle_theta_star"] - v["angle_mu_w"]) for s, v in tg.items() if v["angle_mu_w"] is not None}
    b3_dev = {s: abs(v["angle_beta_star"] - v["angle_mu_w"]) for s, v in tg.items() if v["angle_mu_w"] is not None}
    map_dev = max(abs(r["response_angle"] - r["latent_angle"]) for rows in P["latent_to_response_angle"].values() for r in rows)
    spec = {
        "title": "Task 05 E1 heterogeneity validation: FROZEN specification",
        "frozen_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "frozen": a.reps == 500,
        "reps": a.reps,
        "n_participants": 12, "order_trials": 20,
        "seed_namespace": "task05-E1-v1",
        "seed_rule": "int(sha256(f'{ns}|{scenario}|{rep}')[:16], 16) -> numpy default_rng",
        "scenarios": {s: em.SCENARIOS[s] for s in em.SCENARIOS},
        "methods": {
            "B2": "B0 random-intercept ternary cumulative logit (marginal ML) + CR1 cluster-robust sandwich; weight CIs est +/- t(11) SE; gate: Wald T2/2 ~ F(2,11), p<0.05; angle CI: 2,000 multivariate t(11) draws, unwrapped percentile.",
            "B3-boot": "Per-participant LS slopes of signed score; group mean; weight CIs mean +/- t(11) SE; gate: one-sample Hotelling F(2,10), p<0.05; angle CI: 2,000 participant-bootstrap resamples, unwrapped percentile.",
            "B3-t": "As B3-boot, but angle CI from 2,000 multivariate t(11) draws using the participant sample covariance / n (AMENDMENT AM3)."},
        "targets": {s: {k: v[k] for k in ("mu_w", "angle_mu_w", "theta_star", "theta_star_mc_se", "angle_theta_star",
                                           "beta_star", "beta_star_mc_se", "angle_beta_star")} for s, v in tg.items()},
        "criteria": {
            "E1a_band": [0.90, 0.98],
            "E1a_definition": "Coverage of each method's OWN target by its 95% weight CIs (B2: theta*; B3: beta*), w_on and w_off, every scenario.",
            "E1a2_band": [0.90, 0.98],
            "E1a2_definition": "AMENDMENT AM5: coverage of the method's own target ANGLE by its angle interval (circular containment), every scenario with a defined angle (not S10).",
            "E1b_onset_scenario": "S01 onset moderate", "E1b_midpoint_scenario": "S04 midpoint moderate", "E1b_min": 0.80,
            "E1b_definition": "P(gate passes AND angle interval excludes 45 deg | S01) >= 0.80 and P(gate passes AND excludes 0 deg | S04) >= 0.80 (circular containment; AMENDMENT AM4).",
            "E1c_guessing_scenario": "S10 guessing", "E1c_max": 0.07,
            "E1c_definition": "P(gate passes | S10 guessing) <= 0.07.",
            "E1d_max": 0.05, "E1d_definition": "Estimation failure rate <= 0.05 in every scenario.",
            "E1e_definition": ("AMENDMENT AM5: interpretation. B2: |angle(theta*) - angle(mu_w)| <= 5 deg in every scenario with defined angle. "
                               "B3: |angle(beta*) - angle(mu_w)| <= 5 deg in every scenario AND max latent-to-response angle distortion over the frozen mapping grid <= 5 deg."),
            "magnitude": "Bias of B2 estimates relative to mu_w is REPORTED (estimand-specific) but not a pass/fail criterion; magnitude is the secondary estimand.",
            "mc_rule": "Each criterion judged on its point estimate; Wilson 95% MC interval classified clearly inside / indeterminate / clearly outside."},
        "E1e_results": {
            "B2": {"max_abs_angle_deviation_deg": round(max(b2_dev.values()), 3), "per_scenario": {k: round(v, 3) for k, v in b2_dev.items()},
                   "met": max(b2_dev.values()) <= 5.0},
            "B3": {"max_abs_angle_deviation_deg": round(max(b3_dev.values()), 3), "per_scenario": {k: round(v, 3) for k, v in b3_dev.items()},
                   "max_mapping_distortion_deg": round(map_dev, 3),
                   "met": max(b3_dev.values()) <= 5.0 and map_dev <= 5.0}},
        "decision_rule": ("A method variant is ACCEPTABLE only if every criterion E1a, E1a2, E1b, E1c, E1d is met at its point "
                          "estimate, none is 'clearly outside' by MC interval, and E1e is met. If more than one variant is "
                          "acceptable, NO automatic selection: report trade-offs (estimand scale, magnitude bias vs mu_w, "
                          "interval width, discrimination) for reviewer decision. If exactly one is acceptable, recommend it "
                          "subject to review. If none, REVISE the analysis plan. Latent-scale interpretation is not a tie-breaker."),
        "amendments_vs_task05_companion_section2": [
            "AM1 B2 target redefined as the pseudo-true working-model weights theta* (KL projection), estimated from 4 fits of 6,000 simulated participants per scenario; the companion's 'mean of individual latent weights in S13 and H2' target is replaced. Bias relative to mu_w reported separately.",
            "AM2 B3 target beta* kept on the response scale; no numeric comparison of B2 and B3 coefficients or angles.",
            "AM3 B3-t angle interval added after the near-zero pre-check showed the specified bootstrap interval falsely excluding the true onset angle in 7.5-9% of datasets at moderate-low sensitivity. The specified B3 bootstrap variant is retained and evaluated unchanged.",
            "AM4 Circular containment for all angle checks; discrimination counted only when the sensitivity gate passes; gate tests defined (B2 robust Wald F(2,11); B3 Hotelling F(2,10)).",
            "AM5 Criteria added: E1a2 (angle coverage of own target), E1e (interpretation). Magnitude bias reported, not gating.",
            "AM6 Decision rule changed: no default preference for B2 when more than one variant is acceptable (reviewer instruction).",
            "AM7 Archived Task 04 Stage 2 S10 angle statistics were computed with linear containment (8 disagreements with circular); not used in any criterion; noted only."],
        "precheck_evidence_sha256": {f: sha(os.path.join(a.precheck, f)) for f in sorted(os.listdir(a.precheck)) if f.endswith(".json")},
        "code_sha256": {f: sha(os.path.join(HERE, f)) for f in CODE},
    }
    json.dump(spec, open(a.out, "w"), indent=1)
    print("written", a.out, "frozen" if spec["frozen"] else "(smoke, not frozen)", "E1e", spec["E1e_results"]["B2"]["met"], spec["E1e_results"]["B3"]["met"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("precheck"); ap.add_argument("out"); ap.add_argument("--reps", type=int, default=500)
    main(ap.parse_args())
