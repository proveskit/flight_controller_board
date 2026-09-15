#!/usr/bin/env python3
"""Insert (or replace) a hierarchical sheet symbol in a KiCad 10 root schematic.

The sheet block is inserted just before the root's (sheet_instances ...) block,
formatted exactly like the ones Eeschema 10 writes. Re-running with the same
--uuid replaces the existing block (idempotent), so a harness can call it freely.

Usage:
  add_sheet_symbol.py ROOT.kicad_sch --name "Emulator MCU" --file emulator_mcu.kicad_sch \
      --uuid 8394a2ec-... --at 57.15 120.65 --size 30.48 12.7 --page 6 --project FlatSat_V1
  add_sheet_symbol.py ROOT.kicad_sch --remove --uuid 8394a2ec-...
"""
import argparse
import re
import sys


def fmt(v):
    s = '%.4f' % float(v)
    s = s.rstrip('0').rstrip('.')
    return s if s else '0'


def block(name, file, uuid, x, y, w, h, page, project, root_uuid):
    x, y, w, h = float(x), float(y), float(w), float(h)
    return (
        '\t(sheet\n'
        f'\t\t(at {fmt(x)} {fmt(y)})\n'
        f'\t\t(size {fmt(w)} {fmt(h)})\n'
        '\t\t(exclude_from_sim no)\n'
        '\t\t(in_bom yes)\n'
        '\t\t(on_board yes)\n'
        '\t\t(dnp no)\n'
        '\t\t(fields_autoplaced yes)\n'
        '\t\t(stroke\n\t\t\t(width 0.1524)\n\t\t\t(type solid)\n\t\t)\n'
        '\t\t(fill\n\t\t\t(color 0 0 0 0)\n\t\t)\n'
        f'\t\t(uuid "{uuid}")\n'
        f'\t\t(property "Sheetname" "{name}"\n'
        f'\t\t\t(at {fmt(x)} {fmt(y - 0.7116)} 0)\n'
        '\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n'
        '\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify left bottom)\n\t\t\t)\n'
        '\t\t)\n'
        f'\t\t(property "Sheetfile" "{file}"\n'
        f'\t\t\t(at {fmt(x)} {fmt(y + h + 0.5846)} 0)\n'
        '\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n'
        '\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify left top)\n\t\t\t)\n'
        '\t\t)\n'
        '\t\t(instances\n'
        f'\t\t\t(project "{project}"\n'
        f'\t\t\t\t(path "/{root_uuid}"\n'
        f'\t\t\t\t\t(page "{page}")\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t)\n'
        '\t)\n'
    )


def find_sheet_block(text, uuid):
    """Return (start, end) of the top-level (sheet ...) block carrying this uuid, or None."""
    for m in re.finditer(r'^\t\(sheet\n', text, re.M):
        depth = 0
        j = m.start()
        while True:
            ch = text[j]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        blk = text[m.start():j + 1]
        if f'(uuid "{uuid}")' in blk:
            end = j + 1
            if text[end:end + 1] == '\n':
                end += 1
            return m.start(), end
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--name')
    ap.add_argument('--file')
    ap.add_argument('--uuid', required=True)
    ap.add_argument('--at', nargs=2, type=float)
    ap.add_argument('--size', nargs=2, type=float, default=[30.48, 12.7])
    ap.add_argument('--page', type=int)
    ap.add_argument('--project', default='FlatSat_V1')
    ap.add_argument('--remove', action='store_true')
    a = ap.parse_args()

    text = open(a.root, encoding='utf-8').read()
    m = re.search(r'^\t\(uuid "([0-9a-f-]{36})"\)', text, re.M)
    if not m:
        print('root uuid not found', file=sys.stderr)
        return 1
    root_uuid = m.group(1)

    existing = find_sheet_block(text, a.uuid)
    if existing:
        text = text[:existing[0]] + text[existing[1]:]
        action = 'replaced' if not a.remove else 'removed'
    else:
        action = 'inserted' if not a.remove else 'not present'

    if not a.remove:
        if not (a.name and a.file and a.at and a.page):
            print('--name, --file, --at and --page are required to insert', file=sys.stderr)
            return 1
        anchor = text.find('\t(sheet_instances')
        if anchor < 0:
            print('root has no (sheet_instances) block', file=sys.stderr)
            return 1
        text = text[:anchor] + block(a.name, a.file, a.uuid, a.at[0], a.at[1], a.size[0], a.size[1], a.page, a.project, root_uuid) + text[anchor:]

    open(a.root, 'w', encoding='utf-8').write(text)
    print(f'{action} sheet {a.uuid} in {a.root}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
