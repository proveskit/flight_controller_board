#!/usr/bin/env python3
"""Report overlapping visible text, text drawn on top of wires or symbol bodies, and
anything placed outside the drawing frame, in a .kicad_sch.

Bounding boxes are estimated with the KiCad stroke-font metrics (advance ~0.95*size,
cap height ~size).  Symbol *fields* inherit the parent symbol's 90/270 rotation the way
SCH_FIELD::GetDrawRotation() does: a field whose stored angle is horizontal is drawn
vertical when the parent symbol transform is rotated 90 or 270 (and vice versa).

Checks
  text vs text        always
  text vs wire        --wires
  text vs symbol body --bodies   (a field drawn over *another* symbol's outline is a
                                  collision; over its own parent's outline it is INFO)
  page bounds         --page A3|A4 (default A3): every placed item must sit inside the
                                  frame, i.e. x 10..410, y 10..287 on A3, with the
                                  ruler band taken off by --margin (default 3 mm).
"""
import argparse
import math
import re
import sys

ADV = 0.87          # per-character advance, in units of text size (measured 0.834 against
                    # the KiCad 10 PDF plot: an 87-char 2.54 mm title spans 189.3 mm)
HEIGHT = 1.0        # cap height, in units of text size
PAD = 0.25          # extra margin per side (mm)

PAPER = {'A3': (420.0, 297.0), 'A4': (297.0, 210.0)}


def parse(text):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack = [[]]
    for t in toks:
        if t == '(':
            stack.append([])
        elif t == ')':
            stack[-2].append(stack.pop())
        else:
            if t.startswith('"') and t.endswith('"'):
                t = t[1:-1].replace('\\"', '"')
            stack[-1].append(t)
    return stack[0]


def head(n):
    return n[0] if isinstance(n, list) and n and isinstance(n[0], str) else None


def child(n, name):
    for c in n:
        if isinstance(c, list) and head(c) == name:
            return c
    return None


def children(n, name):
    return [c for c in n if isinstance(c, list) and head(c) == name]


def eff_of(node):
    e = child(node, 'effects')
    size, justify, hidden = 1.27, [], False
    h0 = child(node, 'hide')
    if h0 and h0[1] == 'yes':
        hidden = True
    if e:
        f = child(e, 'font')
        if f:
            s = child(f, 'size')
            if s:
                size = float(s[1])
        j = child(e, 'justify')
        if j:
            justify = [str(x) for x in j[1:]]
        h = child(e, 'hide')
        if h and h[1] == 'yes':
            hidden = True
    return size, justify, hidden


def box(s, x, y, angle, size, justify, extra=0.0):
    """Axis-aligned bbox of a stroke-font string drawn at (x, y)."""
    w = len(s) * size * ADV + extra
    h = size * HEIGHT
    hj = 'left'
    vj = 'center'
    for j in justify:
        if j in ('left', 'right'):
            hj = j
        if j in ('top', 'bottom'):
            vj = j
    # local coords: +u along reading direction, +v "up" on screen
    if hj == 'left':
        u0, u1 = 0.0, w
    elif hj == 'right':
        u0, u1 = -w, 0.0
    else:
        u0, u1 = -w / 2, w / 2
    if vj == 'bottom':
        v0, v1 = 0.0, h
    elif vj == 'top':
        v0, v1 = -h, 0.0
    else:
        v0, v1 = -h / 2, h / 2
    a = round(angle) % 360
    if a in (0, 180):
        bx0, bx1 = x + u0, x + u1
        by0, by1 = y - v1, y - v0
    else:
        # vertical text: reading direction is -y on screen
        bx0, bx1 = x - v1, x - v0
        by0, by1 = y - u1, y - u0
    return (bx0 - PAD, by0 - PAD, bx1 + PAD, by1 + PAD)


def overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def sym_xform(x0, y0, rot, mir):
    """Return f(lx, ly) -> (x, y): library coords (y up) to sheet coords (y down)."""
    r = math.radians(rot)

    def f(px, py):
        x, y = px, -py
        if mir == 'x':
            y = -y
        elif mir == 'y':
            x = -x
        xr = x * math.cos(r) + y * math.sin(r)
        yr = -x * math.sin(r) + y * math.cos(r)
        return (x0 + xr, y0 + yr)
    return f


