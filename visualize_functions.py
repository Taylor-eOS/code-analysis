SOURCE_FILE = "Rome.c"
STATE = {"lines": None, "buckets": [False] * 100}

def load_source():
    with open(SOURCE_FILE, "r") as f:
        STATE["lines"] = f.readlines()

def analyze_functions():
    lines = STATE["lines"]
    total_lines = len(lines)
    if total_lines == 0:
        return
    for i, line in enumerate(lines):
        if not line or line[0].isspace():
            continue
        idx = line.find("FUN_")
        if idx == -1 or "(" not in line or "=" in line or ";" in line:
            continue
        name_end = line.find("(", idx)
        name = line[idx:name_end].strip()
        if len(name) > 12:
            bucket_idx = int((i / total_lines) * 100)
            if bucket_idx >= 100:
                bucket_idx = 99
            STATE["buckets"][bucket_idx] = True

def draw_visualization():
    bar = "["
    for bucket in STATE["buckets"]:
        if bucket:
            bar += "\033[91m█\033[0m"
        else:
            bar += "\033[97m█\033[0m"
    bar += "]"
    print("Codebase distribution (Red: Renamed, White: Unmodified)")
    print("0% " + bar + " 100%")

def main():
    load_source()
    analyze_functions()
    draw_visualization()

if __name__ == "__main__":
    main()
