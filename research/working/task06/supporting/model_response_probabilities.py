"""
Task 06 supporting calculation (deterministic; NO random sampling; not a simulation).

Evaluates, by Gauss-Hermite quadrature, the response probabilities implied by the
FROZEN Task 05 generator (ordinal_model.simulate_responses, sha256 590db5f3...):
  latent z = w_on*d_on + w_off*d_off + b + logistic noise, b ~ N(0, 0.5^2),
  respond L if z > tau, R if z < -tau, else S; tau = 1; lapse 0.02 uniform over 3.
Purpose: translate the validated sensitivity grid (onset weight a) into observable
cell-level proportions, so that human pilot data and feasibility criteria F5-F7 can
be read against the simulation operating characteristics. The mapping depends on
tau, bias SD and lapse, which are ASSUMPTIONS about humans, not estimates.
Usage: python3 model_response_probabilities.py OUT_JSON
"""
import json, sys
import numpy as np
from numpy.polynomial.hermite_e import hermegauss

X, W = hermegauss(80); W = W / W.sum()
sig = lambda u: 1 / (1 + np.exp(-u))


def probs(eta, tau=1.0, bsd=0.5, lapse=0.02):
    b = bsd * X
    pL = float((W * (1 - sig(tau - (eta + b)))).sum())
    pR = float((W * sig(-tau - (eta + b))).sum())
    p = np.array([pR, 1 - pL - pR, pL])
    p = (1 - lapse) * p + lapse / 3
    return {"R": round(float(p[0]), 4), "S": round(float(p[1]), 4), "L": round(float(p[2]), 4)}


S = 3.0
rows = {}
for a in [0.0, 0.05, 0.10, 0.20, 1 / 3, 0.70, 1.07]:
    rows[f"onset observer a={a:.3f}"] = {
        "onset_only_(+3,0)": probs(a * S), "simultaneous_(0,0)": probs(0.0),
        "offset_only_(0,+3)": probs(0.0), "conflict_(+3,-3)": probs(a * S), "congruent_(+3,+3)": probs(a * S)}  # w_off = 0, so only d_on contributes
rows["midpoint observer (0.35, 0.35)"] = {
    "onset_only_(+3,0)": probs(0.35 * S), "simultaneous_(0,0)": probs(0.0), "offset_only_(0,+3)": probs(0.35 * S),
    "conflict_(+3,-3)": probs(0.0), "congruent_(+3,+3)": probs(0.35 * 2 * S)}
out = {"label": "Deterministic quadrature of the frozen Task 05 generator; assumptions tau=1, bias SD 0.5, lapse 0.02",
       "note": "L = left began first. For cells with positive asynchrony the left disc leads, so P(L) is the correct-leader proportion.",
       "rows": rows}
json.dump(out, open(sys.argv[1], "w"), indent=1)
for k, v in rows.items():
    print(k, "| onset-only P(L)", v["onset_only_(+3,0)"]["L"], "| simultaneous P(S)", v["simultaneous_(0,0)"]["S"],
          "| conflict P(L)", v["conflict_(+3,-3)"]["L"], "| congruent P(L)", v["congruent_(+3,+3)"]["L"])
