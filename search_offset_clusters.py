#!/usr/bin/env python3
import sys

WINDOW = 100
TARGETS = ['DAT_0757cc40', 'DAT_0757cc48', 'DAT_0757cae0', 'DAT_0757cc18', 'DAT_0757cac8']

with open('Rome.c', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
total = len(lines)
scores = []
for i in range(0, total, WINDOW):
    chunk = ''.join(lines[i:i+WINDOW])
    found = [t for t in TARGETS if t in chunk]
    if found:
        scores.append((len(found), i, found))
scores.sort(key=lambda x: x[0], reverse=True)
with open('dense_offset_windows.c', 'w') as out:
    for count, start, found in scores:
        end = min(total, start + WINDOW)
        unique = list(set(f.replace('+ ','+').replace(')','') for f in found))
        out.write(f"// Window lines {start+1}-{end}: {count} hits, offsets: {', '.join(sorted(unique))}\n")
        for j in range(start, end):
            stripped = lines[j].rstrip()
            if stripped:
                out.write(stripped + '\n')
        out.write('\n')
print(f"Scanned {total} lines in {WINDOW}-line windows")
print(f"Windows with hits: {len(scores)}")
print(f"Top 10 windows:")
for count, start, found in scores[:10]:
    unique = list(set(f.replace('+ ','+').replace(')','') for f in found))
    print(f"  Lines {start+1}-{start+WINDOW}: {count} hits, offsets: {', '.join(sorted(unique))}")
print(f"\nOutput written to dense_offset_windows.c")

