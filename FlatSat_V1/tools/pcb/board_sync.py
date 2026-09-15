#!/usr/bin/env python3
"""Scripted equivalent of Eeschema's "Update PCB from Schematic" for the FlatSat project.

Run with KiCad's bundled Python (it needs the pcbnew module):
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 \
      tools/pcb/board_sync.py --board FlatSat_V1.kicad_pcb --netlist <kicadxml> --out <out.kicad_pcb> \
      [--stage-origin 245 50] [--stage-pitch 4.0] [--dry-run]

What it does, in order:
  1. Renames board nets whose schematic name changed (the eight Phase-1 label promotions:
     "/Power Systems/B-" -> "B-", ...). Renaming the NETINFO_ITEM in place keeps every pad, track,
     via and zone that referenced it.
  2. Creates every schematic net the board does not have yet.
  3. For every schematic component whose reference has no footprint on the board: loads the footprint
     from the library named in the netlist (project fp-lib-table first, then the global easyeda2kicad
     library, then the KiCad standard footprints), sets reference/value/fields, sets the KiCad path
     ("/<sheet symbol uuid>/<symbol uuid>", i.e. the sheetpath tstamps below the root plus the symbol's
     tstamp), assigns pad nets by pad number, and places it on a staging grid east of the board outline
     (F.Cu). Nothing already on the board is moved.
  4. For every existing footprint: re-checks pad nets against the schematic and fixes mismatches
     (reported), sets Sheetname/Sheetfile fields if missing.
  5. Reports components on the board that the schematic no longer has (never deleted automatically).
  6. Saves to --out (never overwrite the input unless --out is the same path on purpose).

Acceptance test afterwards:
  kicad-cli pcb drc --schematic-parity --severity-all --format json --output x.json <out.kicad_pcb>
  -> "schematic_parity" must be an empty list (tools/pcb/drc_summary.py prints it).
"""
import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET

try:
    import pcbnew
except ImportError:
    sys.exit('run this with KiCad\'s bundled python3 (pcbnew module not found)')

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
STD_FP = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'
GLOBAL_TABLE = os.path.expanduser('~/Library/Preferences/kicad/10.0/fp-lib-table')
INTERNAL_PROPS = {'Sheetname', 'Sheetfile', 'ki_keywords', 'ki_fp_filters', 'ki_description', 'Footprint', 'Reference', 'Value', 'Datasheet', 'Description'}


def parse_lib_table(path, base):
    libs = {}
    if not os.path.exists(path):
        return libs
    text = open(path, encoding='utf-8').read()
    for m in re.finditer(r'\(lib\s+\(name\s+"([^"]+)"\)\s*\(type\s+"([^"]+)"\)\s*\(uri\s+"([^"]+)"\)', text):
        name, typ, uri = m.groups()
        uri = uri.replace('${KIPRJMOD}', base).replace('${KICAD10_FOOTPRINT_DIR}', STD_FP).replace('${KICAD_3RD_PARTY}', os.path.expanduser('~/Documents/KiCad/10.0/3rdparty'))
        libs[name] = (typ, uri)
    return libs


def resolve_footprint_dir(nickname, proj_dir):
    tables = [parse_lib_table(os.path.join(proj_dir, 'fp-lib-table'), proj_dir), parse_lib_table(GLOBAL_TABLE, proj_dir)]
    for t in tables:
        if nickname in t and t[nickname][0] == 'KiCad':
            return t[nickname][1]
    cand = os.path.join(STD_FP, nickname + '.pretty')
    if os.path.isdir(cand):
        return cand
    return None


AUTO_NET = re.compile(r'^(Net-\(|unconnected-\()(.*)(\))$')


def board_netname(name):
    """The kicadxml netlist writes auto-generated net names unescaped (Net-(U12-TR/SS)); the board stores them
    the way Eeschema escapes them (Net-(U12-TR{slash}SS)) and the DRC parity check compares against that form.
    Hierarchical path separators ("/Power Systems/X") are real slashes and are left alone."""
    m = AUTO_NET.match(name)
    if not m:
        return name
    return m.group(1) + m.group(2).replace('/', '{slash}') + m.group(3)


