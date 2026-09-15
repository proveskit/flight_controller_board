#!/usr/bin/env python3
"""Summarize a kicad-cli DRC JSON report (violations, unconnected items, schematic parity),
optionally as a delta against a baseline report, optionally listing items.

  drc_summary.py DRC.json [--baseline BASE.json] [--list] [--types t1,t2] [--refs R2,U3] [--new-only]

--new-only  keep only items that mention a refdes in the Phase-1 blocks (200-799) or a new net name
            (EMU_*, 3V3_EMU, VBUS_*, VSOLAR_BENCH*, VBAT_BENCH*, PYRO_*, CHG_*), i.e. layout work.
"""
import argparse
import json
import re
import sys
from collections import Counter

NEW_REF = re.compile(r'\b[A-Z]{1,3}(2\d\d|3\d\d|4[0-4]\d|5\d\d|6[0-4]\d|7\d\d)\b')
NEW_NET = re.compile(r'EMU_|3V3_EMU|1V1_EMU|VBUS_(EMU|CHG)|VSOLAR_BENCH|VBAT_BENCH|PYRO_|CHG_')


def rows(d):
    out = []
    for kind in ('violations', 'unconnected_items', 'schematic_parity'):
        for v in d.get(kind, []):
            items = v.get('items', [])
            desc = '; '.join(i.get('description', '') for i in items)
            pos = items[0].get('pos', {}) if items else {}
            out.append((kind, v.get('severity', '?'), v.get('type', '?'), v.get('description', ''), desc, pos.get('x'), pos.get('y')))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('drc')
    ap.add_argument('--baseline')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--types')
    ap.add_argument('--refs')
    ap.add_argument('--new-only', action='store_true')
    a = ap.parse_args()
    r = rows(json.load(open(a.drc)))
    if a.new_only:
        r = [x for x in r if NEW_REF.search(x[4]) or NEW_NET.search(x[3] + x[4])]
    if a.refs:
        refs = set(a.refs.split(','))
        r = [x for x in r if any(re.search(r'\b' + re.escape(ref) + r'\b', x[4]) for ref in refs)]
    c = Counter((x[0], x[1], x[2]) for x in r)
    if a.baseline:
        b = Counter((x[0], x[1], x[2]) for x in rows(json.load(open(a.baseline))))
        print('%-18s %-8s %-30s %6s %6s %6s' % ('section', 'sev', 'type', 'base', 'now', 'delta'))
        for k in sorted(set(c) | set(b)):
            print('%-18s %-8s %-30s %6d %6d %+6d' % (k[0], k[1], k[2], b[k], c[k], c[k] - b[k]))
        print('total baseline %d, now %d' % (sum(b.values()), sum(c.values())))
    else:
        for k, n in sorted(c.items()):
            print('%-18s %-8s %-30s %6d' % (k[0], k[1], k[2], n))
        print('total', sum(c.values()))
    errs = sum(n for (sec, sev, _), n in c.items() if sev == 'error')
    unc = sum(n for (sec, _, _), n in c.items() if sec == 'unconnected_items')
    par = sum(n for (sec, _, _), n in c.items() if sec == 'schematic_parity')
    print(f'errors: {errs}  unconnected: {unc}  parity: {par}')
    if a.list:
        types = set(a.types.split(',')) if a.types else None
        for sec, sev, typ, desc, items, x, y in r:
            if types and typ not in types:
                continue
            print(f'- [{sec}/{sev}] {typ}: {desc} | {items} @({x},{y})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
