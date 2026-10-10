"""
Continuous-time process observer for condition A (real-time observation).

Used for Validation C2 (lapse and attention mechanisms) and for adversarial
checks. This is a MODEL of an observer, chosen to make specific mechanisms
explicit. Its parameters are assumptions, not estimates from human data.

Per trial and disc i:
  detection time (if attending)  t_i = onset_i + q * dur_i + e_i,  e_i ~ N(0, sigma^2)
      q = fraction of the change needed before it is noticed (threshold),
      sigma = timing noise of noticing.
  Sustained attention: alternating engaged / disengaged episodes with
      exponential durations (means E and D). A detection that would occur
      while disengaged is deferred to the moment of re-engagement. A disc not
      detected by the end of the trial is treated as detected at T.
  Decision (timing policy): diff = t_R - t_L; L if diff > c, R if diff < -c, else S.
  Snapshot policy (M2b): if BOTH detections were deferred to the same
      re-engagement, the observer instead compares how far each disc has
      changed at that moment (progress fraction + N(0, sigma_p^2) noise):
      L if p_L - p_R > c_p, R if < -c_p, else S.
  Response lapse: with probability lam, a uniformly random response.
"""
import numpy as np

import stimulus as st
import catch_trials as ct

T = st.T_TRIAL

BASE = dict(q=0.10, sigma=1.2, c=1.0, lam=0.02, E=None, D=6.0, policy="timing", sigma_p=0.08, c_p=0.04)


def disengaged_intervals(rng, E, D, T=T):
    if E is None:
        return []
    out = []
    engaged = rng.random() < E / (E + D)
    t = 0.0
    while t < T:
        dur = rng.exponential(E if engaged else D)
        if not engaged:
            out.append((t, t + dur))
        t += dur
        engaged = not engaged
    return out


def deferred(t, intervals):
    for a, b in intervals:
        if a <= t < b:
            return b, True
    return t, False


def respond(tr, prm, rng):
    if rng.random() < prm["lam"]:
        return int(rng.integers(0, 3))
    iv = disengaged_intervals(rng, prm["E"], prm["D"])
    det = []
    for on, du in ((tr.onset_L, tr.dur_L), (tr.onset_R, tr.dur_R)):
        t = on + prm["q"] * du + rng.normal(0, prm["sigma"])
        t = max(t, on)                     # cannot notice before the change starts
        t2, was_def = deferred(t, iv)
        if t2 > T:
            t2 = T
        det.append((t2, was_def))
    (tL, dL), (tR, dR) = det
    if prm["policy"] == "snapshot" and dL and dR and abs(tR - tL) < 1e-9:
        ts = tL
        pL = np.clip((ts - tr.onset_L) / tr.dur_L, 0, 1) + rng.normal(0, prm["sigma_p"])
        pR = np.clip((ts - tr.onset_R) / tr.dur_R, 0, 1) + rng.normal(0, prm["sigma_p"])
        d = pL - pR
        return 2 if d > prm["c_p"] else (0 if d < -prm["c_p"] else 1)
    d = tR - tL
    return 2 if d > prm["c"] else (0 if d < -prm["c"] else 1)


def participant_trials(pseed, rng, with_catch=True):
    sch = st.generate_schedule(int(pseed))
    main = sch["order"]
    catch = [ct.realise_catch(t, rng) for t in ct.catch_templates()] if with_catch else []
    return main, catch


def simulate_dataset(prm, rng, n_part=12, with_catch=True):
    """Returns arrays for main trials (n_part x 20) and catch trials (n_part x 4)."""
    don, doff, y, yc, cd = [], [], [], [], []
    for i in range(n_part):
        main, catch = participant_trials(rng.integers(0, 4_294_967), rng, with_catch)
        don.append([t.d_on for t in main]); doff.append([t.d_off for t in main])
        y.append([respond(t, prm, rng) for t in main])
        if with_catch:
            yc.append([respond(t, prm, rng) for t in catch])
            cd.append([t.d_on for t in catch])
    out = {"don": np.array(don), "doff": np.array(doff), "y": np.array(y)}
    if with_catch:
        out["yc"] = np.array(yc); out["catch_don"] = np.array(cd)
    return out


def b3_slopes(don, doff, y):
    s = y.astype(float) - 1.0
    return (s * don).sum(1) / (don ** 2).sum(1), (s * doff).sum(1) / (doff ** 2).sum(1)


def pooled_b_on(prm, n_part, rng):
    d = simulate_dataset(prm, rng, n_part=n_part, with_catch=False)
    b_on, b_off = b3_slopes(d["don"], d["doff"], d["y"])
    return float(b_on.mean()), float(b_off.mean())


def snapshot_decisions(t_rel, n=4000, rng=None, sigma_p=0.0):
    """Deliberate state comparison at a fixed time t_rel after the mean onset,
    for every order-block cell (no attention model). Used in adversarial checks."""
    rng = rng or np.random.default_rng(5)
    rows = []
    for _ in range(n // 20):
        sch = st.generate_schedule(int(rng.integers(0, 4_294_967)))
        for tr in sch["order"]:
            ts = tr.m_on + t_rel
            pL = np.clip((ts - tr.onset_L) / tr.dur_L, 0, 1) + rng.normal(0, sigma_p)
            pR = np.clip((ts - tr.onset_R) / tr.dur_R, 0, 1) + rng.normal(0, sigma_p)
            rows.append((tr.d_on, tr.d_off, pL - pR))
    return np.array(rows)
