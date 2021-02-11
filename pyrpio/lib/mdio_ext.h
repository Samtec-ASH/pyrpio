#ifndef MDIO_EXT_H

#include <Python.h>
#include "mdio.h"

static PyObject *py_mdio_init(PyObject *self, PyObject *args)
{
  int gpiomem, val;
  if (!PyArg_ParseTuple(args, "H", &gpiomem))
  {
    return NULL;
  }
  val = bcm2835_init(gpiomem);
  return Py_BuildValue("I", val);
}

static PyObject *py_mdio_open(PyObject *self, PyObject *args)
{
  uint8_t clk_pin, data_pin;
  int rst;
  if (!PyArg_ParseTuple(args, "BB", &clk_pin, &data_pin))
  {
    return NULL;
  }
  rst = mdio_open(clk_pin, data_pin);
  return Py_BuildValue("i", rst);
}

static PyObject *py_mdio_close(PyObject *self, PyObject *args)
{
  uint8_t clk_pin, data_pin;
  int rst;
  if (!PyArg_ParseTuple(args, "BB", &clk_pin, &data_pin))
  {
    return NULL;
  }
  rst = mdio_close(clk_pin, data_pin);
  return Py_BuildValue("i", rst);
}

static PyObject *py_mdio_c22_read(PyObject *self, PyObject *args)
{
  uint8_t clk_pin, data_pin, pad, reg;
  uint16_t val;
  if (!PyArg_ParseTuple(args, "BBBB", &clk_pin, &data_pin, &pad, &reg))
  {
    return NULL;
  }
  val = mdio_c22_read(clk_pin, data_pin, pad, reg);
  return Py_BuildValue("H", val);
}

static PyObject *py_mdio_c22_write(PyObject *self, PyObject *args)
{
  uint8_t clk_pin, data_pin, pad, reg;
  uint16_t val, rst;
  if (!PyArg_ParseTuple(args, "BBBBH", &clk_pin, &data_pin, &pad, &reg, &val))
  {
    return NULL;
  }
  rst = mdio_c22_write(clk_pin, data_pin, pad, reg, val);
  return Py_BuildValue("i", rst);
}

static PyObject *py_mdio_c45_read(PyObject *self, PyObject *args)
{
  uint8_t clk_pin, data_pin, pad, dad;
  uint16_t reg, val;
  if (!PyArg_ParseTuple(args, "BBBBH", &clk_pin, &data_pin, &pad, &dad, &reg))
  {
    return NULL;
  }
  val = mdio_c45_read(clk_pin, data_pin, pad, dad, reg);
  return Py_BuildValue("H", val);
}

static PyObject *py_mdio_c45_write(PyObject *self, PyObject *args)
{
  uint8_t clk_pin, data_pin;
  uint8_t pad, dad;
  uint16_t reg, val, rst;
  if (!PyArg_ParseTuple(args, "BBBBHH", &clk_pin, &data_pin, &pad, &dad, &reg, &val))
  {
    return NULL;
  }
  rst = mdio_c45_write(clk_pin, data_pin, pad, dad, reg, val);
  return Py_BuildValue("H", rst);
}

static PyObject *py_mdio_c45_read_dword(PyObject *self, PyObject *args)
{
  uint8_t clk_pin, data_pin, pad, dad;
  uint16_t reg, val;
  if (!PyArg_ParseTuple(args, "BBBBI", &clk_pin, &data_pin, &pad, &dad, &reg))
  {
    return NULL;
  }
  val = mdio_c45_read_dword(clk_pin, data_pin, pad, dad, reg);
  return Py_BuildValue("I", val);
}

static PyObject *py_mdio_c45_write_dword(PyObject *self, PyObject *args)
{
  uint8_t clk_pin, data_pin;
  uint8_t pad, dad;
  uint32_t reg, val, rst;
  if (!PyArg_ParseTuple(args, "BBBBII", &clk_pin, &data_pin, &pad, &dad, &reg, &val))
  {
    return NULL;
  }
  rst = mdio_c45_write_dword(clk_pin, data_pin, pad, dad, reg, val);
  return Py_BuildValue("I", rst);
}

#endif
