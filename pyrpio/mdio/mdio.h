#ifndef MDIO_H
#define MDIO_H

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

int mdio_open(uint8_t clk_pin, uint8_t data_pin);
int mdio_close(uint8_t clk_pin, uint8_t data_pin);

int mdio_write_reg(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t reg, uint16_t val);
uint16_t mdio_read_reg(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t reg);

uint16_t mdio_read_val(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad);
int mdio_write_add(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t val);
int mdio_write_val(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t val);

#endif
