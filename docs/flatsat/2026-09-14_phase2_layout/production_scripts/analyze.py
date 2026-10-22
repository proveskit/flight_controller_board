import csv, json, sqlite3, collections, sys
D = sys.argv[1]          # project dir with jlcpcb/
BAK = sys.argv[2]        # project.db backup
old = {r[0]: r for r in sqlite3.connect(BAK).execute('select * from part_info')}
new = {r[0]: r for r in sqlite3.connect(f'{D}/jlcpcb/project.db').execute('select * from part_info')}
added = sorted(set(new) - set(old)); removed = sorted(set(old) - set(new))
changed = [(k, old[k], new[k]) for k in sorted(set(old) & set(new)) if old[k][:3] + old[k][4:] != new[k][:3] + new[k][4:] or (old[k][3] or '') != (new[k][3] or '')]
print('rows before', len(old), 'after', len(new), 'added', len(added), 'removed', removed)
print('changed rows', len(changed)); [print('  ', c) for c in changed]
print('added with lcsc', sum(1 for k in added if new[k][3]), 'added blank', [k for k in added if not new[k][3]])
print('added excluded', [(k, new[k][5], new[k][6]) for k in added if new[k][5] or new[k][6]])
json.dump({'added': [list(new[k]) for k in added], 'changed': [[c[0], list(c[1]), list(c[2])] for c in changed]}, open(f'{D}/../sync_diff.json' if False else 'sync_diff.json', 'w'), indent=0)
cpl = list(csv.DictReader(open(f'{D}/jlcpcb/production_files/CPL-FlatSat_V1.csv')))
bom = list(csv.DictReader(open(f'{D}/jlcpcb/production_files/BOM-FlatSat_V1.csv')))
lc = [r for r in bom if r['LCSC']]
print('CPL rows', len(cpl), dict(collections.Counter(r['Layer'] for r in cpl)))
print('BOM lines', len(bom), 'with LCSC', len(lc), 'blank', len(bom) - len(lc))
print('unique LCSC', len({r['LCSC'] for r in lc}), 'placements with LCSC', sum(int(r['Quantity']) for r in lc), 'all BOM refs', sum(int(r['Quantity']) for r in bom))
bomrefs = [x for r in bom for x in r['Designator'].split(',')]
cplrefs = [r['Designator'] for r in cpl]
print('dup refs bom', len(bomrefs) - len(set(bomrefs)), 'cpl', len(cplrefs) - len(set(cplrefs)))
print('CPL-BOM', sorted(set(cplrefs) - set(bomrefs)), 'BOM-CPL', sorted(set(bomrefs) - set(cplrefs)))
d = collections.defaultdict(set)
for r in lc: d[r['LCSC']].add((r['Comment'], r['Footprint']))
print('LCSC with >1 value/footprint:', {k: sorted(v) for k, v in d.items() if len(v) > 1})
json.dump(sorted({r['LCSC'] for r in lc}), open('codes.json', 'w'))
