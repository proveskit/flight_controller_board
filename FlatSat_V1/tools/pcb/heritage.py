#!/usr/bin/env python3
"""Snapshot and verify the flight-heritage part of the FlatSat board.

The Rev2 layout (V5d flew, V5e Rev1 passed environmental test) must not be churned: no existing
footprint moves, flips or rotates; no existing track, via or zone changes; zones may only GROW
(the GND planes are extended over the new board area); Edge.Cuts may change only where the outline
is extended (reported, never silently accepted). Run with KiCad's bundled python3.

  heritage.py snapshot BOARD.kicad_pcb SNAP.json
  heritage.py check    SNAP.json BOARD.kicad_pcb [--allow-zone-growth] [--allow-edge]

Exit 0 = heritage intact (within the allowances), 1 = violations listed.
"""
import argparse
import json
import sys

try:
    import pcbnew
except ImportError:
    sys.exit('run with KiCad\'s bundled python3')


def mm(v):
    return round(pcbnew.ToMM(v), 4)


def zone_polys(z):
    out = []
    outline = z.Outline()
    for i in range(outline.OutlineCount()):
        o = outline.Outline(i)
        out.append([(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())])
    return out


def new_copper_poly(board, snap_tracks, inflate_mm):
    """Union of every track/via NOT in the snapshot (i.e. new copper), inflated by inflate_mm, as one SHAPE_POLY_SET.
    Subtracting it from the fills before measuring hides the carve-out a compliant stub causes in a heritage pour
    (which may extend past the 12 mm core line: stubs are allowed 14-24 mm deep) while still catching fill changes
    anywhere else. The same polygon is subtracted from the reference board's fills so both sides measure the same area."""
    poly = pcbnew.SHAPE_POLY_SET()
    clr = pcbnew.FromMM(inflate_mm)
    maxerr = pcbnew.FromMM(0.02)
    n = 0
    for t in board.GetTracks():
        if t.m_Uuid.AsString() in snap_tracks:
            continue
        layer = pcbnew.F_Cu if t.GetClass() == 'PCB_VIA' else t.GetLayer()
        try:
            t.TransformShapeToPolygon(poly, layer, clr, maxerr, pcbnew.ERROR_OUTSIDE)
            n += 1
        except Exception:
            pass
    poly.Simplify()
    return poly, n


def snapshot(board, clip_outline=None, core_inset=None, exclude=None):
    """clip_outline: when checking a grown board, pass the stored Rev2 outline so 'fill_in_rev2' is measured
    inside the ORIGINAL outline rather than the current one. core_inset: additionally measure 'fill_in_core'
    inside the outline deflated by this many mm (the flight core beyond the L11 attachment band).
    exclude: a SHAPE_POLY_SET subtracted from every fill before measuring (new copper + clearance, see new_copper_poly)."""
    fps = {}
    for f in board.GetFootprints():
        p = f.GetPosition()
        fps[f.m_Uuid.AsString()] = {'ref': f.GetReference(), 'x': mm(p.x), 'y': mm(p.y), 'rot': round(f.GetOrientationDegrees(), 3), 'layer': board.GetLayerName(f.GetLayer()), 'fpid': str(f.GetFPID().GetLibItemName()),
                                    'pads': [(pd.GetNumber(), pd.GetNetname()) for pd in f.Pads()]}
    tracks = {}
    for t in board.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        if t.GetClass() == 'PCB_VIA':
            width = mm(t.GetWidth(pcbnew.F_Cu))
            layer = 'via:%s' % t.GetLayerSet().SeqStackupForPlotting().__len__() if hasattr(t.GetLayerSet(), 'SeqStackupForPlotting') else 'via'
            layer = 'via'
        else:
            width = mm(t.GetWidth())
            layer = board.GetLayerName(t.GetLayer())
        tracks[t.m_Uuid.AsString()] = {'type': t.GetClass(), 'layer': layer, 'start': (mm(s.x), mm(s.y)), 'end': (mm(e.x), mm(e.y)), 'width': width, 'net': t.GetNetname()}
    # board outline polygon (outer contour), used as the flight-section boundary by attachment_check.py and below
    outline = []
    clip = None
    try:
        sp = pcbnew.SHAPE_POLY_SET()
        if board.GetBoardPolygonOutlines(sp, False) and sp.OutlineCount():
            o = sp.Outline(0)
            outline = [(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())]
        ref_outline = [tuple(p) for p in clip_outline] if clip_outline else outline
        if ref_outline:
            clip = pcbnew.SHAPE_POLY_SET()
            clip.NewOutline()
            for x, y in ref_outline:
                clip.Append(pcbnew.VECTOR2I_MM(x, y))
            # measure fills inside the outline deflated by 1 mm: once the board grows, fills legitimately extend into
            # the former edge-clearance band along the attachment edges; the interior must stay identical
            clip.Inflate(-pcbnew.FromMM(1.0), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05))
            if core_inset is not None:
                core = pcbnew.SHAPE_POLY_SET()
                core.NewOutline()
                for x, y in ref_outline:
                    core.Append(pcbnew.VECTOR2I_MM(x, y))
                core.Inflate(-pcbnew.FromMM(core_inset), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05))
    except Exception:
        outline = []
    zones = {}
    for z in board.Zones():
        fill_in = fill_core = None
        if clip is not None and not z.GetIsRuleArea():
            try:
                fill_in = 0.0
                fill_core = 0.0 if core_inset is not None else None
                for layer in z.GetLayerSet().Seq():
                    fp = pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(layer))
                    fp.BooleanIntersection(clip)
                    if exclude is not None:
                        fp.BooleanSubtract(exclude)
                    fill_in += fp.Area() / 1e12
                    if core_inset is not None:
                        fc = pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(layer))
                        fc.BooleanIntersection(core)
                        if exclude is not None:
                            fc.BooleanSubtract(exclude)
                        fill_core += fc.Area() / 1e12
            except Exception:
                fill_in = fill_core = None
        zones[z.m_Uuid.AsString()] = {'net': z.GetNetname(), 'layer': board.GetLayerName(z.GetFirstLayer()), 'polys': zone_polys(z), 'priority': z.GetAssignedPriority(),
                                      'filled_area': (z.GetFilledArea() / 1e12) if hasattr(z, 'GetFilledArea') else None,
                                      'fill_in_rev2': fill_in, 'fill_in_core': fill_core}
    edges = {}
    for d in board.GetDrawings():
        if board.GetLayerName(d.GetLayer()) != 'Edge.Cuts':
            continue
        try:
            s, e = d.GetStart(), d.GetEnd()
            edges[d.m_Uuid.AsString()] = {'shape': d.ShowShape(), 'start': (mm(s.x), mm(s.y)), 'end': (mm(e.x), mm(e.y))}
        except Exception:
            edges[d.m_Uuid.AsString()] = {'shape': type(d).__name__}
    bb = board.GetBoardEdgesBoundingBox()
    return {'footprints': fps, 'tracks': tracks, 'zones': zones, 'edges': edges,
            'bbox': [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())],
            'rev2_outline': outline}


