import re
import sys

STATE = {
    "path": None,
    "text": "",
    "results": [],
}

def load(path):
    STATE["path"] = path
    with open(path, "r", errors="replace") as f:
        STATE["text"] = f.read()

def get_func_bounds():
    starts = [m.start() for m in re.finditer(r"\n(void|uint|int|long|char|bool|undefined\w*)\s+FUN_[0-9a-fA-F]+", STATE["text"])]
    starts.append(len(STATE["text"]))
    return starts

def func_name_at(pos):
    chunk = STATE["text"][pos:pos + 200]
    m = re.match(r"\s*\S+\s+(FUN_[0-9a-fA-F]+[A-Za-z0-9_]*)", chunk)
    return m.group(1) if m else "UNKNOWN"

def scan():
    bounds = get_func_bounds()
    pattern = re.compile(
        r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\*\s*\(\s*(?:int|uint)\s*\*\s*\)\s*\(\s*DAT_0757cde0\s*\+\s*(0x[0-9a-fA-F]+)\s*\)"
    )
    cmp_pattern = re.compile(r"\b(\w+)\s*==\s*(\d+)\b")
    for i in range(len(bounds) - 1):
        start = bounds[i]
        end = bounds[i + 1]
        body = STATE["text"][start:end]
        fname = func_name_at(start)
        assigns = list(pattern.finditer(body))
        if not assigns:
            continue
        for am in assigns:
            varname = am.group(1)
            offset = am.group(2)
            line_no = body.count("\n", 0, am.start()) + 1
            for cm in cmp_pattern.finditer(body):
                if cm.group(1) == varname:
                    cline = body.count("\n", 0, cm.start()) + 1
                    const = int(cm.group(2))
                    if const <= 8:
                        STATE["results"].append((fname, offset, varname, cline, const))

def report():
    for fname, offset, varname, cline, const in STATE["results"]:
        print(fname + " offset=" + offset + " var=" + varname + " line=" + str(cline) + " cmp=" + str(const))

if __name__ == "__main__":
    load("Rome.c")
    scan()
    report()

