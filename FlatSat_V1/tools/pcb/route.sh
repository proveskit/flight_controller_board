#!/usr/bin/env bash
# Freerouting round trip that routes ONLY the new connections and leaves the flight-heritage copper untouched.
# Implements the recipe validated in tools/pcb/README.md (prep → keep-out on the export copy → DSN → fixdsn →
# Freerouting -mt 1 → SES into a fresh copy of PRE → merge (heritage from PRE + new copper only) → checks).
#
#   tools/pcb/route.sh PRE.kicad_pcb OUT.kicad_pcb [max_passes] [extra freerouting args...]
#
# PRE   = the placed board copy you want routed (never the live project board). Its .kicad_pro should sit next to it.
# OUT   = the merged result (heritage byte-for-byte from PRE + only genuinely new tracks/vias).
# Env:  KEEPOUT_JSON   (default tools/pcb/fc_keepout.json, built by make_keepout.py; "" to disable) — rule areas applied to
#                      the DSN-export copy only: flight core, via_keepout over the flight section, heritage copper in the band
#       HERITAGE_SNAP  (default tools/baseline/heritage_rev2.json) — for heritage.py check and attachment_check.py
#       REF_BOARD      (optional) Rev2 .kicad_pcb: also verifies refilled copper inside the flight core (outline - BAND_MM)
#       BAND_MM        (default 12) attachment band depth used for that core check
#       PRUNE          (default 1) remove everything the attachment gate rejects from OUT (unpruned copy kept next to it)
#       JAVA, FREEROUTING_JAR, FR_TIMEOUT_MIN (default 180 — Freerouting on the full board takes 30-60+ min; do not
#       kill it for log silence, check CPU%)
# Exit: 0 when Freerouting produced a session and the merge/prune/heritage checks ran (results are printed; heritage must
#       be 0 violations; after PRUNE the attachment gate must be 0 and the pruned connections show up as DRC unconnected).
set -uo pipefail
PRE="$1"; OUT="$2"; PASSES="${3:-3}"; shift 3 2>/dev/null || shift $#
HERE="$(cd "$(dirname "$0")" && pwd)"; PROJ="$(cd "$HERE/../.." && pwd)"
JAVA="${JAVA:-/opt/homebrew/opt/openjdk/bin/java}"
JAR="${FREEROUTING_JAR:-$HOME/Documents/KiCad/10.0/3rdparty/freerouting/freerouting-2.4.1.jar}"
KPY="/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
KICAD="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
KEEPOUT_JSON="${KEEPOUT_JSON-$PROJ/tools/pcb/fc_keepout.json}"
HERITAGE_SNAP="${HERITAGE_SNAP:-$PROJ/tools/baseline/heritage_rev2.json}"
FR_TIMEOUT_MIN="${FR_TIMEOUT_MIN:-180}"
WORK="$(dirname "$OUT")"; BASE="$(basename "${OUT%.kicad_pcb}")"
PREP="$WORK/$BASE.prep.kicad_pcb"; EXPORT="$WORK/$BASE.export.kicad_pcb"; DSN="$WORK/$BASE.dsn"; DSNF="$WORK/$BASE.fixed.dsn"
SES="$WORK/$BASE.ses"; POST="$WORK/$BASE.post.kicad_pcb"; LOG="$WORK/$BASE.freerouting.log"
py() { "$KPY" "$@" 2>&1 | grep -vE 'stdpbase\.cpp|pcb_track\.cpp|memory leak|Debug:'; }