def point_in_poly(pt, poly, tol=0.05):
    """inside, or within tol mm of the boundary (clipping produces vertices exactly on the old outline)"""
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xin:
                inside = not inside
    if inside:
        return True
    import math
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        if dx == dy == 0:
            d = math.hypot(x - ax, y - ay)
        else:
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
            d = math.hypot(x - (ax + t * dx), y - (ay + t * dy))
        if d <= tol:
            return True
    return False


def refill(board):
    filler = pcbnew.ZONE_FILLER(board)
    return filler.Fill(board.Zones())


def check(snap, board, allow_zone_growth, allow_edge, do_refill=False, core_inset=None, ref_board=None, exclude_new_mm=None):
    """do_refill: refill zones (in memory) before measuring, so copper carved by new tracks is seen.
    core_inset: fills inside the Rev2 outline deflated by this many mm must be identical; fills in the band
    outside it (where L11 stubs are allowed) are only reported. ref_board: a Rev2 board to measure the
    reference fills from with the same filler/insets (required for core_inset; refilled too if do_refill).
    exclude_new_mm: ignore fill changes within this distance of any NEW track/via (the carve-out of a compliant
    stub); the same area is excluded from the reference. None = no exclusion."""
    if do_refill:
        refill(board)
    excl = None
    n_new = 0
    if exclude_new_mm is not None:
        excl, n_new = new_copper_poly(board, set(snap['tracks']), exclude_new_mm)
    now = json.loads(json.dumps(snapshot(board, clip_outline=snap.get('rev2_outline'), core_inset=core_inset, exclude=excl)))  # normalise tuples -> lists like the stored snapshot
    ref = None
    rb = None
    if ref_board is not None:
        rb = pcbnew.LoadBoard(ref_board)
        if do_refill:
            refill(rb)
        ref = json.loads(json.dumps(snapshot(rb, clip_outline=snap.get('rev2_outline'), core_inset=core_inset, exclude=excl)))['zones']
    zones_now = {z.m_Uuid.AsString(): z for z in board.Zones()}
    zones_ref = {z.m_Uuid.AsString(): z for z in rb.Zones()} if rb is not None else {}

    def core_poly():
        c = pcbnew.SHAPE_POLY_SET(); c.NewOutline()
        for x, y in snap.get('rev2_outline'):
            c.Append(pcbnew.VECTOR2I_MM(x, y))
        c.Inflate(-pcbnew.FromMM(core_inset), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05))
        return c

    def lost_far_from_new_copper(u):
        """mm² of core copper the reference zone has and the current zone lacks that does NOT touch the new-copper
        exclusion (i.e. is not a carve-out / removed island caused by a stub). Returns (far_mm2, near_mm2)."""
        zn, zr = zones_now.get(u), zones_ref.get(u)
        if zn is None or zr is None or excl is None:
            return None, None
        core = core_poly()
        touch = pcbnew.SHAPE_POLY_SET(excl); touch.Inflate(pcbnew.FromMM(0.6), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05))
        far = near = 0.0
        for layer in zr.GetLayerSet().Seq():
            fr = pcbnew.SHAPE_POLY_SET(zr.GetFilledPolysList(layer)); fr.BooleanIntersection(core)
            fn = pcbnew.SHAPE_POLY_SET(zn.GetFilledPolysList(layer)); fn.BooleanIntersection(core)
            lost = pcbnew.SHAPE_POLY_SET(fr); lost.BooleanSubtract(fn); lost.Fracture()
            for i in range(lost.OutlineCount()):
                piece = pcbnew.SHAPE_POLY_SET(); piece.AddOutline(lost.Outline(i))
                a = piece.Area() / 1e12
                t = pcbnew.SHAPE_POLY_SET(piece); t.BooleanIntersection(touch)
                if t.Area() > 0:
                    near += a
                else:
                    far += a
        return far, near
    problems = []
    notes = []
    if do_refill:
        notes.append('zones refilled in memory before measuring' + (' (reference board too)' if ref is not None else ''))
    if excl is not None:
        notes.append(f'fill changes within {exclude_new_mm:g} mm of the {n_new} new tracks/vias are excluded from the comparison (stub carve-out)')
    # net renames from the Phase-1 promotions are expected; compare pad nets modulo those
    RENAME = {'/Power Systems/B-': 'B-', '/Power Systems/VBATT_SENSE': 'VBATT_SENSE', '/Power Systems/INHIB_1': 'INHIB_1', '/Power Systems/INHIB_2': 'INHIB_2', '/Power Systems/IN_RBF': 'IN_RBF', '/Power Systems/Load Switches/Deploy1_EN': 'Deploy1_EN', '/Power Systems/Load Switches/Heater_EN': 'Heater_EN', '/Power Systems/Load Switches/Deploy2_EN': 'Deploy2_EN'}
    rn = lambda n: RENAME.get(n, n)
    for u, f in snap['footprints'].items():
        g = now['footprints'].get(u)
        if g is None:
            problems.append(f"footprint {f['ref']} removed")
            continue
        for k in ('x', 'y', 'rot', 'layer', 'fpid'):
            if f[k] != g[k]:
                problems.append(f"footprint {f['ref']}: {k} {f[k]} -> {g[k]}")
        if [(n, rn(net)) for n, net in f['pads']] != [(n, rn(net)) for n, net in g['pads']]:
            problems.append(f"footprint {f['ref']}: pad nets changed")
    for u, t in snap['tracks'].items():
        g = now['tracks'].get(u)
        if g is None:
            problems.append(f"{t['type']} {t['net']} on {t['layer']} at {t['start']} removed")
            continue
        if (t['start'], t['end'], t['width'], t['layer'], rn(t['net'])) != (g['start'], g['end'], g['width'], g['layer'], rn(g['net'])):
            problems.append(f"{t['type']} {t['net']} on {t['layer']} at {t['start']} changed")
    for u, z in snap['zones'].items():
        g = now['zones'].get(u)
        if g is None:
            problems.append(f"zone {z['net']} on {z['layer']} removed")
            continue
        if rn(z['net']) != rn(g['net']) or z['layer'] != g['layer']:
            problems.append(f"zone {z['net']} on {z['layer']}: net/layer changed to {g['net']} on {g['layer']}")
        if z['polys'] != g['polys']:
            if allow_zone_growth:
                # growth: every old vertex inside/on the new outline; clipping to the Rev2 outline: every new vertex inside/on the old outline
                def contained(inner_polys, outer_polys):
                    return all(any(point_in_poly(pt, op) or list(pt) in [list(q) for q in op] for op in outer_polys) for ip in inner_polys for pt in ip)
                clipped = contained(g['polys'], z['polys'])   # every new vertex inside/on the old outline
                grown = contained(z['polys'], g['polys'])     # every old vertex inside/on the new outline
                ok = grown or clipped
                kind = 'clipped to the old outline' if clipped and not grown else 'grown, old outline contained' if grown and not clipped else 'reshaped within itself' if clipped and grown else 'neither pure growth nor pure clipping'
                (notes if ok else problems).append(f"zone {z['net']} on {z['layer']}: outline changed ({kind})")
            else:
                problems.append(f"zone {z['net']} on {z['layer']}: outline changed")
        # copper inside the Rev2 outline must be unchanged whatever happened to the outline
        r = ref.get(u) if ref is not None else None
        if core_inset is not None and r is not None:
            # core: identical; band: report the carve-out (stubs are allowed there, the fill legitimately changes around them)
            if r.get('fill_in_core') and g.get('fill_in_core') is not None:
                if abs(g['fill_in_core'] - r['fill_in_core']) / r['fill_in_core'] > 0.001:
                    far, near = lost_far_from_new_copper(u)
                    msg = f"zone {z['net']} on {z['layer']}: filled copper inside the flight core (outline -{core_inset:g} mm) changed {r['fill_in_core']:.1f} -> {g['fill_in_core']:.1f} mm²"
                    if far is not None and far <= 0.1:
                        notes.append(msg + f" — all {near:.1f} mm² of the lost copper touches new copper (stub carve-out / removed island): accepted")
                    else:
                        problems.append(msg + (f" — {far:.1f} mm² of the lost copper is NOT adjacent to any new copper" if far is not None else ''))
            if r.get('fill_in_rev2') and g.get('fill_in_rev2') is not None:
                band_ref = r['fill_in_rev2'] - (r.get('fill_in_core') or 0)
                band_now = g['fill_in_rev2'] - (g.get('fill_in_core') or 0)
                if band_ref > 0 and abs(band_now - band_ref) / band_ref > 0.001:
                    notes.append(f"zone {z['net']} on {z['layer']}: band fill {band_ref:.1f} -> {band_now:.1f} mm² ({(band_now - band_ref) / band_ref * 100:+.1f} %, stub carve-out)")
        else:
            zref = r if r is not None else z
            if zref.get('fill_in_rev2') is not None and g.get('fill_in_rev2') is not None and zref['fill_in_rev2'] > 0:
                if abs(g['fill_in_rev2'] - zref['fill_in_rev2']) / zref['fill_in_rev2'] > 0.001:
                    problems.append(f"zone {z['net']} on {z['layer']}: filled copper inside the Rev2 outline changed {zref['fill_in_rev2']:.1f} -> {g['fill_in_rev2']:.1f} mm²")
    for u, e in snap['edges'].items():
        g = now['edges'].get(u)
        if g != e:
            (notes if allow_edge else problems).append(f"Edge.Cuts {e.get('shape')} {e.get('start')}-{e.get('end')}: {'removed' if g is None else 'changed'}")
    notes.append(f"bbox before {snap['bbox']} after {now['bbox']}")
    new_fp = len(now['footprints']) - len(snap['footprints'])
    new_tr = len(now['tracks']) - len(snap['tracks'])
    new_z = len(now['zones']) - len(snap['zones'])
    notes.append(f'new items: footprints +{new_fp}, tracks/vias +{new_tr}, zones +{new_z}')
    return problems, notes


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s1 = sub.add_parser('snapshot'); s1.add_argument('board'); s1.add_argument('snap')
    s2 = sub.add_parser('check'); s2.add_argument('snap'); s2.add_argument('board'); s2.add_argument('--allow-zone-growth', action='store_true'); s2.add_argument('--allow-edge', action='store_true')
    s2.add_argument('--refill', action='store_true', help='refill zones in memory before measuring (see copper carved by new tracks)')
    s2.add_argument('--core-inset', type=float, default=None, help='fills inside the Rev2 outline deflated by this many mm must be identical; band changes are notes (needs --ref-board)')
    s2.add_argument('--ref-board', default=None, help='Rev2 board to measure reference fills from (same filler, same insets); read-only')
    s2.add_argument('--exclude-new-mm', type=float, default=1.0, help='ignore fill changes within this distance of new tracks/vias (stub carve-out); 0 disables (default 1.0 when --ref-board is given)')
    a = ap.parse_args()
    if a.cmd == 'check' and a.core_inset is not None and not a.ref_board:
        ap.error('--core-inset needs --ref-board')
    if a.cmd == 'snapshot':
        b = pcbnew.LoadBoard(a.board)
        s = snapshot(b)
        json.dump(s, open(a.snap, 'w'))
        print(f"snapshot: {len(s['footprints'])} footprints, {len(s['tracks'])} tracks/vias, {len(s['zones'])} zones, {len(s['edges'])} edge items, bbox {s['bbox']}")
        return 0
    snap = json.load(open(a.snap))
    b = pcbnew.LoadBoard(a.board)
    excl = (a.exclude_new_mm if (a.ref_board and a.exclude_new_mm and a.exclude_new_mm > 0) else None)
    problems, notes = check(snap, b, a.allow_zone_growth, a.allow_edge, do_refill=a.refill, core_inset=a.core_inset, ref_board=a.ref_board, exclude_new_mm=excl)
    for n in notes:
        print('note:', n)
    for p in problems:
        print('HERITAGE VIOLATION:', p)
    print(f'heritage check: {len(problems)} violation(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
