"""
Checkpointed, resumable parameter-recovery runner (v3, Task 05).

Identical to Task 04 simulate_recovery_v2.py except: (1) --scenarios selects a
subset of the v1 scenarios; (2) --no-lapse-refits omits lapse-model refits;
(3) CODE_FILES lists this file. Fits, seeds and job_ids are unchanged, so
repetitions 0-99 reproduce Task 04 Stage 2 fits exactly.

--- original v2 docstring follows ---
Checkpointed, resumable parameter-recovery runner (v2).

Successor to simulate_recovery.py (v1), whose full run was interrupted with no
recoverable output because it wrote results only at completion. Scenario
definitions, seeds, criteria, summaries and the fitting model are imported
unchanged from v1 / ordinal_model.py, so v2 fits are the same computation.

Architecture
  * A run directory holds manifest.json (config + code hashes), batch files,
    progress.jsonl and, after aggregation, fits.csv and summary.json.
  * Jobs are enumerated deterministically and grouped into fixed batches.
    Batch membership depends only on the config, never on worker scheduling.
  * Each finished batch is written to batch_XXXXX.jsonl via a temporary file
    and os.replace (atomic on POSIX). A batch file either exists complete or
    not at all.
  * Resuming skips batches whose files exist. The manifest must match exactly
    (same config, same code hashes) or the run refuses to start.
  * Aggregation refuses duplicate job_ids and reports missing ones.
  * Every job records its seed; exceptions are recorded as status "error".

Usage
  python3 simulate_recovery_v2.py run  --run-dir DIR --reps 100 --allocations "J20 (k=2)" \
                                       --workers 2 --batch-size 40
  python3 simulate_recovery_v2.py status    --run-dir DIR
  python3 simulate_recovery_v2.py aggregate --run-dir DIR
  python3 simulate_recovery_v2.py reproducibility-check --out DIR
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import time
import traceback
from multiprocessing import Pool

import numpy as np

import simulate_recovery as v1   # scenario definitions, seeds, criteria, summaries (unchanged)

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_FILES = ["ordinal_model.py", "stimulus.py", "simulate_recovery.py", "simulate_recovery_v3.py"]


def file_hash(name):
    with open(os.path.join(HERE, name), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def enumerate_jobs(reps, allocations, scenarios, lapse_scenarios):
    jobs = []
    for alloc in allocations:
        for scen in scenarios:
            for rep in range(reps):
                jobs.append((scen, alloc, rep, False))
                if scen in lapse_scenarios:
                    jobs.append((scen, alloc, rep, True))
    return jobs


def job_id(job):
    scen, alloc, rep, lapse = job
    return f"{scen}|{alloc}|rep{rep}|{'lapse' if lapse else 'standard'}"


def run_one(job):
    t0 = time.perf_counter()
    scen, alloc, rep, lapse = job
    seed = v1.rep_seed(scen, alloc, rep)
    try:
        row = v1.one_job(job)
        row["status"] = "ok" if row["stable"] else "unstable"
        row["error"] = ""
    except Exception as e:  # recorded, never swallowed silently
        row = {"scenario": scen, "allocation": alloc, "rep": rep, "lapse_model": lapse,
               "status": "error", "error": f"{type(e).__name__}: {e} | {traceback.format_exc(limit=2)}"}
    row["job_id"] = job_id(job)
    row["seed"] = str(seed)
    row["observer_type"] = scen.split(" ", 1)[1]
    row["fit_seconds"] = round(time.perf_counter() - t0, 4)
    return row


def to_jsonable(row):
    out = {}
    for k, v in row.items():
        if isinstance(v, (np.floating,)):
            v = float(v)
        elif isinstance(v, (np.integer,)):
            v = int(v)
        elif isinstance(v, (np.bool_,)):
            v = bool(v)
        if isinstance(v, float) and not np.isfinite(v):
            v = None
        out[k] = v
    return out


def atomic_write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def selected_scenarios(args):
    sel = list(v1.SCENARIOS.keys()) if not args.scenarios else args.scenarios
    unknown = [s for s in sel if s not in v1.SCENARIOS]
    if unknown:
        sys.exit(f"Unknown scenarios: {unknown}")
    return sel


def selected_lapse(args):
    if args.no_lapse_refits:
        return []
    return sorted(s for s in v1.LAPSE_MODEL_SCENARIOS if s in selected_scenarios(args))


def build_manifest(args):
    cfg = {"reps": args.reps, "allocations": args.allocations,
           "scenarios": selected_scenarios(args),
           "lapse_model_scenarios": selected_lapse(args),
           "batch_size": args.batch_size, "n_participants": v1.N_PARTICIPANTS,
           "seed_namespace": v1.MASTER, "criteria": v1.CRITERIA}
    return {"config": cfg, "code_sha256": {f: file_hash(f) for f in CODE_FILES}}


def cmd_run(args):
    os.makedirs(args.run_dir, exist_ok=True)
    man_path = os.path.join(args.run_dir, "manifest.json")
    man = build_manifest(args)
    if os.path.exists(man_path):
        old = json.load(open(man_path))
        if old["config"] != man["config"] or old["code_sha256"] != man["code_sha256"]:
            sys.exit("REFUSING TO RESUME: manifest differs (config or code changed). "
                     "Use a new --run-dir.")
        print("Resuming existing run; manifest matches.")
    else:
        man["created"] = time.strftime("%Y-%m-%d %H:%M:%S %Z")
        atomic_write(man_path, json.dumps(man, indent=1))

    jobs = enumerate_jobs(args.reps, args.allocations, selected_scenarios(args),
                          set(selected_lapse(args)))
    batches = [jobs[i:i + args.batch_size] for i in range(0, len(jobs), args.batch_size)]
    total = len(jobs)
    done_batches = {i for i in range(len(batches))
                    if os.path.exists(os.path.join(args.run_dir, f"batch_{i:05d}.jsonl"))}
    pending = [i for i in range(len(batches)) if i not in done_batches]
    done_jobs = sum(len(batches[i]) for i in done_batches)
    print(f"Jobs total {total}; batches {len(batches)}; already complete {len(done_batches)} "
          f"({done_jobs} fits); pending {len(pending)}")
    if args.max_batches is not None:
        pending = pending[:args.max_batches]
        print(f"--max-batches {args.max_batches}: running {len(pending)} batch(es) this invocation")

    prog_path = os.path.join(args.run_dir, "progress.jsonl")
    t_start = time.time()
    session_id = time.strftime("%Y%m%d-%H%M%S")
    fits_this_session = 0
    with Pool(args.workers) as pool:
        for bi in pending:
            rows = pool.map(run_one, batches[bi], chunksize=max(1, len(batches[bi]) // (2 * args.workers)))
            text = "".join(json.dumps(to_jsonable(r)) + "\n" for r in rows)
            atomic_write(os.path.join(args.run_dir, f"batch_{bi:05d}.jsonl"), text)
            fits_this_session += len(rows)
            done_jobs += len(rows)
            elapsed = time.time() - t_start
            rate = fits_this_session / elapsed
            rec = {"session_id": session_id, "time": time.strftime("%H:%M:%S"), "batch": bi,
                   "completed_fits": done_jobs, "total_fits": total,
                   "batch_unstable": sum(r.get("status") == "unstable" for r in rows),
                   "batch_errors": sum(r.get("status") == "error" for r in rows),
                   "session_elapsed_s": round(elapsed, 1),
                   "rate_fits_per_s": round(rate, 3),
                   "eta_remaining_s": round((total - done_jobs) / rate, 1) if rate > 0 else None,
                   "batch_scenarios": sorted({r["scenario"] for r in rows}),
                   "batch_allocations": sorted({r["allocation"] for r in rows})}
            with open(prog_path, "a") as f:
                f.write(json.dumps(rec) + "\n")
            try:   # progress.jsonl is authoritative; a closed stdout must not stop the run
                print(json.dumps(rec), flush=True)
            except BrokenPipeError:
                pass


def load_rows(run_dir):
    rows, seen, dups = [], set(), []
    for name in sorted(os.listdir(run_dir)):
        if name.startswith("batch_") and name.endswith(".jsonl"):
            for line in open(os.path.join(run_dir, name)):
                r = json.loads(line)
                if r["job_id"] in seen:
                    dups.append(r["job_id"])
                seen.add(r["job_id"])
                rows.append(r)
    return rows, dups


def cmd_status(args):
    man = json.load(open(os.path.join(args.run_dir, "manifest.json")))
    c = man["config"]
    expected = enumerate_jobs(c["reps"], c["allocations"], c["scenarios"], set(c["lapse_model_scenarios"]))
    rows, dups = load_rows(args.run_dir)
    st = {}
    for r in rows:
        st[r["status"]] = st.get(r["status"], 0) + 1
    print(json.dumps({"expected_fits": len(expected), "completed_fits": len(rows),
                      "by_status": st, "duplicates": len(dups),
                      "missing": len({job_id(j) for j in expected} - {r["job_id"] for r in rows})}, indent=1))


def session_runtimes(prog):
    """Wall-clock seconds per run session (last cumulative elapsed in each session)."""
    out = {}
    for p in prog:
        out[p.get("session_id", "unknown")] = p["session_elapsed_s"]
    return out


def evaluate_allocation(summary, alloc):
    """v1.evaluate logic, restricted to one allocation (v1 assumes all three exist)."""
    def g(s):
        return summary.get(f"{s} | {alloc} | standard-model")
    if any(g(s) is None or "bias_w_on_over_a" not in g(s) for s in v1.SCENARIOS):
        return "not evaluable: missing scenarios or no stable fits"
    core = [s for s, v in v1.SCENARIOS.items() if v[4] == "core"]
    rc1 = {s: (abs(g(s)["bias_w_on_over_a"]) <= 0.10 and abs(g(s)["bias_w_off_over_a"]) <= 0.10) for s in core}
    rc2 = {s: (0.90 <= g(s)["coverage_w_on"] <= 0.98 and 0.90 <= g(s)["coverage_w_off"] <= 0.98) for s in core}
    rc3 = {s: g(s)["unstable_rate"] <= 0.05 for s in v1.SCENARIOS}
    rc4 = {"onset_excludes_45": g("S01 onset moderate")["p_angle_ci_excludes_45"],
           "midpoint_excludes_0": g("S04 midpoint moderate")["p_angle_ci_excludes_0"]}
    rc5 = g("S10 guessing")["p_wald_reject_0.05"]
    res = {"RC1_pass": all(rc1.values()), "RC1_detail": rc1,
           "RC2_pass": all(rc2.values()), "RC2_detail": rc2,
           "RC3_pass": all(rc3.values()), "RC3_detail": rc3,
           "RC4_pass": rc4["onset_excludes_45"] >= 0.80 and rc4["midpoint_excludes_0"] >= 0.80,
           "RC4_detail": rc4, "RC5_pass": rc5 <= 0.07, "RC5_detail": rc5}
    res["ALL_PASS"] = all(res[k] for k in ["RC1_pass", "RC2_pass", "RC3_pass", "RC4_pass", "RC5_pass"])
    return res


def cmd_aggregate(args):
    man = json.load(open(os.path.join(args.run_dir, "manifest.json")))
    c = man["config"]
    expected = {job_id(j) for j in enumerate_jobs(c["reps"], c["allocations"], c["scenarios"],
                                                  set(c["lapse_model_scenarios"]))}
    rows, dups = load_rows(args.run_dir)
    if dups:
        sys.exit(f"REFUSING TO AGGREGATE: {len(dups)} duplicate job_ids, e.g. {dups[:3]}")
    got = {r["job_id"] for r in rows}
    missing = sorted(expected - got)
    extra = sorted(got - expected)
    if extra:
        sys.exit(f"REFUSING TO AGGREGATE: {len(extra)} job_ids not in manifest")
    errors = [r for r in rows if r["status"] == "error"]
    ok_rows = [r for r in rows if r["status"] != "error"]
    for r in ok_rows:   # restore NaN for summary arithmetic
        for k, v in r.items():
            if v is None:
                r[k] = float("nan")
    summary = v1.summarise(ok_rows)
    evaluation = {alloc: evaluate_allocation(summary, alloc) for alloc in c["allocations"]}
    keys = sorted({k for r in rows for k in r.keys()})
    with open(os.path.join(args.run_dir, "fits.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows)
    prog = [json.loads(l) for l in open(os.path.join(args.run_dir, "progress.jsonl"))] \
        if os.path.exists(os.path.join(args.run_dir, "progress.jsonl")) else []
    fit_secs = [r["fit_seconds"] for r in rows if "fit_seconds" in r]
    result = {"manifest": man, "expected_fits": len(expected), "completed_fits": len(rows),
              "missing_fits": len(missing), "error_fits": len(errors),
              "error_examples": [e["error"][:300] for e in errors[:5]],
              "runtime": {"sessions": session_runtimes(prog),
                          "total_wall_s_all_sessions": round(sum(session_runtimes(prog).values()), 1),
                          "mean_fit_seconds_single_worker": round(float(np.mean(fit_secs)), 4) if fit_secs else None,
                          "median_fit_seconds_single_worker": round(float(np.median(fit_secs)), 4) if fit_secs else None},
              "evaluation_note": ("Criteria evaluation is preliminary unless reps >= the planned confirmatory "
                                  "count; see Task 04 document."),
              "evaluation": evaluation, "summary": summary}
    atomic_write(os.path.join(args.run_dir, "summary.json"), json.dumps(result, indent=1, default=str))
    print(json.dumps({"completed": len(rows), "missing": len(missing), "errors": len(errors),
                      "evaluation": evaluation}, indent=1, default=str))


def cmd_repro(args):
    """Same jobs under 1 worker, 2 workers, and an interrupted-then-resumed
    2-worker run; all three must give byte-identical fit results."""
    os.makedirs(args.out, exist_ok=True)
    rng_jobs = enumerate_jobs(3, ["J20 (k=2)"], ["S01 onset moderate", "S04 midpoint moderate",
                                                  "S10 guessing", "S12 lapse-heavy onset"],
                              v1.LAPSE_MODEL_SCENARIOS)
    def canon(rows):
        drop = {"fit_seconds"}
        return sorted(json.dumps({k: v for k, v in to_jsonable(r).items() if k not in drop}, sort_keys=True)
                      for r in rows)
    with Pool(1) as p:
        a = canon(p.map(run_one, rng_jobs))
    with Pool(2) as p:
        b = canon(p.map(run_one, rng_jobs, chunksize=1))
    half = len(rng_jobs) // 2
    with Pool(2) as p:
        c1 = p.map(run_one, rng_jobs[half:], chunksize=1)   # "resumed" second half first
    with Pool(2) as p:
        c0 = p.map(run_one, rng_jobs[:half], chunksize=3)
    c = canon(c0 + c1)
    res = {"n_jobs": len(rng_jobs), "identical_1worker_vs_2workers": a == b,
           "identical_1worker_vs_split_resumed": a == c,
           "sha256_1worker": hashlib.sha256("".join(a).encode()).hexdigest(),
           "sha256_2workers": hashlib.sha256("".join(b).encode()).hexdigest(),
           "sha256_split": hashlib.sha256("".join(c).encode()).hexdigest()}
    atomic_write(os.path.join(args.out, "reproducibility_check.json"), json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--run-dir", required=True)
    r.add_argument("--reps", type=int, required=True)
    r.add_argument("--allocations", nargs="+", default=["J20 (k=2)"])
    r.add_argument("--workers", type=int, default=2)
    r.add_argument("--batch-size", type=int, default=40)
    r.add_argument("--max-batches", type=int, default=None)
    r.add_argument("--scenarios", nargs="+", default=None)
    r.add_argument("--no-lapse-refits", action="store_true")
    s = sub.add_parser("status"); s.add_argument("--run-dir", required=True)
    g = sub.add_parser("aggregate"); g.add_argument("--run-dir", required=True)
    q = sub.add_parser("reproducibility-check"); q.add_argument("--out", required=True)
    args = ap.parse_args()
    {"run": cmd_run, "status": cmd_status, "aggregate": cmd_aggregate,
     "reproducibility-check": cmd_repro}[args.cmd](args)


if __name__ == "__main__":
    main()
