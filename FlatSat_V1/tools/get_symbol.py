#!/usr/bin/env python3
"""Print a KiCad 10 lib_symbols entry for "Lib:Name", flattened and ready to paste
into a schematic's (lib_symbols ...) block, indented with two tabs like Eeschema does.

Search order (first hit wins), unless --from restricts it:
  1. schematics that already embed the symbol (this project's sheets, then the
     upgraded reference schematics listed in --sch-dirs)
  2. the KiCad 10 standard libraries  (/Applications/KiCad/.../SharedSupport/symbols/<Lib>.kicad_sym)
  3. the user's global easyeda2kicad library and this project's sym-lib-table libraries

Derived library symbols ((extends "Parent")) are flattened: the parent body is used
with the child's properties overlaid and unit names renamed, which is exactly what
Eeschema stores in a schematic's lib_symbols cache.

Usage:
  get_symbol.py "Device:R"                      # print the block
  get_symbol.py "Transistor_FET:IRF7404" --where # only say where it was found
  get_symbol.py "batteryboard-rescue:R5460N233AF-symbols" --rename "flatsat:R5460N208AA"
  get_symbol.py --list-embedded FILE.kicad_sch   # list symbols a schematic embeds
Options:
  --from PATH        only search this .kicad_sch or .kicad_sym file
  --sch-dirs D1,D2   extra directories to scan for *.kicad_sch (recursively)
  --rename NEW       emit the block under a different "Lib:Name"
"""
import argparse
import glob
import os
import re
import sys

KICAD_SYMS = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DEFAULT_SCH_DIRS = [PROJ]
EXTRA_LIBS = [os.path.expanduser('~/Documents/KiCad/easyeda2kicad/easyeda2kicad.kicad_sym')]


# ---------- S-expression parse / print ----------
def parse(text):
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack = [[]]
    for t in tokens:
        if t == '(':
            stack.append([])
        elif t == ')':
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(t)  # keep quotes as-is so we can re-emit verbatim
    return stack[0]


def head(n):
    return n[0] if isinstance(n, list) and n and isinstance(n[0], str) else None


def unq(s):
    return s[1:-1] if isinstance(s, str) and len(s) >= 2 and s[0] == '"' and s[-1] == '"' else s


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


INLINE = {'at', 'xy', 'size', 'width', 'type', 'offset', 'number', 'name', 'length', 'color', 'font', 'justify',
          'hide', 'show_name', 'do_not_autoplace', 'exclude_from_sim', 'in_bom', 'on_board', 'in_pos_files',
          'duplicate_pin_numbers_are_jumpers', 'power', 'extends', 'embedded_fonts', 'unit', 'version',
          'generator', 'generator_version', 'uuid', 'fill', 'stroke', 'pin_numbers', 'pin_names', 'radius',
          'start', 'mid', 'end', 'center', 'diameter', 'thickness', 'bold', 'italic', 'face', 'href', 'alternate'}


def emit(node, indent=0, out=None):
    """Pretty-print close to Eeschema style: atoms of a node on one line, list children on new lines."""
    if out is None:
        out = []
    tab = '\t' * indent
    if not isinstance(node, list):
        out.append(tab + node)
        return out
    atoms = [c for c in node if not isinstance(c, list)]
    lists = [c for c in node if isinstance(c, list)]
    # short leaf nodes on one line
    if not lists:
        out.append(tab + '(' + ' '.join(atoms) + ')')
        return out
    # nodes whose children are all tiny leaves (e.g. (font (size 1.27 1.27))) -> still multi-line like KiCad
    out.append(tab + '(' + ' '.join(atoms))
    for c in lists:
        emit(c, indent + 1, out)
    out.append(tab + ')')
    return out


def render(node, indent=2):
    return '\n'.join(emit(node, indent))


# ---------- finders ----------
def symbols_in_sch(path):
    text = open(path, encoding='utf-8', errors='replace').read()
    i = text.find('(lib_symbols')
    if i < 0:
        return {}
    depth = 0
    j = i
    while True:
        ch = text[j]
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                break
        j += 1
    tree = parse(text[i:j + 1])[0]
    return {unq(s[1]): s for s in tree[1:] if head(s) == 'symbol'}


def symbols_in_lib(path):
    text = open(path, encoding='utf-8', errors='replace').read()
    tree = parse(text)[0]
    return {unq(s[1]): s for s in tree[1:] if head(s) == 'symbol'}


