"""Item 3: shrink the copper inside the R5460 V-/VSS sense loop.
 * Q500/Q501 common drain: In1 block (3 x 1.0 mm + 2.8 mm fill) with three 0.8/0.4 vias at each drain row and
   1.2 mm F.Cu bars over both drain-pad columns, replacing the 0.25 mm In1 neck and its two 0.46/0.20 vias.
 * VSS Kelvin: U500 VSS cluster (U500.6/C500/C501/C502/R504) no longer taps VBAT_BENCH_N at J500.3; a dedicated
   1.0 mm B.Cu sense run joins it at Q500 source pad 2, so the J500.3 -> Q500 heavy run is outside the loop.
 * Heavy VBAT_BENCH_N run: 0.3 mm F.Cu neck widened, partner 0.8/0.4 vias where they fit."""
import sys, math, ed

E = ed.Editor(sys.argv[1])
T = ed.T
D, N = 'Net-(Q500-D-Pad5)', 'VBAT_BENCH_N'


def seg(net, a, b, layer=None):
    hits = [t for t in E.items(net, layer, 'track')
            if {(round(T(t.GetStart().x), 3), round(T(t.GetStart().y), 3)), (round(T(t.GetEnd().x), 3), round(T(t.GetEnd().y), 3))} == {a, b}]
    assert len(hits) == 1, (net, a, b, len(hits))
    return hits[0]


# ---------- COUT_GATE: move its via out of the drain-link corridor and its F.Cu run off Q501 drain pad 5
C = 'COUT_GATE'
E.remove([seg(C, (206.448, 157.998), (207.687, 156.759)), seg(C, (202.09, 157.998), (206.448, 157.998)),
          seg(C, (201.569, 157.476), (202.09, 157.998)), seg(C, (201.569, 157.476), (198.946, 157.476)),
          seg(C, (201.569, 157.476), (195.163, 163.881), 'In1.Cu'), seg(C, (195.163, 163.881), (195.163, 164.696), 'In1.Cu')]
         + E.items(C, None, 'via', near=(201.569, 157.476)), 'COUT_GATE re-run around the new drain link')
E.path([(198.946, 157.476), (200.4, 157.476), (201.824, 158.9), (206.0, 158.9), (207.687, 157.213), (207.687, 156.759)], 0.25, 'F.Cu', C)
E.via((201.4, 158.476), C, 0.46, 0.2)
E.track((201.4, 158.476), (195.163, 164.696), 0.25, 'In1.Cu', C)

# ---------- common drain
E.remove(E.items(D), 'old drain link (0.25 mm In1 neck, two 0.46/0.20 vias, 0.25 mm pad joiners)')
E.track((195.075, 153.545), (195.075, 157.355), 1.2, 'F.Cu', D)
E.track((203.775, 153.545), (203.775, 157.355), 1.2, 'F.Cu', D)
E.via((196.6, 152.6), D); E.track((196.6, 152.6), (195.4, 153.4), 0.8, 'F.Cu', D)
E.via((196.95, 155.1), D); E.track((196.95, 155.1), (195.6, 155.1), 0.8, 'F.Cu', D)
E.via((202.4, 157.0), D); E.track((202.4, 157.0), (203.3, 157.355), 0.6, 'F.Cu', D)
E.via((202.9, 158.0), D); E.track((202.9, 158.0), (203.3, 157.45), 0.6, 'F.Cu', D)
E.track((196.6, 152.6), (202.4, 157.0), 1.5, 'In1.Cu', D)
E.track((196.95, 155.1), (202.4, 157.0), 2.0, 'In1.Cu', D)
E.track((202.4, 157.0), (202.9, 158.0), 1.0, 'In1.Cu', D)

# ---------- VSS Kelvin sense: Q500 S pad 2 -> B.Cu -> U500 VSS cluster (cut its J500.3 tap)
E.remove([seg(N, (217.581, 160.7), (213.08, 165.2), 'In1.Cu')], 'VSS cluster tap at J500.3 (now Kelvin at Q500 S)')
E.via((188.35, 154.8), N, 0.46, 0.2)
E.track((189.4, 154.815), (188.35, 154.8), 0.4, 'F.Cu', N)
E.path([(188.35, 154.8), (189.5, 155.95), (189.5, 162.9), (216.3, 162.9), (217.581, 161.62)], 1.0, 'B.Cu', N)
E.via((217.581, 161.62), N, 0.46, 0.2)
E.track((217.581, 160.7), (217.581, 161.62), 1.5, 'In1.Cu', N)

# ---------- heavy run J500.3 -> Q500 S: widen the 0.3 mm neck, partner vias
ok = E.via((194.0, 161.6), N)
if ok:
    E.track((194.963, 161.288), (194.0, 161.6), 1.0, 'In2.Cu', N)
ok = E.via((190.5, 158.9), N)
if ok:
    E.track((190.5, 158.9), (191.286, 158.546), 0.6, 'B.Cu', N)
    E.track((190.5, 158.9), (191.286, 158.546), 0.6, 'F.Cu', N)
ok = E.via((191.95, 155.2), N)
if ok:
    E.track((191.95, 155.2), (190.125, 155.2), 1.0, 'F.Cu', N)
    E.track((191.95, 155.2), (191.2, 156.2), 1.0, 'B.Cu', N)

E.save(sys.argv[2] if len(sys.argv) > 2 else None, allow_fail=True)
