from pathlib import Path

def get_files(root_path):
    print("Getting files")
    root_folder = Path(root_path)
    files = []
    for subfolder in sorted(p for p in root_folder.iterdir() if p.is_dir()):
        for p in subfolder.rglob("*"):
            if p.is_file():
                files.append((subfolder.name, p))
    return files

def get_subfolder_file_counts(files):
    counts = {}
    for name, _ in files:
        counts[name] = counts.get(name, 0) + 1
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)

def get_largest_files(files, top_n=10):
    sized = [(name, p, p.stat().st_size) for name, p in files]
    sized.sort(key=lambda x: x[2], reverse=True)
    return sized[:top_n]

def print_subfolder_file_counts(results):
    for name, count in results:
        print(f"{name}: {count}")

def print_largest_files(results):
    for name, p, size in results:
        print(f"{name}/{p.name}: {size} bytes")

def main():
    files = get_files("rome_functions")
    print("1. Subfolder file counts")
    print("2. Show largest 10 files")
    choice = input("Select an analysis option: ")
    if choice == "1":
        results = get_subfolder_file_counts(files)
        print_subfolder_file_counts(results)
    elif choice == "2":
        results = get_largest_files(files)
        print_largest_files(results)
    else:
        print("Invalid option")

if __name__ == "__main__":
    main()
