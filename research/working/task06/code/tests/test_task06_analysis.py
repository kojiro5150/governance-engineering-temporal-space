"""
Deterministic unit tests for the Task 06 analysis wrapper.

No stochastic simulation: every fixture is hand-constructed from deterministic
response rules applied to the frozen 20-trial order template. The only random
numbers are those drawn INSIDE the frozen B3-t procedure and the Level 1
bootstrap, from fixed pre-registered seeds, exactly as in a real analysis.

Run:  TASK05_CODE=<path to research/working/task05/code> python3 -m unittest -v tests/test_task06_analysis.py
(from the task06/code directory). If TASK05_CODE is unset, ../../task05/code is
tried (repository layout research/working/task06/code).
"""
import copy
import csv
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import numpy as np  # noqa: E402
from scipy.stats import t as student_t  # noqa: E402

import task06_analysis as ta  # noqa: E402

CODE = os.environ.get("TASK05_CODE") or os.path.normpath(os.path.join(HERE, "..", "..", "..", "task05", "code"))
EM, ST = ta.load_frozen(CODE)


# ----------------------------------------------------------------- fixtures --
def sgn(x):
    return "L" if x > 0 else ("R" if x < 0 else "S")


def rule(i, don, doff):
    """Deterministic participant-specific response rules (varied so that the
    participant slope covariance is non-singular)."""
    r = sgn(don)
    if i % 3 == 1 and don == 0:
        r = sgn(doff)                      # uses offset when onsets are equal
    if i % 4 == 2 and don != 0 and doff == 0:
        r = "S"                            # says 'same' on onset-only trials
    if i == 5 and don > 0 and doff < 0:
        r = "S"
    if i == 7 and don < 0 and doff > 0:
        r = "L"                            # follows offset on one conflict cell
    return r


def build(n_per_cond=12, conditions=("A", "B", "C"), rule_fn=rule, mutate=None):
    trials, sessions = [], []
    tmpl = ST.order_templates(2, 4)
    for c in conditions:
        for i in range(n_per_cond):
            code = f"{c}{i:02d}"
            sessions.append({"participant_code": code, "condition": c, "calibration_correct": 10,
                             "attention_pass": True, "frame_prop_within_1p5": 0.99,
                             "viewport_css_px": 1280, "withdrawn": False})
            for t in tmpl:
                trials.append({"participant_code": code, "condition": c, "block": "order", "trial_kind": "main",
                               "template_id": t.template_id, "d_on": t.d_on, "d_off": t.d_off, "valid": 1,
                               "response": rule_fn(i, t.d_on, t.d_off)})
            for k, d in enumerate((8.0, 8.0, -8.0, -8.0)):
                trials.append({"participant_code": code, "condition": c, "block": "order", "trial_kind": "catch",
                               "template_id": f"catch#{k}", "d_on": d, "d_off": d, "valid": 1, "response": sgn(d)})
    if mutate:
        mutate(trials, sessions)
    return trials, sessions


def write(tmp, trials, sessions, name="t"):
    tp, sp = os.path.join(tmp, f"{name}.csv"), os.path.join(tmp, f"{name}.json")
    with open(tp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(trials[0].keys()))
        w.writeheader(); w.writerows(trials)
    with open(sp, "w") as f:
        json.dump(sessions, f)
    return tp, sp


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_all(self, trials, sessions, name="t", **kw):
        tp, sp = write(self.tmp, trials, sessions, name)
        return ta.run_analysis(tp, sp, CODE, **kw)


# -------------------------------------------------------------------- tests --
class TestFrozenCode(Base):
    def test_hashes_verified(self):
        for f, h in ta.FROZEN_SHA256.items():
            self.assertEqual(ta.sha256_file(os.path.join(CODE, f)), h)

    def test_refuses_modified_copy(self):
        d = os.path.join(self.tmp, "code"); shutil.copytree(CODE, d, ignore=shutil.ignore_patterns("__pycache__"))
        with open(os.path.join(d, "e1_methods.py"), "a") as f:
            f.write("\n# tampered\n")
        with self.assertRaises(RuntimeError):
            ta.load_frozen(d)


