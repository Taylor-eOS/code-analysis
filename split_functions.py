import os
from utils import find_function_boundaries

SOURCE_FILE = input("Input file: ")
OUTPUT_DIR = os.path.splitext(SOURCE_FILE)[0].lower() + "_functions"
STATE = {"lines": None, "starts": [], "ends": [], "reported_dirs": set()}

def load_source():
    print("Loading source")
    with open(SOURCE_FILE, "r") as f:
        STATE["lines"] = f.readlines()

def find_ends():
    lines = STATE["lines"]
    ends = []
    for start in STATE["starts"]:
        end = start
        for i in range(start, len(lines)):
            if lines[i].rstrip() == "}":
                end = i
                break
        ends.append(end)
    STATE["ends"] = ends

def write_functions():
    lines = STATE["lines"]
    starts = STATE["starts"]
    ends = STATE["ends"]
    for start, end in zip(starts, ends):
        line = lines[start]
        idx = line.find("FUN_")
        name_end = line.find("(", idx)
        name = line[idx:name_end].strip()
        suffix = name[4:7] if len(name) >= 6 else name[4:]
        sub_dir = os.path.join(OUTPUT_DIR, suffix)
        if sub_dir not in STATE["reported_dirs"]:
            print(f"Writing {sub_dir}")
            STATE["reported_dirs"].add(sub_dir)
        os.makedirs(sub_dir, exist_ok=True)
        out_path = os.path.join(sub_dir, name + ".c")
        with open(out_path, "w") as f:
            f.writelines(lines[start:end + 1])

def main():
    load_source()
    STATE["starts"] = find_function_boundaries(STATE["lines"])
    find_ends()
    write_functions()
    print(f"Wrote {len(STATE['starts'])} functions")

if __name__ == "__main__":
    main()
