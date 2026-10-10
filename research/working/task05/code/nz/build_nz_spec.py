"""
Build the frozen NZ specification. Usage: python3 build_nz_spec.py OUT [--reps N] (N != 200 -> smoke, not frozen)
"""
import argparse, hashlib, json, os, time
import nz_common as c
CODE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TASK = os.path.dirname(CODE_ROOT)
CODE = ["nz/nz_common.py", "nz/nz_run.py", "nz/nz_analyse.py", "nz/nz_precheck.py", "nz/build_nz_spec.py",
        "e1_methods.py", "e1_run.py", "e1_analyse.py", "heterogeneity_methods.py", "ordinal_model.py", "stimulus.py"]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def main(a):
    pre = os.path.join(TASK, "results/NZ/precheck/precheck.json"); P = json.load(open(pre))["targets"]
    tg = {}
    for g in c.GRID:
        lab = c.label(g)
        tg[lab] = {"a": g, "beta_star": [P[lab]["beta_star"][0], 0.0], "beta_star_on_mc_se": P[lab]["beta_star_mc_se"][0],
                   "angle": 0.0 if g > 0 else None}
    spec = {
        "title": "Task 05 closure addendum: B3-t near-zero sensitivity validation (NZ). FROZEN specification",
        "status": "Reviewer-authorised targeted validation after the Task 05 closure record. Does not alter the frozen E1 verdict (REVISE), the E1-H2 results or the closure record's earlier sections.",
        "frozen_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "frozen": a.reps == 200,
        "grid": c.GRID, "reps_per_grid": a.reps, "batch_size": 50,
        "design": "12 participants x 20 order trials, homogeneous: onset weight a, offset weight 0, lapse 0.02, tau 1.0, bias SD 0.5 (e1_methods.sweep_scenario).",
        "seed_namespace": "task05-NZ-v1", "seed_rule": "int(sha256(f'{ns}|a=<a:.3f>|{rep}')[:16], 16) -> numpy default_rng",
        "procedure": "e1_methods.run_b3 unchanged; evaluated variant B3-t (angle_ci_t). B3-boot recorded descriptively only.",
        "targets": tg,
        "target_notes": "beta*_on by MC (400,000 draws; pre-check). beta*_off = 0 and angle 0 deg for a > 0, and beta* = (0, 0) at a = 0, by symmetry of the zero-mean orthogonal design (deduction; MC agrees to 1e-20).",
        "criteria": {
            "coverage_band": [0.90, 0.98],
            "N1": "Weight-CI coverage of beta*, w_on and w_off, within [0.90, 0.98] at every grid point.",
            "N2_grid": [0.20, 1 / 3],
            "N2": "Angle-interval coverage of the target angle 0 deg (circular containment) within [0.90, 0.98] at a = 0.20 and 1/3. At a = 0.05 and 0.10 angle coverage is reported descriptively, because strategy is interpreted only when the gate passes and the gate has low power there (pre-check P4: 0.05-0.33). This restriction was chosen before execution, with knowledge of P4.",
            "N3_max": 0.07,
            "N3": "False strategy claim: P(gate passes AND angle interval excludes the true angle 0 deg) <= 0.07 at every a > 0.",
            "N4_max": 0.07,
            "N4": "Gate false positive at a = 0: P(gate passes) <= 0.07.",
            "N5_max": 0.05, "N5": "Failure rate <= 0.05 at every grid point.",
            "mc_rule": "Point estimate decides met / not met; Wilson 95% MC interval classified clearly inside / indeterminate / clearly outside (as E1).",
            "descriptive": ["gate pass rate (power) by a", "P(gate and excludes 45 deg) by a", "angle interval width (all; gate-passed); share >= 180 and >= 360 deg",
                            "wrapping: share of intervals extending beyond +/-180 deg; circular vs linear containment disagreements at 0 and 45 deg",
                            "angle point estimate: circular mean, mean resultant length, share |angle| > 90 deg", "bias vs beta*", "B3-boot equivalents"]},
        "decision_rule": "NZ CONFIRMED for B3-t iff N1-N5 all met at point estimates and none clearly outside. Otherwise NOT CONFIRMED and returned to the reviewer; the provisional acceptance is not changed automatically in either direction. No other method is evaluated or selected.",
        "scope_limit": "1,000 datasets (5 grid points x 200). No extension of grid, reps or methods without reviewer approval.",
        "related_frozen": {"E1_spec_sha256": sha(os.path.join(TASK, "results/E1/E1_FROZEN_SPEC.json")),
                           "E1H2_spec_sha256": sha(os.path.join(TASK, "results/E1H2/E1H2_FROZEN_SPEC.json")),
                           "closure_record_sha256": sha(os.path.join(TASK, "task05-closure-decision-record.md"))},
        "precheck_sha256": sha(pre),
        "code_sha256": {f: sha(os.path.join(CODE_ROOT, f)) for f in CODE},
    }
    json.dump(spec, open(a.out, "w"), indent=1); print("written", a.out, "frozen" if spec["frozen"] else "(smoke)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--reps", type=int, default=200); main(ap.parse_args())