class TestCoding(Base):
    def test_response_coding_matches_frozen_convention(self):
        self.assertEqual(ta.RESPONSE_CODE, {"R": 0, "S": 1, "L": 2})
        # frozen b3_individual uses score = y - 1: one participant answering L on every
        # left-leading onset trial gets a positive onset slope
        don, doff = EM.design(1)
        y = np.where(don > 0, 2, np.where(don < 0, 0, 1))
        import heterogeneity_methods as hm
        b_on, b_off = hm.b3_individual(don, doff, y)
        self.assertAlmostEqual(float(b_on[0]), 36.0 / 108.0, places=12)
        self.assertAlmostEqual(float(b_off[0]), 0.0, places=12)

    def test_seed_rule(self):
        self.assertEqual(ta.seed_for("task06-primary-B3t-v1|A"),
                         int(__import__("hashlib").sha256(b"task06-primary-B3t-v1|A").hexdigest()[:16], 16))
        self.assertNotEqual(ta.seed_for("task06-primary-B3t-v1|A"), ta.seed_for("task06-primary-B3t-v1|B"))


class TestExclusions(Base):
    def excl(self, mutate):
        trials, sessions = build(n_per_cond=12, conditions=("A",), mutate=mutate)
        return ta.apply_exclusions({s["participant_code"]: s for s in sessions}, trials, ST)

    def test_complete_participants_included(self):
        e = self.excl(None)
        self.assertTrue(all(not v["excluded"] for v in e.values()))

    def test_each_rule(self):
        def m(trials, sessions):
            sessions[0]["calibration_correct"] = 8
            sessions[2]["attention_pass"] = False
            sessions[3]["frame_prop_within_1p5"] = 0.94
            sessions[4]["viewport_css_px"] = 899
            sessions[6]["withdrawn"] = True
            k = 0
            for t in trials:
                if t["participant_code"] == "A01" and t["trial_kind"] == "catch" and k < 3:
                    t["response"] = "S"; k += 1
            for t in trials:
                if t["participant_code"] == "A05" and t["trial_kind"] == "main":
                    t["valid"] = 0
                    break
        e = self.excl(m)
        self.assertEqual(e["A00"]["rules"], ["X1"])
        self.assertEqual(e["A01"]["rules"], ["X2"])
        self.assertEqual(e["A02"]["rules"], ["X3"])
        self.assertEqual(e["A03"]["rules"], ["X4"])
        self.assertEqual(e["A04"]["rules"], ["X5"])
        self.assertEqual(e["A05"]["rules"], ["X6"])
        self.assertEqual(e["A06"]["rules"], ["X7"])
        self.assertFalse(e["A07"]["excluded"])

    def test_requeued_trial_restores_completeness(self):
        def m(trials, sessions):
            t0 = next(t for t in trials if t["participant_code"] == "A05" and t["trial_kind"] == "main")
            again = dict(t0); t0["valid"] = 0; trials.append(again)   # invalid original + valid re-queue
        self.assertFalse(self.excl(m)["A05"]["excluded"])

    def test_duplicate_valid_main_trial_is_x6(self):
        def m(trials, sessions):
            t0 = next(t for t in trials if t["participant_code"] == "A05" and t["trial_kind"] == "main")
            trials.append(dict(t0))
        self.assertEqual(self.excl(m)["A05"]["rules"], ["X6"])

    def test_missing_catch_is_x6(self):
        def m(trials, sessions):
            next(t for t in trials if t["participant_code"] == "A05" and t["trial_kind"] == "catch")["valid"] = 0
        self.assertEqual(self.excl(m)["A05"]["rules"], ["X6"])

    def test_exclusions_never_read_main_responses(self):
        trials, sessions = build(conditions=("A",))
        blank = copy.deepcopy(trials)
        for t in blank:
            if t["trial_kind"] == "main":
                t["response"] = None
        S = {s["participant_code"]: s for s in sessions}
        self.assertEqual(ta.apply_exclusions(S, trials, ST), ta.apply_exclusions(S, blank, ST))


