import pcbnew, sys, collections
b = pcbnew.LoadBoard(sys.argv[1])
vias = collections.Counter(); tw = collections.Counter()
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        vias[(round(pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu)),3), round(pcbnew.ToMM(t.GetDrill()),3), t.GetViaType())] += 1
    else:
        tw[round(pcbnew.ToMM(t.GetWidth()),3)] += 1
print('vias (dia, drill, type):', sorted(vias.items()))
print('min track widths:', sorted(tw.items())[:6], 'total segs', sum(tw.values()))
holes = collections.Counter()
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetDrillSize().x > 0: holes[(round(pcbnew.ToMM(p.GetDrillSize().x),2), round(pcbnew.ToMM(p.GetDrillSize().y),2), p.GetAttribute())] += 1
print('pad holes:', sorted(holes.items())[:8])
ds = b.GetDesignSettings()
print('min clearance', pcbnew.ToMM(ds.m_MinClearance), 'min track', pcbnew.ToMM(ds.m_TrackMinWidth), 'min hole', pcbnew.ToMM(ds.m_MinThroughDrill), 'layers', b.GetCopperLayerCount(), 'thickness', pcbnew.ToMM(ds.GetBoardThickness()))
