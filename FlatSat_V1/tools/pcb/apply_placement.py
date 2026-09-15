#!/usr/bin/env python3
"""Apply a placement JSON to a board copy and report parts outside the outline.

  kicad-python apply_placement.py --board IN.kicad_pcb --placement floorplan.json --out OUT.kicad_pcb [--only-new]

floorplan.json: {"placements": {"U200": {"x": 250.0, "y": 60.0, "rot": 90, "side": "F"}, ...},
                 "notes": "..."}   (mm, degrees; side F or B)
Rules enforced here: a placement for a reference outside the Phase-1 blocks (200-799) is refused
unless --allow-heritage is given (heritage must not move). After applying, every footprint whose
pad copper is not fully inside the board outline is listed (exit 1 if any) -- pads are used rather
than the courtyard here because a courtyard is a mechanical keep-clear zone that routinely and
correctly overhangs the board edge for edge-mounted connectors, so it is the wrong shape to test
board containment with, unlike copper, which does need to be on the board. Separately, every
same-side pair of footprints (at least one of them newly placed) whose real F.CrtYd/B.CrtYd
courtyard polygons overlap is listed (exit 1 if any) -- courtyard is the right shape for that check
since it is the part-to-part keep-clear zone. Both checks fall back to the other shape, then to a
plain bounding box, when a footprint has no usable version of their preferred shape (noted in the
output); this replaces the previous axis-aligned-bounding-box tests, which gave false positives at
non-convex outline notches and for circular pads (mounting holes).
"""
import argparse
import json
import re
import sys

try:
    import pcbnew
except ImportError:
    sys.exit('run with KiCad\'s bundled python3')

NEW = re.compile(r'^[A-Z]{1,3}(2\d\d|3\d\d|4[0-4]\d|5\d\d|6[0-4]\d|7\d\d)$')

AREA_EPS_MM2 = 1e-4  # ignore polygon-boolean noise below this (mm^2); ~ a 0.01 x 0.01 mm speck
MM2_PER_IU2 = 1e-12  # pcbnew internal units are nm; 1 mm^2 = (1e6 nm)^2


def _area_mm2(poly):
    return poly.Area() * MM2_PER_IU2


def _bbox_poly(f):
    """Rectangle SHAPE_POLY_SET from f's axis-aligned bounding box (last-resort fallback)."""
    bb = f.GetBoundingBox(False, False)
    poly = pcbnew.SHAPE_POLY_SET()
    chain = poly.Outline(poly.NewOutline())
    for x, y in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()),
                 (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())):
        chain.Append(int(x), int(y))
    return poly


def _pad_union_poly(f, cu_layer):
    """Union of f's pad shapes on cu_layer, as a SHAPE_POLY_SET."""
    poly = pcbnew.SHAPE_POLY_SET()
    for pad in f.Pads():
        p = pad.GetEffectivePolygon(cu_layer)
        if p is not None and not p.IsEmpty():
            poly.BooleanAdd(p)
    return poly


