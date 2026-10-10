"""
NZ execution: checkpointed (atomic batch files), resumable, frozen-hash checked.
Usage: python3 nz_run.py run|status --spec SPEC --run-dir DIR
"""
import argparse, hashlib, json, os, sys, time, traceback
import numpy as np
import nz_common as c
import e1_methods as em
from e1_run import clean, atomic_write, load

CODE_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def job_seed(ns, lab, rep):
    return int(hashlib.sha256(f"{ns}|{lab}|{rep}".encode()).hexdigest()[:16], 16)


def run_job(ns, a, rep):
    lab = c.label(a); s = job_seed(ns, lab, rep); t0 = time.perf_counter()
    row = {"job_id": f"{lab}|rep{rep}", "grid": lab, "a": a, "rep": rep, "seed": str(s)}
    try:
        rng = np.random.default_rng(s)
        don, doff, y = em.generate(c.scenario(a), rng)
        row["B3"] = em.run_b3(don, doff, y, rng); row["share_S"] = float(np.mean(y == 1)); row["status"] = "ok"
    except Exception as e:
        row["status"] = "error"; row["error"] = f"{type(e).__name__}: {e} | {traceback.format_exc(limit=2)}"
    row["seconds"] = round(time.perf_counter() - t0, 5)
    return row


def verify(spec):
    return [f for f, h in spec["code_sha256"].items() if sha(os.path.join(CODE_ROOT, f)) != h]


def cmd_run(a):
    spec = json.load(open(a.spec))
    if verify(spec):
        sys.exit(f"REFUSING: code differs from frozen spec: {verify(spec)}")
    os.makedirs(a.run_dir, exist_ok=True)
    man = {"frozen_spec_sha256": sha(a.spec), "code_sha256": spec["code_sha256"], "reps_per_grid": spec["reps_per_grid"],
           "grid": spec["grid"], "seed_namespace": spec["seed_namespace"], "batch_size": spec["batch_size"]}
    mp = os.path.join(a.run_dir, "manifest.json")
    if os.path.exists(mp):
        if {k: json.load(open(mp)).get(k) for k in man} != man:
            sys.exit("REFUSING TO RESUME: manifest differs")
        print("Resuming; manifest matches.")
    else:
        atomic_write(mp, json.dumps({**man, "created": time.strftime("%Y-%m-%d %H:%M:%S %Z")}, indent=1))
    jobs = [(g, r) for g in spec["grid"] for r in range(spec["reps_per_grid"])]
    B = spec["batch_size"]; batches = [jobs[i:i + B] for i in range(0, len(jobs), B)]
    t0 = time.time(); done = 0
    for bi, jb in enumerate(batches):
        p = os.path.join(a.run_dir, f"batch_{bi:05d}.jsonl")
        if os.path.exists(p):
            done += len(jb); continue
        rows = [run_job(spec["seed_namespace"], g, r) for g, r in jb]
        atomic_write(p, "".join(json.dumps(clean(x)) + "\n" for x in rows)); done += len(rows)
        rec = {"time": time.strftime("%H:%M:%S"), "batch": bi, "completed": done, "total": len(jobs),
               "errors_in_batch": sum(x["status"] == "error" for x in rows), "elapsed_s": round(time.time() - t0, 2)}
        with open(os.path.join(a.run_dir, "progress.jsonl"), "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)


def cmd_status(a):
    spec = json.load(open(a.spec)); rows, dups = load(a.run_dir)
    exp = {f"{c.label(g)}|rep{r}" for g in spec["grid"] for r in range(spec["reps_per_grid"])}; got = {x["job_id"] for x in rows}
    print(json.dumps({"expected": len(exp), "completed": len(rows), "duplicates": len(dups), "missing": len(exp - got),
                      "unexpected": len(got - exp), "errors": sum(x["status"] == "error" for x in rows)}, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run", "status"])
    ap.add_argument("--spec", required=True); ap.add_argument("--run-dir", required=True)
    a = ap.parse_args(); {"run": cmd_run, "status": cmd_status}[a.cmd](a)
