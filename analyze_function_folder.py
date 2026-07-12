from pathlib import Path

SHORT_FILE_LENGTH = 7 #min 6
LIST_FILE = "list.txt"
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

def get_largest_files():
    sized = [(name, p, p.stat().st_size) for name, p in state["files"]]
    sized.sort(key=lambda x: x[2], reverse=True)
    state["results"] = sized[:10]

def get_short_files():
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
    get_short_files()
    state["results"] = len(state["results"])

def print_largest_files():
    for name, p, size in state["results"]:
        print(f"{name}/{p.name}: {size} bytes")

def save_short_file_count():
    try:
        with open(LIST_FILE, "w", encoding="utf-8") as f:
            for item in state["results"]:
                f.write(f"{item}\n")
        print(f"Saved short functions to {LIST_FILE}")
    except Exception:
        pass

def main():
    get_files()
    print("1. Show largest 10 files")
    print(f"2. Count files under {SHORT_FILE_LENGTH} lines")
    print(f"3. Save list of files under {SHORT_FILE_LENGTH} lines")
    choice = input("Select analysis option: ")
    if choice == "1":
        get_largest_files()
        print_largest_files()
    elif choice == "2":
        get_short_file_count()
        print(f"Files under {SHORT_FILE_LENGTH} lines: {state['results']}")
    elif choice == "3":
        get_short_files()
        save_short_file_count()
    else:
        print("Invalid option")

if __name__ == "__main__":
    main()
