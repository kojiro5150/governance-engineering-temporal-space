"""Integrity checks on the committed Task 05 record.
Usage (from research/working/task05/): python3 INTEGRITY/verify_task05_record.py . ../task04/task04_stage2_artefacts.zip "" INTEGRITY/integrity_report.json
The third argument (originally delivered package zip) is optional; pass "" when unavailable."""
import hashlib, json, os, sys, zipfile
R = sys.argv[1]; T4 = sys.argv[2] if len(sys.argv) > 2 else None; OP = (sys.argv[3] or None) if len(sys.argv) > 3 else None
sha = lambda p: hashlib.sha256(open(os.path.join(R, p), "rb").read()).hexdigest()
rep = {}

def check_sums(manifest, base_for):
    ok, bad, miss = 0, [], []
    for line in open(os.path.join(R, manifest)):
        if not line.strip(): continue
        h, f = line.rstrip("\n").split(None, 1); f = f.lstrip("*")
        p = os.path.normpath(os.path.join(base_for(f), f))
        if not os.path.isfile(os.path.join(R, p)): miss.append(p)
        elif sha(p) != h: bad.append(p)
        else: ok += 1
    return {"entries": ok + len(bad) + len(miss), "match": ok, "mismatch": bad, "missing": miss}

# 1 closure + A1 manifests (base = task05 root, paths may start with ../ from logs? they were written from task05 root)
rep["TASK05_CLOSURE_SHA256SUMS"] = check_sums("logs/TASK05_CLOSURE_SHA256SUMS.txt", lambda f: ".")
rep["TASK05_ADDENDUM_A1_SHA256SUMS"] = check_sums("logs/TASK05_ADDENDUM_A1_SHA256SUMS.txt", lambda f: ".")
# 2 raw-output manifests: mixed bases (run outputs relative to run/, summaries relative to the experiment dir)
RUNFILES = lambda f: f.startswith("batch_") or f in ("manifest.json", "progress.jsonl")
rep["E1_raw_SHA256SUMS"] = check_sums("results/E1/E1_raw_SHA256SUMS", lambda f: "results/E1/run" if RUNFILES(f) else "results/E1")
rep["E1H2_raw_SHA256SUMS"] = check_sums("results/E1H2/E1H2_raw_SHA256SUMS", lambda f: "results/E1H2/run" if RUNFILES(f) else "results/E1H2")
rep["NZ_raw_SHA256SUMS"] = check_sums("results/NZ/NZ_raw_SHA256SUMS", lambda f: "results/NZ/run" if RUNFILES(f) else "results/NZ")
# 3 original-E1 integrity logs written from code/e1h2 and code/nz (paths ../../)
rep["E1H2_original_E1_hashes_before"] = check_sums("logs/E1H2_original_E1_hashes_before.txt", lambda f: "code/e1h2")
rep["NZ_prior_hashes_before"] = check_sums("logs/NZ_prior_hashes_before.txt", lambda f: "code/nz")
# 4 frozen-spec hash files (written from code/ or code/e1h2 etc.)
for name, spec, base in [("E1", "results/E1/E1_FROZEN_SPEC.json", "code"), ("E1H2", "results/E1H2/E1H2_FROZEN_SPEC.json", "code/e1h2"), ("NZ", "results/NZ/NZ_FROZEN_SPEC.json", "code/nz")]:
    rec = open(os.path.join(R, f"logs/{name}_FROZEN_SPEC.sha256")).read().split()[0]
    S = json.load(open(os.path.join(R, spec)))
    code_bad = [f for f, h in S["code_sha256"].items() if sha(os.path.join("code", f)) != h]
    runman = json.load(open(os.path.join(R, os.path.dirname(spec), "run", "manifest.json")))
    rep[f"{name}_frozen_spec"] = {"spec_hash_matches_log": rec == sha(spec), "spec_hash": sha(spec),
                                  "code_files": len(S["code_sha256"]), "code_mismatch": code_bad,
                                  "run_manifest_points_to_spec": runman["frozen_spec_sha256"] == sha(spec)}
S = json.load(open(os.path.join(R, "results/E1/E1_FROZEN_SPEC.json")))
rep["E1_precheck_evidence"] = {f: sha(os.path.join("results/E1/prechecks", f)) == h for f, h in S["precheck_evidence_sha256"].items()}
S = json.load(open(os.path.join(R, "results/E1H2/E1H2_FROZEN_SPEC.json")))
rep["E1H2_links"] = {"original_E1_spec": S["original_E1"]["spec_sha256"] == sha("results/E1/E1_FROZEN_SPEC.json"),
                     "original_E1_results": S["original_E1"]["results_sha256"] == sha("results/E1/E1_results.json"),
                     "precheck": S["targets"]["precheck_sha256"] == sha("results/E1H2/precheck/precheck.json")}
S = json.load(open(os.path.join(R, "results/NZ/NZ_FROZEN_SPEC.json")))
rep["NZ_links"] = {"E1_spec": S["related_frozen"]["E1_spec_sha256"] == sha("results/E1/E1_FROZEN_SPEC.json"),
                   "E1H2_spec": S["related_frozen"]["E1H2_spec_sha256"] == sha("results/E1H2/E1H2_FROZEN_SPEC.json"),
                   "closure_record": S["related_frozen"]["closure_record_sha256"] == sha("task05-closure-decision-record.md"),
                   "precheck": S["precheck_sha256"] == sha("results/NZ/precheck/precheck.json")}
# 5 config.json and inherited code
C = json.load(open(os.path.join(R, "config.json")))
rep["config_inherited"] = {f: sha("code/" + f) == h for f, h in C["inherited_from_task04_archive_unchanged"].items()}
rep["config_task05_code"] = {f: sha("code/" + f) == h for f, h in C["task05_code"].items() if os.path.isfile(os.path.join(R, "code", f))}
rep["config_task05_code_absent"] = [f for f in C["task05_code"] if not os.path.isfile(os.path.join(R, "code", f))]
rep["inherited_code_sha256"] = check_sums("logs/inherited_code_sha256.txt", lambda f: "code")
if T4:
    z = zipfile.ZipFile(T4); names = {os.path.basename(n): n for n in z.namelist() if n.endswith(".py")}
    rep["inherited_vs_repo_task04_archive"] = {f: (hashlib.sha256(z.read(names[f])).hexdigest() == h if f in names else "not in archive")
                                               for f, h in C["inherited_from_task04_archive_unchanged"].items()}
# 6 DEVIATIONS append-only reconciliation
dev = open(os.path.join(R, "logs/DEVIATIONS.md"), "rb").read()
cl = {l.split(None, 1)[1].strip(): l.split()[0] for l in open(os.path.join(R, "logs/TASK05_CLOSURE_SHA256SUMS.txt"))}
recon = {"closure_manifest_hash": cl.get("logs/DEVIATIONS.md")}
recon["closure_version_is_prefix_of_current"] = any(hashlib.sha256(dev[:i]).hexdigest() == recon["closure_manifest_hash"] for i in range(len(dev) + 1) if i == len(dev) or dev[i - 1:i] == b"\n")
if OP:
    oz = zipfile.ZipFile(OP); o = oz.read("task05/logs/DEVIATIONS.md")
    recon["delivered_package_version_is_prefix_of_current"] = dev.startswith(o)
recon["append_only"] = recon["closure_version_is_prefix_of_current"] and recon.get("delivered_package_version_is_prefix_of_current", True)
rep["DEVIATIONS_reconciliation"] = recon
json.dump(rep, open(sys.argv[4] if len(sys.argv) > 4 else "/dev/stdout", "w"), indent=1)
