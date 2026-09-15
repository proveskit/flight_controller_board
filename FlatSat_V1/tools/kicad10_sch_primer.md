# KiCad 10 schematic S-expression primer (samples extracted verbatim from FC_V5e_Production_Rev2)

File header used by every sheet in this project (copy exactly; only the uuid changes):
```
(kicad_sch
	(version 20260306)
	(generator "eeschema")
	(generator_version "10.0")
	(uuid "<fresh uuid4 for the sheet file>")
	(paper "A3")
	(lib_symbols
		... one full (symbol "Lib:Name" ...) definition per distinct lib_id used on this sheet ...
	)
	... junctions, no_connects, wires, labels, global_labels, texts, symbol instances ...
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
	(embedded_fonts no)
)
```
Notes: tabs for indentation; every symbol instance and every wire/label/junction has its own (uuid "..."); coordinates are mm on a 1.27 mm grid (pins must land exactly on wire endpoints); a symbol instance lists every pin of the lib symbol with a uuid; the (instances (project "<PROJECT>" (path "/<root-uuid>/<this-sheet-symbol-uuid>" (reference "R201") (unit 1)))) block carries the reference designator for this sheet path.


## Resistor symbol instance R104 (load_switches sheet)
```
	(symbol
		(lib_id "mainboard:RESISTOR0603")
		(at 218.44 81.28 180)
		(unit 1)
		(body_style 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(dnp no)
		(uuid "59e2c234-6af0-4ef7-b0ad-478bae69dfd1")
		(property "Reference" "R104"
			(at 221.996 77.724 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.778 1.778)
				)
				(justify bottom)
			)
		)
		(property "Value" "4.7k"
			(at 213.614 79.756 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.778 1.778)
				)
				(justify top)
			)
		)
		(property "Footprint" "Resistor_SMD:R_0402_1005Metric"
			(at 218.44 81.28 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Datasheet" ""
			(at 218.44 81.28 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Description" "4.7K 0603"
			(at 218.44 85.344 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(pin "1"
			(uuid "928573d3-be08-45a6-8de8-185dd1233c20")
		)
		(pin "2"
			(uuid "debcbc2c-4016-4d48-8b9e-bd48a17fa1e5")
		)
		(instances
			(project "FC_V5e_Production_Rev2"
				(path "/c64c0d72-a9f6-4f3a-891e-1f647558f538/7cbc73fc-c188-4597-842f-d15f69db7471/1ac8f3d4-e8b4-451e-be76-8bf59103b6c5"
					(reference "R104")
					(unit 1)
				)
			)
		)
	)
```


## Power symbol instance (GND)
```
	(symbol
		(lib_id "power:GND")
		(at 389.89 238.76 0)
		(unit 1)
		(body_style 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(dnp no)
		(fields_autoplaced yes)
		(uuid "026be261-bcce-4e46-bdb1-71f102535785")
		(property "Reference" "#PWR047"
			(at 389.89 245.11 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "GND"
			(at 389.89 243.2034 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" ""
			(at 389.89 238.76 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Datasheet" ""
			(at 389.89 238.76 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Description" ""
			(at 389.89 238.76 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(pin "1"
			(uuid "cb0d5c7b-b3b7-4cbc-bedf-491c8db71729")
		)
		(instances
			(project "FC_V5e_Production_Rev2"
				(path "/c64c0d72-a9f6-4f3a-891e-1f647558f538"
					(reference "#PWR047")
					(unit 1)
				)
			)
		)
	)
```


## Global label sample
```
	(global_label "F0_SDA"
		(shape output)
		(at 231.14 200.66 180)
		(fields_autoplaced yes)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify right)
		)
		(uuid "001c30a3-a557-47f8-a466-bc6c032fce2d")
		(property "Intersheetrefs" "${INTERSHEET_REFS}"
			(at 221.321 200.66 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify right)
			)
		)
	)
```


## Local label sample
```
	(label "V_SOLAR_SENSE"
		(at 55.88 63.5 0)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify left bottom)
		)
		(uuid "1f8f512c-37fe-4175-a218-3b9a9618e59b")
	)
```


## Wire sample
```
	(wire
		(pts
			(xy 231.14 64.77) (xy 232.41 64.77)
		)
		(stroke
			(width 0)
			(type default)
		)
		(uuid "0023e085-5400-40f4-b9a0-70d6d53dfc38")
	)
```


## Junction sample
```
	(junction
		(at 165.1 187.96)
		(diameter 0)
		(color 0 0 0 0)
		(uuid "00a45fd6-5d49-4bcf-9e54-57544d6d81b4")
	)
```


## No-connect sample
```
	(no_connect
		(at 50.8 242.57)
		(uuid "223f6822-58bf-4c88-9c4e-15dd51e66d98")
	)
```


