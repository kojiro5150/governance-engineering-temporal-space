"""
Pre-specified catch trials (Task 05, Validation C).

SPECIFICATION (fixed before any simulation of catch trials was run)
  Count        K = 4 per participant, all conditions, inside the order block.
  Cells        (d_on, d_off) = (+8, +8) twice and (-8, -8) twice: congruent,
               so onset, offset and midpoint cues all give the same answer.
  Ramps        6.0 s for both discs (rate 1.67 L*/s, magnitude M = 10 L*,
               same direction for both discs; directions 2 lightening,
               2 darkening, crossed with leader side).
  Overlap      none: the second ramp starts 2.0 s after the first ends.
  Timing       mean onset m ~ U[5.5, 8.5] s; first onset m - 4 in [1.5, 4.5];
               last offset m + 10 in [15.5, 18.5]; trial length T = 24 s
               (same as main trials, so exposure and vigilance demand match).
  Condition B  compressed x8 like all trials; condition C plotted like all trials.
  Placement    one catch trial at a random position within each quarter of the
               24-trial order block (positions drawn from the seeded PRNG).
  Scoring      correct = the leader response; "same" or the other side = error.
  Use          NOT included in the cue-weight model. Used only to estimate a
               response-lapse rate (and as an exclusion indicator).
  Assumption   A participant who is attending and responding as instructed is
               correct on these trials with probability close to 1. This is an
               assumption about human observers, not a tested fact.
"""
import numpy as np

import stimulus as st

K_CATCH = 4
CATCH_D = 8.0
CATCH_DUR = 6.0
CATCH_M_RANGE = (5.5, 8.5)


def catch_templates():
    t = []
    for i, (d, direction) in enumerate([(+CATCH_D, +1), (+CATCH_D, -1), (-CATCH_D, +1), (-CATCH_D, -1)]):
        tr = st.Trial("order", f"catch({d:+.0f},{d:+.0f})#{i}", d, d, direction, True, True)
        t.append(tr)
    return t


def realise_catch(tr, rng):
    m = rng.uniform(*CATCH_M_RANGE)
    tr.m_on = m
    tr.dur_L = CATCH_DUR
    tr.dur_R = CATCH_DUR
    tr.onset_L = m - tr.d_on / 2.0
    tr.onset_R = m + tr.d_on / 2.0
    return tr


def check_catch_spec(n=2000, seed=11):
    rng = np.random.default_rng(seed)
    worst = {"min_onset": 1e9, "max_offset": 0.0, "min_gap": 1e9}
    for _ in range(n):
        for tr in catch_templates():
            realise_catch(tr, rng)
            on = sorted([(tr.onset_L, tr.offset_L), (tr.onset_R, tr.offset_R)])
            worst["min_onset"] = min(worst["min_onset"], on[0][0])
            worst["max_offset"] = max(worst["max_offset"], on[1][1])
            worst["min_gap"] = min(worst["min_gap"], on[1][0] - on[0][1])
            assert abs((tr.onset_R - tr.onset_L) - tr.d_on) < 1e-9
            assert abs((tr.offset_R - tr.offset_L) - tr.d_off) < 1e-9
    return worst


if __name__ == "__main__":
    print(check_catch_spec())
