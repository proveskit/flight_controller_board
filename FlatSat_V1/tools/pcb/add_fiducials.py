#!/usr/bin/env python3
"""Place the panel-reserved fiducials (brief F10 / PLM-09) as board-only footprints. Idempotent: an existing
FIDn is moved to its site, not duplicated. Run with KiCad's bundled python3.

  add_fiducials.py BOARD.kicad_pcb
"""
import sys

import pcbnew

LIB = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Fiducial.pretty'
SITES = {'FID1': (232.5, 50.5), 'FID2': (252.0, 140.0)}

board = pcbnew.LoadBoard(sys.argv[1])
for ref, (x, y) in SITES.items():
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        fp = pcbnew.FootprintLoad(LIB, 'Fiducial_1mm_Mask2mm')
        fp.SetReference(ref)
        fp.SetBoardOnly(True)
        fp.SetExcludedFromBOM(True)
        fp.SetExcludedFromPosFiles(True)
        fp.Reference().SetVisible(False)
        board.Add(fp)
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    print(f'{ref} at ({x}, {y})')
pcbnew.SaveBoard(sys.argv[1], board)
