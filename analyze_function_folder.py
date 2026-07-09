from pathlib import Path

SHORT_FILE_LENGTH = 8

state = {
    "root_path": "rome_functions",
    "files": [],
    "results": None
}

def get_files():
    print("Getting files")
    root_folder = Path(state["root_path"])
    for subfolder in sorted(p for p in root_folder.iterdir() if p.is_dir()):
        for p in subfolder.rglob("*"):
            if p.is_file():
                state["files"].append((subfolder.name, p))

def get_subfolder_file_counts():
    counts = {}
    for name, _ in state["files"]:
        counts[name] = counts.get(name, 0) + 1
    state["results"] = sorted(counts.items(), key=lambda x: x[1], reverse=True)

def get_largest_files():
    sized = [(name, p, p.stat().st_size) for name, p in state["files"]]
    sized.sort(key=lambda x: x[2], reverse=True)
    state["results"] = sized[:10]

def get_short_file():
    short_files = []
    for name, p in state["files"]:
        try:
            with open(p, "r", encoding="utf-8") as f:
                if sum(1 for _ in f) < SHORT_FILE_LENGTH:
                    short_files.append(f"{name}/{p.name}")
        except Exception:
            pass
    state["results"] = short_files

def get_short_file_count():
    count = 0
    for _, p in state["files"]:
        try:
            with open(p, "r", encoding="utf-8") as f:
                if sum(1 for _ in f) < SHORT_FILE_LENGTH:
                    count += 1
        except Exception:
            pass
    state["results"] = count

def print_subfolder_file_counts():
    for name, count in state["results"]:
        print(f"{name}: {count}")

def print_largest_files():
    for name, p, size in state["results"]:
        print(f"{name}/{p.name}: {size} bytes")

def print_short_file_count():
    try:
        with open("short_functions.txt", "w", encoding="utf-8") as f:
            for item in state["results"]:
                f.write(f"{item}\n")
        print("Saved short functions to short_functions.txt")
    except Exception:
        pass

def main():
    get_files()
    print("1. Subfolder file counts")
    print("2. Show largest 10 files")
    print(f"3. Count files under {SHORT_FILE_LENGTH} lines")
    print(f"4. Save files under {SHORT_FILE_LENGTH} lines")
    choice = input("Select an analysis option: ")
    if choice == "1":
        get_subfolder_file_counts()
        print_subfolder_file_counts()
    elif choice == "2":
        get_largest_files()
        print_largest_files()
    elif choice == "3":
        get_short_file_count()
        print(f"Files under {SHORT_FILE_LENGTH} lines: {state['results']}")
    elif choice == "4":
        get_short_file()
        print_short_file_count()
    else:
        print("Invalid option")

if __name__ == "__main__":
    main()
