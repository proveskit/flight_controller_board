"""Item 4 (with item 1's SYS feed): BQ25886 power stage re-layout around U511.
C513 (CSYS) at the SYS pins, L510 vertical (SW pad at the SW pins, PMID pad toward C511), C512 beside the SW run,
SYS to JP510 on In2 1.5 mm through paired 0.8/0.4 vias, CHG_BAT In1 run under U511 removed (BAT carries no load
after item 1; C515 + TP512 on F.Cu), 9 EP thermal PTH pads (U18 convention), GND vias at every charger cap."""
import sys, math, ed

E = ed.Editor(sys.argv[1])
T = ed.T


def seg(net, a, b, layer=None):
    """the one new track of `net` with endpoints a and b (either order)"""
    hits = []
    for t in E.items(net, layer, 'track'):
        s, e = (T(t.GetStart().x), T(t.GetStart().y)), (T(t.GetEnd().x), T(t.GetEnd().y))
        if (math.dist(s, a) < 0.01 and math.dist(e, b) < 0.01) or (math.dist(s, b) < 0.01 and math.dist(e, a) < 0.01):
            hits.append(t)
    assert len(hits) == 1, (net, a, b, len(hits))
    return hits[0]


def via_at(net, p):
    v = E.items(net, None, 'via', near=p)
    assert len(v) == 1, (net, p, len(v))
    return v[0]


# ---------- removals
SYS, BAT, PMID, SW, BTST = 'CHG_SYS', 'CHG_BAT', 'Net-(C511-Pad1)', 'Net-(C512-Pad1)', 'Net-(U511-BTST)'
dead = []
dead += [seg(SYS, (279.663, 152.2), (279.663, 152.2)), seg(SYS, (279.050, 152.345), (279.663, 152.2)),
         seg(SYS, (279.100, 152.060), (279.663, 152.2)), via_at(SYS, (279.663, 152.2))]
dead += [t for t in E.items(SYS, 'In2.Cu', 'track') if T(t.GetStart().x) > 272 or T(t.GetEnd().x) > 272]
dead += [via_at(SYS, (281.462, 154.95)), seg(SYS, (281.462, 154.95), (281.462, 154.95)), seg(SYS, (281.072, 155.317), (281.462, 154.95))]
dead += [seg(SYS, (281.959, 157.664), (280.845, 156.55)), seg(SYS, (282.146, 157.476), (281.959, 157.664)),
         seg(SYS, (282.572, 158.277), (281.959, 157.664)), seg(SYS, (285.835, 158.277), (282.572, 158.277)),
         seg(SYS, (282.572, 158.277), (282.572, 162.403)), seg(SYS, (282.572, 162.403), (280.845, 164.13))]
dead += [seg(SYS, (270.097, 147.097), (272.397, 147.197)), via_at(SYS, (272.397, 147.197))]
dead += [t for t in E.items(BAT) if not (t.GetClass() != 'PCB_VIA' and abs(T(t.GetStart().x) - 278.962) < 0.01 and abs(T(t.GetEnd().x) - 278.962) < 0.01)]
dead += [t for t in E.items(PMID) if not (t.GetClass() != 'PCB_VIA' and t.GetLayer() == ed.L['F.Cu']
                                        and abs(T(t.GetStart().y) - 150.238) < 0.01 and abs(T(t.GetEnd().y) - 150.238) < 0.01)]
dead += [seg(SW, (281.612, 153.0), (281.112, 153.5)), seg(SW, (279.226, 150.687), (278.962, 150.95)),
         seg(SW, (281.612, 149.4), (281.612, 153.0)), seg(SW, (280.376, 149.35), (279.276, 150.65)),
         seg(SW, (280.75, 153.452), (280.75, 153.855))]
dead += [seg(BTST, (280.1, 153.055), (280.75, 152.305)), via_at(BTST, (280.1, 153.055)), seg(BTST, (278.725, 154.33), (280.1, 153.055), 'In2.Cu')]
E.remove(dead, 'charger re-layout')
keep_pmid = [t for t in E.items(PMID, 'F.Cu', 'track')]
assert len(keep_pmid) == 2, len(keep_pmid)       # the pin 21/22 joiners; the 277.0 riser is re-added wider below

# ---------- trim TP511 link to its own vias; extend the In2 run back to 271.151
ed.set_end(E, seg(SYS, (266.497, 145.797), (270.097, 147.097)), 'end', (267.5, 146.159))
ed.set_end(E, seg(SYS, (259.236, 145.031), (267.5, 145.031), 'In2.Cu'), 'end', (271.151, 145.031))

