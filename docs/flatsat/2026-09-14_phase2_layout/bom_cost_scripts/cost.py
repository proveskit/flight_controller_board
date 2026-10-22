import json, sys
S = sys.argv[1]
board = {f['ref']: f for f in json.load(open(f'{S}/board.json'))['fps']}
parts = json.load(open(f'{S}/parts_table.json'))
XRAY = {'U2', 'U7', 'U15', 'U18', 'U200', 'U511', 'Q510'}
smd_j = tht_j = 0; tht_refs = []
for p in parts:
    for r in p['refs'].split():
        n = board[r]['npads']
        if p['proc'] == 'THT': tht_j += n; tht_refs.append(r)
        else: smd_j += n
uniq = len(parts); ext = sum(p['lib'] == 'expand' for p in parts)
area_cm2 = 153.15 * 124.66 / 100
print(f'unique {uniq} ext {ext} basic {uniq-ext}; SMD joints/board {smd_j}; THT joints/board {tht_j}; THT refs {len(tht_refs)}')
for N in (2, 5):
    fees = {
        'setup (Standard, double-side)': 51.12,
        'stencil (Standard, double-side)': 16.42,
        f'feeder loading {uniq} types x $1.53': uniq * 1.53,
        f'SMT joints {smd_j*N} x $0.0016': smd_j * N * 0.0016,
        f'THT joints {tht_j*N} x $0.0164': tht_j * N * 0.0164,
        'hand-soldering labor': 3.58,
        f'X-ray {len(XRAY)*N} parts': len(XRAY) * N * (1.64 if len(XRAY)*N <= 10 else 0.82),
        'packing': 0.50 + 0.00003 * area_cm2 * N,
        'confirm placement': 0.45,
    }
    parts_cost = sum(p[f'cost{N}'] for p in parts)
    feeder_ext_only = ext * 1.53
    asm = sum(fees.values())
    print(f'--- N={N}: parts ${parts_cost:.2f}; assembly fees ${asm:.2f} (ext-only feeder variant ${asm - uniq*1.53 + feeder_ext_only:.2f})')
    for k, v in fees.items(): print(f'   {k}: ${v:.2f}')
    top = sorted(parts, key=lambda p: -p[f'cost{N}'])[:10]
    print('   top parts:', [(p['code'], p['mpn'], round(p[f'cost{N}'], 2)) for p in top])
