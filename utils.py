import re

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

STRIP_RE = re.compile(
    r'"(?:\\.|[^"\\])*"'
    r"|'(?:\\.|[^'\\])*'"
    r"|//[^\n]*"
    r"|/\*.*?\*/",
    re.DOTALL
)

def _strip_replacement(m):
    matched = m.group(0)
    return "".join(c if c == "\n" else " " for c in matched)

def strip_comments_and_strings(text):
    return STRIP_RE.sub(_strip_replacement, text)

def compute_depths(clean):
    n = len(clean)
    depths = [0] * (n + 1)
    depth = 0
    for i in range(n):
        depths[i] = depth
        if clean[i] == "{":
            depth += 1
        elif clean[i] == "}":
            depth -= 1
    depths[n] = depth
    return depths

def matching_close(clean, open_pos):
    depth = 0
    n = len(clean)
    i = open_pos
    while i < n:
        if clean[i] == "{":
            depth += 1
        elif clean[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None

def matching_paren_close(clean, open_paren_pos):
    depth = 0
    n = len(clean)
    i = open_paren_pos
    while i < n:
        if clean[i] == "(":
            depth += 1
        elif clean[i] == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None

def match_definition_before_brace(clean, brace_pos):
    k = brace_pos - 1
    while k >= 0 and clean[k].isspace():
        k -= 1
    if k < 0 or clean[k] != ")":
        return None
    close_paren = k
    line_start = clean.rfind("\n", 0, close_paren) + 1
    if line_start >= close_paren or clean[line_start].isspace():
        return None
    paren_pos = matching_paren_open(clean, close_paren, line_start)
    if paren_pos is None:
        return None
    name_match = None
    for match in IDENT_RE.finditer(clean, line_start, paren_pos):
        name_match = match
    if name_match is None or name_match.end() != paren_pos:
        return None
    return (name_match.group(0), line_start)

def matching_paren_open(clean, close_paren_pos, lower_bound):
    depth = 0
    i = close_paren_pos
    while i >= lower_bound:
        if clean[i] == ")":
            depth += 1
        elif clean[i] == "(":
            depth -= 1
            if depth == 0:
                return i
        i -= 1
    return None

def find_functions(text):
    clean = strip_comments_and_strings(text)
    n = len(clean)
    depth = 0
    stack = []
    functions = []
    for i in range(n):
        c = clean[i]
        if c == "{":
            if depth == 0:
                entry = match_definition_before_brace(clean, i)
                stack.append(entry)
            else:
                stack.append(None)
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and stack:
                entry = stack.pop()
                if entry is not None:
                    name, decl_start = entry
                    functions.append((decl_start, i, name))
            elif stack:
                stack.pop()
    return functions
