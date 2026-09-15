#!/usr/bin/env python3
"""Helpers for the Freerouting round-trip recipe (see tools/pcb/README.md).

Freerouting's default DSN/SES round trip does not preserve flight heritage: (1) KiCad's
ExportSpecctraDSN silently fails (returns False / writes nothing) if any two footprints share a
reference designator, which happens on this board because of 5 unannotated "G***" LOGO graphics;
(2) every existing track/via is exported as Specctra `(type route)`, i.e. free for Freerouting to
rip up, fan out vias next to, or shift during optimization; (3) KiCad's SES importer deletes and
re-creates ALL track/via objects on the board (new uuids for heritage items too), so a uuid-keyed
heritage check (tools/pcb/heritage.py) reports every pre-existing track/via as "removed" even when
its geometry did not move a micron.

Run all subcommands with KiCad's bundled python3:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 \\
      tools/pcb/route_merge.py <subcommand> ...

Subcommands
-----------
prep BOARD OUT
    Disambiguate duplicate/blank footprint references (renamed to REF__dup2, REF__dup3, ...) so
    ExportSpecctraDSN succeeds. Safe: tools/pcb/heritage.py never compares the reference string,
    only uuid/position/rotation/layer/fpid/pad-nets, so renaming a duplicated ref does not trip it.
    Run this on your routing copy before tools/pcb/route.sh.

fixdsn DSN OUT
    Mark every wire and via in a Specctra DSN's `wiring` section `(type fix)` instead of
    `(type route)`. Every wire/via present in the DSN at export time is, by definition, a
    pre-existing (heritage) connection -- nets added by the sync have nothing routed yet. Freerouting
    honours `(type fix)`: fixed wires/vias are excluded from rip-up and from the optimizer, so it
    only touches the actually-unrouted (new) connections. Run this on the .dsn that
    tools/pcb/route.sh's DSN-export step produces, before invoking Freerouting (route.sh does the
    export/route/import/DRC in one shot, so either call route.sh's export step yourself and hand it
    the fixed DSN via `-de`, or run route.sh once to get IN.dsn, fix it in place, then re-run
    Freerouting by hand with the same -do/-mp flags route.sh would have used -- see README.md).

keepout BOARD OUT --outline-source SRC_BOARD [--inset-mm 12]
    Add a temporary pcbnew rule-area zone (tracks/vias forbidden, zone fills/copper pour still
    allowed) covering SRC_BOARD's own Edge.Cuts outline, inset by --inset-mm, on every copper layer.
    Confirmed empirically: KiCad's ExportSpecctraDSN emits this as a proper Specctra keepout, one
    `(keepout "" (polygon LAYER 0 ...))` record per copper layer in the `structure` section --
    Freerouting then refuses to place a wire or via inside it. Add this to the DSN-export copy only
    (never to the copy SES gets imported into) so no leftover keepout zone ends up in the delivered
    board -- see README.md "Flight-section keep-out".

keepout-check PRE POST --outline-source SRC_BOARD [--inset-mm 12]
    After routing with (or without) a keepout: list every track/via in POST that is new relative to
    PRE (same signature diff as `merge`) and has an endpoint inside SRC_BOARD's outline inset by
    --inset-mm. Exit 1 if any are found. Use this as the actual proof that nothing landed in the
    flight section -- do not rely on the keepout zone alone (it depends on Freerouting choosing to
    honour it).

merge PRE POST OUT [--report]
    The safety net. PRE is the exact board handed to the DSN exporter (after `prep`); POST is the
    board tools/pcb/route.sh produced after SES import. OUT is written by literally copying PRE
    (so every heritage footprint/track/via/zone/edge keeps its original uuid and geometry, byte
    for byte) and then adding only the tracks/vias from POST whose (net, layer, start, end, width)
    signature -- for vias: (net, position, pad diameter, drill) -- has no match anywhere in PRE.
    That is the "new" set regardless of what uuids SES import assigned. Nothing from PRE is ever
    replaced, moved, or deleted, so tools/pcb/heritage.py is guaranteed 0 violations on OUT (edges
    reported only if PRE's outline already differs from the snapshot, e.g. a deliberate outline
    extension -- pass --allow-edge to heritage.py check in that case).
    Echo filter (default): Freerouting redraws/splits/merges (type fix) heritage wires when it
    writes the SES, so many "new-signature" items are just echoes of untouched heritage copper
    (measured on the 2026-09-14 smoke run: 120 of 337). New items are grouped into connected chains
    and a chain is adopted only if it reaches a pad of a NEW (ref 200-799) footprint; echo chains
    and degenerate (<0.01 mm) segments are dropped. --adopt-all restores the old adopt-everything
    behaviour. --report adds a per-net breakdown of what was adopted.

Usage examples:
  route_merge.py prep synced.kicad_pcb prepped.kicad_pcb
  tools/pcb/route.sh prepped.kicad_pcb routed.kicad_pcb 3        # (or export the DSN yourself, run fixdsn, then freerouting + SES import by hand)
  route_merge.py merge prepped.kicad_pcb routed.kicad_pcb merged.kicad_pcb --report
  heritage.py check heritage.json merged.kicad_pcb --allow-zone-growth --allow-edge
"""
import argparse
import re
import sys
from collections import Counter, defaultdict

