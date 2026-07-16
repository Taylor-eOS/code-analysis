import explore_functions

OUTPUT_FILE = "leaf_functions.txt"

def is_leaf(entry):
    for callee in entry["calls"]:
        if callee in explore_functions.STATE["function_map"]:
            return False
    return True

def main():
    explore_functions.index_all_functions()
    leaves = [name for name, entry in explore_functions.STATE["function_map"].items() if is_leaf(entry)]
    leaves.sort()
    with open(OUTPUT_FILE, "w") as out:
        out.write(f"Leaf functions ({len(leaves)}):\n")
        for name in leaves:
            out.write(f"{name}\n")
    print(f"Wrote {len(leaves)} leaf functions to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
