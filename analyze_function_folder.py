from pathlib import Path

SHORT_FILE_LENGTH = 7 #min 6
LIST_FILE = "list.txt"
ROOT_PATH = "rome_functions"

def get_files(root_path):
    print("Getting files")
    files = []
    root_folder = Path(root_path)
    for subfolder in sorted(p for p in root_folder.iterdir() if p.is_dir()):
        for p in subfolder.rglob("*"):
            if p.is_file():
                files.append((subfolder.name, p))
    return files

def get_largest_files(files):
    sized = [(name, p, p.stat().st_size) for name, p in files]
    sized.sort(key=lambda x: x[2], reverse=True)
    return sized[:10]

def get_short_files(files):
    short_files = []
    for name, p in files:
        try:
            with open(p, "r", encoding="utf-8") as f:
                if sum(1 for _ in f) < SHORT_FILE_LENGTH:
                    short_files.append(f"{name}/{p.name}")
        except Exception:
            pass
    return short_files

def print_largest_files(largest_files):
    for name, p, size in largest_files:
        print(f"{name}/{p.name}: {size} bytes")

def save_short_file_count(short_files):
    try:
        with open(LIST_FILE, "w", encoding="utf-8") as f:
            for item in short_files:
                f.write(f"{item}\n")
        print(f"Saved short functions to {LIST_FILE}")
    except Exception:
        pass

def main():
    files = get_files(ROOT_PATH)
    print("1. Show largest 10 files")
    print(f"2. Count files under {SHORT_FILE_LENGTH} lines")
    print(f"3. Save list of files under {SHORT_FILE_LENGTH} lines")
    choice = input("Select analysis option: ")
    if choice == "1":
        print_largest_files(get_largest_files(files))
    elif choice == "2":
        short_files = get_short_files(files)
        print(f"Files under {SHORT_FILE_LENGTH} lines: {len(short_files)}")
    elif choice == "3":
        save_short_file_count(get_short_files(files))
    else:
        print("Invalid option")

if __name__ == "__main__":
    main()