def flatten(name, lib):
    """Return a flattened copy of lib[name] (resolving extends), or None."""
    s = lib.get(name)
    if s is None:
        return None
    ext = next((c for c in s if isinstance(c, list) and head(c) == 'extends'), None)
    if not ext:
        return s
    parent = flatten(unq(ext[1]), lib)
    if parent is None:
        raise SystemExit('parent %s of %s not found' % (unq(ext[1]), name))
    import copy
    out = copy.deepcopy(parent)
    out[1] = q(name)
    pname = unq(parent[1])
    # overlay properties
    child_props = {unq(c[1]): c for c in s if isinstance(c, list) and head(c) == 'property'}
    new = []
    seen = set()
    for c in out[2:]:
        if isinstance(c, list) and head(c) == 'property':
            pn = unq(c[1])
            if pn in child_props:
                new.append(child_props[pn])
                seen.add(pn)
                continue
        if isinstance(c, list) and head(c) == 'symbol':
            c[1] = q(unq(c[1]).replace(pname, name, 1))
        new.append(c)
    for pn, c in child_props.items():
        if pn not in seen:
            # insert extra child properties after the last property
            idx = max((i for i, x in enumerate(new) if isinstance(x, list) and head(x) == 'property'), default=-1)
            new.insert(idx + 1, c)
    # other child-level flags (e.g. exclude_from_sim/in_bom) override the parent's
    for c in s[2:]:
        if isinstance(c, list) and head(c) in ('exclude_from_sim', 'in_bom', 'on_board', 'in_pos_files', 'power'):
            for i, x in enumerate(new):
                if isinstance(x, list) and head(x) == head(c):
                    new[i] = c
    return [out[0], out[1]] + new


def prefix_names(sym, full):
    """Rename a library-format symbol "Name" to "Lib:Name" (sub-units keep bare names)."""
    import copy
    s = copy.deepcopy(sym)
    s[1] = q(full)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('symbol', nargs='?')
    ap.add_argument('--from', dest='src')
    ap.add_argument('--sch-dirs', default='')
    ap.add_argument('--rename')
    ap.add_argument('--where', action='store_true')
    ap.add_argument('--list-embedded')
    a = ap.parse_args()

    if a.list_embedded:
        for n in sorted(symbols_in_sch(a.list_embedded)):
            print(n)
        return 0
    if not a.symbol:
        ap.error('symbol required')
    full = a.symbol
    lib, _, bare = full.partition(':')

    found = None
    where = None
    sources = []
    if a.src:
        sources = [a.src]
    else:
        dirs = DEFAULT_SCH_DIRS + [d for d in a.sch_dirs.split(',') if d]
        for d in dirs:
            sources += sorted(glob.glob(os.path.join(d, '**', '*.kicad_sch'), recursive=True))
    for p in sources:
        if p.endswith('.kicad_sch'):
            syms = symbols_in_sch(p)
            if full in syms:
                found, where = syms[full], p
                break
        elif p.endswith('.kicad_sym'):
            syms = symbols_in_lib(p)
            if bare in syms:
                found, where = prefix_names(flatten(bare, syms), full), p
                break
    if found is None and not a.src:
        cand = [os.path.join(KICAD_SYMS, lib + '.kicad_sym')] + EXTRA_LIBS
        # project sym-lib-table
        slt = os.path.join(PROJ, 'sym-lib-table')
        if os.path.exists(slt):
            for m in re.finditer(r'\(lib \(name "([^"]+)"\)[^)]*\(uri "([^"]+)"\)', open(slt).read()):
                if m.group(1) == lib:
                    cand.insert(0, m.group(2).replace('${KIPRJMOD}', PROJ))
        for p in cand:
            if not os.path.exists(p):
                continue
            syms = symbols_in_lib(p)
            if bare in syms:
                found, where = prefix_names(flatten(bare, syms), full), p
                break
    if found is None:
        print('NOT FOUND: %s' % full, file=sys.stderr)
        return 1
    if a.where:
        print(where)
        return 0
    if a.rename:
        old = unq(found[1])
        found = prefix_names(found, a.rename)
        oldbare = old.partition(':')[2] or old
        newbare = a.rename.partition(':')[2] or a.rename
        for c in found:
            if isinstance(c, list) and head(c) == 'symbol':
                c[1] = q(unq(c[1]).replace(oldbare, newbare, 1))
    sys.stderr.write('# from %s\n' % where)
    print(render(found))
    return 0


if __name__ == '__main__':
    sys.exit(main())
