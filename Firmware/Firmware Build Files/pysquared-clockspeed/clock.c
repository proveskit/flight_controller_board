#include "py/runtime.h"
#include "hardware/clocks.h"

STATIC mp_obj_t machine_set_clock(mp_obj_t speed) {
    uint new_speed = mp_obj_get_int(speed);
    clock_configure(clk_sys, CLOCKS_CLK_SYS_CTRL_SRC_VALUE_CLKSRC_CLK_SYS_AUX,
                CLOCKS_CLK_SYS_CTRL_AUXSRC_VALUE_CLKSRC_PLL_SYS, 125 * MHZ, new_speed);
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(machine_set_clock_obj, machine_set_clock);

STATIC const mp_rom_map_elem_t machine_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_machine) },
    { MP_ROM_QSTR(MP_QSTR_set_clock), MP_ROM_PTR(&machine_set_clock_obj) },
};

STATIC MP_DEFINE_CONST_DICT(machine_module_globals, machine_module_globals_table);

const mp_obj_module_t machine_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&machine_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_machine, machine_module);
    