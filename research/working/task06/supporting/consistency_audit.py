"""Task 06 consistency audit (deterministic text checks). Usage: python3 consistency_audit.py TASK06_DIR"""
import glob, json, os, re, sys
D = sys.argv[1]
docs = {os.path.basename(p).split("-")[1]: open(p).read() for p in glob.glob(os.path.join(D, "task06-D*.md"))}
heads = {k: set(re.findall(r"^#{2,3} (\d+(?:\.\d+)?)[. ]", t, re.M)) for k, t in docs.items()}
allt = {os.path.basename(p): open(p).read() for p in glob.glob(os.path.join(D, "task06-*.md"))}
res = {"broken_section_refs": [], "undefined_OD": [], "stale_terms": [], "em_dashes": {}, "open_items": []}
for f, t in allt.items():
    for d, sec in re.findall(r"\b(D[1-6]) §(\d+(?:\.\d+)?)", t):
        if sec not in heads.get(d, set()):
            res["broken_section_refs"].append((f, d, sec))
    own = os.path.basename(f).split("-")[1]
    if own in ("D1", "D2", "D3", "D4"):
        for m in re.finditer(r"(?<!D[1-6] )§(\d+(?:\.\d+)?)", t):
            s = m.group(1)
            if s not in heads[own] and not re.search(r"(Task|T0|S\d|closure|A1|E1|record|review|spec|S6|item)\s*\S*\s*$", t[max(0, m.start()-25):m.start()]):
                res["broken_section_refs"].append((f, own + "(self)", s))
    if "—" in t:
        res["em_dashes"][f] = t.count("—")
d5 = docs["D5"]
defined = set(re.findall(r"^\| \**(OD-\d\d)\b", d5, re.M))
for f, t in allt.items():
    for od in set(re.findall(r"OD-\d\d", t)) - defined:
        res["undefined_OD"].append((f, od))
    for term in ("H1c", "H2c", "Holm", "97.5% interval", "confidence rating (1–3)"):
        n = t.count(term) - len(re.findall(r"(?:renamed from|replace|replacing|r1)[^|\n]{0,40}" + re.escape(term), t))
        if n > 0 and f != "task06-CHANGELOG.md":
            res["stale_terms"].append((f, term, n))
    for od in re.findall(r"OPEN[^\n]{0,12}(OD-\d\d)", t):
        if od not in ("OD-14",):
            res["stale_terms"].append((f, "OPEN " + od, 1))
    for m in re.finditer(r"OPEN[^\n]{0,40}", t):
        res["open_items"].append((f, m.group(0)[:50]))
res["OD_defined"] = sorted(defined)
print(json.dumps(res, indent=1, ensure_ascii=False))
