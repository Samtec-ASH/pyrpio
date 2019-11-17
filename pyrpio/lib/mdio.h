#ifndef MDIO_H
#define MDIO_H

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

int mdio_open(uint8_t clk_pin, uint8_t data_pin);
int mdio_close(uint8_t clk_pin, uint8_t data_pin);

void mdio_cmd(uint8_t clk_pin, uint8_t data_pin, uint8_t sf, uint8_t op, uint8_t pad, uint8_t dad);

uint16_t mdio_c22_read(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad);
int mdio_c22_write(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t val);

int mdio_c45_write_addr(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t reg);
int mdio_c45_write_val(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t val);
uint16_t mdio_c45_read_val(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad);

uint16_t mdio_c45_read(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t reg);
int mdio_c45_write(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t reg, uint16_t val);

uint32_t mdio_c45_read_dword(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint32_t reg);
int mdio_c45_write_dword(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint32_t reg, uint32_t val);

#endif
