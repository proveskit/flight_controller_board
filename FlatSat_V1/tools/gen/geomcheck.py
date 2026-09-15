#!/usr/bin/env python3
"""Geometric readability check for a KiCad 10 .kicad_sch sheet.

Reports every place a wire segment passes through the drawn body of a piece of
text (global label hexagon, local label, free text block, visible symbol field)
and every place two text bodies overlap.

Metrics follow KiCad's own label geometry:
  * label box expansion  margin = 0.375 * text size          (GetLabelBoxExpansion)
  * global label body    w = text_w + 2*margin + box_h ,  h = size + 2*margin
  * stroke font advance  ~0.95 em per character (conservative: real is ~0.90)

Usage: geomcheck.py SHEET.kicad_sch [--verbose]
"""
import argparse
import math
import re
import sys

ADV = 0.95          # em per character, conservative
LINE = 1.62         # line pitch used by the generator for multi-line (text) blocks


def parse(text):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack = [[]]
    for t in toks:
        if t == '(':
            stack.append([])
        elif t == ')':
            n = stack.pop()
            stack[-1].append(n)
        else:
            if t.startswith('"'):
                t = t[1:-1].replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
            stack[-1].append(t)
    return stack[0]


def head(n):
    return n[0] if isinstance(n, list) and n and isinstance(n[0], str) else None


def ch(node, name):
    for c in node:
        if isinstance(c, list) and head(c) == name:
            return c
    return None


def chs(node, name):
    return [c for c in node if isinstance(c, list) and head(c) == name]


def walk(node):
    """Depth-first over the sheet, skipping the (lib_symbols ...) subtree whose
    coordinates are library-relative, not sheet coordinates."""
    if isinstance(node, list):
        if head(node) == 'lib_symbols':
            return
        yield node
        for c in node:
            yield from walk(c)


def eff(node):
    """-> (size, justify_h, hidden)"""
    e = ch(node, 'effects')
    size, just, hidden = 1.27, None, False
    if e:
        f = ch(e, 'font')
        if f:
            s = ch(f, 'size')
            if s:
                size = float(s[2])
        j = ch(e, 'justify')
        if j:
            for tok in j[1:]:
                if tok in ('left', 'right', 'center'):
                    just = tok
        h = ch(e, 'hide')
        if h and h[1] == 'yes':
            hidden = True
    h2 = ch(node, 'hide')
    if h2 and h2[1] == 'yes':
        hidden = True
    return size, just, hidden


def text_w(s, size):
    return len(s) * ADV * size


class Box:
    def __init__(self, kind, label, x0, y0, x1, y1):
        self.kind, self.label = kind, label
        self.x0, self.y0, self.x1, self.y1 = min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)

    def __repr__(self):
        return '%s %r [%.2f,%.2f]-[%.2f,%.2f]' % (self.kind, self.label,
                                                 self.x0, self.y0, self.x1, self.y1)


