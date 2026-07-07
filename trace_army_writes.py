import re
import sys

STATE = {
    "path": None,
    "functions": [],
    "results": [],
}

def load_functions():
    with open(STATE["path"], "r", errors="replace") as f:
        text = f.read()
    blocks = re.split(r"\n\s*\n(?=void FUN_)", text)
    STATE["functions"] = [b for b in blocks if b.strip()]

def get_func_name(body):
    m = re.match(r"\s*void\s+(FUN_[0-9a-fA-F]+[A-Za-z0-9_]*)", body)
    return m.group(1) if m else "UNKNOWN"

def find_helper_assignments(body):
    pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*FUN_01358450[A-Za-z0-9_]*\s*\(")
    return set(pattern.findall(body))

def find_stores_through_vars(body, varnames):
    hits = []
    for var in varnames:
        pattern = re.compile(
            r"\*\s*\(\s*[A-Za-z0-9_ ]+\*\s*\)\s*\(\s*" + re.escape(var) +
            r"\s*\+\s*(0x[0-9a-fA-F]+)\s*\)\s*="
        )
        for m in pattern.finditer(body):
            line_no = body.count("\n", 0, m.start()) + 1
            hits.append((var, m.group(1), line_no, m.group(0)))
        pattern2 = re.compile(
            re.escape(var) + r"\s*\[\s*(0x[0-9a-fA-F]+|\d+)\s*\]\s*="
        )
        for m in pattern2.finditer(body):
            line_no = body.count("\n", 0, m.start()) + 1
            hits.append((var, m.group(1), line_no, m.group(0)))
    return hits

def scan():
    for body in STATE["functions"]:
        varnames = find_helper_assignments(body)
        if not varnames:
            continue
        hits = find_stores_through_vars(body, varnames)
        if hits:
            fname = get_func_name(body)
            STATE["results"].append((fname, hits))

def report():
    if not STATE["results"]:
        print("No stores found through FUN_01358450 result pointers.")
        return
    for fname, hits in STATE["results"]:
        print(fname)
        for var, offset, line_no, snippet in hits:
            print("  line %d, var %s, offset %s: %s" % (line_no, var, offset, snippet.strip()))

def main():
    STATE["path"] = "extracted_functions.c"
    load_functions()
    scan()
    report()

if __name__ == "__main__":
    main()

