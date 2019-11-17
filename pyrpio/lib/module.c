#include <Python.h>
#include "bcm2835_ext.h"
#include "mdio_ext.h"

static PyMethodDef RPIOMethods[] = {
    {"rpio_init", py_rpio_init, METH_VARARGS, "RPIO Open"},
    // GPIO
    {"gpio_function", py_gpio_function, METH_VARARGS, "GPIO set mode"},
    {"gpio_read", py_gpio_read, METH_VARARGS, "GIO get value"},
    {"rpio_gpio_write", py_gpio_write, METH_VARARGS, "GIO set value"},
    {"gpio_get_pad", py_gpio_get_pad, METH_VARARGS, "GPIO get PAD"},
    {"gpio_set_pad", py_gpio_set_pad, METH_VARARGS, "GPIO set PAD"},
    {"gpio_get_pud", py_gpio_get_pud, METH_VARARGS, "GPIO get PUD"},
    {"gpio_set_pud", py_gpio_set_pud, METH_VARARGS, "GPIO set PUD"},
    // I2C
    {"i2c_begin", py_i2c_begin, METH_VARARGS, "I2C Begin"},
    {"i2c_end", py_i2c_end, METH_VARARGS, "I2C End"},
    {"i2c_set_clock_divider", py_i2c_set_clock_divider, METH_VARARGS, "I2C set clock divider"},
    {"i2c_set_baudrate", py_i2c_set_baudrate, METH_VARARGS, "I2C set baudrate"},
    {"i2c_set_slave_address", py_i2c_set_slave_address, METH_VARARGS, "I2C set slave address"},
    {"i2c_read", py_i2c_read, METH_VARARGS, "I2C read"},
    {"i2c_write", py_i2c_write, METH_VARARGS, "I2C write"},
    // PWM
    {"pwm_set_mode", py_pwm_set_mode, METH_VARARGS, "PWM set mode"},
    {"pwm_set_range", py_pwm_set_range, METH_VARARGS, "PWM set range"},
    {"pwm_set_data", py_pwm_set_data, METH_VARARGS, "PWM set data"},
    // MDIO
    {"mdio_init", py_mdio_init, METH_VARARGS, "MDIO init"},
    {"mdio_open", py_mdio_open, METH_VARARGS, "MDIO open"},
    {"mdio_close", py_mdio_close, METH_VARARGS, "MDIO close"},
    {"mdio_c22_read", py_mdio_c22_read, METH_VARARGS, "MDIO C22 write"},
    {"mdio_c22_write", py_mdio_c22_write, METH_VARARGS, "MDIO C22 read"},
    {"mdio_c45_read", py_mdio_c45_read, METH_VARARGS, "MDIO C45 write word"},
    {"mdio_c45_write", py_mdio_c45_write, METH_VARARGS, "MDIO C45 read word"},
    {"mdio_c45_read_dword", py_mdio_c45_read_dword, METH_VARARGS, "MDIO C45 Write dword"},
    {"mdio_c45_write_dword", py_mdio_c45_write_dword, METH_VARARGS, "MDIO C45 Read dword"},
    // DONE
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef rpiomodule = {
    PyModuleDef_HEAD_INIT,
    "rpiolib",
    "rpio module",
    -1,
    RPIOMethods};

PyMODINIT_FUNC PyInit_rpiolib(void)
{
  return PyModule_Create(&rpiomodule);
}