import re

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

def strip_comments_and_strings(text):
    result = list(text)
    n = len(text)
    in_line_comment = False
    in_block_comment = False
    in_string = False
    in_char = False
    i = 0
    while i < n:
        c = text[i]
        c2 = text[i:i + 2]
        if in_line_comment:
            if c == "\n":
                in_line_comment = False
            else:
                result[i] = " "
            i += 1
            continue
        if in_block_comment:
            if c2 == "*/":
                result[i] = " "
                result[i + 1] = " "
                in_block_comment = False
                i += 2
            else:
                if c != "\n":
                    result[i] = " "
                i += 1
            continue
        if in_string:
            if c == "\\" and i + 1 < n:
                result[i] = " "
                result[i + 1] = " "
                i += 2
                continue
            if c == '"':
                in_string = False
            else:
                result[i] = " "
            i += 1
            continue
        if in_char:
            if c == "\\" and i + 1 < n:
                result[i] = " "
                result[i + 1] = " "
                i += 2
                continue
            if c == "'":
                in_char = False
            else:
                result[i] = " "
            i += 1
            continue
        if c2 == "//":
            in_line_comment = True
            result[i] = " "
            result[i + 1] = " "
            i += 2
            continue
        if c2 == "/*":
            in_block_comment = True
            result[i] = " "
            result[i + 1] = " "
            i += 2
            continue
        if c == '"':
            in_string = True
            i += 1
            continue
        if c == "'":
            in_char = True
            i += 1
            continue
        i += 1
    return "".join(result)

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

def find_all_open_braces(clean, depths):
    n = len(clean)
    opens = []
    for i in range(n):
        if clean[i] == "{" and depths[i] == 0:
            opens.append(i)
    return opens

def find_definitions_at_column_zero(clean):
    definitions = []
    for m in re.finditer(r"(?m)^\S", clean):
        line_start = m.start()
        j = line_start
        while True:
            paren_pos = clean.find("(", j)
            if paren_pos == -1:
                break
            name_match = None
            for match in IDENT_RE.finditer(clean[line_start:paren_pos]):
                name_match = match
            if name_match is not None and name_match.end() + line_start == paren_pos:
                close_paren = matching_paren_close(clean, paren_pos)
                if close_paren is not None:
                    k = close_paren + 1
                    while k < len(clean) and clean[k].isspace():
                        k += 1
                    if k < len(clean) and clean[k] == "{":
                        name = name_match.group(0)
                        definitions.append((name, line_start, k))
                        break
            j = paren_pos + 1
    return definitions

def find_functions(text):
    clean = strip_comments_and_strings(text)
    depths = compute_depths(clean)
    defs = find_definitions_at_column_zero(clean)
    all_top_braces = find_all_open_braces(clean, depths)
    brace_to_def = {fbrace: (fname, fstart) for fname, fstart, fbrace in defs}
    functions = []
    for brace_pos in all_top_braces:
        entry = brace_to_def.get(brace_pos)
        close_pos = matching_close(clean, brace_pos)
        if close_pos is None:
            break
        if entry is not None:
            name, decl_start = entry
            functions.append((decl_start, close_pos, name))
    return functions
