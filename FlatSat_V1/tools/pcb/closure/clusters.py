#!/usr/bin/env python3
"""Connected-component view of a net, using KiCad's own connectivity engine.

Promoted from .flatsat_work/phase2/clusters.py (closure round 2, route_report.md D7)
unchanged except for the argparse wrapper below -- the algorithm in build()/describe()
is byte-for-byte the scratch version.

WHAT IT DOES
    For every net on the board, walks KiCad's connectivity graph (board.BuildConnectivity() /
    GetConnectivity()) starting from every track and pad on that net and groups them into
    electrically-connected clusters. A net with exactly one cluster is fully connected. A net
    with N > 1 clusters has N - 1 missing connections -- this is the same number KiCad's own DRC
    "unconnected items" count reports for that net, but with every item that makes up each
    cluster named, not just the ratsnest endpoints.

INPUTS
    BOARD   a .kicad_pcb path, loaded read-only (LoadBoard never mutates and this script never
            calls SaveBoard) -- safe to run directly against a live board.
    NET     zero or more net names to report in detail (bare name or full hierarchical name,
            e.g. both "GND" and ".../GND" match). With no net names, every net that has more
            than one cluster is listed (summary line only).

OUTPUT
    stdout only, nothing written to disk:
      - with NET args: one summary line per requested net plus, for each net, one indented line
        per cluster listing up to 8 member items (pad ref.num or track/via class, position in mm).
      - with no NET args: one summary line per net that is NOT fully connected, sorted by
        cluster count descending, followed by "total extra clusters (= minimum missing
        connections): N" -- N is a lower bound on DRC's unconnected-item count for the board.

EXACTNESS GUARANTEE
    Uses pcbnew's own BuildConnectivity()/GetConnectivity(), the same engine KiCad's DRC and
    ratsnest use -- no independent geometry model, so it never disagrees with DRC's unconnected
    count in the direction that matters (it can only look wrong if the caller reads a name that
    doesn't exist; the algorithm itself is exact, not heuristic).

USAGE
    clusters.py BOARD [NET ...]
    clusters.py BOARD --net GND --net "+3V3_EMU"   (equivalent long form, repeatable)
"""
import argparse
from collections import defaultdict

import pcbnew

TOMM = pcbnew.ToMM


def build(board):
    """Return {netcode: [cluster, ...]} where each cluster is a list of connected items.

    Unchanged from the scratch version (route_report.md D7) -- algorithm untouched by promotion.
    """
    board.BuildConnectivity()
    conn = board.GetConnectivity()
    items = defaultdict(list)          # netcode -> [item]
    for t in board.GetTracks():
        if t.GetNetCode():
            items[t.GetNetCode()].append(t)
    for fp in board.GetFootprints():
        for pd in fp.Pads():
            if pd.GetNetCode():
                items[pd.GetNetCode()].append(pd)
    out = {}
    for nc, its in items.items():
        seen = {}
        clusters = []
        for it in its:
            k = it.m_Uuid.AsString()
            if k in seen:
                continue
            grp = [it]
            for o in conn.GetConnectedItems(it):
                if o.GetNetCode() == nc:
                    grp.append(o)
            idx = len(clusters)
            keep = []
            for g in grp:
                gk = g.m_Uuid.AsString()
                if gk in seen:
                    continue
                seen[gk] = idx
                keep.append(g)
            clusters.append(keep)
        out[nc] = [c for c in clusters if c]
    return out


def describe(it):
    """One-line human description of a pad/track/via item. Unchanged from scratch version."""
    if it.GetClass() == 'PAD':
        p = it.GetPosition()
        return f'pad {it.GetParentFootprint().GetReference()}.{it.GetNumber()} ({TOMM(p.x):.2f},{TOMM(p.y):.2f})'
    p = it.GetPosition()
    return f'{it.GetClass()} ({TOMM(p.x):.2f},{TOMM(p.y):.2f})'


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description='Connected-component view of every net on a board (KiCad connectivity engine).')
    ap.add_argument('board', help='.kicad_pcb path (read-only -- this tool never writes)')
    ap.add_argument('nets', nargs='*', metavar='NET',
                     help='net names to report in detail (bare or full hierarchical name); '
                          'with none given, every multi-cluster net is summarised')
    ap.add_argument('--net', action='append', dest='nets_opt', default=[],
                     help='same as a positional NET; repeatable long form')
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    want = set(args.nets) | set(args.nets_opt)
    board = pcbnew.LoadBoard(args.board)
    cl = build(board)
    tot = 0
    for nc, cs in sorted(cl.items(), key=lambda kv: -len(kv[1])):
        name = board.FindNet(nc).GetNetname()
        if want and name not in want and name.rsplit('/', 1)[-1] not in want:
            continue
        if len(cs) < 2 and not want:
            continue
        tot += len(cs) - 1
        print(f'{name:45s} {len(cs)} cluster(s), sizes {[len(c) for c in cs]}')
        if want:
            for i, c in enumerate(cs):
                print(f'   [{i}] ' + '; '.join(describe(x) for x in c[:8]) + (' ...' if len(c) > 8 else ''))
    print(f'total extra clusters (= minimum missing connections): {tot}')


if __name__ == '__main__':
    main()
