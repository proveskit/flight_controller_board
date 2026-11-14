#!/usr/bin/env python3
"""kv: drive kicad-cli against a staged copy of one board folder and keep the evidence.

  kv.py doctor  BOARD_DIR
  kv.py stage   BOARD_DIR [--rev GIT_REF]           -> prints RUN dir
  kv.py erc     RUN [--baseline RUN] [--list]
  kv.py drc     RUN [--baseline RUN] [--list]
  kv.py render  RUN
  kv.py netlist RUN
  kv.py netdiff BASE_RUN HEAD_RUN
  kv.py fab     RUN [--against ZIP_OR_RUN]
  kv.py cleanup RUN
"""
import argparse
import datetime
import glob
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter

EVIDENCE_ROOT = os.environ.get('KV_EVIDENCE_ROOT', os.path.expanduser('~/kicad-verify-evidence'))
MAC_CLI = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
NOISE = {'lib_symbol_issues', 'lib_symbol_mismatch', 'footprint_link_issues', 'endpoint_off_grid'}
CLI_TIMEOUT = 900


def die(msg):
    print('FAIL ' + msg)
    sys.exit(1)


def kicad_cli():
    for c in (os.environ.get('KICAD_CLI'), shutil.which('kicad-cli'), MAC_CLI):
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def cli_version(cli):
    out = subprocess.run([cli, 'version'], capture_output=True, text=True, timeout=60).stdout.strip()
    m = re.match(r'(\d+)\.(\d+)', out)
    return out, (int(m.group(1)) if m else 0)


def needed_major(path):
    """KiCad major that wrote the file: its generator_version, else the file format date."""
    with open(path, encoding='utf-8', errors='replace') as f:
        head = f.read(4096)
    m = re.search(r'\(generator_version "(\d+)', head)
    if m:
        return int(m.group(1))
    m = re.search(r'\(version (\d+)\)', head)
    version = int(m.group(1)) if m else 0
    for floor, major in ((20250201, 10), (20240101, 9), (20230101, 8), (20221018, 7)):
        if version >= floor:
            return major
    return 6


def project_name(board_dir):
    pros = glob.glob(os.path.join(board_dir, '*.kicad_pro'))
    if len(pros) != 1:
        die('%s holds %d .kicad_pro files; point at one board folder' % (board_dir, len(pros)))
    return os.path.splitext(os.path.basename(pros[0]))[0]


def git(args, cwd):
    return subprocess.run(['git'] + args, cwd=cwd, capture_output=True, text=True)


def run_cli(run, args, log_name):
    cli = run['kicad_cli']
    p = subprocess.run([cli] + args, cwd=run['src'], capture_output=True, text=True, timeout=CLI_TIMEOUT)
    with open(os.path.join(run['dir'], log_name + '.log'), 'w') as f:
        f.write('$ kicad-cli %s\nexit %d\n--- stdout\n%s\n--- stderr\n%s\n' % (' '.join(args), p.returncode, p.stdout, p.stderr))
    return p


def load_run(path):
    path = os.path.abspath(path)
    try:
        with open(os.path.join(path, 'run.json')) as f:
            run = json.load(f)
    except FileNotFoundError:
        die('%s is not a kv run (no run.json); create one with kv.py stage' % path)
    run['dir'] = path
    run['src'] = os.path.join(path, 'src')
    if not os.path.isdir(run['src']):
        die('%s was cleaned up; stage a new run' % path)
    return run


