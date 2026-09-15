		(symbol "easyeda2kicad:TCA4311ADGKR"
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(in_pos_files yes)
			(duplicate_pin_numbers_are_jumpers no)
			(property "Reference" "U4"
				(at 0 13.97 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Value" "TCA4311ADGKR"
				(at 0 11.43 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Footprint" "easyeda2kicad:MSOP-8_L3.0-W3.0-P0.65-LS5.0-BL"
				(at 0 -13.97 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Datasheet" "https://lcsc.com/product-detail/Interface-ICs_TI_TCA4311ADGKR_TCA4311ADGKR_C130025.html"
				(at 0 -16.51 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Description" ""
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
			(property "LCSC Part" "C130025"
				(at 0 -19.05 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(symbol "TCA4311ADGKR_0_1"
				(rectangle
					(start -10.16 8.89)
					(end 10.16 -8.89)
					(stroke
						(width 0)
						(type default)
					)
					(fill
						(type background)
					)
				)
				(pin unspecified line
					(at -15.24 -1.27 0)
					(length 5.08)
					(name "EN"
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
				(pin unspecified line
					(at 15.24 3.81 180)
					(length 5.08)
					(name "SCLOUT"
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
				(pin unspecified clock
					(at -15.24 3.81 0)
					(length 5.08)
					(name "SCLIN"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "3"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin power_in line
					(at 15.24 -6.35 180)
					(length 5.08)
					(name "GND"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "4"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin unspecified line
					(at 15.24 -1.27 180)
					(length 5.08)
					(name "READY"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "5"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin unspecified line
					(at -15.24 6.35 0)
					(length 5.08)
					(name "SDAIN"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "6"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin unspecified line
					(at 15.24 6.35 180)
					(length 5.08)
					(name "SDAOUT"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "7"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin power_in line
					(at -15.24 -6.35 0)
					(length 5.08)
					(name "VCC"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "8"
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
