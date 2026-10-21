"""Item 6: widen the residual sub-1.0 mm power-path segments that have room (exact clearance check per segment)."""
import sys, json, fnmatch, ed
E = ed.Editor(sys.argv[1])
T = ed.T
targets = {'B-': None, 'Dir_Chrg_In': None, 'PROT_DRAIN': None, 'VBAT_BENCH_N': [(190.986, 155.846), (194.583, 160.408), (190.5, 158.9)],
           'CHG_PMID': None, 'CHG_SW': None, 'CHG_SYS': None, 'INJ_A_OR': None, 'INJ_A_PTC': None, 'INJ_B_OR': None, 'INJ_B_PTC': None,
           'VBUS_CHG': None, 'CHG_DVIN': None, 'INHIB_2': None, 'IN_RBF': None}
poly = [tuple(p) for p in ed.HER['rev2_outline']]
def inside(p):
    x, y = p; c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): c = not c
    return c
n_ok = n_try = 0
for net, only in targets.items():
    for t in E.items(net, None, 'track'):
        if t.m_Uuid.AsString() in ed.HER_T or T(t.GetWidth()) >= 1.0 - 1e-6:
            continue
        s, e = (T(t.GetStart().x), T(t.GetStart().y)), (T(t.GetEnd().x), T(t.GetEnd().y))
        if inside(s) or inside(e):
            continue
        if only and not any(min(abs(s[0] - x) + abs(s[1] - y), abs(e[0] - x) + abs(e[1] - y)) < 0.02 for x, y in only):
            continue
        n_try += 1
        for w in (1.0, 0.9, 0.8):
            if w <= T(t.GetWidth()) + 1e-6:
                break
            if ed.widen(E, t, w):
                n_ok += 1
                break
print(f'widened {n_ok}/{n_try}')
E.save()
