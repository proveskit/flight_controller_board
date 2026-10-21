import json, sys
from collections import Counter
def key(v): return (v['severity'], v['type'], tuple(sorted(i['description'] for i in v['items'])))
def load(p):
    d = json.load(open(p)); return Counter(key(v) for s in ('violations', 'unconnected_items') for v in d.get(s, []))
a, b = load(sys.argv[1]), load(sys.argv[2])
for k in sorted((b - a).keys()):
    if k[0] == 'error' or len(sys.argv) > 3: print('NEW ', k)
for k in sorted((a - b).keys()):
    if k[0] == 'error' or len(sys.argv) > 3: print('GONE', k)