def footprint_silhouette(f, prefer):
    """2D silhouette of footprint f on its own side, trying sources in preference order
    (falling through when a source is empty/negligible) down to prefer's alternate, then
    the bounding box (always available, least exact). Returns (poly, side, source) where
    side is 'F'/'B' and source is 'courtyard', 'pad-shape' or 'bbox'.

    Which source to prefer differs by what is being tested: a courtyard is a mechanical
    keep-clear zone, correct for testing whether two parts' zones collide, but routinely
    -- and correctly -- overhangs the board edge for edge-mounted connectors, so it is the
    wrong shape for testing whether a part is on the board; its copper pads are what
    actually needs to be on the board, so those are preferred for that test instead."""
    assert prefer in ('courtyard', 'pad-shape')
    side = 'B' if f.IsFlipped() else 'F'
    for source in (prefer, 'courtyard' if prefer == 'pad-shape' else 'pad-shape'):
        if source == 'courtyard':
            poly = f.GetCourtyard(pcbnew.B_CrtYd if side == 'B' else pcbnew.F_CrtYd)
        else:
            poly = _pad_union_poly(f, pcbnew.B_Cu if side == 'B' else pcbnew.F_Cu)
        if not poly.IsEmpty() and _area_mm2(poly) > AREA_EPS_MM2:
            return poly, side, source
    return _bbox_poly(f), side, 'bbox'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--board', required=True)
    ap.add_argument('--placement', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--allow-heritage', action='store_true')
    ap.add_argument('--check-only', action='store_true')
    a = ap.parse_args()
    board = pcbnew.LoadBoard(a.board)
    plan = json.load(open(a.placement))
    pl = plan.get('placements', plan)
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    applied, refused, missing = 0, [], []
    if not a.check_only:
        for ref, p in pl.items():
            f = fps.get(ref)
            if f is None:
                missing.append(ref)
                continue
            if not NEW.match(ref) and not a.allow_heritage:
                refused.append(ref)
                continue
            side = p.get('side', 'F').upper()
            if (side == 'B') != f.IsFlipped():
                f.Flip(f.GetPosition(), False)
            f.SetPosition(pcbnew.VECTOR2I_MM(float(p['x']), float(p['y'])))
            f.SetOrientationDegrees(float(p.get('rot', 0)))
            applied += 1
    outline = pcbnew.SHAPE_POLY_SET()
    try:
        ok = board.GetBoardPolygonOutlines(outline, False)
    except TypeError:
        ok = board.GetBoardPolygonOutlines(outline)

    # Two real per-footprint silhouettes, computed once and reused by both checks below
    # -- pads-preferred for board-containment, courtyard-preferred for part-vs-part
    # overlap (see footprint_silhouette's docstring for why they differ).
    bboxes = {}
    contain_info = {}  # ref -> (SHAPE_POLY_SET, source)
    overlap_info = {}  # ref -> (SHAPE_POLY_SET, side, source)
    is_new = {}
    fallback = []
    for ref, f in fps.items():
        bboxes[ref] = f.GetBoundingBox(False, False)
        is_new[ref] = bool(NEW.match(ref))
        c_poly, _side, c_source = footprint_silhouette(f, 'pad-shape')
        contain_info[ref] = (c_poly, c_source)
        o_poly, o_side, o_source = footprint_silhouette(f, 'courtyard')
        overlap_info[ref] = (o_poly, o_side, o_source)
        if c_source != 'pad-shape' or o_source != 'courtyard':
            fallback.append(f'{ref}(outline:{c_source},overlap:{o_source})')

    outside = []
    if ok:
        for ref, (poly, source) in contain_info.items():
            leftover = pcbnew.SHAPE_POLY_SET(poly)
            leftover.BooleanSubtract(outline)
            if _area_mm2(leftover) > AREA_EPS_MM2:
                outside.append(ref)

    # Courtyard overlaps: same side only (a top and a bottom courtyard cannot collide),
    # at least one of the pair a newly-placed (Phase-2) part -- heritage-vs-heritage
    # overlaps are pre-existing and out of scope here (kicad-cli DRC already tracks the
    # one accepted Rev2 case). A cheap bounding-box pre-filter runs before the exact
    # polygon intersection test.
    refs = list(overlap_info.keys())
    overlaps = []
    for i, ref_i in enumerate(refs):
        poly_i, side_i, _s = overlap_info[ref_i]
        for ref_j in refs[i + 1:]:
            if not (is_new[ref_i] or is_new[ref_j]):
                continue
            poly_j, side_j, _s = overlap_info[ref_j]
            if side_i != side_j or not bboxes[ref_i].Intersects(bboxes[ref_j]):
                continue
            inter = pcbnew.SHAPE_POLY_SET(poly_i)
            inter.BooleanIntersection(poly_j)
            if _area_mm2(inter) > AREA_EPS_MM2:
                overlaps.append((ref_i, ref_j))

    print(f'applied {applied}; refused (heritage) {refused[:10]}{"..." if len(refused) > 10 else ""}; missing refs {missing[:10]}')
    print(f'footprints not fully inside the outline: {len(outside)}: {sorted(outside)[:40]}')
    print(f'courtyard overlaps (same-side, >=1 new part; real polygons): {len(overlaps)}: {sorted(overlaps)[:40]}')
    print(f'footprints missing their preferred silhouette (pad-shape for outline, courtyard for overlap), using a fallback: {len(fallback)}: {sorted(fallback)[:40]}')
    if not a.check_only:
        pcbnew.SaveBoard(a.out, board)
        print('saved', a.out)
    return 1 if outside or refused or missing or overlaps else 0


if __name__ == '__main__':
    sys.exit(main())
