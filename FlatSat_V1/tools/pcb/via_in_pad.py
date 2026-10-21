#!/usr/bin/env python3
"""List board vias that land on an SMD pad (owner ruling F16, 2026-10-21). Run with KiCad's bundled python3.

  via_in_pad.py BOARD.kicad_pcb [--snap heritage_rev2.json] [--json OUT.json] [--list]

A via is IN-PAD when its centre lies inside an SMD pad's copper on F.Cu or B.Cu, EDGE when only its
annular ring overlaps the pad. --snap skips heritage vias (flown Rev2 has 0 in-pad, 42 edge). Both need a fix: move off-pad (dogbone) or order filled-and-capped (POFV).
Exit 0 = none, 1 = some.
"""
import argparse
import json
import sys

try:
    import pcbnew
except ImportError:
    sys.exit("run with KiCad's bundled python3")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('board')
    ap.add_argument('--snap')
    ap.add_argument('--json')
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    board = pcbnew.LoadBoard(a.board)
    smd = [p for fp in board.GetFootprints() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    heritage = set(json.load(open(a.snap))['tracks']) if a.snap else set()
    hits = []
    for v in board.GetTracks():
        if v.Type() != pcbnew.PCB_VIA_T or v.m_Uuid.AsString() in heritage:
            continue
        c = v.GetPosition()
        r = v.GetWidth(pcbnew.F_Cu) // 2
        for p in smd:
            layer = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            shape = p.GetEffectivePolygon(layer, pcbnew.ERROR_INSIDE)
            if shape.Contains(c):
                kind = 'IN-PAD'
            elif shape.Collide(c, r):
                kind = 'EDGE'
            else:
                continue
            hits.append({'kind': kind, 'ref': p.GetParentFootprint().GetReference(), 'pad': p.GetNumber(),
                         'via_net': v.GetNetname(), 'pad_net': p.GetNetname(),
                         'x': round(pcbnew.ToMM(c.x), 3), 'y': round(pcbnew.ToMM(c.y), 3),
                         'via': f'{pcbnew.ToMM(v.GetWidth(pcbnew.F_Cu)):.2f}/{pcbnew.ToMM(v.GetDrill()):.2f}',
                         'uuid': v.m_Uuid.AsString()})
    hits.sort(key=lambda h: (h['kind'], h['ref'], h['pad']))
    if a.list:
        for h in hits:
            print(f"{h['kind']:6} {h['ref']}.{h['pad']:<4} pad {h['pad_net']:<20} via {h['via_net']:<20} {h['via']} ({h['x']}, {h['y']})")
    n_in = sum(h['kind'] == 'IN-PAD' for h in hits)
    print(f'via-in-pad: {n_in} in-pad, {len(hits) - n_in} edge, {len({h["uuid"] for h in hits})} distinct vias')
    if a.json:
        json.dump(hits, open(a.json, 'w'), indent=1)
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(main())