def doctor(a):
    board = os.path.abspath(a.board_dir)
    ok = True
    name = project_name(board)
    pcb, sch = os.path.join(board, name + '.kicad_pcb'), os.path.join(board, name + '.kicad_sch')
    for p in (pcb, sch):
        if not os.path.isfile(p):
            print('FAIL missing %s' % p)
            ok = False
    need = max(needed_major(p) for p in (pcb, sch)) if ok else 0
    cli = kicad_cli()
    if not cli:
        print('FAIL kicad-cli not found (set KICAD_CLI, or install KiCad %d+)' % need)
        ok = False
    else:
        text, major = cli_version(cli)
        state = 'ok' if major >= need else 'FAIL'
        ok &= major >= need
        print('%s kicad-cli %s at %s; files need %d+' % (state, text, cli, need))
    top = git(['rev-parse', '--show-toplevel'], board)
    if top.returncode == 0:
        head = git(['rev-parse', '--short', 'HEAD'], board).stdout.strip()
        dirty = git(['status', '--porcelain', '--', '.'], board).stdout.splitlines()
        print('ok git %s, %d uncommitted paths in this board folder' % (head, len(dirty)))
        tracked = set(git(['ls-files', '--', '.'], board).stdout.split('\n'))
    else:
        tracked = set()
        print('ok not a git checkout; --rev is unavailable')
    for lck in glob.glob(os.path.join(board, '~*.lck')):
        why = 'committed junk' if os.path.basename(lck) in {os.path.basename(t) for t in tracked} else 'KiCad GUI may have this open'
        print('warn lock file %s (%s); runs use a staged copy, so it does not block' % (os.path.basename(lck), why))
    print('ok evidence root %s' % EVIDENCE_ROOT)
    print('READY' if ok else 'NOT READY')
    return 0 if ok else 1


def stage(a):
    board = os.path.abspath(a.board_dir)
    name = project_name(board)
    cli = kicad_cli()
    if not cli:
        die('kicad-cli not found; run kv.py doctor')
    version, _ = cli_version(cli)
    rev = 'worktree'
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    if a.rev:
        top = git(['rev-parse', '--show-toplevel'], board).stdout.strip()
        rev = git(['rev-parse', '--short', a.rev], board).stdout.strip() or die('unknown rev %s' % a.rev)
        rel = os.path.relpath(board, top)
        if not git(['ls-tree', a.rev, '--', rel], top).stdout.strip():
            die('%s does not exist at %s (%s); pick a revision that has the board folder: git log --oneline -- %s' % (rel, a.rev, rev, rel))
    run_dir = os.path.join(EVIDENCE_ROOT, '%s@%s-%s' % (name, rev, stamp))
    src = os.path.join(run_dir, 'src')
    os.makedirs(run_dir)
    if a.rev:
        tar =subprocess.run(['git', 'archive', '--format=tar', a.rev, '--', rel], cwd=top, capture_output=True, check=True).stdout
        tmp = os.path.join(run_dir, 'archive')
        with tarfile.open(fileobj=io.BytesIO(tar)) as t:
            t.extractall(tmp, **({'filter': 'data'} if hasattr(tarfile, 'data_filter') else {}))
        shutil.move(os.path.join(tmp, rel), src)
        shutil.rmtree(tmp)
    else:
        shutil.copytree(board, src, ignore=shutil.ignore_patterns('*-backups', '~*.lck', '*.kicad_prl', 'fp-info-cache', '_autosave-*'))
    run = {'board': name, 'source_dir': board, 'rev': rev, 'kicad_cli': cli, 'kicad_version': version, 'created': stamp}
    with open(os.path.join(run_dir, 'run.json'), 'w') as f:
        json.dump(run, f, indent=2)
    print(run_dir)
    return 0


def violations(report_path, sections):
    with open(report_path) as f:
        d = json.load(f)
    rows = []
    if 'sheets' in d:
        for s in d['sheets']:
            for v in s.get('violations', []):
                rows.append((v['severity'], v['type'], s.get('path', ''), v))
    for sec in sections:
        for v in d.get(sec, []):
            rows.append((v['severity'], v['type'] if sec == 'violations' else sec + ':' + v['type'], '', v))
    return [r for r in rows if r[1] not in NOISE]


def describe(v):
    items = '; '.join('%s @(%s,%s)' % (i.get('description', ''), i.get('pos', {}).get('x'), i.get('pos', {}).get('y')) for i in v.get('items', []))
    return '%s | %s' % (v.get('description', ''), items)


