#include <Python.h>
#include "bcm2835.h"

static PyObject *py_rpio_init(PyObject *self, PyObject *args) {
  int gpiomem, val;
  if (!PyArg_ParseTuple(args, "H", &gpiomem)) {
    return NULL;
  }
  val = bcm2835_init(gpiomem);
  return Py_BuildValue("I", val);
}

static PyObject *py_rpio_gpio_fsel(PyObject *self, PyObject *args) {
  uint8_t pin, mode;
  if (!PyArg_ParseTuple(args, "BB", &pin, &mode)) {
    return NULL;
  }
  bcm2835_gpio_fsel(pin, mode);
  Py_RETURN_NONE;
}

static PyObject *py_rpio_gpio_lev(PyObject *self, PyObject *args) {
  uint8_t pin, val;
  if (!PyArg_ParseTuple(args, "B", &pin)) {
    return NULL;
  }
  val = bcm2835_gpio_lev(pin);
  return Py_BuildValue("B", val);
}

static PyObject *py_rpio_gpio_write(PyObject *self, PyObject *args) {
  uint8_t pin, val;
  if (!PyArg_ParseTuple(args, "BB", &pin, &val)) {
    return NULL;
  }
  bcm2835_gpio_write(pin, val);
  Py_RETURN_NONE;
}

static PyObject *py_rpio_gpio_pad(PyObject *self, PyObject *args) {
  uint8_t group;
  uint32_t val;
  if (!PyArg_ParseTuple(args, "B", &group)) {
    return NULL;
  }
  val = bcm2835_gpio_pad(group);
  return Py_BuildValue("I", val);
}

static PyObject *py_rpio_gpio_set_pad(PyObject *self, PyObject *args) {
  uint8_t group;
  uint32_t control;
  if (!PyArg_ParseTuple(args, "BI", &group, &control)) {
    return NULL;
  }
  bcm2835_gpio_set_pad(group, control);
  Py_RETURN_NONE;
}

static PyObject *py_rpio_gpio_set_pud(PyObject *self, PyObject *args) {
  uint8_t pin, pud;
  if (!PyArg_ParseTuple(args, "BB", &pin, &pud)) {
    return NULL;
  }
  bcm2835_gpio_set_pud(pin, pud);
  Py_RETURN_NONE;
}

static PyObject *py_rpio_gpio_get_pud(PyObject *self, PyObject *args) {
  uint8_t pin, pud;
  if (!PyArg_ParseTuple(args, "B", &pin)) {
    return NULL;
  }
  pud = bcm2835_gpio_get_pud(pin);
  return Py_BuildValue("B", pud);
}


static PyMethodDef RPIOMethods[] = {
  {"rpio_init", py_rpio_init, METH_VARARGS, "RPIO Open"},
  {"rpio_gpio_fsel", py_rpio_gpio_fsel, METH_VARARGS, "GPIO set mode"},
  {"rpio_gpio_lev", py_rpio_gpio_lev, METH_VARARGS, "GIO get value"},
  {"rpio_gpio_write", py_rpio_gpio_write, METH_VARARGS, "GIO set value"},
  {"rpio_gpio_pad", py_rpio_gpio_pad, METH_VARARGS, "GPIO get PAD"},
  {"rpio_gpio_set_pad", py_rpio_gpio_set_pad, METH_VARARGS, "GPIO set PAD"},
  {"rpio_gpio_set_pud", py_rpio_gpio_set_pud, METH_VARARGS, "GPIO set PUD"},
  {"rpio_gpio_get_pud", py_rpio_gpio_get_pud, METH_VARARGS, "GPIO get PUD"},

  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef rpiomodule = {
  PyModuleDef_HEAD_INIT,
  "rpiolib",
  "rpio module",
  -1,
  RPIOMethods
};

PyMODINIT_FUNC PyInit_rpiolib(void) {
  return PyModule_Create(&rpiomodule);
}