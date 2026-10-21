"""rulearea.py BOARD : add (idempotent) the FC_COPY rule area = Rev2 outline from the heritage snapshot, all copper layers, no keepouts"""
import sys, ed, pcbnew
E = ed.Editor(sys.argv[1])
b = E.b
if any(z.GetZoneName() == 'FC_COPY' for z in b.Zones()):
    sys.exit('FC_COPY exists')
z = pcbnew.ZONE(b)
z.SetIsRuleArea(True)
z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False); z.SetDoNotAllowPads(False)
z.SetDoNotAllowZoneFills(False); z.SetDoNotAllowFootprints(False)
z.SetLayerSet(pcbnew.LSET.AllCuMask(b.GetCopperLayerCount()))
z.SetZoneName('FC_COPY')
ol = z.Outline(); ol.NewOutline()
for x, y in ed.HER['rev2_outline']:
    ol.Append(pcbnew.VECTOR2I_MM(x, y))
b.Add(z)
E.log.append(('add', f'rule area FC_COPY {len(ed.HER["rev2_outline"])} pts', ''))
E.save()