class TestPrimaryAnalysis(Base):
    def test_matches_frozen_run_b3_exactly(self):
        trials, sessions = build()
        res = self.run_all(trials, sessions)["results"]["A"]
        don = np.zeros((12, 20)); doff = np.zeros((12, 20)); y = np.zeros((12, 20), dtype=int)
        tmpl = sorted(ST.order_templates(2, 4), key=lambda t: (t.d_on, t.d_off, t.template_id))
        for i in range(12):
            don[i] = [t.d_on for t in tmpl]; doff[i] = [t.d_off for t in tmpl]
            y[i] = [ta.RESPONSE_CODE[rule(i, t.d_on, t.d_off)] for t in tmpl]
        direct = EM.run_b3(don, doff, y, np.random.default_rng(ta.seed_for("task06-primary-B3t-v1|A")))
        self.assertEqual(res["angle_ci_B3t_95"], direct["angle_ci_t"])
        self.assertEqual(res["beta_mean"], direct["est"])
        self.assertEqual(res["gate"]["p"], direct["gate_p"])
        self.assertEqual(res["weight_ci_95"], direct["ci_w"])
        self.assertEqual(res["departures"], [])

    def test_closed_form_equals_ols_with_intercept_on_complete_data(self):
        trials, sessions = build()
        res = self.run_all(trials, sessions)["results"]["A"]
        tmpl = sorted(ST.order_templates(2, 4), key=lambda t: (t.d_on, t.d_off, t.template_id))
        X = np.column_stack([np.ones(20), [t.d_on for t in tmpl], [t.d_off for t in tmpl]])
        for i, (b_on, b_off) in enumerate(res["participant_slopes"]):
            s = np.array([ta.RESPONSE_CODE[rule(i, t.d_on, t.d_off)] - 1 for t in tmpl], dtype=float)
            coef = np.linalg.lstsq(X, s, rcond=None)[0]
            self.assertAlmostEqual(coef[1], b_on, places=12)
            self.assertAlmostEqual(coef[2], b_off, places=12)

    def test_deterministic_and_order_invariant(self):
        trials, sessions = build()
        r1 = self.run_all(trials, sessions, "a")
        r2 = self.run_all(list(reversed(trials)), list(reversed(sessions)), "b")
        for k in ("inputs_sha256", "wrapper_sha256"):
            r1.pop(k); r2.pop(k)
        self.assertEqual(json.dumps(r1, sort_keys=True), json.dumps(r2, sort_keys=True))

    def test_singular_covariance_fails_gate(self):
        trials, sessions = build(rule_fn=lambda i, don, doff: sgn(don))   # identical participants
        res = self.run_all(trials, sessions)["results"]["A"]
        self.assertFalse(res["gate"]["pass"])
        cls = res["exploratory_descriptive_classification"]
        self.assertIsNone(cls["label"])
        self.assertIn("gate failed", cls["suppressed_reason"])
        self.assertFalse(res["Q2_cue_weighting"]["issued"])
        self.assertIsNone(res["Q2_cue_weighting"]["outcome"])

    def test_n11_departure_flag_and_t10(self):
        trials, sessions = build(n_per_cond=12, mutate=lambda t, s: s[0].update({"withdrawn": True}))
        res = self.run_all(trials, sessions)["results"]["A"]
        self.assertEqual(res["n"], 11)
        self.assertEqual(len(res["departures"]), 1)
        tc = student_t.ppf(0.975, 10)
        self.assertAlmostEqual(res["weight_ci_95"][0][1] - res["beta_mean"][0], tc * res["se"][0], places=12)

    def test_n_below_3_not_computable(self):
        trials, sessions = build(n_per_cond=2)
        self.assertTrue(self.run_all(trials, sessions)["results"]["A"]["status"].startswith("not computable"))


def _x2(code, n_err=3):
    """Mutator: make participant `code` fail X2 (catch errors only)."""
    def m(trials, sessions):
        k = 0
        for t in trials:
            if t["participant_code"] == code and t["trial_kind"] == "catch" and k < n_err:
                t["response"] = "S"; k += 1
    return m


