STATE = {
    'path': 'Rome.c',
    'targets': ['0x30', '0x2c'],
    'stride': '0x180',
    'context_lines': 60,
    'stride_window': 5,
    'hits': [],
}

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
        rest = after[close_pos + 1:]
        stripped = rest.lstrip()
        if stripped.startswith('='):
            if len(stripped) > 1 and stripped[1] == '=':
                idx = pos + len(offset_token)
                continue
            return True
        idx = pos + len(offset_token)
    return False

def stride_in_window(lines, hit_idx, window):
    start = max(0, hit_idx - window)
    end = min(len(lines), hit_idx + window + 1)
    for i in range(start, end):
        if STATE['stride'] in lines[i]:
            return True, i
    return False, -1

def scan_file():
    with open(STATE['path'], 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    total = len(lines)
    for i, line in enumerate(lines):
        if i % 200000 == 0 and i > 0:
            print('scanned ' + str(i) + '/' + str(total) + ' lines, ' + str(len(STATE['hits'])) + ' hits so far')
        for token in STATE['targets']:
            if line_has_offset_write(line, token):
                found, stride_line = stride_in_window(lines, i, STATE['stride_window'])
                if found:
                    STATE['hits'].append((i + 1, token, line.rstrip(), stride_line + 1))
    STATE['total_lines'] = total

def write_regions():
    with open(STATE['path'], 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    total = len(lines)
    seen_targets = set()
    out = []
    for line_no, token, matched_line, stride_line_no in STATE['hits']:
        if line_no in seen_targets:
            continue
        seen_targets.add(line_no)
        region_start = min(line_no, stride_line_no)
        region_end = max(line_no, stride_line_no)
        start = max(0, region_start - STATE['context_lines'] - 1)
        end = min(total, region_end + STATE['context_lines'])
        out.append('\n' + '=' * 80 + '\n')
        out.append('// Offset write candidate at line ' + str(line_no) + ' (token ' + token + '), stride 0x180 found at line ' + str(stride_line_no) + ', showing lines ' + str(start + 1) + '-' + str(end) + '\n')
        out.append('// Matched line: ' + matched_line + '\n')
        out.append('=' * 80 + '\n\n')
        out.extend(lines[start:end])
    with open('offset_write_candidates.c', 'w', encoding='utf-8') as f:
        f.writelines(out)

def main():
    scan_file()
    print('total hits: ' + str(len(STATE['hits'])))
    write_regions()
    print('wrote offset_write_candidates.c')

if __name__ == '__main__':
    main()

