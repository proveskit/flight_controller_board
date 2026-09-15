#!/usr/bin/env python3
"""Add the Phase-2 net classes (brief L5) to FlatSat_V1.kicad_pro (plain python, JSON edit).

  netclasses.py FlatSat_V1.kicad_pro [--dry-run]

Classes written (existing 'Default' untouched):
  BenchPower: clearance 0.25, track 1.0, via 0.8/0.4  — VBAT_BENCH_N, VSOLAR_BENCH_A/B, VBUS_CHG, CHG_SYS, CHG_BAT, CHG_PMID, VBUS_EMU, 3V3_EMU, MID_BENCH
  USB_EMU:    clearance 0.2,  track 0.25, via 0.6/0.3, diff pair 0.25/0.15 — EMU_USB_DP, EMU_USB_DM
Assignments use net_settings.netclass_patterns (KiCad 8+). Existing FC nets keep Default; the wide
copper on Dir_Chrg_In / B- / VBUSP / VBATT_SENSE / INHIB_x / IN_RBF / VSOLAR is a routing instruction
(L5), not a class change, so the FC's own tracks are not re-flagged.
"""
import json
import sys

BENCH = ['VBAT_BENCH_N', 'VSOLAR_BENCH_A', 'VSOLAR_BENCH_B', 'VBUS_CHG', 'CHG_SYS', 'CHG_BAT', 'CHG_PMID', 'VBUS_EMU', '3V3_EMU', 'MID_BENCH']
USB = ['EMU_USB_DP', 'EMU_USB_DM']


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    p = sys.argv[1]
    dry = '--dry-run' in sys.argv
    d = json.load(open(p))
    ns = d.setdefault('net_settings', {})
    classes = ns.setdefault('classes', [])
    names = {c.get('name') for c in classes}
    base = next((c for c in classes if c.get('name') == 'Default'), {})

    def cls(name, clearance, track, via_d, via_drill, dp_w=None, dp_gap=None):
        c = dict(base)
        c.update({'name': name, 'clearance': clearance, 'track_width': track, 'via_diameter': via_d, 'via_drill': via_drill, 'microvia_diameter': base.get('microvia_diameter', 0.3), 'microvia_drill': base.get('microvia_drill', 0.1), 'wire_width': base.get('wire_width', 6), 'bus_width': base.get('bus_width', 12), 'line_style': base.get('line_style', 0), 'pcb_color': 'rgba(0, 0, 0, 0.000)', 'schematic_color': 'rgba(0, 0, 0, 0.000)'})
        if dp_w:
            c['diff_pair_width'] = dp_w
            c['diff_pair_gap'] = dp_gap
            c['diff_pair_via_gap'] = dp_gap
        return c

    added = []
    if 'BenchPower' not in names:
        classes.append(cls('BenchPower', 0.25, 1.0, 0.8, 0.4))
        added.append('BenchPower')
    if 'USB_EMU' not in names:
        classes.append(cls('USB_EMU', 0.2, 0.25, 0.6, 0.3, 0.25, 0.15))
        added.append('USB_EMU')
    pats = ns.setdefault('netclass_patterns', [])
    have = {(x.get('pattern'), x.get('netclass')) for x in pats}
    for n in BENCH:
        if (n, 'BenchPower') not in have:
            pats.append({'netclass': 'BenchPower', 'pattern': n})
    for n in USB:
        if (n, 'USB_EMU') not in have:
            pats.append({'netclass': 'USB_EMU', 'pattern': n})
    print('classes added:', added, '| patterns now:', len(pats))
    if not dry:
        json.dump(d, open(p, 'w'), indent=2)
        open(p, 'a').write('\n')
        print('written', p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