# ---------- moves
E.move_fp('C513', (281.75, 153.675), 270)     # pad1 SYS (281.75,152.2), pad2 GND (281.75,155.15)
E.move_fp('C512', (280.5, 149.3), 90)         # pad1 SW (280.5,150.075), pad2 BTST (280.5,148.525)
E.move_fp('L510', (284.85, 147.3), 90)        # pad1 SW (284.85,150.1), pad2 PMID (284.85,144.5)
E.move_fp('TP512', (279.9, 167.6), 0)
for p in (('C513', 1), ('C513', 2), ('C512', 1), ('C512', 2), ('L510', 1), ('L510', 2), ('TP512', 1)):
    print('pad', p, E.padxy(*p))

# ---------- EP thermal pads (U18 convention: PTH pads numbered as the EP)
ed.ep_pads(E, 'U511', 25, [(277 + dx, 152.2 + dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)], 0.6, 0.3)
E.track((278.0, 150.45), (278.0, 151.0), 0.25, 'F.Cu', 'GND')                      # PGND pins 19/20 -> EP

# ---------- SYS: pins -> C513.1 -> paired vias -> In2 1.5 mm -> JP510.1; spine to C514/C517/C518
E.track((279.15, 152.2), (281.2, 152.2), 0.7, 'F.Cu', SYS)
E.track((282.6, 152.2), (283.95, 152.2), 1.0, 'F.Cu', SYS)
E.via((283.95, 152.2), SYS)
E.via((283.95, 153.15), SYS)
E.path([(283.95, 152.2), (283.95, 156.0), (282.32, 157.63), (282.32, 162.6), (280.95, 163.97)], 1.0, 'F.Cu', SYS)
E.track((283.95, 155.0), (285.5, 155.7), 1.0, 'F.Cu', SYS)
E.path([(283.95, 153.15), (283.95, 146.6), (272.72, 146.6), (271.151, 145.031)], 1.5, 'In2.Cu', SYS)

# ---------- SW: pins -> L510.1 at 0.8 mm, C512.1 on the run
E.track((279.1, 150.95), (283.5, 150.95), 0.8, 'F.Cu', SW)
E.track((280.5, 150.95), (280.5, 150.075), 0.5, 'F.Cu', SW)

# ---------- BTST: pin 12 via (kept) -> B.Cu -> via -> C512.2
E.via((279.5, 148.4), BTST, 0.46, 0.2)
E.path([(278.725, 154.33), (279.4, 153.65), (279.4, 148.5), (279.5, 148.4)], 0.25, 'B.Cu', BTST)
E.track((279.5, 148.4), (280.5, 148.525), 0.25, 'F.Cu', BTST)

# ---------- PMID: pins -> C511.1 (0.6) -> L510.2 at 1.0 mm on F.Cu
E.track((277.0, 150.0), (277.0, 148.6), 0.6, 'F.Cu', PMID)
E.path([(278.0, 148.2), (279.6, 146.6), (284.0, 146.6), (284.0, 145.0)], 1.0, 'F.Cu', PMID)

# ---------- BAT: pins 13/14 -> C515.1 -> TP512 (no load after item 1)
E.path([(279.15, 153.45), (279.88, 153.45), (279.88, 158.6), (280.55, 159.27)], 0.4, 'F.Cu', BAT)
E.path([(279.88, 158.6), (279.6, 158.88), (279.6, 166.4), (279.9, 167.6)], 0.4, 'F.Cu', BAT)

# ---------- GND vias at the charger cap GND pads
E.via((281.0, 156.35), 'GND', 0.46, 0.2); E.track((281.0, 156.35), (281.0, 155.3), 0.4, 'F.Cu', 'GND')
E.via((281.95, 156.35), 'GND', 0.46, 0.2); E.track((281.95, 156.35), (281.95, 155.3), 0.4, 'F.Cu', 'GND')
E.via((283.795, 162.235), 'GND', 0.46, 0.2); E.track((283.795, 161.4), (283.795, 163.1), 0.4, 'F.Cu', 'GND')
E.via((288.785, 154.65), 'GND', 0.46, 0.2); E.track((288.785, 154.65), (288.785, 155.5), 0.4, 'F.Cu', 'GND')
E.via((289.0, 158.45), 'GND', 0.46, 0.2); E.track((288.85, 157.6), (289.0, 158.45), 0.4, 'F.Cu', 'GND'); E.track((289.0, 158.45), (289.035, 159.3), 0.4, 'F.Cu', 'GND')
E.via((276.3, 144.2), 'GND', 0.46, 0.2); E.track((276.3, 144.2), (276.3, 145.1), 0.4, 'F.Cu', 'GND')
E.via((277.7, 144.2), 'GND', 0.46, 0.2); E.track((277.7, 144.2), (277.7, 145.1), 0.4, 'F.Cu', 'GND')
E.via((274.0, 145.2), 'GND', 0.46, 0.2); E.track((274.0, 145.2), (274.0, 146.3), 0.4, 'F.Cu', 'GND')

print('courtyard overlaps:', ed.court_overlaps(E, {'C513', 'C512', 'L510', 'TP512'}))
E.save(sys.argv[2] if len(sys.argv) > 2 else None)