def collect(root):
    boxes, wires = [], []
    for node in walk(root):
        h = head(node)
        if h == 'wire':
            pts = ch(node, 'pts')
            xy = chs(pts, 'xy')
            if len(xy) == 2:
                wires.append(((float(xy[0][1]), float(xy[0][2])),
                              (float(xy[1][1]), float(xy[1][2]))))
        elif h in ('global_label', 'hierarchical_label'):
            name = node[1]
            at = ch(node, 'at')
            x, y, rot = float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0
            size, just, _ = eff(node)
            m = 0.375 * size
            bh = size + 2 * m
            bw = text_w(name, size) + 2 * m + bh
            if rot in (0, 0.0):
                b = Box('glabel', name, x, y - bh / 2, x + bw, y + bh / 2)
            elif rot == 180:
                b = Box('glabel', name, x - bw, y - bh / 2, x, y + bh / 2)
            elif rot == 90:      # points up: text runs toward -y
                b = Box('glabel', name, x - bh / 2, y - bw, x + bh / 2, y)
            else:                # 270, points down
                b = Box('glabel', name, x - bh / 2, y, x + bh / 2, y + bw)
            boxes.append(b)
        elif h == 'label':
            name = node[1]
            at = ch(node, 'at')
            x, y, rot = float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0
            size, just, _ = eff(node)
            w, ht = text_w(name, size), size * 1.2
            # justify "<h> bottom": text sits above the anchor line
            if rot in (0, 0.0):
                b = Box('label', name, x, y - ht, x + w, y) if just != 'right' else \
                    Box('label', name, x - w, y - ht, x, y)
            elif rot == 180:
                b = Box('label', name, x - w, y - ht, x, y)
            elif rot == 90:
                b = Box('label', name, x, y - w, x + ht, y)
            else:
                b = Box('label', name, x, y, x + ht, y + w)
            boxes.append(b)
        elif h == 'text':
            body = node[1]
            at = ch(node, 'at')
            x, y = float(at[1]), float(at[2])
            size, just, _ = eff(node)
            lines = body.split('\n')
            w = max(text_w(l, size) for l in lines)
            ht = size * 1.2 if len(lines) == 1 else len(lines) * size * LINE
            boxes.append(Box('text', lines[0][:40], x, y - ht / 2, x + w, y + ht / 2))
        elif h == 'symbol':
            sat = ch(node, 'at')
            srot = float(sat[3]) if sat and len(sat) > 3 else 0.0
            for p in chs(node, 'property'):
                pname, pval = p[1], p[2]
                if pname not in ('Reference', 'Value'):
                    continue
                size, just, hidden = eff(p)
                if hidden or not pval:
                    continue
                at = ch(p, 'at')
                x, y = float(at[1]), float(at[2])
                ang = float(at[3]) if len(at) > 3 else 0
                w, ht = text_w(pval, size), size * 1.2
                # SCH_FIELD::GetDrawRotation() swaps horizontal/vertical for a symbol
                # whose own transform is rotated 90/270, so the drawn orientation is
                # the XOR of the field angle and the symbol rotation.
                drawn_vertical = (ang in (90, 270)) != (srot in (90, 270))
                if drawn_vertical:
                    if just == 'left':
                        b = Box('field', pval, x - ht / 2, y - w, x + ht / 2, y)
                    elif just == 'right':
                        b = Box('field', pval, x - ht / 2, y, x + ht / 2, y + w)
                    else:
                        b = Box('field', pval, x - ht / 2, y - w / 2, x + ht / 2, y + w / 2)
                else:
                    if just == 'left':
                        b = Box('field', pval, x, y - ht / 2, x + w, y + ht / 2)
                    elif just == 'right':
                        b = Box('field', pval, x - w, y - ht / 2, x, y + ht / 2)
                    else:
                        b = Box('field', pval, x - w / 2, y - ht / 2, x + w / 2, y + ht / 2)
                boxes.append(b)
    return boxes, wires


def seg_box_hit(a, b, box, slack=0.0):
    """True if segment a-b passes through the interior of box (endpoints touching the
    edge do not count)."""
    x0, y0, x1, y1 = box.x0 + slack, box.y0 + slack, box.x1 - slack, box.y1 - slack
    if x1 <= x0 or y1 <= y0:
        return False
    # Liang-Barsky
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
        if abs(p) < 1e-12:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                if r > t1:
                    return False
                t0 = max(t0, r)
            else:
                if r < t0:
                    return False
                t1 = min(t1, r)
    return t1 - t0 > 1e-9


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sheet')
    ap.add_argument('--slack', type=float, default=0.05,
                    help='shrink every box by this much before testing (mm)')
    ap.add_argument('--overlaps', action='store_true', help='also report text/text overlaps')
    a = ap.parse_args()
    root = parse(open(a.sheet, encoding='utf-8').read())
    boxes, wires = collect(root)
    hits = []
    for w in wires:
        for b in boxes:
            if seg_box_hit(w[0], w[1], b, a.slack):
                hits.append((w, b))
    print('%s: %d wires, %d text bodies' % (a.sheet, len(wires), len(boxes)))
    print('--- wire-through-text: %d ---' % len(hits))
    for w, b in sorted(hits, key=lambda h: (h[1].kind, h[1].label, h[0])):
        print('  wire (%.2f,%.2f)-(%.2f,%.2f)  through  %s' % (w[0][0], w[0][1], w[1][0], w[1][1], b))
    if a.overlaps:
        ov = []
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                p, q = boxes[i], boxes[j]
                if (p.x0 < q.x1 - a.slack and q.x0 < p.x1 - a.slack
                        and p.y0 < q.y1 - a.slack and q.y0 < p.y1 - a.slack):
                    ov.append((p, q))
        print('--- text-over-text: %d ---' % len(ov))
        for p, q in ov:
            print('  %s   OVERLAPS   %s' % (p, q))
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(main())
