import json, sys, urllib.request, time, os
S = sys.argv[1]
rows = json.load(open(f'{S}/align_rows.json'))
codes = sorted({r['eff'] for r in rows if r['eff']})
for c in codes:
    p = f'{S}/live/{c}.json'
    if os.path.exists(p): continue
    u = f'https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail?componentCode={c}'
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read()
        open(p, 'wb').write(d)
    except Exception as e:
        print(c, 'ERR', e)
    time.sleep(0.4)
print(len(codes))
