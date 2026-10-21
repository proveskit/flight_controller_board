#!/usr/bin/env bash
# Run every Phase-2 layout gate on one board and print a one-line table row at the end.
#   gates.sh PROJECT_DIR/FlatSat_V1.kicad_pcb OUT_DIR
# The board must sit in a project directory with its own .kicad_pro/.kicad_dru (KiCad silently falls back to
# factory rules otherwise). Gates: heritage (stored fills), heritage (--refill --core-inset 12 --ref-board),
# attachment_check (F15: fill change = warning), DRC with parity + drc_summary vs the pre-layout baseline,
# via_in_pad (F16). Nothing here writes the board.
set -uo pipefail
BOARD=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
OUT=$2
mkdir -p "$OUT"
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../../.." && pwd)
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
KCLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
SNAP=$HERE/../baseline/heritage_rev2.json
REF=$REPO/FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb
PROJ=${BOARD%.kicad_pcb}
[ -f "$PROJ.kicad_pro" ] && [ -f "$PROJ.kicad_dru" ] || { echo "no sibling .kicad_pro/.kicad_dru for $BOARD"; exit 2; }

$KPY "$HERE/heritage.py" check "$SNAP" "$BOARD" --allow-zone-growth --allow-edge >"$OUT/heritage.txt" 2>&1
$KPY "$HERE/heritage.py" check "$SNAP" "$BOARD" --allow-zone-growth --allow-edge --refill --core-inset 12 --ref-board "$REF" >"$OUT/heritage_refill.txt" 2>&1
$KPY "$HERE/attachment_check.py" "$SNAP" "$BOARD" --json "$OUT/attachment.json" >"$OUT/attachment.txt" 2>&1
$KCLI pcb drc --severity-all --all-track-errors --schematic-parity --refill-zones --format json -o "$OUT/drc.json" "$BOARD" >"$OUT/drc_cli.txt" 2>&1
$KPY "$HERE/drc_summary.py" "$OUT/drc.json" --baseline "$HERE/../baseline/drc_prelayout.json" >"$OUT/drc_summary.txt" 2>&1
$KPY "$HERE/via_in_pad.py" "$BOARD" --snap "$SNAP" --json "$OUT/via_in_pad.json" --list >"$OUT/via_in_pad.txt" 2>&1

her=$(grep -Eo '[0-9]+ violation' "$OUT/heritage.txt" | tail -1 | grep -Eo '^[0-9]+')
herf=$(grep -Eo '[0-9]+ violation' "$OUT/heritage_refill.txt" | tail -1 | grep -Eo '^[0-9]+')
att=$(python3 -c "import json;d=json.load(open('$OUT/attachment.json'));print(len(d['violations']),len(d['warnings']),d['stubs'])")
drc=$(grep -E '^errors:' "$OUT/drc_summary.txt")
vip=$(tail -1 "$OUT/via_in_pad.txt")
for f in heritage heritage_refill attachment drc_summary via_in_pad; do echo "== $f"; tail -4 "$OUT/$f.txt"; done
echo "GATES heritage=${her:-?} heritage_refill=${herf:-?} attachment(viol,warn,stubs)=${att} | ${drc} | ${vip}"
