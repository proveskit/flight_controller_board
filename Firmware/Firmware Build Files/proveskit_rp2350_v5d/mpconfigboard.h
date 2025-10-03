// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2024 Scott Shawcroft for Adafruit Industries
//
// SPDX-License-Identifier: MIT

#ifndef MICROPY_INCLUDED_BOARDS_PROVESKIT_RP2350_V5D_MPCONFIGBOARD_H
#define MICROPY_INCLUDED_BOARDS_PROVESKIT_RP2350_V5D_MPCONFIGBOARD_H

#define MICROPY_HW_BOARD_NAME       "PROVESKit FC Board RP2350 V5d"
#define MICROPY_HW_MCU_NAME         "rp2350a"

#define CIRCUITPY_DRIVE_LABEL       "PYSQAURED"

// Default I2C
#define DEFAULT_I2C_BUS_SDA (&pin_GPIO2)
#define DEFAULT_I2C_BUS_SCL (&pin_GPIO3)

// Default SPI
#define DEFAULT_SPI_BUS_SCK  (&pin_GPIO10)
#define DEFAULT_SPI_BUS_MOSI (&pin_GPIO11)
#define DEFAULT_SPI_BUS_MISO (&pin_GPIO12)

// Default UART
#define DEFAULT_UART_BUS_TX (&pin_GPIO0)
#define DEFAULT_UART_BUS_RX (&pin_GPIO1)

// PSRAM
#define CIRCUITPY_PSRAM_CHIP_SELECT (&pin_GPIO8)


#endif // MICROPY_INCLUDED_BOARDS_PROVESKIT_RP2350_V5D_MPCONFIGBOARD_H
