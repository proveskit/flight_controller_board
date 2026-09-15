#!/usr/bin/env bash
# Build a throw-away copy of the FlatSat_V1 project in a scratch directory, add every
# new Phase-1 sheet that currently exists on disk (and parses) as a hierarchical sheet
# of the copied root, then run kicad-cli ERC + netlist export on the copy and print:
#   * ERC counts, delta vs the post-promotion baseline (Rev2 + the 8 label promotions; library-metadata noise excluded)
#   * the full violation list for the sheet named in $1 (or all new sheets if omitted)
#   * the netlist diff vs baseline restricted to nets touching the new sheets
# Nothing in the real project directory is modified.
#
# Usage: tools/harness_erc.sh [SheetName-substring] [--all-violations]
# Env:   FLATSAT_DIR (default: dir above tools/), SCRATCH (default: $TMPDIR/flatsat_harness_$USER)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PROJ="${FLATSAT_DIR:-$(cd "$HERE/.." && pwd)}"
KICAD="${KICAD_CLI:-/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
SCRATCH="${SCRATCH:-${TMPDIR:-/tmp}/flatsat_harness_$$}"
BASE_ERC="${BASE_ERC:-$PROJ/tools/baseline/erc_promoted.json}"
BASE_NET="${BASE_NET:-$PROJ/tools/baseline/netlist_promoted.kicadxml}"
FILTER="${1:-}"
ROOT_UUID="c64c0d72-a9f6-4f3a-891e-1f647558f538"

# key | sheet file | sheet symbol uuid | Sheetname | page | at-x | at-y
# Same table as docs/flatsat/.../00_pm_brief.md (sheet uuid, page, root placement). Keep in sync.
SHEETS='
emulator_mcu|emulator_mcu.kicad_sch|8394a2ec-8c1e-41a1-b086-be3289cedfbc|Emulator MCU|7|33.02|154.94
solar_emulation|solar_emulation.kicad_sch|0ec7a68a-65de-4eda-8407-9dcf20e51c0b|Solar and Sensor Emulation|8|71.12|154.94
solar_power_injection|solar_power_injection.kicad_sch|88d5f13b-6a4a-4f50-805f-872821082e52|Solar Power Injection|9|109.22|154.94
battery_protection_replica|battery_protection_replica.kicad_sch|bb4d499a-05c5-44dd-bd1a-4ed07bbd6ca0|Battery Replica and Bench Power|10|33.02|176.53
pyro_inhibit|pyro_inhibit.kicad_sch|ba398093-e7fc-4f25-8f04-4265c3e55b54|Pyro Inhibit and Jumpers|11|71.12|176.53
bench_io|bench_io.kicad_sch|54b8f29e-9dcb-4e24-99b9-415a110b338a|Bench IO|12|109.22|176.53
'

rm -rf "$SCRATCH"; mkdir -p "$SCRATCH"
# copy everything except the 12 MB board and git noise
rsync -a --exclude '*.kicad_pcb' --exclude '.history' --exclude '*-backups' --exclude 'jlcpcb' --exclude '~*.lck' "$PROJ/" "$SCRATCH/proj/"
ROOT="$SCRATCH/proj/FlatSat_V1.kicad_sch"

added=()
while IFS='|' read -r key file uuid name page x y; do
  [ -z "$key" ] && continue
  f="$SCRATCH/proj/$file"
  if [ ! -f "$f" ]; then echo "harness: $file not present yet, skipped"; continue; fi
  if grep -q "(uuid \"$uuid\")" "$ROOT"; then
    echo "harness: $file already referenced by the real root (integrated), left as is"; added+=("$name"); continue
  fi
  # parse check so one broken sheet from another agent does not sink everyone's ERC
  if ! python3 - "$f" <<'PY'
import sys,re
t=open(sys.argv[1],encoding='utf-8').read()
depth=0
for ch in re.sub(r'"(?:[^"\\]|\\.)*"','',t):
    if ch=='(': depth+=1
    elif ch==')': depth-=1
    if depth<0: sys.exit(1)
sys.exit(0 if depth==0 and t.lstrip().startswith('(kicad_sch') else 1)
PY
  then echo "harness: $file does not parse (unbalanced parens or bad header), skipped"; continue; fi
  python3 "$HERE/add_sheet_symbol.py" "$ROOT" --name "$name" --file "$file" --uuid "$uuid" --at "$x" "$y" --size 35.56 12.7 --page "$page" >/dev/null || { echo "harness: failed to add $file"; continue; }
  added+=("$name")
done <<< "$SHEETS"
echo "harness: sheets in hierarchy: ${added[*]:-none}"

"$KICAD" sch erc --format json --severity-all --output "$SCRATCH/erc.json" "$ROOT" 2>&1 | grep -v Fontconfig | tail -1
if [ ! -s "$SCRATCH/erc.json" ]; then echo "harness: ERC produced no report; the schematic failed to load. Check the sheet with tools/sch_lint.py and fix parse errors first."; exit 2; fi
"$KICAD" sch export netlist --format kicadxml --output "$SCRATCH/netlist.xml" "$ROOT" 2>&1 | grep -v Fontconfig | grep -v '^Done' || true

echo
echo "=== ERC delta vs baseline (default: Rev2 + 8 promotions; noise types excluded) ==="
python3 "$HERE/erc_summary.py" "$SCRATCH/erc.json" --baseline "$BASE_ERC" --ignore-noise
echo
if [ -n "$FILTER" ]; then
  echo "=== violations on sheets matching '$FILTER' ==="
  python3 "$HERE/erc_summary.py" "$SCRATCH/erc.json" --sheet "$FILTER" --list --ignore-noise
else
  for n in "${added[@]:-}"; do
    [ -z "$n" ] && continue
    echo "=== violations on '$n' ==="
    python3 "$HERE/erc_summary.py" "$SCRATCH/erc.json" --sheet "$n" --list --ignore-noise
  done
fi
if [ "${2:-}" = "--all-violations" ]; then
  echo "=== every non-noise violation in the project ==="
  python3 "$HERE/erc_summary.py" "$SCRATCH/erc.json" --list --ignore-noise
fi
echo
echo "=== netlist diff vs baseline (default: Rev2 + 8 promotions): nets that gained/lost pins, components added ==="
python3 "$HERE/netlist_diff.py" "$BASE_NET" "$SCRATCH/netlist.xml" --ignore-unconnected | head -400
echo
echo "harness dir: $SCRATCH (erc.json, netlist.xml)"