class TestAddBackR3(Base):
    def test_ids_flags_and_suppression_n13(self):
        # 13 participants in A, one fails X2 only: primary n = 12, add-back n = 13
        trials, sessions = build(n_per_cond=13, conditions=("A",), mutate=_x2("A03"))
        out = self.run_all(trials, sessions)
        prim, ab = out["results"]["A"], out["exploratory_addback_analyses"]["A"]
        self.assertEqual(prim["analysis_id"], "PRIMARY-B3T-A")
        self.assertEqual(ab["analysis_id"], "EXPLORATORY-ADDBACK-X2X3-A")
        self.assertNotEqual(prim["analysis_id"], ab["analysis_id"])
        self.assertEqual((prim["n"], ab["n"]), (12, 13))
        self.assertTrue(ab["exploratory"] and ab["sample_size_departure"] and ab["inclusion_criteria_differ_from_primary"])
        self.assertFalse(ab["within_validated_design"])
        self.assertIn("UNVALIDATED", ab["numeric_status"])
        self.assertIn("does not establish validated coverage", ab["numeric_status"])
        self.assertIn("does NOT establish validated coverage", ab["departures"][0])
        self.assertIsNone(ab["exploratory_descriptive_classification"]["label"])
        self.assertIn("outside the validated design", ab["exploratory_descriptive_classification"]["suppressed_reason"])
        self.assertFalse(ab["Q2_cue_weighting"]["issued"])
        self.assertNotIn("level1", ab)

    def test_addback_n12_still_exploratory_and_suppressed(self):
        def m(trials, sessions):
            _x2("A03")(trials, sessions)
            sessions[5]["withdrawn"] = True
        trials, sessions = build(n_per_cond=12, conditions=("A",), mutate=m)
        out = self.run_all(trials, sessions)
        ab = out["exploratory_addback_analyses"]["A"]
        self.assertEqual((out["results"]["A"]["n"], ab["n"]), (10, 11))
        def m2(trials, sessions):
            _x2("A03")(trials, sessions)
        trials, sessions = build(n_per_cond=12, conditions=("A",), mutate=m2)
        ab = self.run_all(trials, sessions, "n12")["exploratory_addback_analyses"]["A"]
        self.assertEqual(ab["n"], 12)
        self.assertFalse(ab["sample_size_departure"])
        self.assertTrue(ab["exploratory"])
        self.assertFalse(ab["within_validated_design"])
        self.assertIsNone(ab["exploratory_descriptive_classification"]["label"])
        self.assertFalse(ab["Q2_cue_weighting"]["issued"])

    def test_difference_from_primary_reported(self):
        trials, sessions = build(n_per_cond=13, conditions=("A",), mutate=_x2("A03"))
        out = self.run_all(trials, sessions)
        prim, ab = out["results"]["A"], out["exploratory_addback_analyses"]["A"]
        d = ab["difference_from_primary"]
        self.assertEqual(d["n"], 1)
        for i in range(2):
            self.assertAlmostEqual(d["beta_mean"][i], ab["beta_mean"][i] - prim["beta_mean"][i], places=15)
        self.assertAlmostEqual(d["angle_deg"], ta.wrap180(ab["angle_deg"] - prim["angle_deg"]), places=12)

    def test_primary_unchanged_by_addback(self):
        trials, sessions = build(n_per_cond=13, conditions=("A",), mutate=_x2("A03"))
        prim = self.run_all(trials, sessions)["results"]["A"]
        keep = [i for i in range(13) if i != 3]
        tmpl = sorted(ST.order_templates(2, 4), key=lambda t: (t.d_on, t.d_off, t.template_id))
        don = np.array([[t.d_on for t in tmpl]] * 12); doff = np.array([[t.d_off for t in tmpl]] * 12)
        y = np.array([[ta.RESPONSE_CODE[rule(i, t.d_on, t.d_off)] for t in tmpl] for i in keep])
        direct = EM.run_b3(don, doff, y, np.random.default_rng(ta.seed_for("task06-primary-B3t-v1|A")))
        self.assertEqual(prim["angle_ci_B3t_95"], direct["angle_ci_t"])
        self.assertEqual(prim["beta_mean"], direct["est"])

    def test_no_addback_when_nothing_to_add(self):
        trials, sessions = build(conditions=("A",))
        ab = self.run_all(trials, sessions)["exploratory_addback_analyses"]["A"]
        self.assertEqual(ab["added_participants"], [])
        self.assertTrue(ab["status"].startswith("not run"))


