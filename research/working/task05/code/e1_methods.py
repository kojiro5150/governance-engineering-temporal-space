"""
E1 methods (Task 05, heterogeneity validation): generators, estimand targets,
sensitivity gates and circular angle intervals for B2 and B3.

Kept SEPARATE by design:
  B2 target  theta* = pseudo-true (KL-projection) weights of the random-
             intercept working model under the scenario's generator. This is
             what the B0/B2 point estimate converges to. It is NOT in general
             the mean of individual latent weights mu_w.
  B3 target  beta*  = population mean of individual expected response-scale
             slopes of the signed score (R=-1, S=0, L=+1) on d_on, d_off.
Coefficients and angles of B2 and B3 are on different scales and must not be
compared numerically.

Reuses Task 05 heterogeneity_methods.py (unchanged) for the B0 fit with
cluster-robust variance and for the per-participant B3 slopes.
"""
import numpy as np
from scipy.stats import f as f_dist

import stimulus as st
import ordinal_model as om
import heterogeneity_methods as hm

N_PART = 12
N_DRAWS = 2000

# --------------------------------------------------------------- scenarios --
SCENARIOS = {
    "S01 onset moderate":                  dict(groups=[(12, 0.70, 0.0)], lapse=0.02),
    "S03 onset high":                      dict(groups=[(12, 1.07, 0.0)], lapse=0.02),
    "S04 midpoint moderate":               dict(groups=[(12, 0.35, 0.35)], lapse=0.02),
    "S13 heterogeneous weights+thresholds": dict(groups=[(12, 0.70, 0.0)], lapse=0.02, w_het_sd=0.3, tau_het_sd=0.3),
    "H2 mixture 6 onset + 6 midpoint":     dict(groups=[(6, 0.70, 0.0), (6, 0.35, 0.35)], lapse=0.02),
    "S12 onset with lapses 0.15":          dict(groups=[(12, 0.70, 0.0)], lapse=0.15),
    "S10 guessing":                        dict(groups=[(12, 0.0, 0.0)], lapse=0.02),
}


def sweep_scenario(a):
    return dict(groups=[(12, a, 0.0)], lapse=0.02)


def design(n=N_PART):
    tm = st.order_templates(2, 4)
    return (np.tile([t.d_on for t in tm], (n, 1)).astype(float),
            np.tile([t.d_off for t in tm], (n, 1)).astype(float))


def generate(spec, rng, n_scale=1):
    """Responses for one dataset (n_scale > 1 builds a large sample for theta*)."""
    ys, dons, doffs = [], [], []
    for (n, w_on, w_off) in spec["groups"]:
        don, doff = design(n * n_scale)
        y = om.simulate_responses(rng, don, doff, w_on, w_off, tau=1.0, bias_sd=0.5,
                                  lapse=spec["lapse"], w_het_sd=spec.get("w_het_sd", 0.0),
                                  tau_het_sd=spec.get("tau_het_sd", 0.0))
        ys.append(y); dons.append(don); doffs.append(doff)
    return np.vstack(dons), np.vstack(doffs), np.vstack(ys)


# ------------------------------------------------------------------ targets --
def mu_w(spec):
    """Mean individual latent weights (deduction). Lognormal weight factor
    exp(N(0, s^2)) has mean exp(s^2/2)."""
    g = np.exp(spec.get("w_het_sd", 0.0) ** 2 / 2)
    n = sum(k for k, _, _ in spec["groups"])
    on = sum(k * w for k, w, _ in spec["groups"]) / n * g
    off = sum(k * w for k, _, w in spec["groups"]) / n * g
    return np.array([on, off])


def beta_star(spec, rng, n_mc=400_000):
    """Population mean of individual expected response-scale slopes (MC)."""
    tm = st.order_templates(2, 4)
    d_on = np.array([t.d_on for t in tm]); d_off = np.array([t.d_off for t in tm])
    n_tot = sum(k for k, _, _ in spec["groups"])
    parts = []
    for (k, w_on, w_off) in spec["groups"]:
        m = int(n_mc * k / n_tot)
        beta = rng.normal(0, 0.5, m)
        gw = np.exp(rng.normal(0, spec.get("w_het_sd", 0.0), m)) if spec.get("w_het_sd") else np.ones(m)
        gt = np.exp(rng.normal(0, spec.get("tau_het_sd", 0.0), m)) if spec.get("tau_het_sd") else np.ones(m)
        eta = gw[:, None] * (w_on * d_on + w_off * d_off)[None, :] + beta[:, None]
        tau = gt[:, None]
        pR = 1.0 / (1.0 + np.exp(tau + eta))          # P(z < -tau)
        pL = 1.0 / (1.0 + np.exp(tau - eta))          # P(z >  tau)
        s = (1 - spec["lapse"]) * (pL - pR)
        b = np.column_stack([(s * d_on).sum(1) / (d_on ** 2).sum(), (s * d_off).sum(1) / (d_off ** 2).sum()])
        parts.append((k / n_tot, b.mean(0), b.std(0, ddof=1) / np.sqrt(m)))
    est = sum(wt * mean for wt, mean, _ in parts)
    se = np.sqrt(sum((wt * s) ** 2 for wt, _, s in parts))
    return est, se


