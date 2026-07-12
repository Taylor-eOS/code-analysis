import os
import sys

LIST_PATH = "list.txt"
DEFAULT = "rome_functions_cut"
BASE_DIR = input(f"Directory ({DEFAULT}): ") or DEFAULT

def remove_listed_files():
    print(f"Checking list file at: {os.path.abspath(LIST_PATH)}")
    if not os.path.exists(LIST_PATH):
        print("Error: List file does not exist.")
        return
    print(f"Checking target directory at: {os.path.abspath(BASE_DIR)}")
    if not os.path.exists(BASE_DIR):
        print("Error: Target directory does not exist.")
        return
    with open(LIST_PATH, "r") as f:
        lines = f.readlines()
    print(f"Found {len(lines)} lines in the list file.")
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            print("Skipping empty line.")
            continue
        target_path = os.path.join(BASE_DIR, cleaned_line)
        print(f"Deleting: {target_path}")
        if os.path.exists(target_path):
            os.remove(target_path)
        else:
            print(f"File not found")

if __name__ == "__main__":
    remove_listed_files()