def lib_body_shapes(libs):
    """lib_id -> list of point lists, one per graphic primitive (pins excluded)."""
    out = {}
    for s in children(libs, 'symbol'):
        shapes = []
        for sub in [s] + children(s, 'symbol'):
            for g in sub:
                if not isinstance(g, list):
                    continue
                k = head(g)
                if k == 'rectangle':
                    a, b = child(g, 'start'), child(g, 'end')
                    if a and b:
                        shapes.append([(float(a[1]), float(a[2])),
                                       (float(b[1]), float(b[2]))])
                elif k == 'circle':
                    c, r = child(g, 'center'), child(g, 'radius')
                    if c and r:
                        cx, cy, rr = float(c[1]), float(c[2]), float(r[1])
                        shapes.append([(cx - rr, cy - rr), (cx + rr, cy + rr)])
                elif k in ('polyline', 'arc', 'bezier'):
                    pts = child(g, 'pts')
                    p = []
                    if pts:
                        p = [(float(c[1]), float(c[2])) for c in pts if head(c) == 'xy']
                    for nm in ('start', 'mid', 'end'):
                        c = child(g, nm)
                        if c:
                            p.append((float(c[1]), float(c[2])))
                    if p:
                        shapes.append(p)
        out[s[1]] = shapes
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sheet')
    ap.add_argument('--wires', action='store_true', help='also report text drawn across wires')
    ap.add_argument('--bodies', action='store_true',
                    help='also report text drawn across another symbol\'s body outline')
    ap.add_argument('--page', default='A3', choices=sorted(PAPER))
    ap.add_argument('--margin', type=float, default=3.0,
                    help='extra keep-out inside the 10 mm frame for the ruler band (mm)')
    ap.add_argument('--no-page-check', action='store_true')
    ap.add_argument('--region', nargs=4, type=float, metavar=('X0', 'Y0', 'X1', 'Y1'),
                    help='list every item whose bbox touches this rectangle, then exit')
    a = ap.parse_args()
    root = parse(open(a.sheet, encoding='utf-8').read())[0]

    items = []   # (label, string, bbox)
    bodies = []  # (ref, bbox)
    wires = []
    points = []  # (what, x, y) for the page-bounds check

    for w in children(root, 'wire') + children(root, 'polyline'):
        pts = child(w, 'pts')
        xy = [c for c in pts if head(c) == 'xy']
        for i in range(len(xy) - 1):
            wires.append((float(xy[i][1]), float(xy[i][2]),
                          float(xy[i + 1][1]), float(xy[i + 1][2])))
        for c in xy:
            points.append(('wire', float(c[1]), float(c[2])))
    for j in children(root, 'junction') + children(root, 'no_connect'):
        at = child(j, 'at')
        points.append((head(j), float(at[1]), float(at[2])))

    for t in children(root, 'text'):
        s = t[1]
        at = child(t, 'at')
        size, justify, hidden = eff_of(t)
        if hidden:
            continue
        for i, line in enumerate(s.split('\n')):
            items.append(('text', line,
                          box(line, float(at[1]), float(at[2]) + i * size * 1.6,
                              float(at[3]), size, justify)))

    for kind in ('label', 'global_label', 'hierarchical_label'):
        for l in children(root, kind):
            s = l[1]
            at = child(l, 'at')
            size, justify, hidden = eff_of(l)
            if hidden:
                continue
            extra = 3.0 if kind != 'label' else 0.0
            items.append((kind, s, box(s, float(at[1]), float(at[2]), float(at[3]),
                                       size, justify, extra)))

    libs = child(root, 'lib_symbols')
    shapes = lib_body_shapes(libs) if libs else {}

    for sym in children(root, 'symbol'):
        at = child(sym, 'at')
        srot = float(at[3]) if len(at) > 3 else 0.0
        mirror = child(sym, 'mirror')
        mir = mirror[1] if mirror else None
        # SCH_FIELD::GetDrawRotation(): swap H/V when the symbol transform has y1 != 0
        flip = round(srot) % 180 == 90
        ref = None
        for p in children(sym, 'property'):
            if p[1] == 'Reference':
                ref = p[2]
        lid = child(sym, 'lib_id')
        f = sym_xform(float(at[1]), float(at[2]), srot, mir)
        for sh in shapes.get(lid[1] if lid else '', []):
            pts = [f(px, py) for (px, py) in sh]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            bb = (min(xs), min(ys), max(xs), max(ys))
            if bb[2] - bb[0] < 1e-6 and bb[3] - bb[1] < 1e-6:
                continue
            bodies.append((ref, bb))
            points.append(('body %s' % ref, bb[0], bb[1]))
            points.append(('body %s' % ref, bb[2], bb[3]))
        for p in children(sym, 'property'):
            name, val = p[1], p[2]
            if name not in ('Reference', 'Value') or not val:
                continue
            size, justify, hidden = eff_of(p)
            if hidden:
                continue
            pat = child(p, 'at')
            ang = float(pat[3]) if len(pat) > 3 else 0.0
            if flip:
                ang = (ang + 90) % 360
            # measured against the KiCad 10 PDF plot: a symbol rotated 90/180/270, or mirrored
            # in y, renders its fields with the horizontal justification swapped
            if flip or round(srot) % 360 == 180 or (mir == 'y'):
                justify = ['right' if j == 'left' else 'left' if j == 'right' else j
                           for j in justify] or ['right']
            items.append(('%s.%s' % (ref, name), val,
                          box(val, float(pat[1]), float(pat[2]), ang, size, justify)))

    for kind, s, b in items:
        points.append(('text %r' % s[:24], b[0], b[1]))
        points.append(('text %r' % s[:24], b[2], b[3]))

    if a.region:
        rx0, ry0, rx1, ry1 = a.region
        reg = (rx0, ry0, rx1, ry1)
        hits = 0
        for kind, s, b in items:
            if overlap(b, reg):
                hits += 1
                print('REGION text  %-16s %-40r %s' % (kind, s[:40], tuple(round(v, 2) for v in b)))
        for ref, b in bodies:
            if overlap(b, reg):
                hits += 1
                print('REGION body  %-16s %s' % (ref, tuple(round(v, 2) for v in b)))
        for (x1, y1, x2, y2) in wires:
            wb = (min(x1, x2) - 0.1, min(y1, y2) - 0.1, max(x1, x2) + 0.1, max(y1, y2) + 0.1)
            if overlap(wb, reg):
                hits += 1
                print('REGION wire  (%.2f,%.2f)-(%.2f,%.2f)' % (x1, y1, x2, y2))
        print('%d items touch region %s' % (hits, reg))
        return 0

    bad = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if overlap(items[i][2], items[j][2]):
                bad += 1
                print('TEXT-OVERLAP  %-18s %-34r  X  %-18s %-34r' %
                      (items[i][0], items[i][1], items[j][0], items[j][1]))
                print('              box1=%s box2=%s' %
                      (tuple(round(v, 2) for v in items[i][2]),
                       tuple(round(v, 2) for v in items[j][2])))
    if a.wires:
        for kind, s, b in items:
            if kind in ('label', 'global_label', 'hierarchical_label'):
                continue   # a label's anchor is meant to sit on its wire
            for (x1, y1, x2, y2) in wires:
                # sample the segment
                n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.3))
                for k in range(n + 1):
                    px = x1 + (x2 - x1) * k / n
                    py = y1 + (y2 - y1) * k / n
                    if b[0] < px < b[2] and b[1] < py < b[3]:
                        bad += 1
                        print('TEXT-ON-WIRE  %-18s %-34r  wire (%.2f,%.2f)-(%.2f,%.2f)' %
                              (kind, s, x1, y1, x2, y2))
                        break
                else:
                    continue
                break
    if a.bodies:
        info = 0
        for kind, s, b in items:
            owner = kind.split('.')[0] if '.' in kind else None
            for ref, bb in bodies:
                if not overlap(b, bb):
                    continue
                if owner is not None and ref == owner:
                    info += 1
                    print('text-on-own-body (INFO)  %-16s %-28r body=%s' %
                          (kind, s, tuple(round(v, 2) for v in bb)))
                else:
                    bad += 1
                    print('TEXT-ON-BODY  %-18s %-34r  over %s body=%s' %
                          (kind, s, ref, tuple(round(v, 2) for v in bb)))
        if info:
            print('(%d text-over-own-symbol-body items, informational)' % info)
    if not a.no_page_check:
        w, h = PAPER[a.page]
        lo = 10.0 + a.margin
        x1, y1 = w - 10.0 - a.margin, h - 10.0 - a.margin
        seen = set()
        for what, px, py in points:
            if px < lo or py < lo or px > x1 or py > y1:
                key = (what, round(px, 2), round(py, 2))
                if key in seen:
                    continue
                seen.add(key)
                bad += 1
                print('OFF-PAGE      %-30s at (%.2f, %.2f)  frame keep-in x %.1f..%.1f y %.1f..%.1f'
                      % (what, px, py, lo, x1, lo, y1))
    print('%d collisions, %d text items, %d symbol bodies' % (bad, len(items), len(bodies)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
