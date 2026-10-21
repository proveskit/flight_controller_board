"""Item 6 (finish): named nets for the auto-named bench power nodes, and the one geometric clearance fix the
0.25 mm BenchPower class needs (VSOLAR run past JP400.1)."""
import sys, ed
E = ed.Editor(sys.argv[1])
B, S = '/Battery Replica and Bench Power/', '/Solar Power Injection/'
for old, new in (('Net-(Q500-D-Pad5)', B + 'PROT_DRAIN'), ('Net-(C511-Pad1)', B + 'CHG_PMID'), ('Net-(C512-Pad1)', B + 'CHG_SW'),
                 ('Net-(D400-A)', S + 'INJ_A_PTC'), ('Net-(D400-K)', S + 'INJ_A_OR'),
                 ('Net-(D401-A)', S + 'INJ_B_PTC'), ('Net-(D401-K)', S + 'INJ_B_OR')):
    ed.rename_net(E, old, new)
E.remove(E.items('VSOLAR', 'F.Cu', 'track', near=(252.63, 148.33)), 'VSOLAR run 0.21 mm from JP400.1 (INJ_A_OR, BenchPower 0.25)')
E.track((252.8, 148.33), (252.63, 148.33), 1.5, 'F.Cu', 'VSOLAR')
E.path([(252.63, 148.33), (251.4, 148.33), (248.8, 145.73), (248.8, 144.5)], 1.0, 'F.Cu', 'VSOLAR')
E.save()
