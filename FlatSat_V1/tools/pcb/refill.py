#!/usr/bin/env python3
"""Refill every zone and save in place (production must refill; owner F15). Run with KiCad's bundled python3
on a board that sits in its project directory, so the filler reads the project's rules.

  refill.py BOARD.kicad_pcb
"""
import sys

import pcbnew

board = pcbnew.LoadBoard(sys.argv[1])
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(sys.argv[1], board)
print(f'refilled {len(board.Zones())} zones -> {sys.argv[1]}')
