"""widths.py DRC.json : list track_width violations grouped by net"""
import json, sys, re, collections
d = json.load(open(sys.argv[1]))
v = [x for x in d['violations'] if x['type'] == 'track_width']
by = collections.defaultdict(list)
for x in v:
    it = x['items'][0]
    by[re.sub(r'.*\[(.*)\].*', r'\1', it['description'])].append((it['description'], it['pos']['x'], it['pos']['y']))
print('track_width items:', len(v), 'severity', {x['severity'] for x in v})
for n, l in sorted(by.items()):
    print(f'{n}: {len(l)}')
    for desc, x, y in l:
        print(f'    {desc[:110]} @({x:.2f},{y:.2f})')
