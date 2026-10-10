"""
Validation B: candidate inference methods under participant heterogeneity.

Methods (specified in the Task 05 report, section 4):
  B0  Baseline. Ternary cumulative logit, random intercepts, marginal ML,
      model-based (Hessian) Wald intervals, z = 1.96. (Task 04 ordinal_model.fit)
  B1  Random intercepts + independent random slopes for w_on and w_off,
      marginal ML by 3-D Gauss-Hermite quadrature, Wald intervals.
  B2  B0 point estimates with participant-cluster-robust (sandwich) variance,
      CR1 small-sample factor G/(G-1), t(G-1) critical values.
  B3  Two-stage summary statistics: per-participant least-squares slopes of
      the signed response score (R=-1, S=0, L=+1) on d_on and d_off, then
      group mean with t(G-1) intervals; strategy angle interval by
      participant bootstrap.
  B4  B0 point estimates with participant (cluster) bootstrap percentile
      intervals. Timing only.

This module is used ONLY for the small timing and feasibility test. It must
not be used for a full heterogeneity simulation before review (Task 05 brief).
"""
import time

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, logsumexp
from scipy.stats import t as student_t

import ordinal_model as om

T11 = float(student_t.ppf(0.975, 11))


# ---------------------------------------------------------------- B0 / B2 ---
def ll_per_participant(p, don, doff, y, lapse=False):
    th1, th2, w_on, w_off, sd_u, lam = om.unpack(p, lapse)
    eta = (w_on * don + w_off * doff)[:, :, None] + sd_u * om.GH_NODES[None, None, :]
    c1 = expit(th1 - eta); c2 = expit(th2 - eta)
    yy = y[:, :, None]
    pr = np.where(yy == 0, c1, np.where(yy == 1, c2 - c1, 1.0 - c2))
    if lapse:
        pr = (1.0 - lam) * pr + lam / 3.0
    lp = np.log(np.clip(pr, 1e-300, None)).sum(axis=1)
    return logsumexp(lp + om.GH_LOGW[None, :], axis=1)


def b0_b2(don, doff, y):
    """One B0 fit; returns B0 Wald and B2 cluster-robust results."""
    f = om.fit(don, doff, y)
    x = np.array(f["params"])
    G = don.shape[0]
    bnds = om._bounds(False)
    free = [i for i in range(len(x)) if not (i == 4 and abs(x[i] - bnds[i][0]) < 1e-3)]
    h = 1e-4
    scores = np.zeros((G, len(free)))
    for k, i in enumerate(free):
        e = np.zeros_like(x); e[i] = h
        scores[:, k] = (ll_per_participant(x + e, don, doff, y) - ll_per_participant(x - e, don, doff, y)) / (2 * h)
    def nll_free(z):
        p = x.copy(); p[free] = z
        return om.negloglik(p, don, doff, y)
    H = om.num_hessian(nll_free, x[free])
    try:
        Hinv = np.linalg.inv(H)
        meat = (G / (G - 1)) * scores.T @ scores
        V = Hinv @ meat @ Hinv
        iw = [free.index(2), free.index(3)]
        Vw = V[np.ix_(iw, iw)]
        se_r = np.sqrt(np.clip(np.diag(Vw), 0, None))
        ok = bool(np.all(np.isfinite(se_r)))
    except np.linalg.LinAlgError:
        Vw = np.full((2, 2), np.nan); se_r = np.array([np.nan, np.nan]); ok = False
    est = np.array([f["w_on"], f["w_off"]])
    return {"B0": {"est": est, "se": np.array([f["se_w_on"], f["se_w_off"]]), "crit": 1.96,
                   "cov": np.array(f["cov_w"]), "ok": f["stable"]},
            "B2": {"est": est, "se": se_r, "crit": T11, "cov": Vw, "ok": f["stable"] and ok},
            "sd_u_boundary": f["sd_u_at_boundary"]}


# ---------------------------------------------------------------- B1 -------
GH3_N = 7
_x, _w = np.polynomial.hermite.hermgauss(GH3_N)
_n1 = np.sqrt(2.0) * _x
_lw1 = np.log(_w / np.sqrt(np.pi))
N3 = np.array(np.meshgrid(_n1, _n1, _n1, indexing="ij")).reshape(3, -1)       # (3, Q)
LW3 = np.array(np.meshgrid(_lw1, _lw1, _lw1, indexing="ij")).reshape(3, -1).sum(0)


def b1_negloglik(p, don, doff, y):
    th1, th2 = p[0], p[0] + np.exp(p[1])
    w_on, w_off = p[2], p[3]
    sd_u, sd_a, sd_b = np.exp(p[4]), np.exp(p[5]), np.exp(p[6])
    u = sd_u * N3[0]; a = sd_a * N3[1]; b = sd_b * N3[2]                         # (Q,)
    eta = ((w_on + a)[None, None, :] * don[:, :, None]
           + (w_off + b)[None, None, :] * doff[:, :, None] + u[None, None, :])
    c1 = expit(th1 - eta); c2 = expit(th2 - eta)
    yy = y[:, :, None]
    pr = np.where(yy == 0, c1, np.where(yy == 1, c2 - c1, 1.0 - c2))
    lp = np.log(np.clip(pr, 1e-300, None)).sum(axis=1)                          # (N, Q)
    return -logsumexp(lp + LW3[None, :], axis=1).sum()


B1_BOUNDS = [(-10, 10), (np.log(0.01), np.log(20)), (-10, 10), (-10, 10),
             (np.log(1e-3), np.log(5)), (np.log(1e-3), np.log(3)), (np.log(1e-3), np.log(3))]