try:
    import pcbnew
except ImportError:
    sys.exit("run with KiCad's bundled python3")

MM = pcbnew.VECTOR2I_MM


def mm(v):
    return round(pcbnew.ToMM(v), 4)


# ---------------------------------------------------------------------------
# prep
# ---------------------------------------------------------------------------

def cmd_prep(a):
    board = pcbnew.LoadBoard(a.board)
    seen = Counter()
    renamed = []
    for f in board.GetFootprints():
        ref = f.GetReference()
        seen[ref] += 1
        if seen[ref] > 1:
            new_ref = '%s__dup%d' % (ref, seen[ref])
            f.SetReference(new_ref)
            renamed.append((ref, new_ref))
    if renamed:
        print('renamed %d duplicate/blank references so ExportSpecctraDSN will succeed:' % len(renamed))
        for old, new in renamed:
            print('  %s -> %s' % (old, new))
    else:
        print('no duplicate references found (DSN export should already work)')
    board.Save(a.out)
    print('saved', a.out)


# ---------------------------------------------------------------------------
# fixdsn
# ---------------------------------------------------------------------------

WIRE_RE = re.compile(r'\(wire \(path (\S+) ([\d.]+)\s+([^)]+)\)(\(net (?:\S+|"[^"]*")\)\(type \S+\)\))')


def _clean_wire(m):
    """Drop a wire record entirely if every path point collapses to one distinct point (a
    zero-length stub); otherwise dedupe consecutive duplicate points and keep it. This board's
    DSN export carries a handful of pre-existing zero-length wire stubs (e.g. a track re-clicked
    at the same point in the KiCad GUI once, years ago). Freerouting 2.4.1 does not just warn about
    them (see the BasicBoard.normalizeTraces 2000-iteration warnings, which ARE capped and
    harmless) -- feeding one to the auto-router's pathfinder makes it spin forever on
    'Polyline: must contain at least 2 different points' with no iteration cap, never producing a
    .ses file. Empirically: on FlatSat_V1 as synced, exactly 4 of 2586 wires are affected; removing
    them (this function) is what let Freerouting finish at all. Safe regardless: these stubs carry
    no heritage geometry (zero length), and the merge step never depends on this DSN's wires for
    what heritage geometry ends up in the output anyway -- it always restores heritage tracks from
    the untouched PRE board."""
    layer, width, coordstr, rest = m.group(1), m.group(2), m.group(3), m.group(4)
    nums = coordstr.split()
    pts = list(zip(nums[0::2], nums[1::2]))
    dedup = [pts[0]]
    for p in pts[1:]:
        if p != dedup[-1]:
            dedup.append(p)
    if len(dedup) < 2:
        return ''
    newcoord = '  ' + '  '.join('%s %s' % p for p in dedup)
    return '(wire (path %s %s%s)%s' % (layer, width, newcoord, rest)