def summarize(run, kind, rows, a):
    counts = Counter((r[0], r[1]) for r in rows)
    lines = []
    if a.baseline:
        base = load_run(a.baseline)
        if not os.path.isfile(os.path.join(base['dir'], kind + '.json')):
            die('baseline %s has no %s.json; run kv.py %s on it first' % (base['dir'], kind, kind))
        base_rows = violations(os.path.join(base['dir'], kind + '.json'), SECTIONS[kind])
        bc = Counter((r[0], r[1]) for r in base_rows)
        lines.append('%-8s %-40s %6s %6s %6s' % ('severity', 'type', 'base', 'now', 'delta'))
        for k in sorted(set(counts) | set(bc)):
            lines.append('%-8s %-40s %6d %6d %+6d' % (k[0], k[1], bc[k], counts[k], counts[k] - bc[k]))
        new = Counter()
        for k in counts:
            new[k[0]] += max(0, counts[k] - bc[k])
        lines.append('VERDICT %s %s@%s vs %s@%s: %d new errors, %d new warnings (baseline %d findings, now %d)' % (
            kind, run['board'], run['rev'], base['board'], base['rev'], new['error'], new['warning'], len(base_rows), len(rows)))
    else:
        for k, n in sorted(counts.items()):
            lines.append('%-8s %-40s %6d' % (k[0], k[1], n))
        errors = sum(n for k, n in counts.items() if k[0] == 'error')
        lines.append('VERDICT %s %s@%s: %d errors, %d warnings (library noise filtered)' % (
            kind, run['board'], run['rev'], errors, len(rows) - errors))
    if a.list:
        lines += ['- [%s] %s %s %s' % (sev, typ, path, describe(v)) for sev, typ, path, v in rows]
    text = '\n'.join(lines)
    with open(os.path.join(run['dir'], kind + '.txt'), 'w') as f:
        f.write(text + '\n')
    print(text)


SECTIONS = {'erc': [], 'drc': ['violations', 'unconnected_items', 'schematic_parity']}


def erc(a):
    run = load_run(a.run)
    out = os.path.join(run['dir'], 'erc.json')
    p = run_cli(run, ['sch', 'erc', '--format', 'json', '--severity-all', '--units', 'mm', '-o', out, run['board'] + '.kicad_sch'], 'erc')
    if not os.path.isfile(out):
        die('kicad-cli sch erc exit %d, no report; see %s/erc.log' % (p.returncode, run['dir']))
    summarize(run, 'erc', violations(out, SECTIONS['erc']), a)
    return 0


def drc(a):
    run = load_run(a.run)
    out = os.path.join(run['dir'], 'drc.json')
    p = run_cli(run, ['pcb', 'drc', '--format', 'json', '--severity-all', '--all-track-errors', '--schematic-parity',
                      '--units', 'mm', '-o', out, run['board'] + '.kicad_pcb'], 'drc')
    if not os.path.isfile(out):
        die('kicad-cli pcb drc exit %d, no report; see %s/drc.log' % (p.returncode, run['dir']))
    summarize(run, 'drc', violations(out, SECTIONS['drc']), a)
    return 0


def svg_to_png(svg, png):
    return subprocess.run(['rsvg-convert', '-z', '2', '-b', 'white', '-o', png, svg], capture_output=True).returncode == 0


def stock_models(cli):
    for c in (os.environ.get('KICAD10_3DMODEL_DIR'),
              os.path.join(os.path.dirname(os.path.realpath(cli)), '..', 'SharedSupport', '3dmodels'),
              '/usr/share/kicad/3dmodels'):
        if c and os.path.isdir(c):
            return os.path.normpath(c)
    return None


