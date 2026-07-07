SOURCE_FILE = "Rome.c"
LIST_FILE = "list.txt"
OUTPUT_FILE = "extracted_functions.c"

STATE = {"names": None, "lines": None, "starts": None}

def load_names():
    with open(LIST_FILE, "r") as f:
        STATE["names"] = set(line.strip() for line in f if line.strip())

def load_source():
    with open(SOURCE_FILE, "r") as f:
        STATE["lines"] = f.readlines()

def index_starts():
    starts = {}
    for i, line in enumerate(STATE["lines"]):
        idx = line.find("FUN_")
        if idx == -1 or "(" not in line:
            continue
        paren_idx = line.find("(", idx)
        name = line[idx:paren_idx]
        if name in STATE["names"] and name not in starts:
            starts[name] = i
    STATE["starts"] = starts

def find_block_end(start_idx):
    lines = STATE["lines"]
    n = len(lines)
    i = start_idx
    while i < n and not lines[i].startswith("{"):
        i += 1
    if i >= n:
        return None
    while i < n:
        if lines[i].startswith("}"):
            return i
        i += 1
    return None

def write_output():
    starts = STATE["starts"]
    lines = STATE["lines"]
    missing = STATE["names"] - set(starts.keys())
    written = 0
    with open(OUTPUT_FILE, "w") as f:
        for name in STATE["names"]:
            if name not in starts:
                continue
            end_idx = find_block_end(starts[name])
            if end_idx is None:
                missing.add(name)
                continue
            f.writelines(lines[starts[name]:end_idx + 1])
            f.write("\n\n")
            written += 1
    if missing:
        print("Missing functions not found in source:")
        for name in sorted(missing):
            print(name)
    print(f"Wrote {written} functions to {OUTPUT_FILE}")

def main():
    load_names()
    load_source()
    index_starts()
    write_output()

if __name__ == "__main__":
    main()

