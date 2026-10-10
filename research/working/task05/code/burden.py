"""
Participant-burden model (Task 04, section 5).

All component durations below are ASSUMPTIONS (methodological judgement), not
measurements. Presentation durations come from Task 03. Response and reading
times are drawn per simulated participant from lognormal distributions so the
output gives a median and a 90th percentile, not a single guess.

Usage:  python3 burden.py [outfile.json]
"""
import json
import sys

import numpy as np

RNG = np.random.default_rng(31)
N_SIM = 20000


def lognorm(median, sd_log, size):
    return median * np.exp(RNG.normal(0, sd_log, size))


ASSUMPTIONS = {
    "device_check_s": 30,
    "instructions_main_s": {"A": 120, "B": 120, "C": 150},     # C also explains the plot
    "calibration": "10 trials x (response median 2.5 s, sd_log 0.4) + 0.5 s ITI",
    "practice": "3 trials x (presentation A 8 s / B 3 s / C 3 s + response median 4 s + 2 s feedback)",
    "detection_presentation_s": {"A": 24.0, "B": 3.0, "C": "median 6 s viewing, min 3 s, max 15 s"},
    "detection_response": "median 4 s, sd_log 0.4 (two yes/no reports)",
    "order_instructions_s": 45,
    "order_presentation_s": {"A": "T (24 s; 21 s variant)", "B": "3 s + replays (each 1 s mask + 3 s); "
                             "replays ~ Binomial(2, 0.5)", "C": "median 7 s viewing, min 3 s, max 15 s"},
    "order_response": "median 4.5 s, sd_log 0.4 (ternary choice + confidence)",
    "iti_s": 1.0,
    "breaks": "detection: 1 break; order: one break per 7 trials; each median 20 s, sd_log 0.5, cap 60 s",
    "attention_and_strategy_questions": "median 60 s, sd_log 0.4",
    "data_export_s": 30,
}


def session(condition, J, T_order=24.0, n=N_SIM):
    tot = np.zeros(n)
    tot += 30
    tot += ASSUMPTIONS["instructions_main_s"][condition]
    tot += np.sum(lognorm(2.5, 0.4, (n, 10)), axis=1) + 10 * 0.5
    pres_prac = {"A": 8.0, "B": 3.0, "C": 3.0}[condition]
    tot += 3 * (pres_prac + 2.0) + np.sum(lognorm(4.0, 0.4, (n, 3)), axis=1)
    # detection block: 12 trials
    if condition == "A":
        det_pres = np.full((n, 12), 24.0)
    elif condition == "B":
        det_pres = np.full((n, 12), 3.0)
    else:
        det_pres = np.clip(lognorm(6.0, 0.4, (n, 12)), 3.0, 15.0)
    tot += det_pres.sum(1) + np.sum(lognorm(4.0, 0.4, (n, 12)), axis=1) + 12 * 1.0
    tot += np.minimum(lognorm(20, 0.5, n), 60)                       # detection break
    tot += 45                                                        # order instructions
    if condition == "A":
        ord_pres = np.full((n, J), T_order)
    elif condition == "B":
        ord_pres = 3.0 + RNG.binomial(2, 0.5, (n, J)) * 4.0
    else:
        ord_pres = np.clip(lognorm(7.0, 0.4, (n, J)), 3.0, 15.0)
    tot += ord_pres.sum(1) + np.sum(lognorm(4.5, 0.4, (n, J)), axis=1) + J * 1.0
    n_breaks = (J - 1) // 7
    tot += np.sum(np.minimum(lognorm(20, 0.5, (n, max(n_breaks, 1))), 60), axis=1) * (n_breaks > 0)
    tot += lognorm(60, 0.4, n) + 30
    return tot / 60.0


def main(out):
    res = {"assumptions": ASSUMPTIONS, "cap_minutes_condition_A": 30, "results": {}}
    for J in (20, 28, 36):
        for T in (24.0, 21.0):
            for c in ("A", "B", "C"):
                if c != "A" and T != 24.0:
                    continue
                m = session(c, J, T)
                key = f"{c} | J={J}" + (f" | T_order={T:.0f}s" if c == "A" else "")
                res["results"][key] = {"median_min": round(float(np.median(m)), 1),
                                       "p90_min": round(float(np.percentile(m, 90)), 1),
                                       "p99_min": round(float(np.percentile(m, 99)), 1)}
    # marginal cost of one additional order trial in condition A
    m20 = np.median(session("A", 20)); m28 = np.median(session("A", 28))
    res["marginal_min_per_order_trial_A"] = round(float((m28 - m20) / 8), 3)
    # fixed (non-order-trial) portion of condition A
    res["condition_A_fixed_portion_min_J0_equivalent"] = round(float(m20 - 20 * (m28 - m20) / 8), 1)
    with open(out, "w") as f:
        json.dump(res, f, indent=1)
    return res


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../results/burden.json"
    r = main(out)
    print(json.dumps(r["results"], indent=1))
    print("marginal min/order trial (A):", r["marginal_min_per_order_trial_A"])
    print("fixed portion (A):", r["condition_A_fixed_portion_min_J0_equivalent"])
