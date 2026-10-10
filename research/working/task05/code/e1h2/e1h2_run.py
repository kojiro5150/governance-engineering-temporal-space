"""
E1-H2 execution: checkpointed, resumable, frozen. Mirrors frozen e1_run.py
(whose clean/atomic_write/load helpers are imported unchanged).

Refuses to run unless every code file listed in the frozen E1-H2 spec matches
its SHA-256 (paths relative to code/).
Usage:
  python3 e1h2_run.py run    --spec SPEC --run-dir DIR --workers 2 --batch-size 50
  python3 e1h2_run.py status --spec SPEC --run-dir DIR
"""
import argparse, hashlib, json, os, sys, time, traceback
from multiprocessing import Pool
import numpy as np
import e1h2_common as c
import e1_methods as em
from e1_run import clean, atomic_write, load

CODE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def job_seed(ns, rep):
    return int(hashlib.sha256(f"{ns}|{rep}".encode()).hexdigest()[:16], 16)


def run_job(args):
    ns, rep = args
    s = job_seed(ns, rep); t0 = time.perf_counter()
    row = {"job_id": f"H2random|rep{rep}", "rep": rep, "seed": str(s)}
    try:
        rng = np.random.default_rng(s)
        don, doff, y, k = c.generate(rng)
        row["n_onset"] = k
        row["B2"] = em.run_b2(don, doff, y, rng)
        row["B3"] = em.run_b3(don, doff, y, rng)
        row["share_S"] = float(np.mean(y == 1)); row["status"] = "ok"
    except Exception as e:
        row["status"] = "error"; row["error"] = f"{type(e).__name__}: {e} | {traceback.format_exc(limit=2)}"
    row["seconds"] = round(time.perf_counter() - t0, 4)
    return row


def verify(spec):
    return [f for f, h in spec["code_sha256"].items() if sha(os.path.join(CODE_ROOT, f)) != h]


def cmd_run(a):
    spec = json.load(open(a.spec))
    bad = verify(spec)
    if bad:
        sys.exit(f"REFUSING: code differs from frozen spec: {bad}")
    os.makedirs(a.run_dir, exist_ok=True)
    man = {"frozen_spec_sha256": sha(a.spec), "code_sha256": spec["code_sha256"], "reps": spec["reps"],
           "seed_namespace": spec["seed_namespace"], "batch_size": a.batch_size}
    mp = os.path.join(a.run_dir, "manifest.json")
    if os.path.exists(mp):
        old = json.load(open(mp))
        if {k: old.get(k) for k in man} != man:
            sys.exit("REFUSING TO RESUME: manifest differs. Use a new --run-dir.")
        print("Resuming; manifest matches.")
    else:
        atomic_write(mp, json.dumps({**man, "created": time.strftime("%Y-%m-%d %H:%M:%S %Z")}, indent=1))
    jobs = [(spec["seed_namespace"], r) for r in range(spec["reps"])]
    batches = [jobs[i:i + a.batch_size] for i in range(0, len(jobs), a.batch_size)]
    pending = [i for i in range(len(batches)) if not os.path.exists(os.path.join(a.run_dir, f"batch_{i:05d}.jsonl"))]
    done = sum(len(batches[i]) for i in range(len(batches)) if i not in pending)
    print(f"jobs {len(jobs)}; batches {len(batches)}; done {done}; pending {len(pending)}", flush=True)
    sid = time.strftime("%Y%m%d-%H%M%S"); t0 = time.time(); n = 0
    with Pool(a.workers) as pool:
        for bi in pending:
            rows = pool.map(run_job, batches[bi], chunksize=max(1, len(batches[bi]) // (2 * a.workers)))
            atomic_write(os.path.join(a.run_dir, f"batch_{bi:05d}.jsonl"), "".join(json.dumps(clean(r)) + "\n" for r in rows))
            n += len(rows); done += len(rows); el = time.time() - t0
            rec = {"session_id": sid, "time": time.strftime("%H:%M:%S"), "batch": bi, "completed": done, "total": len(jobs),
                   "errors_in_batch": sum(r["status"] == "error" for r in rows), "elapsed_s": round(el, 1),
                   "rate_per_s": round(n / el, 2), "eta_s": round((len(jobs) - done) / (n / el), 1)}
            with open(os.path.join(a.run_dir, "progress.jsonl"), "a") as f:
                f.write(json.dumps(rec) + "\n")
            try:
                print(json.dumps(rec), flush=True)
            except BrokenPipeError:
                pass


def cmd_status(a):
    spec = json.load(open(a.spec)); rows, dups = load(a.run_dir)
    exp = {f"H2random|rep{r}" for r in range(spec["reps"])}; got = {r["job_id"] for r in rows}
    print(json.dumps({"expected": len(exp), "completed": len(rows), "duplicates": len(dups), "missing": len(exp - got),
                      "unexpected": len(got - exp), "errors": sum(r["status"] == "error" for r in rows)}, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--spec", required=True); r.add_argument("--run-dir", required=True)
    r.add_argument("--workers", type=int, default=2); r.add_argument("--batch-size", type=int, default=50)
    s = sub.add_parser("status"); s.add_argument("--spec", required=True); s.add_argument("--run-dir", required=True)
    a = ap.parse_args(); {"run": cmd_run, "status": cmd_status}[a.cmd](a)
