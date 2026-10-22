import pcbnew, json, sys
b = pcbnew.LoadBoard(sys.argv[1])
out = []
for fp in b.GetFootprints():
    a = fp.GetAttributes()
    fields = {f.GetName(): f.GetText() for f in fp.GetFields()}
    out.append(dict(ref=fp.GetReference(), value=fp.GetValue(), fpid=fp.GetFPIDAsString(),
        side='bottom' if fp.IsFlipped() else 'top',
        smd=bool(a & pcbnew.FP_SMD), tht=bool(a & pcbnew.FP_THROUGH_HOLE),
        ex_pos=bool(a & pcbnew.FP_EXCLUDE_FROM_POS_FILES), ex_bom=bool(a & pcbnew.FP_EXCLUDE_FROM_BOM),
        dnp=fp.IsDNP(), board_only=bool(a & pcbnew.FP_BOARD_ONLY),
        npads=len(fp.Pads()), lcsc=fields.get('LCSC Part', '') or fields.get('LCSC','')))
bb = b.GetBoardEdgesBoundingBox()
json.dump(dict(fps=out, bbox_mm=[pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())]), open(sys.argv[2],'w'), indent=0)