## Text note sample
```
	(text "I2C Address: 0x41"
		(exclude_from_sim no)
		(at 40.894 23.622 0)
		(effects
			(font
				(size 1.27 1.27)
			)
		)
		(uuid "08ad6ed9-b79b-4dab-8848-8afd0ed914a1")
	)
```


## IC symbol instance U6 TPS4H160 (load_switches sheet): multi-pin instance with MPN/LCSC-style properties
```
	(symbol
		(lib_id "easyeda2kicad:TPS4H160AQPWPRQ1")
		(at 247.65 96.52 0)
		(unit 1)
		(body_style 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(in_pos_files yes)
		(dnp no)
		(uuid "afb524b5-ff79-4415-82c8-9daa19ec0991")
		(property "Reference" "U6"
			(at 234.442 72.39 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "TPS4H160AQPWPRQ1"
			(at 233.172 74.422 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" "easyeda2kicad:HTSSOP-28_L9.7-W4.4-P0.65-LS6.4-BL-EP"
			(at 247.65 120.65 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Datasheet" "https://lcsc.com/product-detail/New-Arrivals_Texas-Instruments-Texas-Instruments-TPS4H160AQPWPRQ1_C485918.html"
			(at 247.65 123.19 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Description" "Quad channel automotive load switch"
			(at 247.65 96.52 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "LCSC Part" "C485918"
			(at 247.65 125.73 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(pin "2"
			(uuid "3b99372d-6994-462d-840b-0af69de12df1")
		)
		(pin "6"
			(uuid "c3ece9a3-da20-42cf-ad9a-dc0b9e40914a")
		)
		(pin "1"
			(uuid "f69abdb0-b5d3-4b1c-a87a-9ea754e323ac")
		)
		(pin "3"
			(uuid "37828c5e-3091-498a-9223-809b65c42391")
		)
		(pin "4"
			(uuid "9dee06b3-6507-487d-9f35-97505c2571c8")
		)
		(pin "7"
			(uuid "957bfd6e-c585-4d1b-8997-a8708c130da6")
		)
		(pin "5"
			(uuid "abce282d-1088-4733-910c-71f56140258f")
		)
		(pin "8"
			(uuid "168621e7-8a47-4c5e-bb20-f70778070a28")
		)
		(pin "9"
			(uuid "8074c3d3-df6e-4886-a7bc-b4f033b95c8e")
		)
		(pin "10"
			(uuid "4ec6b15f-5c3b-42c7-b3e2-de24bc0a750b")
		)
		(pin "11"
			(uuid "60f2f5f4-0c94-4285-8109-f5f14cdbe225")
		)
		(pin "12"
			(uuid "a63a6589-4223-4479-a85c-dcc237466135")
		)
		(pin "13"
			(uuid "e960bf5a-5901-4ae0-90da-7f449aa1fe5b")
		)
		(pin "14"
			(uuid "5b7e78e0-020d-4613-8985-7307001b3764")
		)
		(pin "29"
			(uuid "dbc89543-7338-4e66-a01d-e139a903775e")
		)
		(pin "28"
			(uuid "ec584291-5fb0-4b74-9bfe-d826e4687b0b")
		)
		(pin "27"
			(uuid "9e0b8ee2-899f-49dc-ab9c-558a36c83309")
		)
		(pin "26"
			(uuid "b803e8bd-a821-4fe7-b4c3-ec5ae987434d")
		)
		(pin "25"
			(uuid "312889f0-cab9-4d0d-a8dd-28b1d6c9b11c")
		)
		(pin "24"
			(uuid "2950d384-9f87-4d43-8db5-4447b4df21f8")
		)
		(pin "23"
			(uuid "7553d714-b4c1-463c-a6b7-d93bdd971271")
		)
		(pin "22"
			(uuid "56838df2-bbff-4988-897d-dea8e30f9c89")
		)
		(pin "21"
			(uuid "5b37c7d1-5bf9-49f3-82cb-fb51b990c99d")
		)
		(pin "20"
			(uuid "8829c0dd-c466-4338-a8cd-55a7f1a5ca4d")
		)
		(pin "19"
			(uuid "d4539d5c-16e8-40c6-b3df-d5a1fdf010b2")
		)
		(pin "18"
			(uuid "71e2a469-2638-44e9-8170-ca4c93819c87")
		)
		(pin "17"
			(uuid "81f48863-5fdf-4f2a-bf24-00c42ef7e4a7")
		)
		(pin "16"
			(uuid "83b9e9ff-8b99-4d6c-83ac-8f15503c24d6")
		)
		(pin "15"
			(uuid "9b821983-c0f3-4576-930e-402e68fe53bf")
		)
		(instances
			(project "FC_V5e_Production_Rev2"
				(path "/c64c0d72-a9f6-4f3a-891e-1f647558f538/7cbc73fc-c188-4597-842f-d15f69db7471/1ac8f3d4-e8b4-451e-be76-8bf59103b6c5"
					(reference "U6")
					(unit 1)
				)
			)
		)
	)
```