def cmd_fixdsn(a):
    text = open(a.dsn, encoding='utf-8').read()
    text, n_dropped = WIRE_RE.subn(_clean_wire, text)
    # subn replaces every match; count how many became '' (dropped) vs kept-but-cleaned
    dropped = len(WIRE_RE.findall(open(a.dsn, encoding='utf-8').read())) - len(re.findall(r'\(wire \(path', text))
    n = text.count('(type route)')
    text = text.replace('(type route)', '(type fix)')
    open(a.out, 'w', encoding='utf-8').write(text)
    print('dropped %d zero-length wire stub(s) (duplicate-point paths -- see docstring)' % dropped)
    print('marked %d wire/via records (type route) -> (type fix) in %s' % (n, a.out))
    if n == 0:
        print('WARNING: no "(type route)" records found -- is this really a freshly exported DSN?')


# ---------------------------------------------------------------------------
# merge
# ---------------------------------------------------------------------------

def track_sig(t):
    s, e = t.GetStart(), t.GetEnd()
    if t.GetClass() == 'PCB_VIA':
        return ('via', t.GetNetname(), mm(s.x), mm(s.y), mm(t.GetWidth(pcbnew.F_Cu)), mm(t.GetDrillValue()))
    layer = t.GetLayer()
    return ('track', t.GetNetname(), layer, mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(t.GetWidth()))


NEW_REF = re.compile(r'^[A-Z]{1,3}(2\d\d|3\d\d|4[0-4]\d|5\d\d|6[0-4]\d|7\d\d)$')  # Phase-1 staged-part ref blocks (matches apply_placement.py / drc_summary.py)


def item_touches_new_footprint(item, new_pad_points, tol_mm=0.001):
    """True if this track/via shares an endpoint with a pad belonging to a Phase-1 (new, ref block
    200-799) footprint. new_pad_points is a list of (x_mm, y_mm) precomputed once per board."""
    pts = [item.GetStart()]
    if item.GetClass() != 'PCB_VIA':
        pts.append(item.GetEnd())
    for p in pts:
        px, py = mm(p.x), mm(p.y)
        for nx, ny in new_pad_points:
            if abs(px - nx) < tol_mm and abs(py - ny) < tol_mm:
                return True
    return False


def _pt_key(p):
    return (round(pcbnew.ToMM(p.x), 3), round(pcbnew.ToMM(p.y), 3))


def chains_of(items, board, keep_layers=None):
    """Group tracks/vias into electrically connected chains (coincident endpoints on the same layer;
    a via joins every layer at its position). Returns a list of lists of items."""
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    via_pts = {_pt_key(t.GetPosition()) for t in items if t.GetClass() == 'PCB_VIA'}
    node_of = {}
    for i, t in enumerate(items):
        if t.GetClass() == 'PCB_VIA':
            nodes = [(_pt_key(t.GetPosition()), '*')]
        else:
            nodes = []
            for p in (t.GetStart(), t.GetEnd()):
                k = _pt_key(p)
                nodes.append((k, t.GetLayer()))
                if k in via_pts:
                    nodes.append((k, '*'))
        node_of[i] = nodes
        for n in nodes:
            union(('item', i), ('node', n))
    groups = defaultdict(list)
    for i, t in enumerate(items):
        groups[find(('item', i))].append(t)
    return list(groups.values())


def item_pads_touched(t, pads):
    """Pads (from the precomputed list of (pad, bbox, layers)) that this track/via lands on."""
    hits = []
    if t.GetClass() == 'PCB_VIA':
        pts = [(t.GetPosition(), None)]
    else:
        pts = [(t.GetStart(), t.GetLayer()), (t.GetEnd(), t.GetLayer())]
    for p, layer in pts:
        for pad, bbox, fp_ref in pads:
            if not bbox.Contains(p):
                continue
            if layer is not None and not pad.IsOnLayer(layer):
                continue
            if pad.HitTest(p):
                hits.append((fp_ref, pad.GetNumber()))
    return hits


