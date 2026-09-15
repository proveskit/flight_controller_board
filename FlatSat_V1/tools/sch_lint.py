#!/usr/bin/env python3
"""Structural lint for a hand-written KiCad 10 schematic sheet (.kicad_sch).

Checks things kicad-cli ERC does not report clearly, and that an agent writing
S-expressions by hand gets wrong most often:

  * balanced parentheses, expected header (version 20260306 / eeschema 10.0)
  * every (lib_id "X") used by a symbol instance has a (symbol "X" ...) in lib_symbols
  * every uuid is unique within the file
  * symbol / label / wire / junction coordinates sit on the 1.27 mm grid
  * every symbol instance carries an (instances (project "<PROJECT>" (path "<PATH>" ...)))
    block whose project and path match what was asked for
  * reference designators fall inside the allowed numeric block for this sheet
  * no duplicate reference designators inside the file
  * wire endpoints that touch nothing (dangling)  -- warning only
  * a symbol pin that no wire, label or other pin touches -- warning only

Usage:
  sch_lint.py SHEET.kicad_sch --project FlatSat_V1 --path /ROOT-UUID/SHEET-UUID \
      --refdes-block 200-299 [--strict]
Exit code 0 = no errors (warnings allowed unless --strict), 1 = errors.
"""
import argparse
import re
import sys
from collections import Counter, defaultdict

GRID = 1.27


def parse(text):
    """Minimal S-expression parser -> nested lists (strings kept quoted-stripped)."""
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack = [[]]
    for t in tokens:
        if t == '(':
            stack.append([])
        elif t == ')':
            node = stack.pop()
            if not stack:
                raise ValueError('unbalanced ) ')
            stack[-1].append(node)
        else:
            if t.startswith('"') and t.endswith('"') and len(t) >= 2:
                t = t[1:-1]
            stack[-1].append(t)
    if len(stack) != 1:
        raise ValueError('unbalanced ( : depth %d at EOF' % (len(stack) - 1))
    return stack[0]


def head(node):
    return node[0] if isinstance(node, list) and node and isinstance(node[0], str) else None


def find_all(node, name, depth=0, max_depth=99):
    out = []
    if isinstance(node, list):
        if head(node) == name:
            out.append(node)
        if depth < max_depth:
            for ch in node:
                if isinstance(ch, list):
                    out.extend(find_all(ch, name, depth + 1, max_depth))
    return out


def child(node, name):
    for ch in node:
        if isinstance(ch, list) and head(ch) == name:
            return ch
    return None


def children(node, name):
    return [ch for ch in node if isinstance(ch, list) and head(ch) == name]


def on_grid(v):
    q = v / GRID
    return abs(q - round(q)) < 1e-3


