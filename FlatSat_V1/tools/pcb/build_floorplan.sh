#!/usr/bin/env bash
# Rebuild a placed, unrouted board from the live board and a floorplan JSON, then run every hand-back gate.
#   tools/pcb/build_floorplan.sh FLOORPLAN.json OUT_DIR [REF_BOARD]
# Everything happens inside OUT_DIR/proj/ with the board named FlatSat_V1.kicad_pcb and its .kicad_pro/.kicad_dru/
# schematics/libraries next to it: KiCad (pcbnew's zone filler AND kicad-cli DRC) silently falls back to factory-default
# design rules when a board has no sibling project file, which changes zone-to-edge clearances and therefore every fill.
# Outputs: proj/FlatSat_V1.kicad_pcb, drc.json, attach.txt, heritage.txt, build.log lines on stdout.
set -uo pipefail
FP="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; OUT="$2"; REF="${3:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"; PROJ="$(cd "$HERE/../.." && pwd)"
KPY="/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
KICAD="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
SNAP="$PROJ/tools/baseline/heritage_rev2.json"
py() { "$KPY" "$@" 2>&1 | grep -vE 'stdpbase\.cpp|pcb_track\.cpp|memory leak|Debug:'; }
rm -rf "$OUT"; mkdir -p "$OUT/proj"
cd "$PROJ" || exit 2
cp ./*.kicad_sch FlatSat_V1.kicad_pro FlatSat_V1.kicad_dru sym-lib-table fp-lib-table "$OUT/proj/" && cp -R symbols footprints.pretty Backup_Footprints "$OUT/proj/" || { echo "build: copying project siblings failed"; exit 2; }
cp FlatSat_V1.kicad_pcb "$OUT/proj/FlatSat_V1.kicad_pcb"
B="$OUT/proj/FlatSat_V1.kicad_pcb"
echo "build: 1/6 outline (in place, project siblings present)"
py tools/pcb/outline.py --board "$B" --out "$B" --spec "$FP" | grep -E 'cutout|added|removed|stitching|pours|holes|Error|Traceback|line [0-9]'
[ -s "$B" ] || { echo "build: outline step produced no board"; exit 3; }
echo "build: 2/6 placement (in place)"
py tools/pcb/apply_placement.py --board "$B" --placement "$FP" --out "$B" | grep -E 'applied|outside|overlap|Error|Traceback' | cut -c1-140
echo "build: 3/6 page A3 + sanity"
py - "$B" "$SNAP" <<'PY'
import sys, json, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
snap = json.load(open(sys.argv[2])); her = set(snap['tracks'])
vias = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA' and t.m_Uuid.AsString() not in her]
print('new vias %d, non-GND: %s' % (len(vias), [(t.GetNetname(), round(mm(t.GetPosition().x), 2), round(mm(t.GetPosition().y), 2)) for t in vias if t.GetNetname() != 'GND']))
poly = pcbnew.SHAPE_POLY_SET(); ok = b.GetBoardPolygonOutlines(poly, False)
print('outline valid %s: %d outline(s), %d hole(s), area %.1f mm2' % (ok, poly.OutlineCount(), poly.HoleCount(0) if poly.OutlineCount() else -1, poly.Area() / 1e12))
ds = b.GetDesignSettings(); print('design rules in effect: copper-to-edge %.3f mm, min clearance %.3f mm' % (mm(ds.m_CopperEdgeClearance), mm(ds.m_MinClearance)))
pcbnew.SaveBoard(sys.argv[1], b)
PY
sed -i '' 's/(paper "A4")/(paper "A3")/' "$B" && echo "page: $(grep -o '(paper "[A-Z0-9]*")' "$B")"   # PAGE_INFO is not exposed to python in KiCad 10; the file token is
echo "build: 4/6 heritage (refilled, 12 mm core vs Rev2)"
if [ -n "$REF" ]; then py tools/pcb/heritage.py check "$SNAP" "$B" --allow-zone-growth --allow-edge --refill --core-inset 12 --ref-board "$REF" | grep -E 'VIOLATION|heritage check|band fill' | tee "$OUT/heritage.txt"
else py tools/pcb/heritage.py check "$SNAP" "$B" --allow-zone-growth --allow-edge | tail -1 | tee "$OUT/heritage.txt"; fi
echo "build: 5/6 attachment gate"
py tools/pcb/attachment_check.py "$SNAP" "$B" > "$OUT/attach.txt"; grep -E '^VIOLATION|^WARNING' "$OUT/attach.txt" | cut -c1-160; tail -1 "$OUT/attach.txt"
echo "build: 6/6 DRC (parity, refill)"
"$KICAD" pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones --output "$OUT/drc.json" "$B" 2>&1 | grep -v Fontconfig | tail -1
python3 tools/pcb/drc_summary.py "$OUT/drc.json" | grep -vE '^\s*$'
echo "build: done -> $B"