## Hierarchical sheet symbol in root (Power Systems)
```
	(sheet
		(at 57.15 54.61)
		(size 25.4 12.7)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(dnp no)
		(fields_autoplaced yes)
		(stroke
			(width 0.1524)
			(type solid)
		)
		(fill
			(color 0 0 0 0)
		)
		(uuid "7cbc73fc-c188-4597-842f-d15f69db7471")
		(property "Sheetname" "Power Systems"
			(at 57.15 53.8984 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left bottom)
			)
		)
		(property "Sheetfile" "eps_side.kicad_sch"
			(at 57.15 67.8946 0)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left top)
			)
		)
		(instances
			(project "FC_V5e_Production_Rev2"
				(path "/c64c0d72-a9f6-4f3a-891e-1f647558f538"
					(page "4")
				)
			)
		)
	)
```


## sheet_instances block in root
```
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
```


## sheet_instances block in a sub-sheet (eps_side)
```
(none)
```


## lib_symbols entry samples (one power symbol, one passive). Every lib_id used on a sheet needs its full definition inside (lib_symbols ...). Copy definitions verbatim from KiCad library files (/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/<Lib>.kicad_sym, changing (symbol "Name" to (symbol "Lib:Name") and from a .kicad_sym the sub-symbols stay "Name_0_1"/"Name_1_1") or from an existing schematic that already embeds it.
```
		(symbol "power:GND"
			(power global)
			(pin_names
				(offset 0)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(in_pos_files yes)
			(duplicate_pin_numbers_are_jumpers no)
			(property "Reference" "#PWR"
				(at 0 -6.35 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Value" "GND"
				(at 0 -3.81 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Footprint" ""
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Description" "Power symbol creates a global label with name \"GND\" , ground"
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "ki_keywords" "power-flag"
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(symbol "GND_0_1"
				(polyline
					(pts
						(xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)
					)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
			(symbol "GND_1_1"
				(pin power_in line
					(at 0 0 270)
					(length 0)
					(hide yes)
					(name "GND"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)

		(symbol "Device:R_US"
			(pin_numbers
				(hide yes)
			)
			(pin_names
				(offset 0)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(in_pos_files yes)
			(duplicate_pin_numbers_are_jumpers no)
			(property "Reference" "R"
				(at 2.54 0 90)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Value" "R_US"
				(at -2.54 0 90)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Footprint" ""
				(at 1.016 -0.254 90)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Description" "Resistor, US symbol"
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "ki_keywords" "R res resistor"
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "ki_fp_filters" "R_*"
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(symbol "R_US_0_1"
				(polyline
					(pts
						(xy 0 2.286) (xy 0 2.54)
					)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 0 2.286) (xy 1.016 1.905) (xy 0 1.524) (xy -1.016 1.143) (xy 0 0.762)
					)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 0 0.762) (xy 1.016 0.381) (xy 0 0) (xy -1.016 -0.381) (xy 0 -0.762)
					)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 0 -0.762) (xy 1.016 -1.143) (xy 0 -1.524) (xy -1.016 -1.905) (xy 0 -2.286)
					)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type none)
					)
				)
				(polyline
					(pts
						(xy 0 -2.286) (xy 0 -2.54)
					)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
			(symbol "R_US_1_1"
				(pin passive line
					(at 0 3.81 270)
					(length 1.27)
					(name ""
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin passive line
					(at 0 -3.81 90)
					(length 1.27)
					(name ""
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "2"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
			)
			(embedded_fonts no)
		)
```


## Root sheet extents (A3 = 420x297 mm): items span x -21.082..402.9747, y -794.92..1022.25

- sheet 'RP2350AHHHHHHHHH' file=RP2350.kicad_sch at=(31.75,86.36) size=(44.45,63.5) uuid=0828f938-6835-4ac8-b7be-ff90971df31f
- sheet 'Power Systems' file=eps_side.kicad_sch at=(57.15,54.61) size=(25.4,12.7) uuid=7cbc73fc-c188-4597-842f-d15f69db7471
- sheet 'Watchdog Circuit' file=watchdog.kicad_sch at=(57.15,33.02) size=(24.13,10.16) uuid=d3e26510-981a-4dd5-9b7d-a587e6324dc6
- (inside eps_side) sheet 'Load Switches' file=load_switches.kicad_sch at=(318.77,196.85) uuid=1ac8f3d4-e8b4-451e-be76-8bf59103b6c5