def missing_models(run):
    """Footprints whose 3D model file KiCad cannot find; kicad-cli pcb render skips them silently."""
    stock = stock_models(run['kicad_cli'])
    with open(os.path.join(run['src'], run['board'] + '.kicad_pcb'), encoding='utf-8') as f:
        footprints = re.split(r'\n\t\(footprint ', f.read())[1:]
    missing, total = [], 0
    for fp in footprints:
        models = re.findall(r'\(model "([^"]*)"', fp)
        if not models:
            continue
        total += 1

        def found(m):
            p = re.sub(r'\$\{(KICAD\d+_3DMODEL_DIR|KISYS3DMOD)\}', lambda _: stock or '\0', m)
            p = os.path.expandvars(p.replace('${KIPRJMOD}', run['src']))
            p = p if os.path.isabs(p) else os.path.join(run['src'], p)
            stem = os.path.splitext(p)[0]
            return any(os.path.isfile(stem + ext) for ext in (os.path.splitext(p)[1], '.step', '.stp', '.wrl'))

        if not any(found(m) for m in models):
            ref = re.search(r'\(property "Reference" "([^"]*)"', fp)
            missing.append((ref.group(1) if ref else '?', models[0]))
    return missing, total


def render(a):
    run = load_run(a.run)
    out = os.path.join(run['dir'], 'render')
    os.makedirs(os.path.join(out, 'sch'), exist_ok=True)
    made = []
    sch, pcb = run['board'] + '.kicad_sch', run['board'] + '.kicad_pcb'
    run_cli(run, ['sch', 'export', 'pdf', '-o', os.path.join(out, 'schematic.pdf'), sch], 'render-sch-pdf')
    run_cli(run, ['sch', 'export', 'svg', '-o', os.path.join(out, 'sch'), sch], 'render-sch-svg')
    if not shutil.which('rsvg-convert'):
        print('note    no rsvg-convert (brew install librsvg); sheets stay SVG only')
    for svg in sorted(glob.glob(os.path.join(out, 'sch', '*.svg'))):
        png = svg[:-4] + '.png'
        if shutil.which('rsvg-convert') and svg_to_png(svg, png):
            made.append(png)
    for side in ('top', 'bottom'):
        png = os.path.join(out, 'pcb-%s.png' % side)
        run_cli(run, ['pcb', 'render', '--side', side, '--quality', 'basic', '--background', 'opaque',
                      '-w', '2000', '-h', '1500', '-o', png, pcb], 'render-pcb-' + side)
        made.append(png)
    made.append(os.path.join(out, 'schematic.pdf'))
    missing = [m for m in made if not os.path.isfile(m)]
    for m in made:
        print(('missing ' if m in missing else 'wrote   ') + m)
    svgs = glob.glob(os.path.join(out, 'sch', '*.svg'))
    no_model, with_model = missing_models(run)
    with open(os.path.join(out, 'missing-3d-models.txt'), 'w') as f:
        f.write(''.join('%s %s\n' % r for r in sorted(no_model, key=lambda r: ref_key(r[0]))))
    print('VERDICT render %s@%s: %d schematic sheets as SVG, %d output files missing, %d of %d footprint 3D models not found '
          '(drawn without a body; see render/missing-3d-models.txt)' % (
              run['board'], run['rev'], len(svgs), len(missing), len(no_model), with_model))
    return 1 if missing or not svgs else 0


def netlist(a):
    run = load_run(a.run)
    out = os.path.join(run['dir'], 'netlist.xml')
    p = run_cli(run, ['sch', 'export', 'netlist', '--format', 'kicadxml', '-o', out, run['board'] + '.kicad_sch'], 'netlist')
    if not os.path.isfile(out):
        die('kicad-cli sch export netlist exit %d; see %s/netlist.log' % (p.returncode, run['dir']))
    nets, comps = read_netlist(out)
    print('VERDICT netlist %s@%s: %d components, %d nets -> %s' % (run['board'], run['rev'], len(comps), len(nets), out))
    return 0


def read_netlist(path):
    root = ET.parse(path).getroot()
    nets = {n.get('name'): frozenset((x.get('ref'), x.get('pin')) for x in n.findall('node')) for n in root.find('nets')}
    comps = {c.get('ref'): (c.findtext('value') or '', c.findtext('footprint') or '') for c in root.find('components')}
    return nets, comps


