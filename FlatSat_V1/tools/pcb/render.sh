#!/usr/bin/env bash
# Render a board to PDFs an agent can Read: one page per layer set (top copper+silk+edge, bottom, inner planes, all copper).
#   tools/pcb/render.sh BOARD.kicad_pcb OUTDIR
set -euo pipefail
B="$1"; O="$2"; mkdir -p "$O"
K="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
"$K" pcb export pdf --layers "F.Cu,F.SilkS,F.Mask,Edge.Cuts,F.Courtyard" --include-border-title --output "$O/top.pdf" "$B" 2>&1 | grep -v Fontconfig | tail -1
"$K" pcb export pdf --layers "B.Cu,B.SilkS,Edge.Cuts,B.Courtyard" --mirror --output "$O/bottom.pdf" "$B" 2>&1 | grep -v Fontconfig | tail -1
"$K" pcb export pdf --layers "In1.Cu,Edge.Cuts" --output "$O/in1.pdf" "$B" 2>&1 | grep -v Fontconfig | tail -1
"$K" pcb export pdf --layers "In2.Cu,Edge.Cuts" --output "$O/in2.pdf" "$B" 2>&1 | grep -v Fontconfig | tail -1
"$K" pcb export pdf --layers "F.Cu,In1.Cu,In2.Cu,B.Cu,Edge.Cuts" --output "$O/all_copper.pdf" "$B" 2>&1 | grep -v Fontconfig | tail -1
"$K" pcb export stats --output "$O/stats.txt" "$B" 2>&1 | grep -v Fontconfig | tail -1 || true
ls -la "$O"
