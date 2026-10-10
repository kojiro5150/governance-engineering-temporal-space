"""
r3 verification (deterministic): the PRIMARY numeric B3-t outputs of the r3
wrapper are identical to those of the r2 wrapper on the same fixed inputs.
Fixtures are the hand-constructed ones from the r3 test suite. No simulation.
Usage: TASK05_CODE=... python3 verify_primary_unchanged_r2_r3.py R2_WRAPPER R3_CODE_DIR OUT_JSON
"""
import importlib.util, json, os, sys, tempfile
sys.dont_write_bytecode = True


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


r2 = load("wrapper_r2", sys.argv[1])
sys.path.insert(0, sys.argv[2]); sys.path.insert(0, os.path.join(sys.argv[2], "tests"))
r3 = load("wrapper_r3", os.path.join(sys.argv[2], "task06_analysis.py"))
import test_task06_analysis as T  # noqa: E402

KEYS = ("n", "status", "seed", "participant_slopes", "beta_mean", "se", "weight_ci_95", "magnitude_response_scale",
        "gate", "angle_deg", "angle_ci_B3t_95", "angle_ci_B3boot_stored_not_reported", "contains", "level1")
fixtures = {"base_12x3": T.build(), "x2_exclusion_13": T.build(n_per_cond=13, mutate=T._x2("A03")),
            "identical_singular": T.build(rule_fn=lambda i, a, b: T.sgn(a)),
            "n11": T.build(mutate=lambda t, s: s[0].update({"withdrawn": True}))}
report = {}
for name, (trials, sessions) in fixtures.items():
    d = tempfile.mkdtemp(); tp, sp = T.write(d, trials, sessions)
    o2 = r2.run_analysis(tp, sp, T.CODE); o3 = r3.run_analysis(tp, sp, T.CODE)
    res = {}
    for c in ("A", "B", "C"):
        a, b = o2["results"][c], o3["results"][c]
        diff = [k for k in KEYS if json.dumps(a.get(k), sort_keys=True) != json.dumps(b.get(k), sort_keys=True)]
        res[c] = {"identical_primary_numeric_keys": not diff, "differing_keys": diff,
                  "same_number_of_departure_flags": len(a.get("departures", [])) == len(b.get("departures", [])),
                  "departure_text_changed": a.get("departures") != b.get("departures"),
                  "r2_S6_class": a.get("S6_class"),
                  "r3_exploratory_label": (b.get("exploratory_descriptive_classification") or {}).get("label")}
    report[name] = res
ok = all(v["identical_primary_numeric_keys"] and v["same_number_of_departure_flags"] for r in report.values() for v in r.values())
json.dump({"all_identical": ok, "keys_compared": KEYS, "fixtures": report}, open(sys.argv[3], "w"), indent=1)
print("all primary numeric outputs identical r2 vs r3 (departure flags present in the same cases; wording extended in r3):", ok)
