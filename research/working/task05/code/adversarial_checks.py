"""
Adversarial computational checks (Task 05 section 6). Model-based, not empirical.

For several decision rules an observer (or a graph reader) might use, generate
ternary responses on the real order-block schedules, fit the baseline ordinal
model (B0) on a LARGE simulated sample, and report the implied cue weights and
strategy angle. Large samples make these approximately the population values
the model would converge to, i.e. what the experiment would "see".

Rules
  R1 onset timing with detection threshold q (process observer, no lapses)
  R2 deliberate snapshot comparison at a fixed time after the mean onset
  R3 condition-C graph-reading proxies:
       kink    = locate where each trace leaves baseline   (onset, with spatial noise)
       top     = which trace reaches its final level first (offset)
       column  = which trace is further from baseline at a fixed plot x position
       area    = which trace has more area between it and baseline (time-averaged progress)

Usage: python3 adversarial_checks.py OUT_JSON
"""
import json
import sys

import numpy as np

import stimulus as st
import ordinal_model as om
import process_observer as po

N_PART = 400


def fit_rule(rule, c, noise, rng, n_part=N_PART):
    don, doff, y = [], [], []
    for _ in range(n_part):
        sch = st.generate_schedule(int(rng.integers(0, 4_294_967)))
        tr = sch["order"]
        dv = np.array([rule(t) for t in tr]) + rng.normal(0, noise, len(tr))
        y.append(np.where(dv > c, 2, np.where(dv < -c, 0, 1)))
        don.append([t.d_on for t in tr]); doff.append([t.d_off for t in tr])
    f = om.fit(np.array(don), np.array(doff), np.array(y))
    ang = float(np.degrees(np.arctan2(f["w_off"], f["w_on"])))
    return {"w_on": round(f["w_on"], 4), "w_off": round(f["w_off"], 4), "angle_deg": round(ang, 2),
            "se_w_on": round(f["se_w_on"], 4), "se_w_off": round(f["se_w_off"], 4), "stable": f["stable"]}


def progress(t, on, du):
    return float(np.clip((t - on) / du, 0, 1))


def main(out):
    rng = np.random.default_rng(606)
    res = {"n_participants_per_fit": N_PART, "R1_threshold_onset": {}, "R2_snapshot": {}, "R3_graph_proxies": {}}
    for q in (0.0, 0.05, 0.1, 0.2, 0.3):
        rule = lambda t, q=q: (t.onset_R + q * t.dur_R) - (t.onset_L + q * t.dur_L)
        r = fit_rule(rule, c=1.0, noise=1.2 * np.sqrt(2), rng=rng)
        r["deduced_angle_deg"] = round(float(np.degrees(np.arctan2(q, 1 - q))), 2)
        res["R1_threshold_onset"][f"q={q}"] = r
    for t_rel in (1.0, 3.0, 6.0, 9.0, 12.0, 15.0):
        rule = lambda t, t_rel=t_rel: progress(t.m_on + t_rel, t.onset_L, t.dur_L) - progress(t.m_on + t_rel, t.onset_R, t.dur_R)
        res["R2_snapshot"][f"t={t_rel}s after mean onset"] = fit_rule(rule, c=0.04, noise=0.08, rng=rng)
    # condition C proxies (time measured in plot seconds; 25 px per s)
    res["R3_graph_proxies"]["kink (onset, 0.5 s localisation noise)"] = fit_rule(
        lambda t: t.onset_R - t.onset_L, c=0.5, noise=0.5 * np.sqrt(2), rng=rng)
    res["R3_graph_proxies"]["top (offset, 0.5 s localisation noise)"] = fit_rule(
        lambda t: t.offset_R - t.offset_L, c=0.5, noise=0.5 * np.sqrt(2), rng=rng)
    for x in (8.0, 12.0):
        res["R3_graph_proxies"][f"column at x={x}s"] = fit_rule(
            lambda t, x=x: progress(x, t.onset_L, t.dur_L) - progress(x, t.onset_R, t.dur_R), c=0.04, noise=0.08, rng=rng)
    grid = np.linspace(0, st.T_TRIAL, 241)
    def area(t):
        pl = np.clip((grid - t.onset_L) / t.dur_L, 0, 1).mean(); pr = np.clip((grid - t.onset_R) / t.dur_R, 0, 1).mean()
        return pl - pr
    res["R3_graph_proxies"]["area (time-averaged progress)"] = fit_rule(area, c=0.01, noise=0.02, rng=rng)
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
