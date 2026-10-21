"""schpins.py SHEET REF [REF...] : absolute pin endpoints of symbol instances (KiCad 10 s-expr, y down)."""
import re, sys, math


def sexp(s, i=0):
    """parse one s-expression starting at s[i] == '('; returns (list, next index)"""
    out = []
    i += 1
    while True:
        c = s[i]
        if c == '(':
            v, i = sexp(s, i); out.append(v)
        elif c == ')':
            return out, i + 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j = i + 1
            while s[j] != '"':
                j += 2 if s[j] == '\\' else 1
            out.append(s[i + 1:j]); i = j + 1
        else:
            j = i
            while not s[j].isspace() and s[j] not in '()':
                j += 1
            out.append(s[i:j]); i = j


def find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def pins_of(libsym):
    pins = []
    def walk(n):
        for x in n:
            if isinstance(x, list):
                if x and x[0] == 'pin':
                    at = find(x, 'at')[0]; ln = float(find(x, 'length')[0][1]); num = find(x, 'number')[0][1]
                    pins.append((num, float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0, ln))
                else:
                    walk(x)
    walk(libsym)
    return pins


def load(path):
    s = open(path).read()
    root, _ = sexp(s, s.index('('))
    libs = {x[1]: x for x in find(find(root, 'lib_symbols')[0], 'symbol')}
    out = {}
    for sym in find(root, 'symbol'):
        lib = find(sym, 'lib_id')[0][1]
        at = find(sym, 'at')[0]
        x, y, rot = float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0
        mir = find(sym, 'mirror')
        ref = None
        for inst in find(sym, 'instances'):
            for pr in find(inst, 'project'):
                for pa in find(pr, 'path'):
                    ref = find(pa, 'reference')[0][1]
        if ref is None:
            continue
        res = {}
        for num, px, py, pa, ln in pins_of(libs[lib]):
            # pin connection point is the pin's (at); lib coords are y-up
            qx, qy = px, -py
            if mir and mir[0][1] == 'x':
                qy = -qy
            if mir and mir[0][1] == 'y':
                qx = -qx
            r = math.radians(-rot)
            ax = x + qx * math.cos(r) - qy * math.sin(r)
            ay = y + qx * math.sin(r) + qy * math.cos(r)
            res[num] = (round(ax, 3), round(ay, 3))
        out[ref] = res
    return out


if __name__ == '__main__':
    d = load(sys.argv[1])
    for r in sys.argv[2:]:
        print(r, d.get(r))
