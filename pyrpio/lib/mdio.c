#include "mdio.h"
#include "bcm2835.h"

#define MDIO_C22_FRAME 1
#define MDIO_C45_FRAME 0

#define MDIO_OP_C22_WR 1
#define MDIO_OP_C22_RD 2

#define MDIO_OP_C45_AD 0
#define MDIO_OP_C45_WR 1
#define MDIO_OP_C45_RD 3
#define MDIO_OP_C45_RD_INC 2

#define MDIO_DELAY 50
#define MDIO_READ_DELAY 50
#define MDIO_DELAY_SETUP 10

#pragma GCC push_options
#pragma GCC optimize("O0")
#define noop ((void)0)
static void ndelay(long delay)
{
  while (delay-- > 0)
  {
    noop;
  }
  return;
}
#pragma GCC pop_options

int mdio_open(uint8_t clk_pin, uint8_t data_pin)
{
  bcm2835_gpio_write(clk_pin, 0);
  bcm2835_gpio_fsel(clk_pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_write(clk_pin, 0);
  bcm2835_gpio_set_pud(data_pin, BCM2835_GPIO_PUD_UP);
  bcm2835_gpio_write(data_pin, 1);
  bcm2835_gpio_fsel(data_pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_write(data_pin, 1);
  return 0;
}

int mdio_close(uint8_t clk_pin, uint8_t data_pin)
{
  bcm2835_gpio_write(clk_pin, 0);
  bcm2835_gpio_fsel(clk_pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_write(clk_pin, 0);
  bcm2835_gpio_set_pud(data_pin, BCM2835_GPIO_PUD_UP);
  bcm2835_gpio_write(data_pin, 1);
  bcm2835_gpio_fsel(data_pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_write(data_pin, 1);
  return 0;
}

static void mdio_write_bit(uint8_t clk_pin, uint8_t data_pin, uint8_t val)
{
  ndelay(MDIO_DELAY);
  bcm2835_gpio_write(data_pin, val);
  ndelay(MDIO_DELAY_SETUP);
  bcm2835_gpio_write(clk_pin, 1);
  ndelay(MDIO_DELAY);
  bcm2835_gpio_write(clk_pin, 0);
}

static int mdio_read_bit(uint8_t clk_pin, uint8_t data_pin)
{
  ndelay(MDIO_DELAY);
  int v = bcm2835_gpio_lev(data_pin);
  ndelay(MDIO_DELAY_SETUP);
  bcm2835_gpio_write(clk_pin, 1);
  ndelay(MDIO_DELAY);
  bcm2835_gpio_write(clk_pin, 0);
  return v;
}

static void mdio_write_bits(uint8_t clk_pin, uint8_t data_pin, uint16_t val, int bits)
{
  int i;
  for (i = bits - 1; i >= 0; i--)
  {
    mdio_write_bit(clk_pin, data_pin, (val >> i) & 1);
  }
}

static uint16_t mdio_read_bits(uint8_t clk_pin, uint8_t data_pin, int bits)
{
  int i;
  uint16_t ret = 0;
  for (i = bits - 1; i >= 0; i--)
  {
    ret <<= 1;
    ret |= mdio_read_bit(clk_pin, data_pin);
  }
  return ret;
}

static void mdio_flush(uint8_t clk_pin, uint8_t data_pin)
{
  int i;
  for (i = 0; i < 32; i++)
  {
    mdio_write_bit(clk_pin, data_pin, 1);
  }
}

void mdio_cmd(uint8_t clk_pin, uint8_t data_pin, uint8_t sf, uint8_t op, uint8_t pad, uint8_t dad)
{
  // Preamble
  mdio_flush(clk_pin, data_pin);
  // Header
  mdio_write_bits(clk_pin, data_pin, sf & 3, 2); // Start frame
  mdio_write_bits(clk_pin, data_pin, op & 3, 2); // OP Code
  mdio_write_bits(clk_pin, data_pin, pad, 5);    // Phy addr
  mdio_write_bits(clk_pin, data_pin, dad, 5);    // Reg addr (C22) / dev type (C45)
}

uint16_t mdio_c22_read(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad)
{
  int ret;
  // Send preamble/header
  mdio_cmd(clk_pin, data_pin, MDIO_C22_FRAME, MDIO_OP_C22_RD, pad, dad);
  // Release data pin
  bcm2835_gpio_fsel(data_pin, BCM2835_GPIO_FSEL_INPT);
  ndelay(1000);
  // Read 2-bit turnaround (gives slave time)
  mdio_read_bits(clk_pin, data_pin, 2);
  // Read 16-bit value
  ret = mdio_read_bits(clk_pin, data_pin, 16);
  // Capture data pin
  bcm2835_gpio_fsel(data_pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_write(data_pin, 1);
  mdio_flush(clk_pin, data_pin);
  return ret;
}

int mdio_c22_write(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t val)
{
  // Send preamble/header
  mdio_cmd(clk_pin, data_pin, MDIO_C22_FRAME, MDIO_OP_C22_WR, pad, dad);
  // Send the turnaround (10)
  mdio_write_bits(clk_pin, data_pin, 2, 2);
  // Send 16-bit value
  mdio_write_bits(clk_pin, data_pin, val, 16);
  mdio_flush(clk_pin, data_pin);
  return 0;
}

int mdio_c45_write_addr(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t reg)
{
  // Send preamble/header - C45 - ADDR
  mdio_cmd(clk_pin, data_pin, MDIO_C45_FRAME, MDIO_OP_C45_AD, pad, dad);
  // Send the turnaround (10)
  mdio_write_bits(clk_pin, data_pin, 2, 2);
  // Send 16-bit value
  mdio_write_bits(clk_pin, data_pin, reg, 16);
  return 0;
}

int mdio_c45_write_val(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t val)
{
  // Send preamble/header - C45 - WRITE
  mdio_cmd(clk_pin, data_pin, MDIO_C45_FRAME, MDIO_OP_C45_WR, pad, dad);
  // Send the turnaround (10)
  mdio_write_bits(clk_pin, data_pin, 2, 2);
  // Send 16-bit value
  mdio_write_bits(clk_pin, data_pin, val, 16);
  return 0;
}

uint16_t mdio_c45_read_val(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad)
{
  int ret;
  // Send preamble/header
  mdio_cmd(clk_pin, data_pin, MDIO_C45_FRAME, MDIO_OP_C45_RD, pad, dad);
  // Release data pin
  bcm2835_gpio_fsel(data_pin, BCM2835_GPIO_FSEL_INPT);
  ndelay(1000);
  // Read 2-bit turnaround (gives slave time)
  mdio_read_bits(clk_pin, data_pin, 2);
  // Read 16-bit value
  ret = mdio_read_bits(clk_pin, data_pin, 16);
  // Capture data pin
  bcm2835_gpio_fsel(data_pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_write(data_pin, 1);
  return ret;
}

uint16_t mdio_c45_read(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t reg)
{
  mdio_c45_write_addr(clk_pin, data_pin, pad, dad, reg);
  uint16_t val = mdio_c45_read_val(clk_pin, data_pin, pad, dad);
  mdio_flush(clk_pin, data_pin);
  return val;
}

int mdio_c45_write(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t reg, uint16_t val)
{
  mdio_c45_write_addr(clk_pin, data_pin, pad, dad, reg);
  uint16_t rst = mdio_c45_write_val(clk_pin, data_pin, pad, dad, val);
  mdio_flush(clk_pin, data_pin);
  return rst;
}

uint32_t mdio_c45_read_dword(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint32_t reg)
{
  mdio_c45_write_addr(clk_pin, data_pin, pad, dad, (uint16_t)(reg & 0xFFFF));
  mdio_c45_write_addr(clk_pin, data_pin, pad, dad, (uint16_t)(reg >> 16));
  uint16_t val_lsb = mdio_c45_read_val(clk_pin, data_pin, pad, dad);
  uint16_t val_msb = mdio_c45_read_val(clk_pin, data_pin, pad, dad);
  mdio_flush(clk_pin, data_pin);
  return (val_msb << 16) & (val_lsb & 0xFFFF);
}

int mdio_c45_write_dword(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint32_t reg, uint32_t val)
{
  int rst;
  mdio_c45_write_addr(clk_pin, data_pin, pad, dad, (uint16_t)(reg & 0xFFFF));
  mdio_c45_write_addr(clk_pin, data_pin, pad, dad, (uint16_t)(reg >> 16));
  rst = mdio_c45_write_val(clk_pin, data_pin, pad, dad, (uint16_t)(val & 0xFFFF));
  rst |= mdio_c45_write_val(clk_pin, data_pin, pad, dad, (uint16_t)(val >> 16));
  mdio_flush(clk_pin, data_pin);
  return rst;
}