class TestInterpretation(Base):
    def test_s6_classifier(self):
        cases = [((-5, 20), "onset-dominant cue weighting"), ((30, 60), "midpoint-like cue weighting"),
                 ((-5, 50), "indeterminate: contains both 0 and 45 deg"), ((-10, 51), "indeterminate: interval wider than 60 deg"),
                 ((70, 110), "offset-dominant cue weighting"), ((-60, -30), "rate or duration cue"),
                 ((150, 190), "numeric description only"), ((-15, 20), "numeric description only")]
        for (lo, hi), want in cases:
            self.assertEqual(ta.classify_s6(EM, True, lo, hi), want, (lo, hi))
        self.assertEqual(ta.classify_s6(EM, False, -5, 20), "no statement: gate failed")  # raw rule only; never reported alone
        self.assertEqual(ta.classify_s6(EM, True, float("nan"), 3), "no statement: interval undefined")

    def test_circular_containment_across_boundary(self):
        self.assertTrue(EM.circ_contains(170, 200, -175))
        self.assertFalse(EM.circ_contains(170, 200, 0))

    def test_q2_outcomes(self):
        self.assertEqual(ta.q2_outcome("onset-dominant cue weighting"), "expectation met")
        self.assertEqual(ta.q2_outcome("midpoint-like cue weighting"), "expectation not met")
        self.assertEqual(ta.q2_outcome("numeric description only"), "indeterminate")


def _walk(o, path=()):
    if isinstance(o, dict):
        yield path, o
        for kk, v in o.items():
            yield from _walk(v, path + (kk,))
    elif isinstance(o, list):
        for n, v in enumerate(o):
            yield from _walk(v, path + (n,))


