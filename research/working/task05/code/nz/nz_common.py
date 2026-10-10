"""
Task 05 closure addendum: B3-t near-zero sensitivity validation (NZ).
Generator: 12 identical-strategy participants with onset weight a, offset
weight 0, lapse 0.02 (frozen E1 sweep_scenario, imported unchanged).
Grid a in {0, 0.05, 0.10, 0.20, 1/3}; same grid as pre-check P4.
Only the B3 procedure (e1_methods.run_b3) is run; B3-t is the evaluated
variant, B3-boot is recorded descriptively because run_b3 computes both.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import e1_methods as em  # noqa: E402

GRID = [0.0, 0.05, 0.10, 0.20, 1 / 3]


def label(a):
    return f"a={a:.3f}"


def scenario(a):
    return em.sweep_scenario(a)