def canon(name):
    """Comparison form: unescape and drop KiCad's _N uniqueness suffix on unconnected-(...) nets."""
    n = name.replace('{slash}', '/')
    return re.sub(r'^(unconnected-\(.*\))_\d+$', r'\1', n)


def load_netlist(path):
    r = ET.parse(path).getroot()
    comps = {}
    for c in r.find('components'):
        ref = c.get('ref')
        props = {p.get('name'): p.get('value') for p in c.findall('property')}
        sp = c.find('sheetpath')
        comps[ref] = {
            'ref': ref,
            'value': c.findtext('value') or '',
            'footprint': c.findtext('footprint') or '',
            'datasheet': c.findtext('datasheet') or '',
            'description': c.findtext('description') or '',
            'sheet_names': sp.get('names') if sp is not None else '/',
            'sheet_tstamps': sp.get('tstamps') if sp is not None else '/',
            'tstamps': c.findtext('tstamps') or '',
            'props': props,
            'pins': {},
        }
    nets = {}
    for n in r.find('nets'):
        name = board_netname(n.get('name'))
        nets[name] = []
        for node in n.findall('node'):
            nets[name].append((node.get('ref'), node.get('pin')))
            if node.get('ref') in comps:
                comps[node.get('ref')]['pins'][node.get('pin')] = name
    return comps, nets


