#!/usr/bin/env python3
"""Summarize a kicad-cli ERC JSON report, optionally filtered to one sheet and
diffed against a baseline report.

Usage:
  erc_summary.py ERC.json [--sheet "Sheet Name"] [--baseline BASE.json] [--list] [--types t1,t2]

--sheet      only violations whose sheet path contains this text
--baseline   print counts as delta vs the baseline (new / fixed)
--list       print each violation (severity, type, description, location)
--types      comma-separated list restricting --list output to those types
--ignore-noise  drop the known library-metadata noise types
              (lib_symbol_issues, lib_symbol_mismatch, footprint_link_issues, endpoint_off_grid)
"""
import argparse
import json
import sys
from collections import Counter

NOISE = {'lib_symbol_issues', 'lib_symbol_mismatch', 'footprint_link_issues', 'endpoint_off_grid'}


def load(path, sheet=None, ignore_noise=False):
    d = json.load(open(path))
    rows = []
    for s in d.get('sheets', []):
        sp = s.get('path') or s.get('uuid_path') or ''
        if sheet and sheet not in sp:
            continue
        for v in s.get('violations', []):
            if ignore_noise and v['type'] in NOISE:
                continue
            items = v.get('items', [])
            loc = '; '.join('%s @(%s,%s)' % (i.get('description', ''), i.get('pos', {}).get('x'), i.get('pos', {}).get('y')) for i in items)
            rows.append((sp, v['severity'], v['type'], v.get('description', ''), loc))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('erc')
    ap.add_argument('--sheet')
    ap.add_argument('--baseline')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--types')
    ap.add_argument('--ignore-noise', action='store_true')
    a = ap.parse_args()
    rows = load(a.erc, a.sheet, a.ignore_noise)
    c = Counter((r[1], r[2]) for r in rows)
    if a.baseline:
        b = Counter((r[1], r[2]) for r in load(a.baseline, a.sheet, a.ignore_noise))
        keys = sorted(set(c) | set(b))
        print('%-8s %-28s %6s %6s %6s' % ('sev', 'type', 'base', 'now', 'delta'))
        for k in keys:
            print('%-8s %-28s %6d %6d %+6d' % (k[0], k[1], b[k], c[k], c[k] - b[k]))
        print('total baseline %d, now %d, delta %+d' % (sum(b.values()), sum(c.values()), sum(c.values()) - sum(b.values())))
    else:
        for k, n in sorted(c.items()):
            print('%-8s %-28s %6d' % (k[0], k[1], n))
        print('total', sum(c.values()))
    errs = sum(n for (sev, _), n in c.items() if sev == 'error')
    print('errors:', errs)
    if a.list:
        types = set(a.types.split(',')) if a.types else None
        for sp, sev, typ, desc, loc in rows:
            if types and typ not in types:
                continue
            print('- [%s] %s (%s): %s | %s' % (sev, typ, sp, desc, loc))
    return 0


if __name__ == '__main__':
    sys.exit(main())