def cmd_merge(a):
    pre = pcbnew.LoadBoard(a.pre)
    post = pcbnew.LoadBoard(a.post)

    pre_sigs = set()
    for t in pre.GetTracks():
        pre_sigs.add(track_sig(t))

    new_items = [t for t in post.GetTracks() if track_sig(t) not in pre_sigs]
    print('PRE tracks/vias: %d   POST tracks/vias: %d   new (by geometry+net): %d'
          % (len(pre_sigs), len(list(post.GetTracks())), len(new_items)))

    if not a.adopt_all:
        # Freerouting redraws, splits or merges (type fix) heritage wires when it writes the SES, and
        # KiCad's SES import rebuilds every track from that file. Those "echo" segments have no PRE
        # signature so they look new, but they are redundant copper on top of untouched heritage
        # (and, worse, land inside the flight section where the L11 rule forbids new copper).
        # Only a chain of new items that actually reaches a pad of a NEW (Phase-1, ref 200-799)
        # footprint can be a genuinely new route; everything else is an echo and is dropped here.
        new_pads = [(pad, pad.GetBoundingBox(), fp.GetReference())
                    for fp in post.GetFootprints() if NEW_REF.match(fp.GetReference())
                    for pad in fp.Pads()]
        chains = chains_of(new_items, post)
        kept, dropped_items, dropped_chains = [], 0, 0
        echo_by_net = Counter()
        for ch in chains:
            if any(item_pads_touched(t, new_pads) for t in ch):
                kept.extend(ch)
            else:
                dropped_chains += 1
                dropped_items += len(ch)
                echo_by_net[ch[0].GetNetname()] += len(ch)
        degenerate = [t for t in kept if t.GetClass() != 'PCB_VIA'
                      and abs(t.GetEnd().x - t.GetStart().x) + abs(t.GetEnd().y - t.GetStart().y) < pcbnew.FromMM(0.01)]
        kept = [t for t in kept if t not in degenerate]
        print('  chains of new items: %d; adopted %d chain(s) (%d items) that reach a new-footprint pad;'
              ' dropped %d heritage-echo chain(s) (%d items) + %d degenerate (<0.01 mm) segment(s)'
              % (len(chains), len(chains) - dropped_chains, len(kept), dropped_chains, dropped_items,
                 len(degenerate)))
        if echo_by_net:
            print('  echo items by net (top 10): ' + ', '.join('%s=%d' % kv for kv in echo_by_net.most_common(10)))
        new_items = kept

    if a.report:
        new_pad_points = [(mm(pad.GetPosition().x), mm(pad.GetPosition().y))
                           for fp in post.GetFootprints() if NEW_REF.match(fp.GetReference())
                           for pad in fp.Pads()]
        touch_new = 0
        review = 0
        by_net = defaultdict(int)
        for t in new_items:
            by_net[t.GetNetname()] += 1
            if item_touches_new_footprint(t, new_pad_points):
                touch_new += 1
            else:
                review += 1
        print('  touching a new (Phase-1, ref 200-799) footprint pad: %d' % touch_new)
        print('  review (no new-footprint pad on this item -- either it is entirely between new'
              ' footprints via an intermediate point, or Freerouting split/redrew a heritage segment;'
              ' the original heritage segment is untouched underneath either way): %d' % review)
        print('  by net (top 20):')
        for net, n in sorted(by_net.items(), key=lambda kv: -kv[1])[:20]:
            print('    %-30s %d' % (net, n))

    # OUT = PRE, verbatim, plus clones of the new items.
    out = pcbnew.LoadBoard(a.pre)
    added = 0
    for t in new_items:
        clone = t.Duplicate().Cast()
        out.Add(clone)
        added += 1
    out.Save(a.out)
    print('wrote %s: %d heritage tracks/vias untouched (original uuids) + %d new tracks/vias adopted'
          % (a.out, len(pre_sigs), added))


# ---------------------------------------------------------------------------
# keepout / keepout-check
# ---------------------------------------------------------------------------

def _deflated_outline_points(source_board_path, inset_mm):
    """Rev2 board outline (from source_board_path's own Edge.Cuts), inset by inset_mm, as a list of
    outlines (each a list of (x_mm, y_mm) tuples)."""
    src = pcbnew.LoadBoard(source_board_path)
    poly = pcbnew.SHAPE_POLY_SET()
    src.GetBoardPolygonOutlines(poly, False)
    poly.Inflate(-pcbnew.FromMM(inset_mm), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05))
    outlines = []
    for i in range(poly.OutlineCount()):
        o = poly.Outline(i)
        outlines.append([(mm(o.CPoint(k).x), mm(o.CPoint(k).y)) for k in range(o.PointCount())])
    return outlines


