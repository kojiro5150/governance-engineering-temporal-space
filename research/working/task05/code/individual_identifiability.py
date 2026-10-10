"""
Can a SINGLE participant's strategy (onset vs midpoint) be classified from
their own trials? Uses the B3 per-participant slopes (closed form, no model
fitting), so large simulated samples are cheap.

Rule: angle = atan2(b_off, b_on); classify "onset" if angle < 22.5 deg,
"midpoint" if 22.5 <= angle < 67.5, else "other". A participant with
|b| below an evidence floor is "unclassifiable".

Usage: python3 individual_identifiability.py OUT_JSON
"""
import json
import sys

import numpy as np

import stimulus as st
import ordinal_model as om

N_SIM = 20000


def run(k, w_on, w_off, a_label, rng):
    tm = st.order_templates(k, 4)
    don = np.tile([t.d_on for t in tm], (N_SIM, 1)); doff = np.tile([t.d_off for t in tm], (N_SIM, 1))
    y = om.simulate_responses(rng, don, doff, w_on, w_off, tau=1.0, bias_sd=0.5, lapse=0.02)
    s = y - 1.0
    b_on = (s * don).sum(1) / (don ** 2).sum(1); b_off = (s * doff).sum(1) / (doff ** 2).sum(1)
    ang = np.degrees(np.arctan2(b_off, b_on))
    # evidence floor: norm of slopes below the 95th percentile under guessing
    yg = om.simulate_responses(rng, don, doff, 0.0, 0.0, tau=1.0, bias_sd=0.5, lapse=0.02)
    sg = yg - 1.0
    ng = np.hypot((sg * don).sum(1) / (don ** 2).sum(1), (sg * doff).sum(1) / (doff ** 2).sum(1))
    floor = np.percentile(ng, 95)
    norm = np.hypot(b_on, b_off)
    cls = np.where(norm < floor, "unclassifiable",
                   np.where(np.abs(ang) < 22.5, "onset", np.where((ang >= 22.5) & (ang < 67.5), "midpoint", "other")))
    return {"J": 8 * k + 4, "truth": a_label, "w": [w_on, w_off],
            "evidence_floor_norm": round(float(floor), 4),
            "p_onset": round(float(np.mean(cls == "onset")), 4),
            "p_midpoint": round(float(np.mean(cls == "midpoint")), 4),
            "p_other": round(float(np.mean(cls == "other")), 4),
            "p_unclassifiable": round(float(np.mean(cls == "unclassifiable")), 4),
            "angle_sd_deg": round(float(np.std(ang[norm >= floor])), 2)}


def main(out):
    rng = np.random.default_rng(20261010)
    res = []
    for k in (2, 3, 4, 6, 8):
        for lab, w in (("onset moderate", (0.7, 0.0)), ("midpoint moderate", (0.35, 0.35)),
                       ("onset low", (1 / 3, 0.0)), ("midpoint low", (1 / 6, 1 / 6))):
            res.append(run(k, *w, lab, rng))
    json.dump({"n_sim_participants_per_cell": N_SIM, "rows": res}, open(out, "w"), indent=1)
    for r in res:
        print(r)


if __name__ == "__main__":
    main(sys.argv[1])
