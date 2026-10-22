"""Drive the released Bouni kicad-jlcpcb-tools (2026.04.03) headlessly: Library corrections, Store sync, Generate.

Runs the same calls, in the same order, as MainWindow.init_library/init_store/init_fabrication and
MainWindow.generate_fabrication_data. The only stand-in is the parent object, which carries the plugin's
own shipped settings.json, project_path, library and store (what the wx MainWindow carries).

  run_plugin.py PLUGIN_DIR BOARD DATA_DIR LOG [--sync-only]
"""
import json
import logging
import os
import sys
import threading
import types

PLUGIN_DIR, BOARD, DATA_DIR, LOG = sys.argv[1:5]
SYNC_ONLY = "--sync-only" in sys.argv

logging.basicConfig(filename=LOG, filemode="w", level=logging.DEBUG,
                    format="%(name)s %(levelname)s %(message)s")

# Import the plugin package without running its __init__ (which registers the ActionPlugin with pcbnew).
pkg = types.ModuleType("jlcplugin")
pkg.__path__ = [PLUGIN_DIR]
sys.modules["jlcplugin"] = pkg
sys.path.append(os.path.join(PLUGIN_DIR, "lib"))

import pcbnew  # noqa: E402

from jlcplugin.fabrication import Fabrication  # noqa: E402
from jlcplugin.library import Library  # noqa: E402
from jlcplugin.store import Store  # noqa: E402

USER_CORRECTIONS = [  # CLAUDE.md rule 5 + PLM-04, entered the way CorrectionManagerDialog.save_correction does
    ("^Hirose_DF11-", 180, (0.0, 0.0)),
    ("^CONN-SMD_4P-P2.00_DF11CZ", 180, (0.0, 0.0)),
    ("^L_pol_2016", 180, (0.0, 0.0)),
    ("^USB_C_Receptacle_HRO_TYPE-C-31-M-12*", 0, (0.0, 0.0)),
    ("^SOT-363_L2.0-W1.3-P0.65-LS2.1-BR", 0, (0.0, 0.0)),
]


class Parent:
    """What MainWindow exposes to Library, Store and Fabrication."""

    def __init__(self, board):
        with open(os.path.join(PLUGIN_DIR, "settings.json"), encoding="utf-8") as f:
            self.settings = json.load(f)
        self.settings["library"]["data_path"] = DATA_DIR
        self.project_path = os.path.dirname(board.GetFileName())
        self.pcbnew = pcbnew


board = pcbnew.LoadBoard(BOARD)
parent = Parent(board)

parent.library = Library(parent)
for t in threading.enumerate():
    if t is not threading.current_thread() and t.daemon:
        t.join(60)
lib = parent.library
for regex, rotation, offset in USER_CORRECTIONS:
    if lib.get_correction_data(regex):
        lib.update_correction_data(regex, rotation, offset)
    else:
        lib.insert_correction_data(regex, rotation, offset)
logging.getLogger("driver").info("corrections db %s rows %d", lib.correctionsdb_file,
                                 len(lib.get_all_correction_data()))

parent.store = Store(parent, parent.project_path, board)
if SYNC_ONLY:
    sys.exit(0)

fab = Fabrication(parent, board)
parent.fabrication = fab
warnings = fab.get_part_consistency_warnings()
logging.getLogger("driver").warning("consistency warnings:\n%s", warnings or "(none)")
fab.fill_zones()
fab.generate_geber(None)  # layer selector "Auto"
fab.generate_excellon()
fab.zip_gerber_excellon()
fab.generate_cpl()
fab.generate_bom()
count = parent.store.increment_generation_count()
logging.getLogger("driver").info("generation count %d", count)
print("done", fab.get_artifact_paths(), "generation", count)