echo "route: 1/8 prep (unique refs so DSN export works)"
py "$HERE/route_merge.py" prep "$PRE" "$PREP" || { echo "route: prep failed"; exit 2; }
siblings() {  # every KiCad load/fill/DRC must see the project rules and libraries: .kicad_pro, .kicad_dru, lib tables, local libs
  local src="${1%.kicad_pcb}" dst="${2%.kicad_pcb}" sdir ddir; sdir="$(dirname "$1")"; ddir="$(dirname "$2")"
  cp "$src.kicad_pro" "$dst.kicad_pro" 2>/dev/null || true; cp "$src.kicad_dru" "$dst.kicad_dru" 2>/dev/null || true
  if [ "$sdir" != "$ddir" ]; then for f in sym-lib-table fp-lib-table; do [ -e "$ddir/$f" ] || cp "$sdir/$f" "$ddir/$f" 2>/dev/null || true; done
    for d in footprints.pretty symbols Backup_Footprints; do [ -e "$ddir/$d" ] || cp -R "$sdir/$d" "$ddir/$d" 2>/dev/null || true; done; fi
}
siblings "$PRE" "$PREP"

echo "route: 2/8 keep-out on the export copy (${KEEPOUT_JSON:-none})"
cp "$PREP" "$EXPORT"; siblings "$PREP" "$EXPORT"
if [ -n "$KEEPOUT_JSON" ]; then
  py - "$EXPORT" "$KEEPOUT_JSON" <<'PY'
import sys, json, pcbnew
from collections import Counter
b = pcbnew.LoadBoard(sys.argv[1]); spec = json.load(open(sys.argv[2])); n = Counter()
ncu = b.GetCopperLayerCount(); all_cu = ['F.Cu'] + ['In%d.Cu' % i for i in range(1, ncu - 1)] + ['B.Cu']
for ks in spec.get('keepouts', []):
    forbid = ks.get('forbid', 'both'); layers = ks.get('layers', 'all')
    z = pcbnew.ZONE(b); z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(forbid == 'both'); z.SetDoNotAllowVias(True)          # tracks-only would export as wire_keepout, which Freerouting ignores
    z.SetDoNotAllowZoneFills(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET()
    for l in (all_cu if layers == 'all' else layers): ls.AddLayer(b.GetLayerID(l))
    z.SetLayerSet(ls); z.SetZoneName(ks.get('name', 'FC_KEEPOUT'))
    ol = z.Outline(); ol.NewOutline()
    for x, y in ks['poly']: ol.Append(pcbnew.VECTOR2I_MM(x, y))
    b.Add(z); n[forbid] += 1
pcbnew.SaveBoard(sys.argv[1], b); print('keep-out rule areas on the export copy:', dict(n))
if sum(n.values()) == 0: sys.exit(1)
print('KEEPOUT_APPLIED')
PY
  KO_OUT="$(py - "$EXPORT" "$KEEPOUT_JSON" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); print('KEEPOUT_PRESENT %d' % sum(1 for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith('FC_')))
PY
)"
  echo "$KO_OUT" | grep -q 'KEEPOUT_PRESENT [1-9]' || { echo "route: keep-out fixture was NOT applied ($KO_OUT) - refusing to route unconstrained"; exit 2; }
fi

echo "route: 3/8 DSN export + fixdsn (existing wires/vias → (type fix), degenerate stubs dropped)"
py - "$EXPORT" "$DSN" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); ok = pcbnew.ExportSpecctraDSN(b, sys.argv[2]); print('DSN export', 'ok' if ok else 'FAILED')
PY
[ -s "$DSN" ] || { echo "route: DSN export failed (duplicate refs? see README)"; exit 3; }
py "$HERE/route_merge.py" fixdsn "$DSN" "$DSNF" || { echo "route: fixdsn failed"; exit 3; }
echo "route: keepout records in DSN: $(grep -c '(keepout' "$DSNF") keepout + $(grep -c '(via_keepout' "$DSNF") via_keepout (mounting-hole rings included)"

echo "route: 4/8 freerouting -mp $PASSES -mt 1 (log: $LOG; timeout ${FR_TIMEOUT_MIN} min; slow ≠ hung, check CPU%)"
( "$JAVA" -jar "$JAR" -de "$DSNF" -do "$SES" -mp "$PASSES" -mt 1 "$@" > "$LOG" 2>&1 ) &
FRPID=$!
SECS=0
while kill -0 "$FRPID" 2>/dev/null; do
  sleep 30; SECS=$((SECS+30))
  if [ $((SECS % 300)) -eq 0 ]; then echo "route:   … $((SECS/60)) min: $(grep -E 'pass|completed|Optimization|score|unrouted' "$LOG" | grep -v 'Polyline' | tail -1 | cut -c1-140)"; fi
  if [ "$SECS" -ge $((FR_TIMEOUT_MIN*60)) ]; then echo "route: timeout after ${FR_TIMEOUT_MIN} min, stopping freerouting"; kill "$FRPID" 2>/dev/null; break; fi
