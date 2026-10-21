import sys, pcbnew
T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1])
f=b.FindFootprintByReference('J510')
print('J510', T(f.GetPosition().x), T(f.GetPosition().y), f.GetOrientationDegrees(), f.GetLayerName())
for p in f.Pads():
    q=p.GetPosition(); s=p.GetSize(pcbnew.F_Cu)
    print(' pad',p.GetNumber(),p.GetNetname(),round(T(q.x),3),round(T(q.y),3),'size',T(s.x),T(s.y),'attr',p.GetAttribute(),'drill',T(p.GetDrillSize().x),T(p.GetDrillSize().y))
cy=f.GetCourtyard(pcbnew.F_CrtYd).BBox(); print('crtyd',T(cy.GetLeft()),T(cy.GetTop()),T(cy.GetRight()),T(cy.GetBottom()))
for g in f.GraphicalItems():
    if b.GetLayerName(g.GetLayer())=='F.Fab':
        bb=g.GetBoundingBox(); print(' fab',T(bb.GetLeft()),T(bb.GetTop()),T(bb.GetRight()),T(bb.GetBottom()))
nets={p.GetNetname() for p in f.Pads()}
print('--tracks touching J510 nets in bbox x250-275 y150-173')
for t in b.GetTracks():
    if t.GetNetname() not in nets: continue
    if t.GetClass()=='PCB_VIA':
        q=t.GetPosition()
        if 250<T(q.x)<275 and 145<T(q.y)<173: print(' via',t.GetNetname(),T(q.x),T(q.y),T(t.GetWidth(pcbnew.F_Cu)),T(t.GetDrill()))
        continue
    s,e=t.GetStart(),t.GetEnd()
    if any(250<T(p.x)<275 and 145<T(p.y)<173 for p in (s,e)):
        print(' trk',t.GetNetname(),b.GetLayerName(t.GetLayer()),T(t.GetWidth()),(round(T(s.x),3),round(T(s.y),3)),(round(T(e.x),3),round(T(e.y),3)),t.m_Uuid.AsString()[:8])
print('--other items x 250-274 y 160-173')
for t in b.GetTracks():
    pts=[t.GetPosition()] if t.GetClass()=='PCB_VIA' else [t.GetStart(),t.GetEnd()]
    if t.GetNetname() in nets: continue
    if any(250<T(p.x)<274 and 160<T(p.y)<173 for p in pts):
        print(' ',t.GetClass(),t.GetNetname(),b.GetLayerName(t.GetLayer()),[ (round(T(p.x),2),round(T(p.y),2)) for p in pts])
for o in b.GetFootprints():
    q=o.GetPosition()
    if 248<T(q.x)<276 and 158<T(q.y)<175: print(' fp',o.GetReference(),T(q.x),T(q.y))
for d in b.GetDrawings():
    if d.GetClass()=='PCB_TEXT' or b.GetLayerName(d.GetLayer()) in ('Edge.Cuts',):
        bb=d.GetBoundingBox()
        if T(bb.GetBottom())>160 and T(bb.GetLeft())<290: print(' draw',d.GetClass(),b.GetLayerName(d.GetLayer()),getattr(d,'GetText',lambda:'')(),T(bb.GetLeft()),T(bb.GetTop()),T(bb.GetRight()),T(bb.GetBottom()))