def theta_star(spec, seeds, n_scale=500):
    """Pseudo-true working-model weights: fit B0 to large samples
    (12 x n_scale participants) from several seeds; return mean and MC SE."""
    vals = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        don, doff, y = generate(spec, rng, n_scale=n_scale)
        f = om.fit(don, doff, y)
        vals.append([f["w_on"], f["w_off"]])
    vals = np.array(vals)
    return vals.mean(0), vals.std(0, ddof=1) / np.sqrt(len(vals)), vals


def angle(v):
    return float(np.degrees(np.arctan2(v[1], v[0])))


# ------------------------------------------------------- circular intervals --
def circ_contains(lo, hi, theta):
    """True if the interval [lo, hi] (degrees, possibly beyond +/-180 after
    unwrapping) contains theta or any of its 360-degree equivalents."""
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return False
    if hi - lo >= 360.0:
        return True
    return any(lo <= theta + 360.0 * k <= hi for k in range(-3, 4))


def unwrapped_percentile_interval(draw_angles, centre):
    a = (np.asarray(draw_angles) - centre + 180.0) % 360.0 - 180.0 + centre
    return float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))


# ------------------------------------------------------------- B2 and B3 ----
def run_b2(don, doff, y, rng):
    o = hm.b0_b2(don, doff, y)
    est, V, ok = o["B2"]["est"], o["B2"]["cov"], o["B2"]["ok"]
    out = {"ok": bool(ok), "sd_u_boundary": bool(o["sd_u_boundary"]),
           "est": est.tolist(), "se": o["B2"]["se"].tolist(),
           "se_model": o["B0"]["se"].tolist()}
    G = don.shape[0]
    if ok and np.all(np.isfinite(V)):
        try:
            T2 = float(est @ np.linalg.solve(V, est))
            F = T2 / 2.0
            p = float(1 - f_dist.cdf(F, 2, G - 1))
        except np.linalg.LinAlgError:
            p = float("nan")
        z = rng.multivariate_normal([0, 0], V, size=N_DRAWS, method="svd")
        z = z / np.sqrt(rng.chisquare(G - 1, size=(N_DRAWS, 1)) / (G - 1))
        d = est[None, :] + z
        lo, hi = unwrapped_percentile_interval(np.degrees(np.arctan2(d[:, 1], d[:, 0])), angle(est))
    else:
        p, lo, hi = float("nan"), float("nan"), float("nan")
    tcrit = hm.T11
    out.update({"ci_w": [[est[i] - tcrit * out["se"][i], est[i] + tcrit * out["se"][i]] for i in range(2)],
                "gate_p": p, "gate_pass": bool(np.isfinite(p) and p < 0.05),
                "angle": angle(est), "angle_ci": [lo, hi]})
    return out


def run_b3(don, doff, y, rng):
    b_on, b_off = hm.b3_individual(don, doff, y)
    B = np.column_stack([b_on, b_off])
    n = B.shape[0]
    m = B.mean(0)
    S = np.cov(B.T, ddof=1)
    se = np.sqrt(np.diag(S) / n)
    try:
        T2 = float(n * m @ np.linalg.solve(S, m))
        F = (n - 2) / (2 * (n - 1)) * T2
        p = float(1 - f_dist.cdf(F, 2, n - 2))
    except np.linalg.LinAlgError:
        p = float("nan")
    idx = rng.integers(0, n, size=(N_DRAWS, n))
    bm = B[idx].mean(1)
    lo, hi = unwrapped_percentile_interval(np.degrees(np.arctan2(bm[:, 1], bm[:, 0])), angle(m))
    # Amendment AM3: second angle interval, multivariate t(n-1) draws from the
    # sample covariance of participant slopes (same construction as B2).
    try:
        z = rng.multivariate_normal([0, 0], S / n, size=N_DRAWS, method="svd")
        z = z / np.sqrt(rng.chisquare(n - 1, size=(N_DRAWS, 1)) / (n - 1))
        d = m[None, :] + z
        lo_t, hi_t = unwrapped_percentile_interval(np.degrees(np.arctan2(d[:, 1], d[:, 0])), angle(m))
    except Exception:
        lo_t, hi_t = float("nan"), float("nan")
    ok = bool(np.all(np.isfinite(se)) and np.all(se > 0))
    return {"ok": ok, "est": m.tolist(), "se": se.tolist(),
            "ci_w": [[m[i] - hm.T11 * se[i], m[i] + hm.T11 * se[i]] for i in range(2)],
            "gate_p": p, "gate_pass": bool(np.isfinite(p) and p < 0.05),
            "angle": angle(m), "angle_ci": [lo, hi], "angle_ci_t": [lo_t, hi_t]}
