"""
Build the frozen E1-H2 confirmatory amendment specification.
Usage: python3 build_e1h2_spec.py OUT_JSON [--reps N]   (N != 500 -> non-frozen smoke spec)
"""
import argparse, hashlib, json, os, time
CODE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TASK = os.path.dirname(CODE_ROOT)
CODE = ["e1h2/e1h2_common.py", "e1h2/e1h2_run.py", "e1h2/e1h2_analyse.py", "e1h2/e1h2_precheck.py", "e1h2/build_e1h2_spec.py",
        "e1_methods.py", "e1_run.py", "e1_analyse.py", "heterogeneity_methods.py", "ordinal_model.py", "stimulus.py"]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def main(a):
    e1spec = os.path.join(TASK, "results/E1/E1_FROZEN_SPEC.json")
    E1T = json.load(open(e1spec))["targets"]["H2 mixture 6 onset + 6 midpoint"]
    pre = os.path.join(TASK, "results/E1H2/precheck/precheck.json")
    spec = {
        "title": "Task 05 E1-H2 confirmatory amendment: FROZEN specification",
        "status": "AMENDMENT made after the original E1 results were seen. The original E1 specification, results and REVISE verdict are unchanged and remain the record of E1.",
        "frozen_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "frozen": a.reps == 500, "reps": a.reps,
        "seed_namespace": "task05-E1H2-confirm-v1",
        "seed_rule": "int(sha256(f'{ns}|{rep}')[:16], 16) -> numpy default_rng",
        "population": {"description": "Each participant independently onset-weighted (w_on 0.70, w_off 0) or midpoint-weighted (w_on 0.35, w_off 0.35) with probability 0.5; membership drawn per participant per dataset; lapse 0.02; tau 1.0; bias SD 0.5; no weight or threshold heterogeneity within groups.",
                       "n_participants": 12, "order_trials": 20, "p_onset": 0.5},
        "methods": "B2, B3-boot and B3-t exactly as in the frozen E1 specification (same code, imported unchanged).",
        "targets": {"mu_w": E1T["mu_w"], "angle_mu_w": E1T["angle_mu_w"],
                    "theta_star": E1T["theta_star"], "theta_star_mc_se": E1T["theta_star_mc_se"], "angle_theta_star": E1T["angle_theta_star"],
                    "beta_star": E1T["beta_star"], "beta_star_mc_se": E1T["beta_star_mc_se"], "angle_beta_star": E1T["angle_beta_star"],
                    "source": "Frozen E1 H2 targets. Population targets are functionals of the 50/50 population, not of a sample's composition, so they are unchanged by random membership (deduction). Pre-freeze check T1 re-estimated theta* under random membership: difference -0.23 and +0.04 combined MC SE; beta* recomputed identical to 5 decimals.",
                    "precheck_sha256": sha(pre)},
        "criteria": {"coverage_band": [0.90, 0.98], "failure_max": 0.05,
                     "H1": "95% weight-CI coverage of the method's own target (B2 theta*, B3 beta*), w_on and w_off, within [0.90, 0.98].",
                     "H2": "Angle-interval coverage of the own target angle (circular containment) within [0.90, 0.98].",
                     "H3": "Failure rate <= 0.05.",
                     "mc_rule": "Judged on point estimates; Wilson 95% MC interval classified clearly inside / indeterminate / clearly outside (same as E1).",
                     "descriptive_not_gating": ["gate pass rate; P(gate and excludes 0); P(gate and excludes 45); P(gate and excludes both); P(gate and excludes neither)",
                                                "bias vs own target with MC SE; empirical SD vs median SE; B2 bias vs mu_w and coverage of mu_w",
                                                "coverage by realised composition (informational)"],
                     "composition_strata": [["n_onset 0-4", 0, 4], ["n_onset 5-7", 5, 7], ["n_onset 8-12", 8, 12]]},
        "decision_rule": ("Per variant: H2-population criteria MET iff H1, H2 and H3 are met at point estimates and none is clearly outside. "
                          "Composite amended status (reported separately from, and never replacing, the original E1 verdict): the variant meets every "
                          "original E1 criterion outside the fixed-composition H2 scenario (from the frozen E1 results, read by hash) AND E1e AND the "
                          "H2-population criteria. No automatic selection: if several variants meet the composite, trade-offs are reported for reviewer "
                          "decision; latent-scale interpretation is not a tie-breaker."),
        "disclosures": ["Criteria bands are identical to E1; none was tuned after the exploratory run.",
                        "An exploratory post-hoc H2 run with random composition (D5, namespace task05-E1-posthoc-H2random-v1, Binomial(12,0.5) composition) was seen before this freeze. It is NOT counted as confirmatory and is not pooled with this run.",
                        "This amendment replaces only the H2 generator. It cannot remove the original E1 shortfalls in other scenarios (e.g. B2's E1c)."],
        "original_E1": {"spec_sha256": sha(e1spec),
                        "results_path_rel_code": "../results/E1/E1_results.json",
                        "results_sha256": sha(os.path.join(TASK, "results/E1/E1_results.json")),
                        "verdict": "REVISE (no variant acceptable)"},
        "code_sha256": {f: sha(os.path.join(CODE_ROOT, f)) for f in CODE},
    }
    json.dump(spec, open(a.out, "w"), indent=1); print("written", a.out, "frozen" if spec["frozen"] else "(smoke, not frozen)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--reps", type=int, default=500); main(ap.parse_args())
