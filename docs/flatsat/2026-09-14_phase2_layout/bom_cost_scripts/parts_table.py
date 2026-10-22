import json, sys, collections
S = sys.argv[1]
rows = json.load(open(f'{S}/align_rows.json'))
by = collections.defaultdict(list)
for r in rows:
    if r['eff']: by[r['eff']].append(r)
def price(d, n):
    for p in d['prices']:
        if n >= p['startNumber'] and (p['endNumber'] == -1 or n <= p['endNumber']): return p['productPrice']
    return d['prices'][-1]['productPrice']
out = []
for c, rs in by.items():
    d = json.load(open(f'{S}/live/{c}.json'))['data']
    q = len(rs)
    e = dict(code=c, qty=q, refs=' '.join(sorted(r['ref'] for r in rs)), value=rs[0]['value'],
             fps=sorted({r['fp'] for r in rs}), sides=sorted({r['side'] for r in rs}),
             mpn=d['componentModelEn'], pkg=d['componentSpecificationEn'], lib=d['componentLibraryType'],
             stock=d['stockCount'], proc=d['assemblyProcess'], moq=d['leastNumber'], loss=d['lossNumber'],
             desc=d['describe'][:70])
    for n in (2, 5):
        units = max(q * n + d['lossNumber'], d['leastNumber'])
        e[f'units{n}'] = units; e[f'unit_price{n}'] = price(d, units); e[f'cost{n}'] = round(units * price(d, units), 4)
    out.append(e)
out.sort(key=lambda e: -e['cost5'])
json.dump(out, open(f'{S}/parts_table.json', 'w'), indent=0)
for e in out:
    print(f"{e['code']:>10} {e['lib'][:3]} {e['proc']} q{e['qty']:>3} st{e['stock']:>8} moq{e['moq']:>3} loss{e['loss']:>2} ${e['cost2']:7.2f} ${e['cost5']:7.2f} | {e['value'][:18]:18} | {','.join(e['fps'])[:45]:45} | {e['mpn'][:22]:22} | {e['pkg'][:20]} | {e['refs'][:40]}")
