"""
Ternary cumulative-logit model with participant random intercepts.

CORRECTED parameterisation (Task 04, section 2):
    responses ordered  R (0) < S (1) < L (2)
    eta_ij   = w_on * d_on_ij + w_off * d_off_ij + u_i,   u_i ~ N(0, sd_u^2)
    P(r <= R) = logistic(theta1 - eta)
    P(r <= S) = logistic(theta2 - eta),     theta1 < theta2
Larger eta shifts responses toward L ("left began first"), so an observer who
uses onset order correctly has w_on > 0 under the sign convention
d_on = onset(R) - onset(L).

Optional lapse: P_obs = (1 - lam) * P_model + lam / 3.

Estimation is maximum marginal likelihood with Gauss-Hermite quadrature over
u_i. (Task 03 proposed a Bayesian fit with weakly informative priors; that is
not used here because thousands of repeated fits are required. See the Task 04
document for the implication.)
"""
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, logsumexp

GH_N = 15
_gh_x, _gh_w = np.polynomial.hermite.hermgauss(GH_N)
GH_NODES = np.sqrt(2.0) * _gh_x               # standard normal nodes
GH_LOGW = np.log(_gh_w / np.sqrt(np.pi))       # log weights summing to 1


def unpack(p, lapse):
    th1 = p[0]
    th2 = p[0] + np.exp(p[1])
    w_on, w_off = p[2], p[3]
    sd_u = np.exp(p[4])
    lam = expit(p[5]) if lapse else 0.0
    return th1, th2, w_on, w_off, sd_u, lam


def negloglik(p, don, doff, y, lapse=False):
    th1, th2, w_on, w_off, sd_u, lam = unpack(p, lapse)
    eta0 = w_on * don + w_off * doff                       # (N, J)
    eta = eta0[:, :, None] + sd_u * GH_NODES[None, None, :]  # (N, J, Q)
    c1 = expit(th1 - eta)
    c2 = expit(th2 - eta)
    pr = np.where(y[:, :, None] == 0, c1, np.where(y[:, :, None] == 1, c2 - c1, 1.0 - c2))
    if lapse:
        pr = (1.0 - lam) * pr + lam / 3.0
    lp = np.log(np.clip(pr, 1e-300, None)).sum(axis=1)       # (N, Q)
    ll = logsumexp(lp + GH_LOGW[None, :], axis=1)            # (N,)
    return -ll.sum()


def num_hessian(f, x, h=1e-4):
    n = len(x)
    H = np.zeros((n, n))
    fx = f(x)
    for i in range(n):
        ei = np.zeros(n); ei[i] = h
        H[i, i] = (f(x + ei) - 2 * fx + f(x - ei)) / h**2
        for j in range(i + 1, n):
            ej = np.zeros(n); ej[j] = h
            H[i, j] = H[j, i] = (f(x + ei + ej) - f(x + ei - ej) - f(x - ei + ej) + f(x - ei - ej)) / (4 * h * h)
    return H


# Parameter bounds (DEVIATION v1 -> v2, recorded in the Task 04 document:
# introduced after an 8-repetition pipeline smoke test and before the main run,
# because unbounded BFGS let a few null-observer fits drift to |w| > 10 and
# sd_u > 50, where 15-node quadrature is unreliable).
W_BOUND = 10.0
LOG_SDU_BOUNDS = (np.log(1e-3), np.log(5.0))
LOGIT_LAPSE_BOUNDS = (-8.0, 0.0)          # lapse in [0.0003, 0.5]


def _bounds(lapse):
    b = [(-10.0, 10.0), (np.log(0.01), np.log(20.0)), (-W_BOUND, W_BOUND), (-W_BOUND, W_BOUND),
         LOG_SDU_BOUNDS]
    if lapse:
        b.append(LOGIT_LAPSE_BOUNDS)
    return b


