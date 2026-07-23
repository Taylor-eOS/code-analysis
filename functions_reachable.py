import explore_functions

OUTPUT_FILE = "leaf_reachability.txt"

def main():
    explore_functions.index_all_functions()
    all_functions = set(explore_functions.STATE["function_map"])
    total = len(all_functions)
    callees_of = {}
    for name in all_functions:
        callees_of[name] = set(c for c in explore_functions.get_callees(name) if c in all_functions)
    leaves = set(name for name in all_functions if not callees_of[name])
    reached = set(leaves)
    levels = [sorted(leaves)]
    frontier = leaves
    while frontier:
        next_frontier = set()
        for name in frontier:
            for caller in explore_functions.get_callers(name):
                if caller in all_functions and caller not in reached:
                    next_frontier.add(caller)
        if not next_frontier:
            break
        reached.update(next_frontier)
        levels.append(sorted(next_frontier))
        frontier = next_frontier
    unreached = sorted(all_functions - reached)
    with open(OUTPUT_FILE, "w") as out:
        out.write(f"Total functions: {total}\n")
        out.write(f"Leaf functions (level 0): {len(leaves)}\n")
        out.write(f"Reached total: {len(reached)} ({100.0 * len(reached) / total:.1f}% of codebase)\n")
        out.write(f"Levels: {len(levels)}\n\n")
        for i, level in enumerate(levels):
            out.write(f"Level {i} ({len(level)} functions):\n")
            for name in level:
                out.write(f"  {name}\n")
            out.write("\n")
        out.write(f"Never reached ({len(unreached)}):\n")
        for name in unreached:
            out.write(f"{name}\n")
    print(f"Total: {total}")
    print(f"Leaves: {len(leaves)}")
    print(f"Reached: {len(reached)} ({100.0 * len(reached) / total:.1f}%)")
    print(f"Levels: {len(levels)}")
    print(f"Never reached: {len(unreached)}")
    print(f"Wrote details to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
