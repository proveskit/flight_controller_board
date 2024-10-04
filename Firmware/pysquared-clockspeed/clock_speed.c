//
// Created by mad on 10/4/24.
//
#include "py/runtime.h"
#include "hardware/clocks.h"

// Function for clock speed
        STATIC mp_obj_t pico_set_clock_speed(mp_obj_t speed) {
    int new_speed = mp_obj_get_int(speed);
    if (!set_sys_clock_khz(new_speed, true)) {
        mp_raise_ValueError("Failed to set the clock speed");
    }
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(pico_set_clock_speed_obj, pico_set_clock_speed);

// Function for testing if functions do actually get passed
STATIC mp_obj_t pico_hello_world(void) {
    printf("Hello, World!\n");
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_0(pico_hello_world_obj, pico_hello_world);