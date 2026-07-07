import re

#target_lines = [
#    1932678, 1946839, 1966156, 1966164, 1966356, 2401516, 2942043,
#    3390095, 3390252, 3390272, 3390307, 3390315, 3390322, 3399003,
#    3503810, 3504779, 4211117, 4245245, 4245262, 4367427, 4367648,
#    4367666, 4391419, 4705597, 4709416, 4714714, 4714817, 4714957,
#    4715129, 4715215, 4715347, 4720620, 5575453, 6535029, 6535199,
#    6535235, 6943046, 6948036, 7181541, 7181629, 7181867, 7182656
#]
target_lines = [6373912]
context_lines = 100
with open('Rome.c', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
total_lines = len(lines)
extracted_regions = []
for target in sorted(set(target_lines)):
    start = max(0, target - context_lines - 1)
    end = min(total_lines, target + context_lines)
    extracted_regions.append(f"\n{'='*80}\n")
    extracted_regions.append(f"// Region around line {target} (lines {start+1}-{end})\n")
    extracted_regions.append(f"{'='*80}\n\n")
    extracted_regions.extend(lines[start:end])
with open('extracted_healing_related.c', 'w', encoding='utf-8') as f:
    f.writelines(extracted_regions)
print(f"Extracted {len(set(target_lines))} regions to 'extracted_healing_related.c'")
