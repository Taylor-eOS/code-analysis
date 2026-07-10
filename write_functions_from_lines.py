SOURCE_FILE = "Rome.c"
LINE_LIST_FILE = "line_list.txt"
OUTPUT_FILE = "extracted_functions.txt"
STATE = {"lines": None, "spans": None, "target_lines": None}

def load_source():
    with open(SOURCE_FILE, "r") as f:
        STATE["lines"] = f.readlines()

def load_target_lines():
    with open(LINE_LIST_FILE, "r") as f:
        STATE["target_lines"] = set(int(l.strip()) for l in f if l.strip())

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

def index_spans():
    lines = STATE["lines"]
    spans = []
    for i, line in enumerate(lines):
        if not line or line[0].isspace():
            continue
        idx = line.find("FUN_")
        if idx == -1 or "(" not in line or "=" in line or ";" in line:
            continue
        end = find_block_end(i)
        if end is None:
            continue
        spans.append((i, end))
    STATE["spans"] = spans

def find_containing_span(line_no):
    idx = line_no - 1
    for start, end in STATE["spans"]:
        if start <= idx <= end:
            return start, end
    return None

def write_output():
    lines = STATE["lines"]
    written_spans = set()
    missing = []
    written = 0
    with open(OUTPUT_FILE, "w") as f:
        for line_no in sorted(STATE["target_lines"]):
            span = find_containing_span(line_no)
            if span is None:
                missing.append(line_no)
                continue
            if span in written_spans:
                continue
            written_spans.add(span)
            start, end = span
            f.writelines(lines[start:end + 1])
            f.write("\n\n")
            written += 1
    if missing:
        print("Lines not contained in any known function:")
        for ln in missing:
            print(ln)
    print(f"Wrote {written} functions to {OUTPUT_FILE}")

def main():
    load_source()
    load_target_lines()
    index_spans()
    write_output()

if __name__ == "__main__":
    main()

