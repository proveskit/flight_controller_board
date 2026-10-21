import sys, ed
E = ed.Editor(sys.argv[1])
ed.set_field(E, 'JP510', 'Description', '2-pin header, shunt REMOVED by default (D3): charger SYS -> Dir_Chrg_In')
ed.set_field(E, 'TP512', 'Description', 'Test point, BQ25886 BAT (CBAT C515 only; JP510 is fed from SYS)')
E.save()