class TestClassificationR3(Base):
    def numeric(self, lo, hi, gate=True):
        return {"beta_mean": [0.2, 0.05], "weight_ci_95": [[0.1, 0.3], [0.0, 0.1]], "angle_deg": (lo + hi) / 2,
                "angle_ci_B3t_95": [lo, hi], "gate": {"p": 0.001 if gate else 0.4, "pass": gate}}

    def label(self, lo, hi, gate=True):
        return ta.descriptive_classification(EM, self.numeric(lo, hi, gate))["label"]

    def test_gate_failure_reports_no_label_but_keeps_numbers(self):
        obj = ta.descriptive_classification(EM, self.numeric(-5, 20, gate=False))
        self.assertIsNone(obj["label"])
        self.assertIn("gate failed", obj["suppressed_reason"])
        self.assertEqual(obj["numeric_context"]["angle_ci_B3t_95"], [-5, 20])
        self.assertFalse(obj["numeric_context"]["gate"]["pass"])

    def test_boundary_containment(self):
        self.assertEqual(self.label(-10.0, 25.0), "onset-dominant cue weighting")
        self.assertEqual(self.label(-10.0, 25.0001), "numeric description only")
        self.assertEqual(self.label(-10.0001, 25.0), "numeric description only")
        self.assertEqual(self.label(30.0, 90.0), "midpoint-like cue weighting")          # width exactly 60
        self.assertEqual(self.label(30.0, 90.0001), "indeterminate: interval wider than 60 deg")
        self.assertEqual(self.label(45.0, 80.0), "midpoint-like cue weighting")          # 45 on the endpoint
        self.assertEqual(self.label(45.0001, 80.0), "numeric description only")

    def test_offset_dominant(self):
        self.assertEqual(self.label(70.0, 110.0), "offset-dominant cue weighting")
        # documents the retained asymmetry: offset needs only the general 60 deg cap,
        # onset-dominant is confined to a 35 deg band (thresholds not validated)
        self.assertEqual(self.label(61.0, 119.0), "offset-dominant cue weighting")
        self.assertEqual(self.label(40.0, 100.0), "midpoint-like cue weighting")
        self.assertEqual(self.label(85.0, 150.0), "indeterminate: interval wider than 60 deg")

    def test_ambiguous_intervals(self):
        self.assertEqual(self.label(-5.0, 50.0), "indeterminate: contains both 0 and 45 deg")
        self.assertEqual(self.label(150.0, 190.0), "numeric description only")
        self.assertEqual(self.label(-15.0, 20.0), "numeric description only")
        self.assertEqual(self.label(float("nan"), 3.0), "no statement: interval undefined")

    def test_exploratory_status_fields(self):
        obj = ta.descriptive_classification(EM, self.numeric(-5, 20))
        self.assertEqual(obj["status"], ta.CLASSIFICATION_STATUS)
        self.assertIn("EXPLORATORY", obj["status"])
        self.assertIn("NOT A VALIDATED MECHANISM IDENTIFICATION", obj["status"])
        self.assertFalse(obj["validated"]); self.assertFalse(obj["mechanism_identified"]); self.assertFalse(obj["confirmatory"])
        self.assertIn("not confirmatory", obj["qualification"])

    def test_numbers_reported_alongside_label(self):
        trials, sessions = build()
        res = self.run_all(trials, sessions)["results"]["A"]
        obj = res["exploratory_descriptive_classification"]
        self.assertIsNotNone(obj["label"])
        for k in ("beta_mean", "weight_ci_95", "angle_deg", "angle_ci_B3t_95", "gate"):
            self.assertEqual(obj["numeric_context"][k], res[k])

    def test_labels_never_appear_outside_exploratory_objects(self):
        trials, sessions = build(n_per_cond=13, mutate=_x2("A03"))
        out = self.run_all(trials, sessions)
        text = json.dumps(out)
        self.assertNotIn('"S6_class"', text)
        for path, d in _walk(out):
            for kk, v in d.items():
                if isinstance(v, str) and v in ta.S6_LABELS:
                    self.assertEqual(kk, "label", path)
                    self.assertEqual(d.get("status"), ta.CLASSIFICATION_STATUS, path)
                    self.assertIs(d.get("validated"), False, path)
                    self.assertIs(d.get("mechanism_identified"), False, path)
        self.assertIn("NOT IDENTIFIED", out["interpretation_status"]["psychological_mechanisms"])

    def test_q2_derived_and_qualified(self):
        trials, sessions = build()
        q2 = self.run_all(trials, sessions)["results"]["A"]["Q2_cue_weighting"]
        self.assertTrue(q2["issued"])
        self.assertEqual(q2["outcome"], "expectation met")
        self.assertIn("not confirmatory evidence", q2["status"])

    def test_ols_analysis_removed_from_outputs(self):
        # r3.1, OD-22: the incomplete-trial OLS analysis is removed, not merely marked
        trials, sessions = build(conditions=("A",))
        out = self.run_all(trials, sessions)
        self.assertNotIn("not_implemented", out)
        self.assertNotIn("OLS", json.dumps(out))


def _direct(n, rule_fn=None):
    """Direct frozen run_b3 on the first n fixture participants (primary seed for A)."""
    rule_fn = rule_fn or rule
    tmpl = sorted(ST.order_templates(2, 4), key=lambda t: (t.d_on, t.d_off, t.template_id))
    don = np.array([[t.d_on for t in tmpl]] * n); doff = np.array([[t.d_off for t in tmpl]] * n)
    y = np.array([[ta.RESPONSE_CODE[rule_fn(i, t.d_on, t.d_off)] for t in tmpl] for i in range(n)])
    return EM.run_b3(don, doff, y, np.random.default_rng(ta.seed_for("task06-primary-B3t-v1|A")))


