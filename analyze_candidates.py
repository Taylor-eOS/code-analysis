#!/usr/bin/env python3
import re
import os

STATE = {
    'path': 'Rome.c',
    'offsets_write': ['0x30', '0x1c'], #healed, returned
    'offsets_read': ['0x2c'], #killed
    'stride': '0x180',
    'stride_window': 3, #lines around write to find stride
    'context_lines': 80,
    'hits': [],
}

def extract_functions(lines):
    functions = {}
    current_func = None
    brace_depth = 0
    func_lines = []
    func_start = None
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if stripped.endswith('{') and not stripped.startswith('}') and not stripped.startswith('#'):
            if '(' in stripped and ')' in stripped and not stripped.startswith('if') and not stripped.startswith('for') and not stripped.startswith('while') and not stripped.startswith('switch'):
                if current_func is not None:
                    functions[func_start] = {
                        'start': func_start,
                        'end': i - 1,
                        'lines': func_lines,
                        'name': func_lines[0].strip() if func_lines else 'unknown'
                    }
                current_func = i
                func_start = i
                func_lines = [line]
                brace_depth = 1
                continue
        if current_func is not None:
            func_lines.append(line)
            brace_depth += stripped.count('{') - stripped.count('}')
            if brace_depth <= 0:
                functions[func_start] = {
                    'start': func_start,
                    'end': i,
                    'lines': func_lines,
                    'name': func_lines[0].strip() if func_lines else 'unknown'
                }
                current_func = None
                func_lines = []
    if current_func is not None:
        functions[func_start] = {
            'start': func_start,
            'end': len(lines) - 1,
            'lines': func_lines,
            'name': func_lines[0].strip() if func_lines else 'unknown'
        }
    return functions

def line_has_offset_write(line, offset_token):
    idx = 0
    while True:
        pos = line.find(offset_token, idx)
        if pos == -1:
            return False
        before = line[:pos]
        if not before.rstrip().endswith('+'):
            idx = pos + len(offset_token)
            continue
        after = line[pos + len(offset_token):]
        close_pos = after.find(')')
        if close_pos == -1:
            idx = pos + len(offset_token)
            continue
        rest = after[close_pos + 1:].lstrip()
        if rest.startswith('=') and not rest.startswith('=='):
            return True
        idx = pos + len(offset_token)

def function_has_stride(func_data):
    for line in func_data['lines']:
        if '0x180' in line:
            return True
    return False

def function_has_read_killed(func_data):
    for line in func_data['lines']:
        if '+ 0x2c)' in line or '+0x2c)' in line:
            return True
    return False

def function_has_percentage_math(func_data):
    text = ''.join(func_data['lines'])
    patterns = [
        r'\*\s*\d+\s*/\s*100',
        r'\*\s*100\s*/\s*\d+',
        r'/\s*100',
        r'\(\s*float\s*\)',
        r'\(\s*double\s*\)',
        r'\*\s*0\.\d+',
        r'\*\s*\w+\s*/\s*\w+',
    ]
    for pat in patterns:
        if re.search(pat, text):
            return True
    return False

def function_has_loop_over_units(func_data):
    text = ''.join(func_data['lines'])
    patterns = [
        r'0x180',
        r'(for|while|do)\s*\(',
        r'\+\=\s*0x180',
        r'\*\s*0x180',
    ]
    score = sum(1 for pat in patterns if re.search(pat, text))
    return score >= 2

def score_candidate(func_data):
    score = 0
    reasons = []
    has_write = False
    for offset in STATE['offsets_write']:
        for line in func_data['lines']:
            if line_has_offset_write(line, offset):
                has_write = True
                reasons.append(f"writes to +{offset}")
                break
        if has_write:
            break
    if has_write:
        score += 1
    if function_has_stride(func_data):
        score += 1
        reasons.append("has 0x180 stride")
    if function_has_read_killed(func_data):
        score += 1
        reasons.append("reads +0x2c (killed)")
    if function_has_percentage_math(func_data):
        score += 1
        reasons.append("percentage/ratio math")
    has_loop = function_has_loop_over_units(func_data)
    return score, reasons, has_loop

def scan_file():
    with open(STATE['path'], 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    print(f"Loaded {len(lines)} lines")
    print("Extracting functions...")
    functions = extract_functions(lines)
    print(f"Found {len(functions)} functions")
    candidates = {}
    for func_start, func_data in functions.items():
        for offset in STATE['offsets_write']:
            for line in func_data['lines']:
                if line_has_offset_write(line, offset):
                    if func_start not in candidates:
                        candidates[func_start] = func_data
                    break
            if func_start in candidates:
                break
    print(f"Functions with offset writes: {len(candidates)}")
    stride_filtered = {}
    for func_start, func_data in candidates.items():
        if function_has_stride(func_data):
            stride_filtered[func_start] = func_data
    print(f"Functions with stride + write: {len(stride_filtered)}")
    scored = []
    for func_start, func_data in stride_filtered.items():
        score, reasons, has_loop = score_candidate(func_data)
        scored.append((score, func_start, func_data, reasons, has_loop))
    scored.sort(key=lambda x: x[0], reverse=True)
    print(f"\n{'='*80}")
    print("RANKED CANDIDATES (score 0-4, +loop bonus)")
    print(f"{'='*80}\n")
    for score, func_start, func_data, reasons, has_loop in scored:
        func_name = func_data['name']
        if len(func_name) > 80:
            func_name = func_name[:80] + "..."
        loop_str = " +loop" if has_loop else ""
        print(f"Score {score}{loop_str} | Line {func_start+1} | {func_name}")
        print(f"  Reasons: {', '.join(reasons)}")
        print()
    with open(STATE['path'], 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    out = []
    seen = set()
    for score, func_start, func_data, reasons, has_loop in scored:
        if func_start in seen:
            continue
        seen.add(func_start)
        start = max(0, func_data['start'] - STATE['context_lines'])
        end = min(len(lines), func_data['end'] + STATE['context_lines'])
        out.append('\n' + '=' * 80 + '\n')
        out.append(f"// Score: {score}/4 {'+loop' if has_loop else ''}\n")
        out.append(f"// Reasons: {', '.join(reasons)}\n")
        out.append(f"// Function: {func_data['name']}\n")
        out.append(f"// Lines: {func_data['start']+1}-{func_data['end']+1}\n")
        out.append('=' * 80 + '\n\n')
        out.extend(lines[start:end])
    with open('healing_candidates_ranked.c', 'w', encoding='utf-8') as f:
        f.writelines(out)
    print(f"\nWrote {len(scored)} candidates to healing_candidates_ranked.c")
    high_scorers = [s for s in scored if s[0] >= 3]
    print(f"\nHigh-confidence candidates (score >= 3): {len(high_scorers)}")
    for score, func_start, func_data, reasons, has_loop in high_scorers:
        print(f"  Line {func_start+1}: {func_data['name'][:100]}")

if __name__ == '__main__':
    scan_file()