def ref_key(ref):
    m = re.match(r'(\D*)(\d*)', ref)
    return (m.group(1), int(m.group(2) or 0), ref)


def netdiff(a):
    base, head = load_run(a.base), load_run(a.head)
    for r in (base, head):
        if not os.path.isfile(os.path.join(r['dir'], 'netlist.xml')):
            die('%s has no netlist.xml; run kv.py netlist on it first' % r['dir'])
    bn, bc = read_netlist(os.path.join(base['dir'], 'netlist.xml'))
    hn, hc = read_netlist(os.path.join(head['dir'], 'netlist.xml'))

    def pins(s):
        return ', '.join('%s.%s' % p for p in sorted(s, key=lambda p: (ref_key(p[0]), p[1])))

    by_pins_b = {v: k for k, v in bn.items()}
    lines = []
    for r in sorted(set(hc) - set(bc), key=ref_key):
        lines.append('+ part %s %s %s' % (r, *hc[r]))
    for r in sorted(set(bc) - set(hc), key=ref_key):
        lines.append('- part %s %s %s' % (r, *bc[r]))
    for r in sorted(set(bc) & set(hc), key=ref_key):
        if bc[r] != hc[r]:
            lines.append('~ part %s %s %s -> %s %s' % (r, *bc[r], *hc[r]))
    renamed, conn = 0, 0
    for k in sorted(set(hn) - set(bn)):
        if hn[k] in by_pins_b:
            renamed += 1
            lines.append('= net renamed %s -> %s' % (by_pins_b[hn[k]], k))
        else:
            conn += 1
            lines.append('+ net %s: %s' % (k, pins(hn[k])))
    renamed_from = {by_pins_b[v] for v in hn.values() if v in by_pins_b}
    for k in sorted(set(bn) - set(hn) - renamed_from):
        conn += 1
        lines.append('- net %s: %s' % (k, pins(bn[k])))
    for k in sorted(set(bn) & set(hn)):
        if bn[k] != hn[k]:
            conn += 1
            lines.append('~ net %s: +[%s] -[%s]' % (k, pins(hn[k] - bn[k]), pins(bn[k] - hn[k])))
    parts = sum(1 for l in lines if 'part' in l.split()[1:2])
    lines.append('VERDICT netdiff %s@%s -> %s@%s: %d part changes, %d connectivity changes, %d pure renames' % (
        base['board'], base['rev'], head['board'], head['rev'], parts, conn, renamed))
    text = '\n'.join(lines)
    with open(os.path.join(head['dir'], 'netdiff-vs-%s.txt' % base['rev']), 'w') as f:
        f.write(text + '\n')
    print(text)
    return 0


def gerber_key(name, data):
    if name.lower().endswith('.drl'):
        return 'drill:' + ('NPTH' if 'NPTH' in name.upper() else 'PTH')
    m = re.search(rb'%TF\.FileFunction,([^*]*)\*%', data)
    return 'gerber:' + (m.group(1).decode() if m else os.path.splitext(name)[0].rsplit('-', 1)[-1])


VOLATILE = re.compile(rb'^(G04|;|%TF\.(CreationDate|GenerationSoftware|ProjectId))')


def fab_layers(files):
    layers = {}
    for name, data in files:
        if name.lower().endswith(('.gbr', '.drl')) or re.search(r'\.g[a-z0-9]{1,3}$', name.lower()):
            body = b'\n'.join(l for l in data.splitlines() if not VOLATILE.match(l))
            layers[gerber_key(name, data)] = (name, body)
    return layers


