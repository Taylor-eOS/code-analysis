STATE = {
    "file_name": "Rome.c",
    "output_name": "healing_candidates.txt",
    "file_lines": [],
    "hits": []
}
OFFSET_TERMS = ["0x470", "0x141c0", "0x14170", "0x14180", "0x14448"]
LOOP_TERMS = ["while", "for "]
BREAK_TERMS = ["break", "goto"]
WINDOW = 40

def load_file():
    with open(STATE["file_name"], "r", encoding="utf-8", errors="ignore") as f:
        STATE["file_lines"] = f.readlines()

def scan():
    lines = STATE["file_lines"]
    n = len(lines)
    for i, line in enumerate(lines):
        if any(term in line for term in OFFSET_TERMS):
            start = max(0, i - WINDOW)
            end = min(n, i + WINDOW)
            window_lines = lines[start:end]
            window_text = "".join(window_lines)
            has_loop = any(term in window_text for term in LOOP_TERMS)
            has_break = any(term in window_text for term in BREAK_TERMS)
            if has_loop and has_break:
                STATE["hits"].append(i + 1)

def save_results():
    seen = set()
    merged = []
    for line_num in STATE["hits"]:
        if line_num not in seen:
            seen.add(line_num)
            merged.append(line_num)
    merged.sort()
    with open(STATE["output_name"], "w", encoding="utf-8") as f:
        f.write(f"Found {len(merged)} hits\n\n")
        for line_num in merged:
            start = max(0, line_num - 6)
            end = min(len(STATE["file_lines"]), line_num + 4)
            f.write(f"line {line_num}\n")
            f.write("```\n")
            for i in range(start, end):
                f.write(STATE["file_lines"][i])
            f.write("```\n\n")
    print(f"Found {len(merged)} hits, written to {STATE['output_name']}")

if __name__ == "__main__":
    load_file()
    scan()
    save_results()

