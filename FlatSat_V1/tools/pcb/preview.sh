#!/usr/bin/env bash
# Regenerate FlatSat_V1/jlcpcb/preview/ (kicad-cli only; NOT the order package, see preview/README.md).
#   preview.sh
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PROJ=$(cd "$HERE/../.." && pwd)
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
OUT=$PROJ/jlcpcb/preview
PCB=$PROJ/FlatSat_V1.kicad_pcb
rm -rf "$OUT/gerber" "$OUT/drill" "$OUT/pos" "$OUT/bom"
mkdir -p "$OUT/gerber" "$OUT/drill" "$OUT/pos" "$OUT/bom"
$K pcb export gerbers --board-plot-params -l "F.Cu,In1.Cu,In2.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,F.Paste,B.Paste,Edge.Cuts" -o "$OUT/gerber/" "$PCB"
$K pcb export drill --excellon-separate-th --generate-map --map-format pdf --generate-report --report-path "$OUT/drill/drill_report.txt" -o "$OUT/drill/" "$PCB"
$K pcb export pos --side both --format csv --units mm -o "$OUT/pos/FlatSat_V1-pos.csv" "$PCB"
$K sch export bom --fields 'Reference,Value,Footprint,LCSC Part,Datasheet,${QUANTITY},${DNP}' \
  --labels 'Designator,Value,Footprint,LCSC,Datasheet,Quantity,DNP' --group-by 'Value,Footprint,LCSC Part' \
  -o "$OUT/bom/FlatSat_V1-bom.csv" "$PROJ/FlatSat_V1.kicad_sch"
find "$OUT" -type f | sort | sed "s#$PROJ/##"
