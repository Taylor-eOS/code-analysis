import os

txt_dir = "rome_functions_analyzed"
c_dir = "early_exit_loops"

def extract_fun_name(c_path):
    with open(c_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    idx = content.find("FUN_")
    if idx == -1:
        return None
    paren_idx = content.find("(", idx)
    if paren_idx == -1:
        return None
    return content[idx:paren_idx].strip()

def main():
    skipped = []
    renamed = 0
    for entry in os.listdir(txt_dir):
        if not entry.lower().endswith(".txt"):
            continue
        base = os.path.splitext(entry)[0]
        c_path = os.path.join(c_dir, base + ".c")
        txt_path = os.path.join(txt_dir, entry)
        if not os.path.isfile(c_path):
            skipped.append((entry, "no matching .c file"))
            continue
        fun_name = extract_fun_name(c_path)
        if not fun_name:
            skipped.append((entry, "FUN_ name not found"))
            continue
        new_path = os.path.join(txt_dir, fun_name + ".txt")
        if os.path.exists(new_path):
            skipped.append((entry, f"target {fun_name}.txt already exists"))
            continue
        os.rename(txt_path, new_path)
        renamed += 1

    print(f"Renamed {renamed} files.")
    if skipped:
        print(f"Skipped {len(skipped)} files:")
        for name, reason in skipped:
            print(f"  {name}: {reason}")

if __name__ == "__main__":
    main()
