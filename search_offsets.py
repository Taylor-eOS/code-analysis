#!/usr/bin/env python3
import re

with open('Rome.c', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
print(f"Loaded {len(lines)} lines")
targets = ['0xdc', '0xd0']
hits = []
for i, line in enumerate(lines):
    for t in targets:
        if t in line:
            hits.append(i)
            break
targets_label = ' or '.join(targets)
print(f"Found {len(hits)} lines containing {targets_label}")

def find_function_start(line_no):
    depth = 0
    i = line_no
    while i >= 0:
        stripped = lines[i].rstrip()
        depth += stripped.count('}') - stripped.count('{')
        if depth < 0 and stripped.endswith('{'):
            before_brace = stripped[:-1].strip()
            if '(' in before_brace and ')' in before_brace:
                if not re.match(r'^(if|for|while|switch|else)\s*\(', before_brace):
                    return i
        i -= 1
    return 0

def find_function_end(start):
    depth = 0
    for i in range(start, len(lines)):
        stripped = lines[i].rstrip()
        depth += stripped.count('{') - stripped.count('}')
        if depth <= 0:
            return i
    return len(lines) - 1

func_starts = set()
for h in hits:
    func_starts.add(find_function_start(h))
print(f"In {len(func_starts)} unique functions")
scored = []
for start in sorted(func_starts):
    end = find_function_end(start)
    func_lines = lines[start:end+1]
    func_text = ''.join(func_lines)
    first_line = func_lines[0].strip()[:120]
    reasons = [targets_label]
    score = 1
    field_map = {'+0x2c': 'killed', '+0x30': 'healed', '+0x1c': 'returned',
                 '+0x24': 'remaining', '+0x14': 'fled', '+0x28': 'captured'}
    for offset, name in field_map.items():
        if f'{offset})' in func_text or f' {offset})' in func_text:
            score += 1
            reasons.append(f'{offset}({name})')
    has_write = bool(re.search(r'\*\s*\([^)]*\*[^)]*\)\s*\([^+]*\+\s*(0x1c|0x30)\s*\)\s*=', func_text))
    if has_write:
        score += 2
        reasons.append('WRITE')
    if '*' in func_text and '/' in func_text:
        score += 1
        reasons.append('arithmetic')
    if '0x180' in func_text:
        score += 1
        reasons.append('0x180')
    scored.append((score, start, end, first_line, reasons, func_lines))
scored.sort(key=lambda x: x[0], reverse=True)
out_name = 'offset_search_functions.c'
with open(out_name, 'w', encoding='utf-8') as f:
    for score, start, end, first_line, reasons, func_lines in scored:
        f.write(f"// Score:{score} Line:{start+1}-{end+1} Reasons:{','.join(reasons)} First:{first_line}\n")
        for line in func_lines:
            stripped = line.rstrip()
            if stripped:
                f.write(stripped + '\n')
        f.write('\n')

print("Summary:")
for score, start, end, first_line, reasons, _ in scored:
    print(f"  Score {score} | Line {start+1}-{end+1} | {first_line[:100]}")
    print(f"    {', '.join(reasons)}")

print(f"\nWrote {len(scored)} functions to {out_name}")