done
wait "$FRPID" 2>/dev/null
[ -s "$SES" ] || { echo "route: no SES produced; tail of log:"; grep -v Polyline "$LOG" | tail -15; exit 4; }
grep -vE 'Polyline|ShapeSearchTree|ConductionArea' "$LOG" | grep -iE 'completed|unrouted|score|Optimization' | tail -6 | sed 's/^/route:   /'

echo "route: 5/8 SES import into a fresh copy of PRE (no keep-out fixture)"
py - "$PREP" "$SES" "$POST" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); ok = pcbnew.ImportSpecctraSES(b, sys.argv[2]); pcbnew.SaveBoard(sys.argv[3], b)
print('SES import', 'ok' if ok else 'FAILED', '| tracks+vias now', len(b.GetTracks()))
PY
[ -s "$POST" ] || { echo "route: SES import failed"; exit 5; }
siblings "$PREP" "$POST"

echo "route: 6/8 merge (heritage from PRE untouched + only new tracks/vias)"
py "$HERE/route_merge.py" merge "$PRE" "$POST" "$OUT" --report || { echo "route: merge failed"; exit 6; }
siblings "$PRE" "$OUT"

echo "route: 7/8 attachment gate (+ prune) and heritage check"
py "$HERE/attachment_check.py" "$HERITAGE_SNAP" "$OUT" > "$WORK/$BASE.attach.txt"; grep -c '^VIOLATION' "$WORK/$BASE.attach.txt" > /dev/null
NV=$(grep -c '^VIOLATION' "$WORK/$BASE.attach.txt" || true); tail -1 "$WORK/$BASE.attach.txt" | sed 's/^/route:   /'
if [ "${PRUNE:-1}" = "1" ] && [ "${NV:-0}" -gt 0 ]; then
  cp "$OUT" "$WORK/$BASE.unpruned.kicad_pcb"
  echo "route:   pruning $NV violation(s) (unpruned copy kept at $WORK/$BASE.unpruned.kicad_pcb; full list in $WORK/$BASE.attach.txt)"
  py "$HERE/attachment_check.py" "$HERITAGE_SNAP" "$OUT" --prune "$OUT" | grep -iE 'pruned|removed' | tail -2 | sed 's/^/route:   /'
  py "$HERE/attachment_check.py" "$HERITAGE_SNAP" "$OUT" | tail -1 | sed 's/^/route:   after prune: /'
  echo "route:   the pruned connections are now unconnected (see DRC); route them by hand as stubs from the allowed pads (tools/pcb/README.md)"
fi
if [ -n "${REF_BOARD:-}" ]; then
  py "$HERE/heritage.py" check "$HERITAGE_SNAP" "$OUT" --allow-zone-growth --allow-edge --refill --core-inset "${BAND_MM:-12}" --ref-board "$REF_BOARD" | grep -E 'VIOLATION|heritage check|band fill' | sed 's/^/route:   /'
else
  py "$HERE/heritage.py" check "$HERITAGE_SNAP" "$OUT" --allow-zone-growth --allow-edge | tail -1 | sed 's/^/route:   /'
  echo "route:   (set REF_BOARD=<Rev2 .kicad_pcb> to also verify refilled copper inside the flight core)"
fi

echo "route: 8/8 DRC on $OUT"
"$KICAD" pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones --output "$WORK/$BASE.drc.json" "$OUT" 2>&1 | grep -v Fontconfig | tail -1
python3 "$HERE/drc_summary.py" "$WORK/$BASE.drc.json" | grep -E 'unconnected|errors:|clearance|courtyard|track_width|via'
