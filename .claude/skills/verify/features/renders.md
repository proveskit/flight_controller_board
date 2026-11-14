# Renders for review

Renders produce the images a reviewer looks at: the full schematic as one PDF, each sheet as an SVG (and PNG when a converter exists), and top and bottom 3D board renders. Project rule: every PR with a visual change carries verification screenshots, and these are them.

## Sub-features

- `render-sch-pdf` writes every sheet into `render/schematic.pdf`.
- `render-sch-sheets` writes one SVG per sheet into `render/sch/`, plus PNG through `rsvg-convert` (`brew install librsvg`).
- `render-pcb-3d` writes `render/pcb-top.png` and `render/pcb-bottom.png`.
- `render-models` lists every footprint whose 3D model file cannot be found in `render/missing-3d-models.txt`.

## How to get to it (user POV)

- In the KiCad GUI, Schematic Editor, File, Plot; PCB Editor, View, 3D Viewer, File, Export Current View as PNG.
- Headless: `kicad-cli sch export pdf|svg` and `kicad-cli pcb render`.

## Driving it with kv.py

Preconditions:

- A staged run `RUN` for the revision under review.

- **Render.** Run `$K render "$RUN"`. Each output prints as `wrote <path>`, and the verdict reads `VERDICT render <board>@<rev>: N schematic sheets as SVG, 0 output files missing, M of T footprint 3D models not found`.
- **Look at it.** Open `render/pcb-top.png` and `render/pcb-bottom.png`. The board outline, silkscreen and placed parts are visible. Open the PNG or SVG of each sheet the change touched.
- **Before and after.** Render the base run too. Put the matching base and head images side by side in the PR.
- **Proof.** Attach the PNGs to the PR. Name the run path they came from.

## Gotchas

- `kicad-cli pcb render` draws a footprint whose 3D model is missing as bare pads and prints no warning. `kv.py` resolves each model path itself and counts the misses in the verdict. `FC_V5e_Production_Rev1` misses 42 of 246, and the render matches the list. The E22 radio (U13), S-band module (U30), DF11 headers (J10, J14, J16, J18, J19, J20), Pico-Lock connectors, USB-C (J12) and coin cell holder (BT1) show as pads only. A part missing from a render is a model path problem unless DRC also reports it.
- Old library variables still resolve. KiCad 10 maps `${KICAD6_3DMODEL_DIR}` to `${KICAD9_3DMODEL_DIR}` onto its own library, and falls back from a missing `.wrl` to the `.step` beside it. The misses come from `${EASYEDA2KICAD}` (not defined on the Mac mini), absolute `/Users/ncc-michael/...` paths, Pico-Lock models that are not in the stock library, and a few stock names that changed.
- `--quality basic` is fast (about 4 s a side) and good enough for review. Rerun by hand with `kicad-cli pcb render --quality high` for docs images.
- Sheet SVG names come from the hierarchical sheet names, joined by `-` under the root name (`FC_V5e_Production_Rev1-Power Systems-Load Switches.svg`), not from sheet file names.
- The requested 2000 by 1500 render comes out 1992 by 1488.