def b1(don, doff, y):
    f = lambda p: b1_negloglik(p, don, doff, y)
    x0 = np.array([-1.0, np.log(2.0), 0.0, 0.0, np.log(0.5), np.log(0.1), np.log(0.1)])
    r = minimize(f, x0, method="L-BFGS-B", bounds=B1_BOUNDS,
                 options={"maxiter": 1000, "ftol": 1e-12, "gtol": 1e-7})
    x = r.x
    at_low = [abs(x[i] - B1_BOUNDS[i][0]) < 1e-3 for i in range(7)]
    at_up = [abs(x[i] - B1_BOUNDS[i][1]) < 1e-3 for i in range(7)]
    free = [i for i in range(7) if not (i >= 4 and at_low[i])]
    def f_free(z):
        p = x.copy(); p[free] = z
        return f(p)
    try:
        H = om.num_hessian(f_free, x[free])
        cov = np.linalg.inv(H)
        iw = [free.index(2), free.index(3)]
        Vw = cov[np.ix_(iw, iw)]
        se = np.sqrt(np.clip(np.diag(Vw), 0, None))
        pd = bool(np.all(np.linalg.eigvalsh(H) > 0))
    except np.linalg.LinAlgError:
        Vw = np.full((2, 2), np.nan); se = np.array([np.nan, np.nan]); pd = False
    ok = bool(r.success and pd and not any(at_up[2:4]) and not any(at_low[2:4]) and np.all(np.isfinite(se)))
    return {"est": np.array([x[2], x[3]]), "se": se, "crit": 1.96, "cov": Vw, "ok": ok,
            "sd_slopes": (float(np.exp(x[5])), float(np.exp(x[6]))),
            "slope_sd_at_lower_bound": (bool(at_low[5]), bool(at_low[6])),
            "converged": bool(r.success)}


# ---------------------------------------------------------------- B3 -------
def b3_individual(don, doff, y):
    """Per-participant LS slopes of signed score on (d_on, d_off).
    Valid as closed form because the design is orthogonal with zero means."""
    score = y.astype(float) - 1.0
    b_on = (score * don).sum(1) / (don ** 2).sum(1)
    b_off = (score * doff).sum(1) / (doff ** 2).sum(1)
    return b_on, b_off


def b3(don, doff, y, rng, n_boot=2000):
    b_on, b_off = b3_individual(don, doff, y)
    G = len(b_on)
    est = np.array([b_on.mean(), b_off.mean()])
    se = np.array([b_on.std(ddof=1), b_off.std(ddof=1)]) / np.sqrt(G)
    cov = np.cov(np.vstack([b_on, b_off])) / G
    idx = rng.integers(0, G, size=(n_boot, G))
    ang = np.degrees(np.arctan2(b_off[idx].mean(1), b_on[idx].mean(1)))
    centre = np.degrees(np.arctan2(est[1], est[0]))
    ang = (ang - centre + 180.0) % 360.0 - 180.0 + centre
    return {"est": est, "se": se, "crit": T11, "cov": cov, "ok": bool(np.all(se > 0)),
            "angle_ci": (float(np.percentile(ang, 2.5)), float(np.percentile(ang, 97.5))),
            "b_on_i": b_on, "b_off_i": b_off}


def b3_expected_slopes(w_on, w_off, tau=1.0, beta=0.0, lapse=0.0, k=2, m=4):
    """Deduction: expected B3 slopes for a homogeneous latent observer
    (logistic noise, ternary thresholds +/-tau, bias beta, uniform lapses)."""
    import stimulus as st
    tm = st.order_templates(k, m)
    d_on = np.array([t.d_on for t in tm]); d_off = np.array([t.d_off for t in tm])
    eta = w_on * d_on + w_off * d_off + beta
    pR = expit(-tau - eta); pL = 1.0 - expit(tau - eta)
    escore = (1 - lapse) * (pL - pR)
    return float((escore * d_on).sum() / (d_on ** 2).sum()), float((escore * d_off).sum() / (d_off ** 2).sum())


# ---------------------------------------------------------------- B4 -------
def b4(don, doff, y, rng, n_boot=100):
    f0 = om.fit(don, doff, y)
    G = don.shape[0]
    draws, fails = [], 0
    for _ in range(n_boot):
        idx = rng.integers(0, G, size=G)
        fb = om.fit(don[idx], doff[idx], y[idx])
        if fb["stable"]:
            draws.append([fb["w_on"], fb["w_off"]])
        else:
            fails += 1
    draws = np.array(draws)
    lo = np.percentile(draws, 2.5, axis=0); hi = np.percentile(draws, 97.5, axis=0)
    return {"est": np.array([f0["w_on"], f0["w_off"]]), "ci_lo": lo, "ci_hi": hi,
            "boot_failures": fails, "n_boot": n_boot}


def wald_ci(res):
    return res["est"] - res["crit"] * res["se"], res["est"] + res["crit"] * res["se"]


def angle_ci_from_cov(est, cov, rng, crit_df=None, n=2000):
    """Simulation interval for atan2(w_off, w_on). With crit_df, draws are
    multivariate t with that many degrees of freedom."""
    try:
        z = rng.multivariate_normal([0, 0], cov, size=n, method="svd")
    except Exception:
        return np.nan, np.nan
    if crit_df is not None:
        z = z / np.sqrt(rng.chisquare(crit_df, size=(n, 1)) / crit_df)
    d = est[None, :] + z
    ang = np.degrees(np.arctan2(d[:, 1], d[:, 0]))
    c = np.degrees(np.arctan2(est[1], est[0]))
    ang = (ang - c + 180.0) % 360.0 - 180.0 + c
    return float(np.percentile(ang, 2.5)), float(np.percentile(ang, 97.5))
