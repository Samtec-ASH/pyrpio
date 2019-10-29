#include <Python.h>
#include "mdio.h"

static PyObject *py_mdio_open(PyObject *self, PyObject *args) {
  uint8_t clk_pin, data_pin;
  if (!PyArg_ParseTuple(args, "BB", &clk_pin, &data_pin)) {
    return NULL;
  }
  mdio_open(clk_pin, data_pin);
  Py_RETURN_NONE;
}

static PyObject *py_mdio_close(PyObject *self, PyObject *args) {
  uint8_t clk_pin, data_pin;
  if (!PyArg_ParseTuple(args, "BB", &clk_pin, &data_pin)) {
    return NULL;
  }
  mdio_close(clk_pin, data_pin);
  Py_RETURN_NONE;
}

static PyObject *py_mdio_write_reg(PyObject *self, PyObject *args) {
  uint8_t clk_pin, data_pin;
  uint8_t pad, dad;
  uint16_t reg, val;
  if (!PyArg_ParseTuple(args, "BBBBHH", &clk_pin, &data_pin, &pad, &dad, &reg, &val)) {
    return NULL;
  }
  mdio_write_reg(clk_pin, data_pin, pad, dad, reg, val);
  Py_RETURN_NONE;
}

static PyObject *py_mdio_read_reg(PyObject *self, PyObject *args) {
  uint8_t clk_pin, data_pin;
  uint8_t pad, dad;
  uint16_t reg, val;
  if (!PyArg_ParseTuple(args, "BBBBH", &clk_pin, &data_pin, &pad, &dad, &reg)) {
    return NULL;
  }
  val = mdio_read_reg(clk_pin, data_pin, pad, dad, reg);
  return Py_BuildValue("H", val);
}

static PyMethodDef MDIOMethods[] = {
  {"mdio_open", py_mdio_open, METH_VARARGS, "MDIO Open"},
  {"mdio_close", py_mdio_close, METH_VARARGS, "MDIO Close"},
  {"mdio_write_reg", py_mdio_write_reg, METH_VARARGS, "MDIO Write"},
  {"mdio_read_reg", py_mdio_read_reg, METH_VARARGS, "MDIO Read"},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef mdiomodule = {
  PyModuleDef_HEAD_INIT,
  "mdio",
  "mdio module",
  -1,
  MDIOMethods
};

PyMODINIT_FUNC PyInit_mdio(void) {
  return PyModule_Create(&mdiomodule);
}