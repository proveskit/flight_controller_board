"""Item 2: Dir_Chrg_In attaches at J14 (brief L11) instead of J16.8.
 * L11 stub on In1 (J14 is THT, so In1 is a pad layer; no via in the band): J14.1 straight to the Rev2 edge.
   F.Cu (heritage VBATT_SENSE), In2 (heritage VBUSP) and B.Cu (heritage Dir_Chrg_In/PAYLOAD_BATT/DEPLOY1) all
   wall J14.1 off to the south; In1 holds only the heritage GND pour there.
 * Bench side on In1: to the trunk via (217.581,152.526) (Mode 2 path from JP510.2) and to JP500.2 (THT, Mode 1).
   The sense-only VSS In1 diagonal that blocked this corridor moves to B.Cu.
 * The J16.8 stub and its 140 mm run (five 0.46/0.20 vias) are removed: J16.8 keeps its heritage copper."""
import sys, math, ed

E = ed.Editor(sys.argv[1])
T = ed.T
N, V = 'Dir_Chrg_In', 'VBAT_BENCH_N'

# ---------- free the In1 corridor: VSS cluster link C501/U500 side <-> R504/sense via moves from In1 to B.Cu
E.remove([t for t in E.items(V, 'In1.Cu', 'track')
          if {(round(T(t.GetStart().x), 3), round(T(t.GetStart().y), 3)), (round(T(t.GetEnd().x), 3), round(T(t.GetEnd().y), 3))}
          & {(214.45, 152.269), (217.581, 155.4)} and T(t.GetLength()) < 5], 'VSS cluster In1 diagonal -> B.Cu')
E.track((219.1, 152.2), (219.0, 152.9), 0.5, 'B.Cu', V)
E.track((219.0, 152.9), (217.581, 155.571), 1.0, 'B.Cu', V)

# ---------- J16.8 run
run = [t for t in E.items(N) if t.m_Uuid.AsString() not in ed.HER_T and all(T(p.y) < 157.7 and T(p.x) > 224.0 for p in
       ([t.GetPosition()] if t.GetClass() == 'PCB_VIA' else [t.GetStart(), t.GetEnd()]))]
E.remove(run, 'J16.8 stub and run (bench current now enters at J14)')

# ---------- J14 stub (In1) and bench trunk links
E.path([(207.0, 131.2), (207.0, 142.6), (209.0, 144.6)], 1.5, 'In1.Cu', N)
E.track((209.0, 144.6), (209.0, 149.5), 1.8, 'In1.Cu', N)
E.path([(209.0, 149.5), (210.6, 151.185), (216.3, 151.185), (217.581, 152.466)], 1.1, 'In1.Cu', N)
E.track((217.581, 152.526), (213.1, 156.72), 0.8, 'In1.Cu', N)

E.save(sys.argv[2] if len(sys.argv) > 2 else None)
