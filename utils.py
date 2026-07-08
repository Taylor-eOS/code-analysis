
def extract_function_name(lines, start):
    line = lines[start]
    idx = line.find("FUN_")
    if idx == -1:
        return None, start
    end = idx
    while end < len(line) and (line[end].isalnum() or line[end] == "_"):
        end += 1
    name = line[idx:end]
    return name, start

def find_function_boundaries(lines):
    boundaries = []
    for i, line in enumerate(lines):
        if not line or line[0].isspace():
            continue
        idx = line.find("FUN_")
        if idx == -1 or "=" in line or ";" in line:
            continue
        if "(" not in line:
            found = False
            for j in range(i + 1, min(i + 5, len(lines))):
                stripped = lines[j].lstrip()
                if stripped.startswith("//") or stripped.startswith("/*"):
                    continue
                if "=" in lines[j] or ";" in lines[j]:
                    break
                if "(" in lines[j]:
                    found = True
                    break
            if not found:
                continue
        boundaries.append(i)
    return boundaries

def find_function_boundaries_all(lines, fun_only=True):
    boundaries = []
    for i, line in enumerate(lines):
        if not line or line[0].isspace():
            continue
        if "(" not in line or "=" in line or ";" in line:
            continue
        idx = line.find("(")
        tokens = line[:idx].split()
        if len(tokens) < 2:
            continue
        name = tokens[-1].strip("*")
        if not name or not (name[0].isalpha() or name[0] == "_"):
            continue
        if name in KEYWORD_NAMES:
            continue
        if fun_only and "FUN_" not in name:
            continue
        boundaries.append((i, name))
    return boundaries