def fab(a):
    run = load_run(a.run)
    out = os.path.join(run['dir'], 'fab')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    pcb = run['board'] + '.kicad_pcb'
    with open(os.path.join(run['src'], pcb), encoding='utf-8') as f:
        copper = re.findall(r'\(\d+ "([^"]+\.Cu)" (?:signal|power|mixed|jumper)', f.read(65536))
    layers = copper + ['F.Paste', 'B.Paste', 'F.Silkscreen', 'B.Silkscreen', 'F.Mask', 'B.Mask', 'Edge.Cuts']
    run_cli(run, ['pcb', 'export', 'gerbers', '--subtract-soldermask', '--no-protel-ext', '-l', ','.join(layers),
                  '-o', out + os.sep, pcb], 'fab-gerbers')
    run_cli(run, ['pcb', 'export', 'drill', '--format', 'excellon', '--excellon-separate-th', '--excellon-units', 'in',
                  '--excellon-oval-format', 'route', '--generate-map', '--map-format', 'pdf', '-o', out + os.sep, pcb], 'fab-drill')
    made = []
    for p in sorted(os.listdir(out)):
        with open(os.path.join(out, p), 'rb') as f:
            made.append((p, f.read()))
    new = fab_layers(made)
    print('generated %d layer/drill files in %s' % (len(new), out))
    ordered = os.path.join(run['src'], 'jlcpcb', 'production_files', 'GERBER-%s.zip' % run['board'])
    against = a.against or (ordered if os.path.isfile(ordered) else None)
    if not against:
        if os.path.exists(os.path.join(run['dir'], 'fab.txt')):
            os.remove(os.path.join(run['dir'], 'fab.txt'))
        print('VERDICT fab %s@%s: %d files generated, no GERBER-%s.zip to compare' % (run['board'], run['rev'], len(new), run['board']))
        return 0 if new else 1
    if os.path.isdir(against):
        other = load_run(against)
        fab_dir = os.path.join(other['dir'], 'fab')
        if not os.path.isdir(fab_dir):
            die('%s has no fab/; run kv.py fab on it first' % other['dir'])
        old = fab_layers([(n, open(os.path.join(fab_dir, n), 'rb').read()) for n in sorted(os.listdir(fab_dir))])
        against_name = '%s@%s' % (other['board'], other['rev'])
        report = 'fab-vs-%s.txt' % other['rev']
    else:
        with zipfile.ZipFile(against) as z:
            old = fab_layers([(n, z.read(n)) for n in z.namelist()])
        against_name = os.path.basename(against)
        report = 'fab.txt'
    lines = []
    same = 0
    for k in sorted(set(old) | set(new)):
        if k not in new:
            lines.append('missing from regenerated: %s (%s)' % (k, old[k][0]))
        elif k not in old:
            lines.append('not in ordered zip:      %s (%s)' % (k, new[k][0]))
        elif old[k][1] == new[k][1]:
            same += 1
            lines.append('identical               %s' % k)
        else:
            lines.append('DIFFERS                 %s (%s vs %s)' % (k, old[k][0], new[k][0]))
    differ = len(set(old) | set(new)) - same
    lines.append('VERDICT fab %s@%s vs %s: %d layers identical, %d differ or missing' % (
        run['board'], run['rev'], against_name, same, differ))
    text = '\n'.join(lines)
    with open(os.path.join(run['dir'], report), 'w') as f:
        f.write(text + '\n')
    print(text)
    return 0


def cleanup(a):
    run = load_run(a.run)
    shutil.rmtree(run['src'])
    kept = sorted(os.listdir(run['dir']))
    print('removed %s; evidence kept in %s: %s' % (run['src'], run['dir'], ', '.join(kept)))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('doctor').add_argument('board_dir')
    s = sub.add_parser('stage')
    s.add_argument('board_dir')
    s.add_argument('--rev')
    for name in ('erc', 'drc'):
        s = sub.add_parser(name)
        s.add_argument('run')
        s.add_argument('--baseline')
        s.add_argument('--list', action='store_true')
    for name in ('render', 'netlist', 'cleanup'):
        sub.add_parser(name).add_argument('run')
    s = sub.add_parser('netdiff')
    s.add_argument('base')
    s.add_argument('head')
    s = sub.add_parser('fab')
    s.add_argument('run')
    s.add_argument('--against')
    a = ap.parse_args()
    return globals()[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
