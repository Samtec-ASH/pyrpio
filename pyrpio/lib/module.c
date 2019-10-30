#include <Python.h>
#include "bcm2835.h"

static PyObject *py_rpio_init(PyObject *self, PyObject *args)
{
  int gpiomem, val;
  if (!PyArg_ParseTuple(args, "H", &gpiomem))
  {
    return NULL;
  }
  val = bcm2835_init(gpiomem);
  return Py_BuildValue("I", val);
}

/****    GPIO    ****/
static PyObject *py_gpio_function(PyObject *self, PyObject *args)
{
  uint8_t pin, mode;
  if (!PyArg_ParseTuple(args, "BB", &pin, &mode))
  {
    return NULL;
  }
  bcm2835_gpio_fsel(pin, mode);
  Py_RETURN_NONE;
}

static PyObject *py_gpio_read(PyObject *self, PyObject *args)
{
  uint8_t pin, val;
  if (!PyArg_ParseTuple(args, "B", &pin))
  {
    return NULL;
  }
  val = bcm2835_gpio_lev(pin);
  return Py_BuildValue("B", val);
}

static PyObject *py_gpio_write(PyObject *self, PyObject *args)
{
  uint8_t pin, val;
  if (!PyArg_ParseTuple(args, "BB", &pin, &val))
  {
    return NULL;
  }
  bcm2835_gpio_write(pin, val);
  Py_RETURN_NONE;
}

static PyObject *py_gpio_get_pad(PyObject *self, PyObject *args)
{
  uint8_t group;
  uint32_t val;
  if (!PyArg_ParseTuple(args, "B", &group))
  {
    return NULL;
  }
  val = bcm2835_gpio_pad(group);
  return Py_BuildValue("I", val);
}

static PyObject *py_gpio_set_pad(PyObject *self, PyObject *args)
{
  uint8_t group;
  uint32_t control;
  if (!PyArg_ParseTuple(args, "BI", &group, &control))
  {
    return NULL;
  }
  bcm2835_gpio_set_pad(group, control);
  Py_RETURN_NONE;
}

static PyObject *py_gpio_set_pud(PyObject *self, PyObject *args)
{
  uint8_t pin, pud;
  if (!PyArg_ParseTuple(args, "BB", &pin, &pud))
  {
    return NULL;
  }
  bcm2835_gpio_set_pud(pin, pud);
  Py_RETURN_NONE;
}

static PyObject *py_gpio_get_pud(PyObject *self, PyObject *args)
{
  uint8_t pin, pud;
  if (!PyArg_ParseTuple(args, "B", &pin))
  {
    return NULL;
  }
  pud = bcm2835_gpio_get_pud(pin);
  return Py_BuildValue("B", pud);
}

/****    I2C    ****/
static PyObject *py_i2c_begin(PyObject *self, PyObject *args)
{
  bcm2835_i2c_begin();
  Py_RETURN_NONE;
}

static PyObject *py_i2c_set_clock_divider(PyObject *self, PyObject *args)
{
  uint32_t divider;
  if (!PyArg_ParseTuple(args, "I", &divider))
  {
    return NULL;
  }
  bcm2835_i2c_setClockDivider(divider);
  Py_RETURN_NONE;
}

static PyObject *py_i2c_set_baudrate(PyObject *self, PyObject *args)
{
  uint32_t baudrate;
  if (!PyArg_ParseTuple(args, "I", &baudrate))
  {
    return NULL;
  }
  bcm2835_i2c_set_baudrate(baudrate);
  Py_RETURN_NONE;
}

static PyObject *py_i2c_set_slave_address(PyObject *self, PyObject *args)
{
  uint32_t addr;
  if (!PyArg_ParseTuple(args, "I", &addr))
  {
    return NULL;
  }
  bcm2835_i2c_setSlaveAddress(addr);
  Py_RETURN_NONE;
}

static PyObject *py_i2c_end(PyObject *self, PyObject *args)
{
  bcm2835_i2c_end();
  Py_RETURN_NONE;
}

static PyObject *py_i2c_read(PyObject *self, PyObject *args)
{
  uint32_t len;
  char *buf;
  PyObject *result;
  if (!PyArg_ParseTuple(args, "I", &len)) { return NULL; }
  buf = (char *)malloc(len);
  bcm2835_i2c_read(buf, len);
  result = Py_BuildValue("s#", buf, len);
  free(buf);
  return result;
}

static PyObject *py_i2c_write(PyObject *self, PyObject *args)
{
  uint32_t len;
  const char *buf;
  if (!PyArg_ParseTuple(args, "s#", &buf, &count)) { return NULL; }
  bcm2835_i2c_write(pbuf, len);
  Py_RETURN_NONE;
}

/****    PWM    ****/
static PyObject *py_pwm_set_mode(PyObject *self, PyObject *args)
{
  uint32_t channel, markspace, enabled;
  if (!PyArg_ParseTuple(args, "III", &channel, &markspace, &enabled))
  {
    return NULL;
  }
  bcm2835_pwm_set_mode(channel, markspace, enabled);
  Py_RETURN_NONE;
}

static PyObject *py_pwm_set_range(PyObject *self, PyObject *args)
{
  uint32_t channel, range;
  if (!PyArg_ParseTuple(args, "II", &channel, &range))
  {
    return NULL;
  }
  bcm2835_pwm_set_range(channel, range);
  Py_RETURN_NONE;
}

static PyObject *py_pwm_set_data(PyObject *self, PyObject *args)
{
  uint32_t channel, data;
  if (!PyArg_ParseTuple(args, "III", &channel, &data))
  {
    return NULL;
  }
  bcm2835_pwm_set_data(channel, data);
  Py_RETURN_NONE;
}

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
  {NULL, NULL, 0, NULL}
};

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