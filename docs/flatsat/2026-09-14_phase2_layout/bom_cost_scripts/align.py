import json, csv, sqlite3, sys, collections
S = sys.argv[1]
board = {f['ref']: f for f in json.load(open(f'{S}/board.json'))['fps']}
sch = {r['Ref']: r for r in csv.DictReader(open(f'{S}/bom_flat.csv'))}
db = sqlite3.connect(f'file:{S}/project_copy.db?mode=ro', uri=True)
pdb = {r[0]: dict(value=r[1], footprint=r[2], lcsc=r[3] or '', stock=r[4], exbom=r[5], expos=r[6]) for r in db.execute('select * from part_info')}
# placed = on board, not DNP, not exclude-from-bom, not board-only
placed = {r: f for r, f in board.items() if not (f['dnp'] or f['ex_bom'] or f['board_only'])}
rows = []
for r, f in sorted(placed.items()):
    s = sch.get(r, {}); p = pdb.get(r)
    sl = (s.get('LCSCPart') or s.get('LCSC') or f['lcsc'] or '').strip()
    pl = p['lcsc'].strip() if p else ''
    fpname = f['fpid'].split(':')[-1]
    mism = []
    if p:
        if p['value'] != f['value']: mism.append(f"value board={f['value']} db={p['value']}")
        if p['footprint'] != fpname: mism.append(f"fp board={fpname} db={p['footprint']}")
    eff = pl or sl
    rows.append(dict(ref=r, value=f['value'], fp=fpname, side=f['side'], smd=f['smd'], tht=f['tht'], expos=f['ex_pos'],
        sch_lcsc=sl, db_lcsc=pl, in_db=bool(p), eff=eff, differ=bool(sl and pl and sl != pl), db_mismatch='; '.join(mism),
        db_exbom=p['exbom'] if p else None))
json.dump(rows, open(f'{S}/align_rows.json','w'), indent=0)
c = collections.Counter
print('board fps', len(board), 'placed', len(placed), 'dnp', sum(f['dnp'] for f in board.values()), 'exbom', sum(f['ex_bom'] for f in board.values()), 'boardonly', sum(f['board_only'] for f in board.values()))
print('side', c(r['side'] for r in rows)); print('smd/tht', c(('SMD' if r['smd'] else 'THT' if r['tht'] else 'other') for r in rows))
print('no lcsc anywhere', [r['ref'] for r in rows if not r['eff']])
print('not in db', len([r for r in rows if not r['in_db']]), 'with sch lcsc', len([r for r in rows if not r['in_db'] and r['sch_lcsc']]))
print('differ', [(r['ref'], r['sch_lcsc'], r['db_lcsc']) for r in rows if r['differ']])
print('db mismatch', [(r['ref'], r['db_mismatch'], r['db_lcsc']) for r in rows if r['db_mismatch']])
print('db rows not on board/placed', sorted(set(pdb) - set(placed)))
print('sch refs not on board', sorted(set(sch) - set(board)))
print('board not in sch', sorted(set(board) - set(sch)))
print('unique eff lcsc', len({r['eff'] for r in rows if r['eff']}))
