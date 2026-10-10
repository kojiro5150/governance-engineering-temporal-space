"""
E1 execution: checkpointed, resumable, frozen.

Refuses to run unless the frozen specification exists and every code file
listed in it matches its frozen SHA-256. Each batch of jobs is written
atomically; resuming skips finished batches; aggregation refuses duplicates.

Usage:
  python3 e1_run.py run    --spec ../results/E1/E1_FROZEN_SPEC.json --run-dir ../results/E1/run --workers 2
  python3 e1_run.py status --run-dir ../results/E1/run
"""
import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from multiprocessing import Pool

import numpy as np

import e1_methods as em

HERE = os.path.dirname(os.path.abspath(__file__))


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def job_seed(ns, scen, rep):
    return int(hashlib.sha256(f"{ns}|{scen}|{rep}".encode()).hexdigest()[:16], 16)


def run_job(args):
    ns, scen, rep = args
    s = job_seed(ns, scen, rep)
    t0 = time.perf_counter()
    row = {"job_id": f"{scen}|rep{rep}", "scenario": scen, "rep": rep, "seed": str(s)}
    try:
        rng = np.random.default_rng(s)
        don, doff, y = em.generate(em.SCENARIOS[scen], rng)
        row["B2"] = em.run_b2(don, doff, y, rng)
        row["B3"] = em.run_b3(don, doff, y, rng)
        row["share_S"] = float(np.mean(y == 1))
        row["status"] = "ok"
    except Exception as e:
        row["status"] = "error"
        row["error"] = f"{type(e).__name__}: {e} | {traceback.format_exc(limit=2)}"
    row["seconds"] = round(time.perf_counter() - t0, 4)
    return row


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def atomic_write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def cmd_run(a):
    spec = json.load(open(a.spec))
    bad = [f for f, h in spec["code_sha256"].items() if sha(os.path.join(HERE, f)) != h]
    if bad:
        sys.exit(f"REFUSING: code differs from frozen spec: {bad}")
    spec_hash = sha(a.spec)
    os.makedirs(a.run_dir, exist_ok=True)
    mpath = os.path.join(a.run_dir, "manifest.json")
    man = {"frozen_spec_sha256": spec_hash, "code_sha256": spec["code_sha256"],
           "reps": spec["reps"], "scenarios": list(spec["scenarios"]), "seed_namespace": spec["seed_namespace"],
           "batch_size": a.batch_size}
    if os.path.exists(mpath):
        old = json.load(open(mpath))
        if {k: old.get(k) for k in man} != man:
            sys.exit("REFUSING TO RESUME: manifest differs. Use a new --run-dir.")
        print("Resuming; manifest matches.")
    else:
        atomic_write(mpath, json.dumps({**man, "created": time.strftime("%Y-%m-%d %H:%M:%S %Z")}, indent=1))
    jobs = [(spec["seed_namespace"], s, r) for s in spec["scenarios"] for r in range(spec["reps"])]
    batches = [jobs[i:i + a.batch_size] for i in range(0, len(jobs), a.batch_size)]
    pending = [i for i in range(len(batches)) if not os.path.exists(os.path.join(a.run_dir, f"batch_{i:05d}.jsonl"))]
    done = sum(len(batches[i]) for i in range(len(batches)) if i not in pending)
    print(f"jobs {len(jobs)}; batches {len(batches)}; done {done}; pending batches {len(pending)}", flush=True)
    sid = time.strftime("%Y%m%d-%H%M%S"); t0 = time.time(); n_sess = 0
    with Pool(a.workers) as pool:
        for bi in pending:
            rows = pool.map(run_job, batches[bi], chunksize=max(1, len(batches[bi]) // (2 * a.workers)))
            atomic_write(os.path.join(a.run_dir, f"batch_{bi:05d}.jsonl"),
                         "".join(json.dumps(clean(r)) + "\n" for r in rows))
            n_sess += len(rows); done += len(rows)
            el = time.time() - t0; rate = n_sess / el
            rec = {"session_id": sid, "time": time.strftime("%H:%M:%S"), "batch": bi, "completed": done,
                   "total": len(jobs), "errors_in_batch": sum(r["status"] == "error" for r in rows),
                   "elapsed_s": round(el, 1), "rate_per_s": round(rate, 2),
                   "eta_s": round((len(jobs) - done) / rate, 1), "scenarios": sorted({r["scenario"] for r in rows})}
            with open(os.path.join(a.run_dir, "progress.jsonl"), "a") as f:
                f.write(json.dumps(rec) + "\n")
            try:
                print(json.dumps(rec), flush=True)
            except BrokenPipeError:
                pass


def load(run_dir):
    rows, seen, dups = [], set(), []
    for n in sorted(os.listdir(run_dir)):
        if n.startswith("batch_") and n.endswith(".jsonl"):
            for l in open(os.path.join(run_dir, n)):
                r = json.loads(l)
                (dups.append(r["job_id"]) if r["job_id"] in seen else seen.add(r["job_id"]))
                rows.append(r)
    return rows, dups


def cmd_status(a):
    man = json.load(open(os.path.join(a.run_dir, "manifest.json")))
    rows, dups = load(a.run_dir)
    exp = {f"{s}|rep{r}" for s in man["scenarios"] for r in range(man["reps"])}
    got = {r["job_id"] for r in rows}
    print(json.dumps({"expected": len(exp), "completed": len(rows), "duplicates": len(dups),
                      "missing": len(exp - got), "unexpected": len(got - exp),
                      "errors": sum(r["status"] == "error" for r in rows)}, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--spec", required=True); r.add_argument("--run-dir", required=True)
    r.add_argument("--workers", type=int, default=2); r.add_argument("--batch-size", type=int, default=50)
    s = sub.add_parser("status"); s.add_argument("--run-dir", required=True)
    a = ap.parse_args()
    {"run": cmd_run, "status": cmd_status}[a.cmd](a)
