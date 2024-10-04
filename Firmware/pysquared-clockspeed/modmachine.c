//
// Created by mad on 10/4/24.
//
#include "clock_speed.c"

// M    odule methods
STATIC const mp_map_elem_t pico_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR_set_clock_speed), MP_ROM_PTR(&pico_set_clock_speed_obj) },
    { MP_ROM_QSTR(MP_QSTR_hello_world), MP_ROM_PTR(&pico_hello_world_obj) },
};

// Dictionary
STATIC MP_DEFINE_CONST_DICT(pico_module_globals, pico_module_globals_table);

// Module Object
const mp_obj_module_t pico_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&pico_module_globals,
};

// Register the module
MP_REGISTER_MODULE(MP_QSTR_pico, pico_module);