def fit(don, doff, y, lapse=False, start=None):
    """Returns dict with estimates, covariance of (w_on, w_off) and status flags.

    Variance-component and lapse parameters that finish at their lower bound
    are treated as boundary estimates: they are held fixed when the Hessian
    is computed, and flagged separately. (DEVIATION v1 -> v2; see document.)
    """
    if start is None:
        start = np.array([-1.0, np.log(2.0), 0.0, 0.0, np.log(0.5)] + ([-3.0] if lapse else []))
    f = lambda p: negloglik(p, don, doff, y, lapse)
    bnds = _bounds(lapse)
    res = minimize(f, start, method="L-BFGS-B", bounds=bnds,
                   options={"maxiter": 1000, "ftol": 1e-12, "gtol": 1e-7})
    x = res.x
    out = {"converged": bool(res.success), "nll": float(res.fun), "params": x.tolist()}
    th1, th2, w_on, w_off, sd_u, lam = unpack(x, lapse)
    out.update({"theta1": th1, "theta2": th2, "w_on": w_on, "w_off": w_off,
                "sd_u": sd_u, "lapse": lam})

    tol = 1e-3
    at_lower = [abs(x[i] - bnds[i][0]) < tol for i in range(len(x))]
    at_upper = [abs(x[i] - bnds[i][1]) < tol for i in range(len(x))]
    out["sd_u_at_boundary"] = bool(at_lower[4])
    out["lapse_at_boundary"] = bool(lapse and at_lower[5])
    out["w_at_bound"] = bool(at_lower[2] or at_upper[2] or at_lower[3] or at_upper[3])
    out["other_param_at_bound"] = bool(any(at_lower[i] or at_upper[i] for i in (0, 1))
                                       or at_upper[4] or (lapse and at_upper[5]))

    # Free parameters for the Hessian: drop nuisance parameters at lower bound
    free = [i for i in range(len(x)) if not ((i == 4 or i == 5) and at_lower[i])]
    def f_free(z):
        p = x.copy(); p[free] = z
        return f(p)
    try:
        H = num_hessian(f_free, x[free])
        ev = np.linalg.eigvalsh(H)
        cov_free = np.linalg.inv(H)
        iw = [free.index(2), free.index(3)]
        cov_w = cov_free[np.ix_(iw, iw)]
        se = np.sqrt(np.clip(np.diag(cov_w), 0, None))
        out.update({"hessian_pd": bool(np.all(ev > 0)), "se_w_on": float(se[0]),
                    "se_w_off": float(se[1]), "cov_w": cov_w.tolist(), "min_eig": float(ev.min())})
    except np.linalg.LinAlgError:
        out.update({"hessian_pd": False, "se_w_on": np.nan, "se_w_off": np.nan,
                    "cov_w": [[np.nan, np.nan], [np.nan, np.nan]], "min_eig": np.nan})
    gnorm = float(np.linalg.norm(np.where(np.array(at_lower) | np.array(at_upper), 0.0, res.jac)))
    out["grad_norm"] = gnorm
    out["stable"] = bool(
        (out["converged"] or gnorm < 1e-2)
        and out["hessian_pd"]
        and not out["w_at_bound"]
        and not out["other_param_at_bound"]
        and np.isfinite(out["se_w_on"]) and np.isfinite(out["se_w_off"])
        and out["se_w_on"] < 5 and out["se_w_off"] < 5)
    return out


def simulate_responses(rng, don, doff, w_on, w_off, tau=1.0, bias_mean=0.0,
                       bias_sd=0.5, lapse=0.02, w_het_sd=0.0, tau_het_sd=0.0):
    """Generative observer: latent z = w.x + b_i + logistic noise.
    Respond L if z > tau_i, R if z < -tau_i, else S. With prob `lapse`
    respond uniformly at random. Optional multiplicative heterogeneity in
    weights (lognormal) and in tau (lognormal) per participant."""
    N, J = don.shape
    b = rng.normal(bias_mean, bias_sd, size=(N, 1))
    gw = np.exp(rng.normal(0, w_het_sd, size=(N, 1))) if w_het_sd > 0 else np.ones((N, 1))
    gt = np.exp(rng.normal(0, tau_het_sd, size=(N, 1))) if tau_het_sd > 0 else np.ones((N, 1))
    eta = gw * (w_on * don + w_off * doff) + b
    z = eta + rng.logistic(0, 1, size=(N, J))
    t = tau * gt
    y = np.where(z > t, 2, np.where(z < -t, 0, 1))
    lap = rng.random((N, J)) < lapse
    y = np.where(lap, rng.integers(0, 3, size=(N, J)), y)
    return y