class TestEnvelopeR31(Base):
    """OD-21: suppress S6 classification and Q2c whenever the PRIMARY analysis has
    n != 12; keep the numeric B3-t results and flag the envelope departure."""

    def _primary(self, n, rule_fn=rule):
        trials, sessions = build(n_per_cond=n, conditions=("A",), rule_fn=rule_fn)
        return self.run_all(trials, sessions, f"n{n}")["results"]["A"]

    def test_n12_gate_pass_classified(self):
        res = self._primary(12)
        self.assertTrue(res["gate"]["pass"])
        self.assertFalse(res["outside_validated_envelope"])
        self.assertTrue(res["within_validated_design"])
        self.assertIsNotNone(res["exploratory_descriptive_classification"]["label"])
        self.assertTrue(res["Q2_cue_weighting"]["issued"])
        self.assertNotIn("envelope_note", res)
        self.assertEqual(res["Q1_sensitivity"], "gate passed")

    def _check_suppressed(self, n):
        res = self._primary(n)
        self.assertEqual(res["n"], n)
        self.assertTrue(res["gate"]["pass"], "fixture must pass the gate for this test")
        self.assertTrue(res["outside_validated_envelope"])
        self.assertFalse(res["within_validated_design"])
        self.assertIn("outside the validated operating-characteristic envelope", res["envelope_note"])
        cls = res["exploratory_descriptive_classification"]
        self.assertIsNone(cls["label"])
        self.assertIn("OD-21", cls["suppressed_reason"])
        self.assertEqual(cls["status"], ta.CLASSIFICATION_STATUS)
        self.assertFalse(res["Q2_cue_weighting"]["issued"])
        self.assertIsNone(res["Q2_cue_weighting"]["outcome"])
        self.assertIn("outside the validated envelope", res["Q1_sensitivity"])
        # numeric B3-t results preserved and identical to the frozen procedure
        d = _direct(n)
        self.assertEqual(res["beta_mean"], d["est"])
        self.assertEqual(res["se"], d["se"])
        self.assertEqual(res["angle_deg"], d["angle"])
        self.assertEqual(res["angle_ci_B3t_95"], d["angle_ci_t"])
        self.assertEqual(res["gate"], {"p": d["gate_p"], "pass": d["gate_pass"]})
        tc = student_t.ppf(0.975, n - 1)
        self.assertAlmostEqual(res["weight_ci_95"][1][1] - res["beta_mean"][1], tc * res["se"][1], places=12)
        self.assertEqual(len(res["departures"]), 1)
        self.assertIn("level1", res)
        return res

    def test_n11_gate_pass_suppressed_numeric_kept(self):
        self._check_suppressed(11)

    def test_n13_gate_pass_suppressed_numeric_kept(self):
        self._check_suppressed(13)

    def test_n13_gate_fail_suppressed(self):
        res = self._primary(13, rule_fn=lambda i, a, b: sgn(a))   # identical participants: singular S
        self.assertFalse(res["gate"]["pass"])
        self.assertTrue(res["outside_validated_envelope"])
        self.assertIsNone(res["exploratory_descriptive_classification"]["label"])
        self.assertFalse(res["Q2_cue_weighting"]["issued"])

    def test_n12_numeric_matches_frozen(self):
        res = self._primary(12)
        d = _direct(12)
        self.assertEqual(res["angle_ci_B3t_95"], d["angle_ci_t"])
        self.assertEqual(res["weight_ci_95"], d["ci_w"])


class TestDescriptive(Base):
    def test_level1_exact(self):
        trials, sessions = build()
        l1 = self.run_all(trials, sessions)["results"]["A"]["level1"]
        # onset-only: 4 trials per participant; participants with i % 4 == 2 (i = 2, 6, 10) answer S
        self.assertAlmostEqual(l1["onset_only_correct_leader"]["proportion"], (9 * 4) / 48, places=12)
        # simultaneous: all answer S (offset rule gives S at d_off = 0)
        self.assertAlmostEqual(l1["simultaneous_same"]["proportion"], 1.0, places=12)
        # conflict: 4 per participant; i = 5 says S on (+3,-3) x2; i = 7 says L on (-3,+3) x2
        self.assertAlmostEqual(l1["conflict_onset_consistent"]["proportion"], (48 - 4) / 48, places=12)

    def test_descriptive_comparison_has_no_intervals(self):
        trials, sessions = build()
        d = self.run_all(trials, sessions)["descriptive_comparison"]
        self.assertIn("DESCRIPTIVE ONLY", d["label"])
        for v in d["point_differences_vs_A"].values():
            self.assertEqual(set(v), {"point_difference_deg", "note"})

    def test_comparison_not_computed_when_a_gate_fails(self):
        def r(i, don, doff):
            return sgn(don)
        trials, sessions = build(rule_fn=r)
        d = self.run_all(trials, sessions)["descriptive_comparison"]
        self.assertIsNone(d["point_differences_vs_A"]["B-A"]["point_difference_deg"])


if __name__ == "__main__":
    unittest.main()
