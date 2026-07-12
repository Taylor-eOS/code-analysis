import sys
import explore_functions

SEED_FILE = "list.txt"
OUTPUT_FILE = "related_functions.txt"

def load_seeds(path):
    print("Loading list")
    with open(path, "r") as f:
        names = [line.strip() for line in f if line.strip()]
    known = []
    unknown = []
    for name in names:
        if name in explore_functions.STATE["function_map"]:
            known.append(name)
        elif name.startswith("FUN_") and len(name) > 12 and name[12] == "_":
            base = name[:12]
            if base in explore_functions.STATE["function_map"]:
                known.append(base)
            else:
                unknown.append(name)
        else:
            found = None
            for key in explore_functions.STATE["function_map"]:
                if key.startswith("FUN_") and len(key) > 12 and key[12] == "_" and key[:12] == name:
                    found = key
                    break
            if found is not None:
                known.append(found)
            else:
                unknown.append(name)
    return known, unknown

def main():
    explore_functions.index_all_functions()
    seeds, unknown = load_seeds(SEED_FILE)
    if unknown:
        print(f"Warning: {len(unknown)} listed names not found in index:")
        for name in unknown:
            print(f"  {name}")
    if not seeds:
        print("No valid list found, aborting")
        sys.exit(1)
    seed_set = set(seeds)
    callers = set()
    callees = set()
    for name in seeds:
        for caller in explore_functions.get_callers(name):
            if caller not in seed_set and caller in explore_functions.STATE["function_map"]:
                callers.add(caller)
        for callee in explore_functions.get_callees(name):
            if callee not in seed_set and callee in explore_functions.STATE["function_map"]:
                callees.add(callee)
    with open(OUTPUT_FILE, "w") as out:
        out.write(f"Callers not yet listed ({len(callers)}):\n")
        for name in sorted(callers):
            out.write(f"{name}\n")
        out.write("\n")
        out.write(f"Callees not yet listed ({len(callees)}):\n")
        for name in sorted(callees):
            out.write(f"{name}\n")
    print(f"Wrote {len(callers)} callers and {len(callees)} callees to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
