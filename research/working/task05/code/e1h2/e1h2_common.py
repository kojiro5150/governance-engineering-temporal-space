"""
Task 05 E1-H2 confirmatory amendment: generator for the H2 population.

Population: each participant independently belongs to the onset-weighted
group (w_on 0.70, w_off 0) or the midpoint-weighted group (w_on 0.35,
w_off 0.35) with probability 0.5 each; lapse 0.02; all other generator
settings as frozen E1 (Task 05 e1_methods.generate, imported unchanged).

RNG order per dataset: 12 Bernoulli(0.5) membership draws, then responses
(onset group first, then midpoint group), then B2, then B3.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import e1_methods as em

N_PART = 12
P_ONSET = 0.5
ONSET = (0.70, 0.0)
MIDPOINT = (0.35, 0.35)
LAPSE = 0.02


def draw_membership(rng, n=N_PART):
    return rng.random(n) < P_ONSET          # True = onset-weighted


def generate(rng):
    m = draw_membership(rng)
    k = int(m.sum())
    groups = [g for g in [(k, *ONSET), (N_PART - k, *MIDPOINT)] if g[0] > 0]
    don, doff, y = em.generate(dict(groups=groups, lapse=LAPSE), rng)
    return don, doff, y, k


def population_spec():
    """For targets: an expected 50/50 population (proportions, not a sample)."""
    return dict(groups=[(6, *ONSET), (6, *MIDPOINT)], lapse=LAPSE)