def _point_in_poly(pt, poly):
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
    return inside


def cmd_keepout(a):
    outlines = _deflated_outline_points(a.outline_source, a.inset_mm)
    print('deflated outline(s):', [len(o) for o in outlines], 'points, inset %.1f mm' % a.inset_mm)
    board = pcbnew.LoadBoard(a.board)
    n_layers = board.GetCopperLayerCount()
    layers = [board.GetLayerID(n) for n in (['F.Cu'] + ['In%d.Cu' % i for i in range(1, n_layers - 1)] + ['B.Cu'])]
    ls = pcbnew.LSET()
    for l in layers:
        ls.AddLayer(l)
    added = 0
    for outline in outlines:
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetDoNotAllowZoneFills(False)
        z.SetDoNotAllowFootprints(False)
        z.SetDoNotAllowPads(False)
        z.SetZoneName('FLIGHT_KEEPOUT')
        z.SetLayerSet(ls)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in outline:
            ol.Append(MM(x, y))
        board.Add(z)
        added += 1
    print('rule-area keepout zone(s) added: %d, on layers %s' % (added, [board.GetLayerName(l) for l in layers]))
    board.Save(a.out)
    print('saved', a.out, '-- export DSN from THIS copy; import the resulting SES into a copy WITHOUT this zone')


def cmd_keepout_check(a):
    outlines = _deflated_outline_points(a.outline_source, a.inset_mm)
    pre = pcbnew.LoadBoard(a.pre)
    post = pcbnew.LoadBoard(a.post)
    pre_sigs = {track_sig(t) for t in pre.GetTracks()}
    new_items = [t for t in post.GetTracks() if track_sig(t) not in pre_sigs]
    violations = []
    for t in new_items:
        pts = [t.GetStart()]
        if t.GetClass() != 'PCB_VIA':
            pts.append(t.GetEnd())
        for p in pts:
            pt = (mm(p.x), mm(p.y))
            if any(_point_in_poly(pt, o) for o in outlines):
                violations.append((t.GetClass(), t.GetNetname(), pt))
                break
    print('new tracks/vias checked: %d' % len(new_items))
    if violations:
        for cls, net, pt in violations:
            print('KEEPOUT VIOLATION: %s net=%s endpoint=%s is inside the flight-section keepout' % (cls, net, pt))
    print('keepout check: %d violation(s)' % len(violations))
    return 1 if violations else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('prep', help='disambiguate duplicate footprint refs so DSN export works')
    p.add_argument('board')
    p.add_argument('out')
    p.set_defaults(func=cmd_prep)

    p = sub.add_parser('fixdsn', help='mark every existing wire/via (type fix) in a Specctra DSN')
    p.add_argument('dsn')
    p.add_argument('out')
    p.set_defaults(func=cmd_fixdsn)

    p = sub.add_parser('merge', help='adopt only new tracks/vias onto an untouched copy of PRE')
    p.add_argument('pre')
    p.add_argument('post')
    p.add_argument('out')
    p.add_argument('--report', action='store_true')
    p.add_argument('--adopt-all', action='store_true',
                   help='old behaviour: adopt every new-signature item, including Freerouting echoes of heritage wires')
    p.set_defaults(func=cmd_merge)

    p = sub.add_parser('keepout', help='add a flight-section rule-area keepout to a DSN-export copy')
    p.add_argument('board')
    p.add_argument('out')
    p.add_argument('--outline-source', required=True, help='board to take the outline from (e.g. the original un-synced Rev2 board)')
    p.add_argument('--inset-mm', type=float, default=12.0)
    p.set_defaults(func=cmd_keepout)

    p = sub.add_parser('keepout-check', help='verify no new track/via landed inside the flight-section keepout')
    p.add_argument('pre')
    p.add_argument('post')
    p.add_argument('--outline-source', required=True)
    p.add_argument('--inset-mm', type=float, default=12.0)
    p.set_defaults(func=cmd_keepout_check)

    a = ap.parse_args()
    rc = a.func(a)
    return rc if rc is not None else 0


if __name__ == '__main__':
    sys.exit(main())
