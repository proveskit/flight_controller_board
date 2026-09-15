#!/usr/bin/env python3
"""Compare two kicad-cli kicadxml netlists: which nets appeared / disappeared /
changed membership, and which components were added / removed / changed.

Usage: netlist_diff.py BASE.xml NEW.xml [--ignore-unconnected] [--only-touching REF1,REF2]

Baseline nets that gained or lost pins are the interesting ones when new sheets
are folded onto an existing board: they show every existing net that a new sheet
now reaches (global labels) and any accidental merge or split.
"""
import argparse
import sys
import xml.etree.ElementTree as ET


def load(path):
    r = ET.parse(path).getroot()
    nets = {}
    for n in r.find('nets'):
        nets[n.get('name')] = frozenset((x.get('ref'), x.get('pin')) for x in n.findall('node'))
    comps = {}
    for c in r.find('components'):
        comps[c.get('ref')] = (c.findtext('value'), c.findtext('footprint') or '', (c.find('sheetpath').get('names') if c.find('sheetpath') is not None else ''))
    return nets, comps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base')
    ap.add_argument('new')
    ap.add_argument('--ignore-unconnected', action='store_true')
    ap.add_argument('--only-touching', help='comma-separated refs; only report nets touching these')
    a = ap.parse_args()
    bn, bc = load(a.base)
    nn, nc = load(a.new)
    touch = set(a.only_touching.split(',')) if a.only_touching else None

    def keep(name, nodes):
        if a.ignore_unconnected and name.startswith('unconnected-'):
            return False
        if touch and not any(ref in touch for ref, _ in nodes):
            return False
        return True

    added = [k for k in nn if k not in bn and keep(k, nn[k])]
    removed = [k for k in bn if k not in nn and keep(k, bn[k])]
    changed = [k for k in nn if k in bn and nn[k] != bn[k] and keep(k, nn[k] | bn[k])]
    print('components: base %d, new %d, added %d, removed %d' % (len(bc), len(nc), len(set(nc) - set(bc)), len(set(bc) - set(nc))))
    for r in sorted(set(nc) - set(bc), key=lambda s: (s.rstrip('0123456789'), int(''.join(ch for ch in s if ch.isdigit()) or 0))):
        v, fp, sp = nc[r]
        print('  + %-6s %-40s %s  [%s]' % (r, (v or '')[:40], fp[:60], sp))
    for r in sorted(set(bc) - set(nc)):
        print('  - %s %s' % (r, bc[r][0]))
    for r in sorted(set(bc) & set(nc)):
        if bc[r][:2] != nc[r][:2]:
            print('  ~ %s: %s -> %s' % (r, bc[r][:2], nc[r][:2]))
    print('nets: base %d, new %d' % (len(bn), len(nn)))
    print('added nets (%d):' % len(added))
    for k in sorted(added):
        print('  + %s: %s' % (k, ', '.join('%s.%s' % n for n in sorted(nn[k]))))
    print('removed nets (%d):' % len(removed))
    for k in sorted(removed):
        print('  - %s: %s' % (k, ', '.join('%s.%s' % n for n in sorted(bn[k]))))
    print('changed nets (%d):' % len(changed))
    for k in sorted(changed):
        gained = nn[k] - bn[k]
        lost = bn[k] - nn[k]
        print('  ~ %s: +[%s] -[%s]' % (k, ', '.join('%s.%s' % n for n in sorted(gained)), ', '.join('%s.%s' % n for n in sorted(lost))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
