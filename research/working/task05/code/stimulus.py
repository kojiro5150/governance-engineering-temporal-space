"""
Deterministic, non-participant-facing stimulus generator for the Task 03
onset-order protocol (research/working/task03-adversarial-protocol-review.md,
Parts 6 and 7).

Implements the specification AS WRITTEN in Task 03. Where Task 03 is silent,
the gap-filling decision is marked SPEC-GAP and listed in the Task 04 document.

No browser code. No participant-facing behaviour.
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, asdict, field

MASK32 = 0xFFFFFFFF

# ---- Task 03 constants (Part 6.3) -----------------------------------------
T_TRIAL = 24.0      # real trial duration, s
D0 = 12.0           # base ramp duration, s
S_STEP = 3.0        # asynchrony step, s
L0 = 55.0           # start lightness, CIELAB L*
M_CHANGE = 10.0     # change magnitude, L*
M_ON_RANGE = (3.0, 6.0)        # mean onset, order block
DET_ONSET_RANGE = (3.0, 9.0)   # onset, detection block
COMPRESSION_B = 8.0

# SPEC-GAP: Task 03 says trial order is randomised "from the seeded PRNG" but
# gives no stream for it. We use two reserved trial indices for the shuffles.
SHUFFLE_INDEX_DETECTION = 900
SHUFFLE_INDEX_ORDER = 901


def imul32(a: int, b: int) -> int:
    """JavaScript Math.imul semantics, returned as unsigned 32-bit."""
    return (a * b) & MASK32


class Mulberry32:
    """Bit-exact port of the common JavaScript mulberry32 PRNG."""

    def __init__(self, seed: int):
        self.a = seed & MASK32

    def next(self) -> float:
        self.a = (self.a + 0x6D2B79F5) & MASK32
        t = self.a
        t = imul32(t ^ (t >> 15), t | 1)
        t ^= (t + imul32(t ^ (t >> 7), t | 61)) & MASK32
        t &= MASK32
        return ((t ^ (t >> 14)) & MASK32) / 4294967296.0

    def uniform(self, lo: float, hi: float) -> float:
        return lo + (hi - lo) * self.next()


def trial_seed(participant_seed: int, trial_index: int) -> int:
    """Task 03 Part 6.2: seed = participantSeed x 1000 + trialIndex.
    Reduced to 32 bits because mulberry32 takes a 32-bit state."""
    return (participant_seed * 1000 + trial_index) & MASK32


def shuffle(items: list, rng: Mulberry32) -> list:
    """Fisher-Yates using the seeded PRNG."""
    out = list(items)
    for i in range(len(out) - 1, 0, -1):
        j = int(rng.next() * (i + 1))
        out[i], out[j] = out[j], out[i]
    return out


@dataclass
class Trial:
    block: str                 # "detection" or "order"
    template_id: str
    d_on: float | None         # onset(R) - onset(L); + means left leads
    d_off: float | None        # offset(R) - offset(L); + means left ends first
    direction: int             # +1 lightening, -1 darkening (same for both discs)
    change_L: bool
    change_R: bool
    onset_L: float | None = None
    onset_R: float | None = None
    dur_L: float | None = None
    dur_R: float | None = None
    m_on: float | None = None
    seed: int | None = None
    position: int | None = None  # presentation position within block

    @property
    def offset_L(self):
        return None if self.onset_L is None else self.onset_L + self.dur_L

    @property
    def offset_R(self):
        return None if self.onset_R is None else self.onset_R + self.dur_R


def lightness(t: float, onset: float | None, dur: float | None, direction: int,
              changes: bool) -> float:
    """Task 03 Part 6.3: L(t) = L0 + dir * M * clamp((t - onset)/dur, 0, 1)."""
    if not changes:
        return L0
    p = (t - onset) / dur
    p = 0.0 if p < 0 else (1.0 if p > 1 else p)
    return L0 + direction * M_CHANGE * p


# ---- Templates (Part 7) ----------------------------------------------------

def order_templates(reps_nonzero: int = 2, reps_simultaneous: int = 4):
    """Task 03 Part 7.2. Default (2, 4) gives the specified 20 trials.
    Direction balance: each non-zero cell alternates +/-; simultaneous half +/-.
    reps_nonzero must be even to keep direction balanced within cell."""
    tmpl = []
    s = S_STEP
    cells = [(+s, +s), (-s, -s), (+s, 0.0), (-s, 0.0),
             (0.0, +s), (0.0, -s), (+s, -s), (-s, +s)]
    for (don, doff) in cells:
        for r in range(reps_nonzero):
            d = +1 if r % 2 == 0 else -1
            tmpl.append(Trial("order", f"cell({don:+.0f},{doff:+.0f})#{r}",
                              don, doff, d, True, True))
    for r in range(reps_simultaneous):
        d = +1 if r % 2 == 0 else -1
        tmpl.append(Trial("order", f"cell(+0,+0)#{r}", 0.0, 0.0, d, True, True))
    return tmpl


def detection_templates():
    """Task 03 Part 7.1. SPEC-GAP: Task 03 lists 'durations 9 and 15 s;
    directions +/-' for single-change trials without the pairing. We pair
    (9,+),(15,-) on the left and (9,-),(15,+) on the right so that across
    sides each duration occurs with each direction once."""
    t = []
    for r in range(4):
        t.append(Trial("detection", f"none#{r}", None, None, +1 if r % 2 == 0 else -1,
                       False, False))
    for (dur, d) in [(9.0, +1), (15.0, -1)]:
        tr = Trial("detection", f"left_only_d{dur:.0f}", None, None, d, True, False)
        tr.dur_L = dur
        t.append(tr)
    for (dur, d) in [(9.0, -1), (15.0, +1)]:
        tr = Trial("detection", f"right_only_d{dur:.0f}", None, None, d, False, True)
        tr.dur_R = dur
        t.append(tr)
    for r in range(4):
        tr = Trial("detection", f"both_sim#{r}", 0.0, 0.0, +1 if r % 2 == 0 else -1,
                   True, True)
        tr.dur_L = D0
        tr.dur_R = D0
        t.append(tr)
    return t


def realise_order_trial(tr: Trial, rng: Mulberry32) -> Trial:
    """Task 03 Part 6.3 equations, verbatim."""
    don, doff = tr.d_on, tr.d_off
    tr.dur_L = D0 + (don - doff) / 2.0
    tr.dur_R = D0 - (don - doff) / 2.0
    tr.m_on = rng.uniform(*M_ON_RANGE)
    tr.onset_L = tr.m_on - don / 2.0
    tr.onset_R = tr.m_on + don / 2.0
    return tr


def realise_detection_trial(tr: Trial, rng: Mulberry32) -> Trial:
    onset = rng.uniform(*DET_ONSET_RANGE)
    if tr.change_L:
        tr.onset_L = onset
    if tr.change_R:
        tr.onset_R = onset  # simultaneous both-change trials share the onset
    return tr


def generate_schedule(participant_seed: int, reps_nonzero: int = 2,
                      reps_simultaneous: int = 4) -> dict:
    """One participant's full schedule: detection block then order block.
    Trial indices: detection 0..11, order 12.. (SPEC-GAP: Task 03 does not
    say whether trialIndex restarts per block; we use one running index)."""
    det = detection_templates()
    order = order_templates(reps_nonzero, reps_simultaneous)

    det = shuffle(det, Mulberry32(trial_seed(participant_seed, SHUFFLE_INDEX_DETECTION)))
    order = shuffle(order, Mulberry32(trial_seed(participant_seed, SHUFFLE_INDEX_ORDER)))

    idx = 0
    for pos, tr in enumerate(det):
        tr.seed = trial_seed(participant_seed, idx)
        tr.position = pos
        realise_detection_trial(tr, Mulberry32(tr.seed))
        idx += 1
    for pos, tr in enumerate(order):
        tr.seed = trial_seed(participant_seed, idx)
        tr.position = pos
        realise_order_trial(tr, Mulberry32(tr.seed))
        idx += 1
    return {"participant_seed": participant_seed,
            "reps_nonzero": reps_nonzero,
            "reps_simultaneous": reps_simultaneous,
            "detection": det, "order": order}


def schedule_digest(sched: dict) -> str:
    """SHA-256 of a canonical JSON serialisation, for reproducibility checks."""
    def row(tr: Trial):
        d = asdict(tr)
        return {k: (round(v, 12) if isinstance(v, float) else v) for k, v in d.items()}
    payload = {"participant_seed": sched["participant_seed"],
               "detection": [row(t) for t in sched["detection"]],
               "order": [row(t) for t in sched["order"]]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


if __name__ == "__main__":
    s = generate_schedule(12345)
    print("digest", schedule_digest(s))
    for tr in s["order"][:5]:
        print(tr.template_id, round(tr.onset_L, 3), round(tr.onset_R, 3),
              tr.dur_L, tr.dur_R, round(tr.offset_L, 3), round(tr.offset_R, 3))