def fmt(x):
    return ('%.2f' % x).rstrip('0').rstrip('.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sheet')
    ap.add_argument('--project', required=True)
    ap.add_argument('--path', required=True, help='instances path, e.g. /ROOTUUID/SHEETUUID')
    ap.add_argument('--refdes-block', help='e.g. 200-299 (applies to every prefix)')
    ap.add_argument('--strict', action='store_true', help='warnings count as errors')
    ap.add_argument('--allow-offgrid', action='store_true')
    a = ap.parse_args()

    errors, warnings = [], []
    text = open(a.sheet, encoding='utf-8').read()
    try:
        tree = parse(text)
    except ValueError as e:
        print('ERROR: %s' % e)
        return 1
    if not tree or head(tree[0]) != 'kicad_sch':
        print('ERROR: file does not start with (kicad_sch')
        return 1
    root = tree[0]

    ver = child(root, 'version')
    if not ver or ver[1] != '20260306':
        errors.append('header: expected (version 20260306), got %s' % (ver[1] if ver else None))
    gen = child(root, 'generator_version')
    if not gen or gen[1] != '10.0':
        warnings.append('header: generator_version is %s, project uses "10.0"' % (gen[1] if gen else None))
    if not child(root, 'uuid'):
        errors.append('header: missing sheet (uuid ...)')
    if child(root, 'sheet_instances') and a.path != '/' + (child(root, 'uuid') or ['', ''])[1]:
        warnings.append('sub-sheet files in this project carry no (sheet_instances ...) block; only the root does')

    # lib_symbols coverage
    libs = child(root, 'lib_symbols') or ['lib_symbols']
    defined = {s[1] for s in children(libs, 'symbol')}
    instances = [s for s in children(root, 'symbol')]
    used = Counter()
    for s in instances:
        lid = child(s, 'lib_id')
        if lid:
            used[lid[1]] += 1
    for name in used:
        if name not in defined:
            errors.append('lib_id "%s" used %d× but has no definition in lib_symbols' % (name, used[name]))
    for name in defined:
        if name not in used:
            warnings.append('lib_symbols defines "%s" but no instance uses it' % name)

    # uuids
    uuids = Counter(u[1] for u in find_all(root, 'uuid'))
    for u, n in uuids.items():
        if n > 1:
            errors.append('uuid %s appears %d times' % (u, n))
    bad_uuid = [u for u in uuids if not re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', u)]
    for u in bad_uuid[:10]:
        errors.append('malformed uuid "%s"' % u)

    # grid checks on placed items
    def at_of(node):
        at = child(node, 'at')
        if not at:
            return None
        try:
            return float(at[1]), float(at[2])
        except (ValueError, IndexError):
            return None

    offgrid = []
    for kind in ('symbol', 'label', 'global_label', 'hierarchical_label', 'junction', 'no_connect'):
        for it in children(root, kind):
            p = at_of(it)
            if p and not (on_grid(p[0]) and on_grid(p[1])):
                offgrid.append('%s at (%s, %s)' % (kind, fmt(p[0]), fmt(p[1])))
    wire_pts = []
    for w in children(root, 'wire'):
        pts = child(w, 'pts')
        if not pts:
            continue
        xy = [(float(x[1]), float(x[2])) for x in children(pts, 'xy')]
        wire_pts.append(xy)
        for p in xy:
            if not (on_grid(p[0]) and on_grid(p[1])):
                offgrid.append('wire endpoint (%s, %s)' % (fmt(p[0]), fmt(p[1])))
    if offgrid and not a.allow_offgrid:
        for o in offgrid[:25]:
            warnings.append('off-grid (1.27 mm): ' + o)
        if len(offgrid) > 25:
            warnings.append('... %d more off-grid items' % (len(offgrid) - 25))

    # instances / references
    refs = Counter()
    lo = hi = None
    if a.refdes_block:
        lo, hi = (int(x) for x in a.refdes_block.split('-'))
    for s in instances:
        ref_prop = None
        for p in children(s, 'property'):
            if len(p) > 2 and p[1] == 'Reference':
                ref_prop = p[2]
        lid = child(s, 'lib_id')
        lidn = lid[1] if lid else '?'
        inst = child(s, 'instances')
        if not inst:
            errors.append('symbol %s (%s) has no (instances ...) block' % (ref_prop, lidn))
            continue
        proj = child(inst, 'project')
        if not proj or proj[1] != a.project:
            errors.append('symbol %s: instances project is %s, expected "%s"' % (ref_prop, proj[1] if proj else None, a.project))
            continue
        path = child(proj, 'path')
        if not path or path[1] != a.path:
            errors.append('symbol %s: instances path is %s, expected "%s"' % (ref_prop, path[1] if path else None, a.path))
            continue
        ref = child(path, 'reference')
        refn = ref[1] if ref else None
        if refn is None:
            errors.append('symbol %s: instances block lacks (reference ...)' % ref_prop)
            continue
        if ref_prop and ref_prop != refn:
            warnings.append('symbol %s: Reference property "%s" differs from instances reference "%s" (instances wins in KiCad)' % (ref_prop, ref_prop, refn))
        is_power = lidn.startswith('power:') or refn.startswith('#')
        unit = child(path, 'unit')
        unitn = unit[1] if unit else '1'
        if not is_power:
            refs[(refn, unitn)] += 1
            m = re.fullmatch(r'([A-Za-z]+)(\d+)', refn)
            if not m:
                errors.append('reference "%s" is not annotated (must be PREFIX+number, no "?")' % refn)
            elif lo is not None and not (lo <= int(m.group(2)) <= hi):
                errors.append('reference "%s" outside allowed block %d-%d' % (refn, lo, hi))
    for (r, u), n in refs.items():
        if n > 1:
            errors.append('reference "%s" unit %s used by %d symbols' % (r, u, n))

    # dangling wire endpoints / untouched pins (approximate; uses pin positions from lib defs)
    endpoints = Counter()
    for xy in wire_pts:
        for p in xy:
            endpoints[(round(p[0], 2), round(p[1], 2))] += 1
    junctions = {(round(float(j[1][1]), 2), round(float(j[1][2]), 2)) for j in children(root, 'junction') if child(j, 'at')}
    label_pts = set()
    for kind in ('label', 'global_label', 'hierarchical_label', 'no_connect'):
        for it in children(root, kind):
            p = at_of(it)
            if p:
                label_pts.add((round(p[0], 2), round(p[1], 2)))

    # pin positions: transform lib pin (x,y) by symbol at/rotation/mirror
    import math
    libpins = {}
    for s in children(libs, 'symbol'):
        pins = []
        for sub in children(s, 'symbol'):
            for p in children(sub, 'pin'):
                at = child(p, 'at')
                num = child(p, 'number')
                if at:
                    pins.append((float(at[1]), float(at[2]), num[1] if num else '?'))
        libpins[s[1]] = pins
    pin_pts = Counter()
    pin_list = []
    for s in instances:
        lid = child(s, 'lib_id')
        at = child(s, 'at')
        if not lid or not at:
            continue
        x0, y0 = float(at[1]), float(at[2])
        rot = float(at[3]) if len(at) > 3 else 0.0
        mir = child(s, 'mirror')
        mir = mir[1] if mir else None
        ref_prop = next((p[2] for p in children(s, 'property') if len(p) > 2 and p[1] == 'Reference'), '?')
        for (px, py, num) in libpins.get(lid[1], []):
            # KiCad symbol coords: y up; schematic y down. Apply mirror, then rotation.
            x, y = px, -py
            if mir == 'x':
                y = -y
            elif mir == 'y':
                x = -x
            r = math.radians(rot)
            xr = x * math.cos(r) + y * math.sin(r)
            yr = -x * math.sin(r) + y * math.cos(r)
            gx, gy = round(x0 + xr, 2), round(y0 + yr, 2)
            pin_pts[(gx, gy)] += 1
            pin_list.append((ref_prop, num, (gx, gy)))
    for (pt, n) in endpoints.items():
        touched = n > 1 or pt in junctions or pt in label_pts or pin_pts.get(pt, 0) > 0
        if not touched:
            # a wire endpoint may also land mid-segment on another wire; check that
            mid = False
            for xy in wire_pts:
                for i in range(len(xy) - 1):
                    (x1, y1), (x2, y2) = xy[i], xy[i + 1]
                    if abs((x2 - x1) * (pt[1] - y1) - (y2 - y1) * (pt[0] - x1)) < 1e-3 and \
                       min(x1, x2) - 1e-3 <= pt[0] <= max(x1, x2) + 1e-3 and min(y1, y2) - 1e-3 <= pt[1] <= max(y1, y2) + 1e-3 and \
                       (round(x1, 2), round(y1, 2)) != pt and (round(x2, 2), round(y2, 2)) != pt:
                        mid = True
            if not mid:
                warnings.append('dangling wire endpoint at (%s, %s)' % (fmt(pt[0]), fmt(pt[1])))
    for (ref, num, pt) in pin_list:
        if ref.startswith('#'):
            continue
        if endpoints.get(pt, 0) == 0 and pt not in label_pts and pin_pts.get(pt, 0) < 2:
            warnings.append('pin %s.%s at (%s, %s) touches no wire/label/pin (needs a wire or a no_connect)' % (ref, num, fmt(pt[0]), fmt(pt[1])))

    for e in errors:
        print('ERROR:   ' + e)
    for w in warnings:
        print('WARNING: ' + w)
    print('%s: %d symbol instances, %d lib symbols, %d wires, %d errors, %d warnings' % (
        a.sheet, len(instances), len(defined), len(wire_pts), len(errors), len(warnings)))
    return 1 if errors or (a.strict and warnings) else 0


if __name__ == '__main__':
    sys.exit(main())
