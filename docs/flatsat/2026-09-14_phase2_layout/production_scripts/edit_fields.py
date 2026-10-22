"""PLM-08 header collapse + U1 LCSC field, on schematic symbols and board footprints (fields only).

Idempotent: rerunning finds every field already at its target and changes nothing.
  edit_fields.py PROJECT_DIR HERITAGE_REFS_CSV   (heritage refs = project.db part_info references)
"""
import re
import sys
from pathlib import Path

P = Path(sys.argv[1])
HEADERS = ["J300", "JP400", "JP401", "JP500", "JP510"] + [f"JP60{i}" for i in range(8)]
HDR_LCSC = "C492401"
HDR_DS = "https://www.lcsc.com/datasheet/lcsc_datasheet_2409302300_XFCN-PZ254V-11-02P_C492401.pdf"
U1_LCSC = "C181596"
HERITAGE = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else set()


def blocks(text, head):
    """Yield (start, end) of each top-level block starting with `head` (a line like '\\t(symbol\\n')."""
    i = 0
    while (s := text.find(head, i)) != -1:
        depth, j = 0, s
        while True:
            c = text[j]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            elif c == '"':
                j += 1
                while text[j] != '"':
                    j += 2 if text[j] == "\\" else 1
            j += 1
        yield s, j + 1
        i = j + 1


def set_prop(block, name, value):
    pat = re.compile(r'(\(property "' + re.escape(name) + r'" ")([^"]*)(")')
    m = pat.search(block)
    if m is None:
        return block, None
    return block[: m.start(2)] + value + block[m.end(2):], m.group(2)


def add_hidden_prop(block, name, value, indent):
    """Insert a hidden property after the last property of a symbol/footprint block, copying its position."""
    if f'(property "{name}" ' in block:
        return set_prop(block, name, value)
    props = list(re.finditer(r"\n" + indent + r'\(property "[^"]*" "[^"]*"\n(?:.*\n)*?' + indent + r"\)", block))
    last = props[-1]
    at = re.search(r"\(at [^)]*\)", last.group(0)).group(0)
    t = indent
    new = (f'\n{t}(property "{name}" "{value}"\n{t}\t{at}\n{t}\t(hide yes)\n{t}\t(show_name no)\n'
           f"{t}\t(do_not_autoplace no)\n{t}\t(effects\n{t}\t\t(font\n{t}\t\t\t(size 1.27 1.27)\n"
           f"{t}\t\t)\n{t}\t)\n{t})")
    return block[: last.end()] + new + block[last.end():], "(absent)"


log = []
for sch in sorted(P.glob("*.kicad_sch")):
    text = sch.read_text()
    out, pos = [], 0
    for s, e in blocks(text, "\n\t(symbol\n"):
        blk = text[s:e]
        m = re.search(r'\(property "Reference" "([^"]+)"', blk)
        ref = m.group(1) if m else None
        new = blk
        if ref in HEADERS:
            new, old = set_prop(new, "LCSC Part", HDR_LCSC)
            log.append((sch.name, ref, "LCSC Part", old, HDR_LCSC))
            new, old = set_prop(new, "Datasheet", HDR_DS)
            log.append((sch.name, ref, "Datasheet", old, HDR_DS))
        elif ref == "U1":
            new, old = add_hidden_prop(new, "LCSC", U1_LCSC, "\t\t")
            unit = re.search(r"\(unit (\d+)\)", blk).group(1)
            log.append((sch.name, f"U1 unit {unit}", "LCSC", old, U1_LCSC))
        out.append(text[pos:s] + new)
        pos = e
    out.append(text[pos:])
    new_text = "".join(out)
    if new_text != text:
        sch.write_text(new_text)

pcb = P / "FlatSat_V1.kicad_pcb"
text = pcb.read_text()
out, pos = [], 0
for s, e in blocks(text, "\n\t(footprint "):
    blk = text[s:e]
    m = re.search(r'\(property "Reference" "([^"]+)"', blk)
    ref = m.group(1) if m else None
    new = blk
    if ref in HEADERS:
        new, old = set_prop(new, "LCSC Part", HDR_LCSC)
        log.append(("pcb", ref, "LCSC Part", old, HDR_LCSC))
        new, old = set_prop(new, "Datasheet", HDR_DS)
        log.append(("pcb", ref, "Datasheet", old, HDR_DS))
    elif ref == "U1":
        new, old = set_prop(new, "LCSC", U1_LCSC)
        log.append(("pcb", ref, "LCSC", old, U1_LCSC))
    # A board-only "LCSC" field cloned from a heritage footprint shadows the schematic's "LCSC Part" in the
    # plugin's get_lcsc_value (first lcsc|jlc field wins). Phase-1/2 refs are not in project.db, so drop it.
    stale = re.search(r'\n\t\t\(property "LCSC" "([^"]*)"\n(?:\t\t\t.*\n)*?\t\t\)', new)
    if ref not in HERITAGE and stale and '(property "LCSC Part" "' in new:
        part = re.search(r'\(property "LCSC Part" "([^"]*)"', new).group(1)
        new = new[: stale.start()] + new[stale.end():]
        log.append(("pcb", ref, "LCSC (board-only, removed)", stale.group(1), f"LCSC Part {part}"))
    out.append(text[pos:s] + new)
    pos = e
out.append(text[pos:])
new_text = "".join(out)
if new_text != text:
    pcb.write_text(new_text)

for row in log:
    if row[3] != row[4] and row[2] != "Datasheet":
        print(" | ".join(str(x) for x in row))
print(len(log), "field visits;", sum(r[3] != r[4] for r in log), "changed")