def kicad_path(comp):
    # kicadxml sheetpath tstamps is "/<sheet symbol uuid>/<sub-sheet uuid>/" (root omitted) or "/" for the root;
    # the board path is that chain plus the symbol's own uuid: "/<sheet uuid>/<symbol uuid>"
    sp = comp['sheet_tstamps'].strip('/')
    parts = sp.split('/') if sp else []
    return '/' + '/'.join(parts + [comp['tstamps'].split(' ')[0]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--board', required=True)
    ap.add_argument('--netlist', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--stage-origin', nargs=2, type=float, default=[245.0, 50.0], help='mm, top-left of the staging grid (east of the board)')
    ap.add_argument('--stage-pitch', type=float, default=12.0)
    ap.add_argument('--stage-cols', type=int, default=20)
    ap.add_argument('--rename', action='append', default=[], help='OLD=NEW net rename (repeatable); default = the eight Phase-1 promotions')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    proj_dir = os.path.dirname(os.path.abspath(a.board))
    board = pcbnew.LoadBoard(a.board)
    comps, nets = load_netlist(a.netlist)
    report = {'renamed': [], 'nets_created': [], 'added': [], 'net_fixes': [], 'missing_footprint': [], 'orphans': [], 'field_updates': 0}

    renames = a.rename or [
        '/Power Systems/B-=B-', '/Power Systems/VBATT_SENSE=VBATT_SENSE', '/Power Systems/INHIB_1=INHIB_1',
        '/Power Systems/INHIB_2=INHIB_2', '/Power Systems/IN_RBF=IN_RBF',
        '/Power Systems/Load Switches/Deploy1_EN=Deploy1_EN', '/Power Systems/Load Switches/Heater_EN=Heater_EN',
        '/Power Systems/Load Switches/Deploy2_EN=Deploy2_EN',
    ]
    # 1. renames
    for spec in renames:
        old, new = spec.split('=', 1)
        ni = board.FindNet(old)
        if ni is None:
            continue
        if board.FindNet(new) is not None:
            print(f'rename {old} -> {new}: target exists, merging is not automatic; skipped', file=sys.stderr)
            continue
        ni.SetNetname(new)
        report['renamed'].append(f'{old} -> {new}')
    # 2. create nets (including KiCad's per-pin "unconnected-(REF-PIN-PadN)" nets, which parity expects on no-connect pads)
    for name in nets:
        if board.FindNet(name) is None:
            board.Add(pcbnew.NETINFO_ITEM(board, name))
            report['nets_created'].append(name)

    def netitem(name):
        if not name:
            return board.FindNet('') or board.GetNetInfo().GetNetItem(0)
        ni = board.FindNet(name)
        if ni is None:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)
            report['nets_created'].append(name)
        return ni

    existing = {f.GetReference(): f for f in board.GetFootprints()}
    bb = board.GetBoardEdgesBoundingBox()
    east = pcbnew.ToMM(bb.GetRight())
    ox = max(a.stage_origin[0], east + 8.0)
    oy = a.stage_origin[1]
    slot = 0
    # 3. add missing footprints, sorted so each sheet's parts are grouped on the staging grid
    order = sorted((c for c in comps.values() if c['ref'] not in existing and not c['ref'].startswith('#')), key=lambda c: (c['sheet_names'], re.sub(r'\d+', lambda m: m.group(0).zfill(5), c['ref'])))
    for comp in order:
        fp_id = comp['footprint']
        if not fp_id or ':' not in fp_id:
            report['missing_footprint'].append((comp['ref'], fp_id or '(empty)'))
            continue
        nick, name = fp_id.split(':', 1)
        fp = None
        # Prefer a copy of the same footprint already on the FC board (identical pads to the heritage part,
        # e.g. the USB-C HRO receptacle whose on-board copy carries the S1 shield pads); else load from a library.
        donor = next((f for f in board.GetFootprints() if f.GetFPIDAsString() == fp_id), None)
        if donor is not None:
            fp = donor.Duplicate(False).Cast()
            fp.SetOrientationDegrees(0)
            if fp.IsFlipped():
                fp.Flip(fp.GetPosition(), False)
            for pad in fp.Pads():
                pad.SetNet(netitem(''))
            for item in list(fp.GraphicalItems()):
                pass
            report.setdefault('cloned', []).append(comp['ref'])
        else:
            d = resolve_footprint_dir(nick, proj_dir)
            if d and os.path.isdir(d):
                try:
                    fp = pcbnew.FootprintLoad(d, name)
                except Exception:  # noqa
                    fp = None
        if fp is None:
            report['missing_footprint'].append((comp['ref'], fp_id))
            continue
        fp.SetFPID(pcbnew.LIB_ID(nick, name))
        fp.SetExcludedFromBOM(False)
        fp.SetExcludedFromPosFiles(False)
        fp.SetDNP(False)
        fp.SetReference(comp['ref'])
        fp.SetValue(comp['value'])
        fp.SetPath(pcbnew.KIID_PATH(kicad_path(comp)))
        fp.SetField('Datasheet', comp['datasheet'])
        fp.SetField('Description', comp['description'])
        fp.SetField('Sheetname', comp['sheet_names'].strip('/').split('/')[-1] if comp['sheet_names'] != '/' else '')
        sheetfile = comp['props'].get('Sheetfile', '')
        fp.SetField('Sheetfile', sheetfile)
        for k, v in comp['props'].items():
            if k in INTERNAL_PROPS or k.startswith('ki_'):
                continue
            fp.SetField(k, v)
        # hide everything but reference/value like Eeschema does
        for fld in fp.GetFields():
            if fld.GetName() not in ('Reference', 'Value'):
                fld.SetVisible(False)
        # symbol attributes Eeschema propagates: exclude from BOM / position files, DNP
        if 'exclude_from_bom' in comp['props']:
            fp.SetExcludedFromBOM(True)
        if 'exclude_from_board' in comp['props']:
            fp.SetExcludedFromBOM(True)
        if 'dnp' in comp['props']:
            fp.SetDNP(True)
        if 'exclude_from_pos' in comp['props'] or 'in_pos_files' in comp['props'] and comp['props'].get('in_pos_files') in ('no', 'false'):
            fp.SetExcludedFromPosFiles(True)
        col, row = slot % a.stage_cols, slot // a.stage_cols
        fp.SetPosition(pcbnew.VECTOR2I_MM(ox + col * a.stage_pitch, oy + row * a.stage_pitch))
        slot += 1
        board.Add(fp)
        for pad in fp.Pads():
            num = pad.GetNumber()
            pad.SetNet(netitem(comp['pins'].get(num, '')))
        report['added'].append(f"{comp['ref']} {fp_id} @ {comp['sheet_names']}")
        existing[comp['ref']] = fp
    # 4. existing footprints: pad nets + sheet fields
    for ref, fp in existing.items():
        comp = comps.get(ref)
        if comp is None:
            if not ref.startswith('#'):
                report['orphans'].append(ref)
            continue
        for pad in fp.Pads():
            want = comp['pins'].get(pad.GetNumber(), '')
            have = pad.GetNetname()
            if canon(want) != canon(have):
                pad.SetNet(netitem(want))
                report['net_fixes'].append(f'{ref}.{pad.GetNumber()}: {have!r} -> {want!r}')
        if not fp.HasField('Sheetname') or not fp.GetFieldText('Sheetname'):
            fp.SetField('Sheetname', comp['sheet_names'].strip('/').split('/')[-1] if comp['sheet_names'] != '/' else '')
            fp.GetField('Sheetname').SetVisible(False)
            report['field_updates'] += 1
        if comp['props'].get('Sheetfile') and (not fp.HasField('Sheetfile') or not fp.GetFieldText('Sheetfile')):
            fp.SetField('Sheetfile', comp['props']['Sheetfile'])
            fp.GetField('Sheetfile').SetVisible(False)
            report['field_updates'] += 1
        if fp.GetPath().AsString() != kicad_path(comp):
            report.setdefault('path_updates', []).append(f"{ref}: {fp.GetPath().AsString()} -> {kicad_path(comp)}")
            fp.SetPath(pcbnew.KIID_PATH(kicad_path(comp)))
        # Phase-1 sheets (refdes 200-799): keep value/datasheet/description/LCSC-style fields in sync with the schematic
        m = re.match(r'^[A-Za-z]+(\d+)$', ref)
        if m and 200 <= int(m.group(1)) <= 799:
            changed = 0
            if fp.GetValue() != comp['value']:
                fp.SetValue(comp['value']); changed += 1
            for fname, fval in (('Datasheet', comp['datasheet']), ('Description', comp['description'])):
                if fp.GetFieldText(fname) != fval:
                    fp.SetField(fname, fval); fp.GetField(fname).SetVisible(False); changed += 1
            for k, v in comp['props'].items():
                if k in INTERNAL_PROPS or k.startswith('ki_') or k in ('exclude_from_bom', 'dnp', 'exclude_from_board', 'in_pos_files'):
                    continue
                if not fp.HasField(k) or fp.GetFieldText(k) != v:
                    fp.SetField(k, v); fp.GetField(k).SetVisible(False); changed += 1
            if changed:
                report.setdefault('field_refresh', []).append(f'{ref} ({changed} fields)')

    print('renamed nets:', len(report['renamed']))
    for r in report['renamed']:
        print('  ', r)
    print('nets created:', len(report['nets_created']))
    print('footprints added:', len(report['added']), f'(staging grid from ({ox:.1f},{oy:.1f}) mm, pitch {a.stage_pitch} mm, {a.stage_cols} columns)')
    print('footprints cloned from an identical FC footprint:', len(report.get('cloned', [])), report.get('cloned', [])[:12])
    print('pad net fixes on existing footprints:', len(report['net_fixes']))
    for r in report['net_fixes'][:40]:
        print('  ', r)
    print('sheet-field updates on existing footprints:', report['field_updates'])
    fr = report.get('field_refresh', [])
    print('field refresh on Phase-1 footprints already on the board:', len(fr), fr[:8])
    pu = report.get('path_updates', [])
    print('path updates on existing footprints:', len(pu))
    for r in pu[:5]:
        print('  ', r)
    if report['missing_footprint']:
        print('MISSING FOOTPRINTS (not added):')
        for r in report['missing_footprint']:
            print('  ', r)
    if report['orphans']:
        print('board footprints absent from schematic (left in place):', report['orphans'])
    if a.dry_run:
        print('dry run: not saved')
        return 1 if report['missing_footprint'] else 0
    pcbnew.SaveBoard(a.out, board)
    print('saved', a.out)
    return 1 if report['missing_footprint'] else 0


if __name__ == '__main__':
    sys.exit(main())
