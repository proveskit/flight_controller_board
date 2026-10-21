"""netclass_add.py PRO CLASS PATTERN... : append netclass patterns (idempotent)"""
import json, sys
p, cl = sys.argv[1], sys.argv[2]
d = json.load(open(p))
pats = d['net_settings']['netclass_patterns']
for pat in sys.argv[3:]:
    if not any(x['pattern'] == pat for x in pats):
        pats.append({'netclass': cl, 'pattern': pat})
open(p, 'w').write(json.dumps(d, indent=2) + '\n')
print([x['pattern'] for x in pats if x['netclass'] == cl])
