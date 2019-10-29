#include "mdio.h"
#include "bcm2835.h"

#define MDIO_WRITE_ADD 0
#define MDIO_WRITE_VAL 1
#define MDIO_READ_INC 2
#define MDIO_READ 3

#define MDIO_DELAY 50
#define MDIO_READ_DELAY 50
#define MDIO_DELAY_SETUP 10

#define noop ((void)0)

static void ndelay(int delay)
{
  while (delay-- > 0)
  {
    noop;
  }
  return;
}

static int mdio_open(uint8_t clk_pin, uint8_t data_pin)
{
  bcm2835_gpio_set_pud(data_pin, BCM2835_GPIO_PUD_UP);
  bcm2835_gpio_write(clk_pin, 0);
  bcm2835_gpio_fsel(clk_pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_write(clk_pin, 0);

  bcm2835_gpio_write(data_pin, 1);
  bcm2835_gpio_fsel(data_pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_write(data_pin, 1);
}

static int mdio_close(uint8_t clk_pin, uint8_t data_pin)
{
  bcm2835_gpio_write(clk_pin, 0);
  bcm2835_gpio_fsel(clk_pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_write(clk_pin, 0);

  bcm2835_gpio_write(data_pin, 1);
  bcm2835_gpio_fsel(data_pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_write(data_pin, 1);
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

/*
 * Transfer routine preamble, address, and register (common to read and write)
 */
static void mdio_cmd(uint8_t clk_pin, uint8_t data_pin, int op, uint8_t pad, uint8_t dad)
{
  int i;
  for (i = 0; i < 32; i++)
  {
    mdio_write_bit(clk_pin, data_pin, 1);
  }

  /* send the start bit (01) and the read opcode (10) or write (10).
       Clause 45 operation uses 00 for the start and 11, 10 for
       read/write */
  mdio_write_bit(clk_pin, data_pin, 0);
  mdio_write_bit(clk_pin, data_pin, 0);
  mdio_write_bit(clk_pin, data_pin, (op >> 1) & 1);
  mdio_write_bit(clk_pin, data_pin, (op >> 0) & 1);

  mdio_write_bits(clk_pin, data_pin, pad, 5);
  mdio_write_bits(clk_pin, data_pin, dad, 5);
}

/* If there is an error during turnover, flush all bits and
* return 0xffff
*/
uint16_t mdio_read_val(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad)
{
  int ret, i;

  mdio_cmd(clk_pin, data_pin, MDIO_READ, pad, dad);

  bcm2835_gpio_fsel(data_pin, BCM2835_GPIO_FSEL_INPT);
  ndelay(1000);

  mdio_read_bit(clk_pin, data_pin); // read and discard two turnaround bits
  mdio_read_bit(clk_pin, data_pin);

  ret = mdio_read_bits(clk_pin, data_pin, 16);
  // mdio_read_bit(clk_pin, data_pin);
  bcm2835_gpio_fsel(data_pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_write(data_pin, 1);

  for (i = 0; i < 32; i++)
    mdio_write_bit(clk_pin, data_pin, 1);

  return ret;
}

uint16_t mdio_read_reg(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t reg) {
  mdio_write_add(clk_pin, data_pin, pad, dad, reg);
  return mdio_read_val(clk_pin, data_pin, pad, dad);
}

int mdio_write_reg(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t reg, uint16_t val) {
  mdio_write_add(clk_pin, data_pin, pad, dad, reg);
  mdio_write_val(clk_pin, data_pin, pad, dad, val);
  return 0;
}

int mdio_write_add(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, u_int8_t dad, uint16_t val)
{
  int i;
  mdio_cmd(clk_pin, data_pin, MDIO_WRITE_ADD, pad, dad);

  /* send the turnaround (10) */
  mdio_write_bit(clk_pin, data_pin, 1);
  mdio_write_bit(clk_pin, data_pin, 0);

  mdio_write_bits(clk_pin, data_pin, val, 16);

  for (i = 0; i < 32; i++)
    mdio_write_bit(clk_pin, data_pin, 1);
  return 0;
}

int mdio_write_val(uint8_t clk_pin, uint8_t data_pin, uint8_t pad, uint8_t dad, uint16_t val)
{
  int i;
  mdio_cmd(clk_pin, data_pin, MDIO_WRITE_VAL, pad, dad);

  /* send the turnaround (10) */
  mdio_write_bit(clk_pin, data_pin, 1);
  mdio_write_bit(clk_pin, data_pin, 0);

  mdio_write_bits(clk_pin, data_pin, val, 16);

  for (i = 0; i < 32; i++) {
    mdio_write_bit(clk_pin, data_pin, 1);
  }
  return 0;
}
