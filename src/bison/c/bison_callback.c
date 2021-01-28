/*
 * Callback functions called by bison.
 *
 * The original py_callback function is removed from bison_.pyx because Cython
 * generated crappy code for that callback. Cython's generated code caused
 * segfaults when python triggered its garbage collection. Thus, something was
 * wrong with references. Debugging the generated code was hard and the
 * callbacks are part of PyBison's core, so implementing the callbacks in C
 * instead of generating them by Cython seems the right way to go.
 *
 * Written januari 2012 by Sander Mathijs van Veen <smvv@kompiler.org>
 * Copyright (c) 2012 by Sander Mathijs van Veen, all rights reserved.
 *
 * Released under the GNU General Public License, a copy of which should appear
 * in this distribution in the file called 'COPYING'. If this file is missing,
 * then you can obtain a copy of the GPL license document from the GNU website
 * at http://www.gnu.org.
 *
 * This software is released with no warranty whatsoever. Use it at your own
 * risk.
 *
 * If you wish to use this software in a commercial application, and wish to
 * depart from the GPL licensing requirements, please contact the author and
 * apply for a commercial license.
 */

#include "Python.h"
#include <stdlib.h>
#if PY_MAJOR_VERSION >= 3
#define PY3
#endif

#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include "log.h"


#ifdef _WIN32
#define likely(x)       (x)
#define unlikely(x)     (x)
#else
#define likely(x)       __builtin_expect((x),1)
#define unlikely(x)     __builtin_expect((x),0)
#endif

static PyObject *py_attr_hook_handler_name;
static PyObject *py_attr_hook_read_after_name;
static PyObject *py_attr_hook_read_before_name;

static PyObject *py_attr_handle_name;
static PyObject *py_attr_read_name;
static PyObject *py_attr_file_name;
static PyObject *py_attr_input_marker;
static PyObject *py_attr_close_name;

// Construct attribute names (only the first time)
// TODO: where do we Py_DECREF(handle_name) ??
#ifdef PY3
#define INIT_ATTR(variable, name, failure) \
    if (unlikely(!variable)) { \
        variable = PyUnicode_FromString(name); \
        if (!variable) {    \
            DEBUG_PRINT("init attr failed %s exit\n", name);    \
            failure;    \
        }   \
        DEBUG_PRINT("init attr success %s: %p\n", name, variable);      \
    }
#define PyComStr_FromString(name) PyUnicode_FromString(name)
#else
#define INIT_ATTR(variable, name, failure) \
    if (unlikely(!variable)) { \
        variable = PyString_FromString(name); \
        if (!variable) {    \
            DEBUG_PRINT("init attr failed %s exit\n", name);    \
            failure;    \
        }   \
        DEBUG_PRINT("init attr success %s: %p\n", name, variable); \
    }
#define PyComStr_FromString(name) PyString_FromString(name)
#endif

#define debug_refcnt(variable, count) { \
        printf(#variable ": %d\n", Py_REFCNT(variable)); \
        assert(Py_REFCNT(variable) == count); \
    }

/*
 * Callback function which is invoked by target handlers within the C yyparse()
 * function. This callback function will return parser._handle's python object
 * or, on failure, NULL is returned.
 */
PyObject* py_callback(PyObject *parser, char *target, int option, int nargs, ...) {
    va_list ap;
    int i;
    PyObject *res;
    PyObject *names = PyList_New(nargs),
        *values = PyList_New(nargs);

    va_start(ap, nargs);
    DEBUG_PRINT("py_callback 3\n");

    // Construct the names and values list from the variable argument list.
    for(i = 0; i < nargs; i++) {
        DEBUG_PRINT("py_callback for loop: %d / %d \n", nargs, i);
        char *name_c_str = va_arg(ap, char *);
        PyObject *name = PyComStr_FromString(name_c_str);

        if(!name){
            DEBUG_PRINT("no name\n");
            Py_INCREF(Py_None);
            name = Py_None;
        } else {
            DEBUG_PRINT("name: %s\n", name_c_str);
        }
        PyList_SetItem(names, i, name);
        DEBUG_PRINT("push name into names\n");

//        PyObject *value = va_arg(ap, PyObject *);
//        DEBUG_PRINT("read stack\n");
//        if(!value){
//          Py_INCREF(Py_None);
//          value = Py_None;
//        }
//        Py_INCREF(value);
//        DEBUG_PRINT("Py incref value\n");
//        PyList_SetItem(values, i, value);
//        DEBUG_PRINT("callback done\n");
    }

    va_end(ap);

    INIT_ATTR(py_attr_handle_name, "_handle", return NULL);
    INIT_ATTR(py_attr_hook_handler_name, "hook_handler", return NULL);

    // Call the handler with the arguments
    PyObject *handle = PyObject_GetAttr(parser, py_attr_handle_name);

    if (unlikely(!handle)) return NULL;

    PyObject *arglist = Py_BuildValue("(siOO)", target, option, names, values);
    if (unlikely(!arglist)) {
        DEBUG_PRINT("is not a arglist\n");
        Py_DECREF(handle);
        return NULL;
    }

    res = PyObject_CallObject(handle, arglist);

    Py_DECREF(handle);
    Py_DECREF(arglist);

    if (unlikely(!res)) return res;

    // Check if the "hook_handler" callback exists
    handle = PyObject_GetAttr(parser, py_attr_hook_handler_name);

    if (!handle) {
        DEBUG_PRINT("Py Error Clear\n");
        PyErr_Clear();
        return res;
    }

    // XXX: PyObject_GetAttr increases the refcnt of py_attr_hook_handler_name
    // by one.
    //debug_refcnt(py_attr_hook_handler_name, 1);

    // Call the "hook_handler" callback
    arglist = Py_BuildValue("(siOOO)", target, option, names, values, res);
    if (unlikely(!arglist)) { Py_DECREF(handle); return res; }

    res = PyObject_CallObject(handle, arglist);

    PyObject *exc = PyErr_Occurred();
    if(unlikely(exc)){
      DEBUG_PRINT(" %p", exc);
      DEBUG_PRINT("exception in callback!!\n");
      return NULL;
    }
    Py_DECREF(handle);
    Py_DECREF(arglist);

    return res;
}

void py_input(PyObject *parser, char *buf, int *result, int max_size) {
    PyObject *handle, *arglist, *res;
    char *bufstr;

    INIT_ATTR(py_attr_hook_read_after_name, "hook_read_after", return);
    INIT_ATTR(py_attr_hook_read_before_name, "hook_read_before", return);
    INIT_ATTR(py_attr_read_name, "read", return);
    INIT_ATTR(py_attr_file_name, "file", return);
    INIT_ATTR(py_attr_input_marker, "marker", return);
    INIT_ATTR(py_attr_close_name, "close", return);

    // Check if the "hook_READ_BEFORE" callback exists
    if (PyObject_HasAttr(parser, py_attr_hook_read_before_name)) {
        DEBUG_PRINT("parase has attr py_attr_hook_read_before_name %p\n", py_attr_hook_read_before_name);
        handle = PyObject_GetAttr(parser, py_attr_hook_read_before_name);
        if (unlikely(!handle)) return;

        // Call the "hook_READ_BEFORE" callback
        arglist = PyTuple_New(0);
        if (unlikely(!arglist)) { Py_DECREF(handle); return; }

        res = PyObject_CallObject(handle, arglist);

        Py_DECREF(handle);
        Py_DECREF(arglist);

        if (unlikely(!res)) return;
    }

    // Read the input string and catch keyboard interrupt exceptions.
    handle = PyObject_GetAttr(parser, py_attr_read_name);
    DEBUG_PRINT("PyObject_GetAttr %p\n", handle);
    if (unlikely(!handle)) return;

    arglist = Py_BuildValue("(i)", max_size);
    if (unlikely(!arglist)) { Py_DECREF(handle); return; }

    res = PyObject_CallObject(handle, arglist);


    DEBUG_PRINT("Py_DECREF start %p\n", handle);
    DEBUG_PRINT("Py_DECREF start %p\n", arglist);
    Py_DECREF(handle);
    Py_DECREF(arglist);
    DEBUG_PRINT("Py_DECREF end\n");

    if (unlikely(!res)) {
        // Catch and reset KeyboardInterrupt exception
        PyObject *given = PyErr_Occurred();
        if (given && PyErr_GivenExceptionMatches(given, PyExc_KeyboardInterrupt)) {
            DEBUG_PRINT("PyErr_GivenExceptionMatches given: %p\n", given);
            PyErr_Clear();
        }
        return;
    }

    // Check if the "hook_read_after" callback exists
    if (unlikely(!PyObject_HasAttr(parser, py_attr_hook_read_after_name))) {
        DEBUG_PRINT("goto finish input \n");
        goto finish_input;
    }

    handle = PyObject_GetAttr(parser, py_attr_hook_read_after_name);
    if (unlikely(!handle)) return;

    // Call the "hook_READ_AFTER" callback
    arglist = Py_BuildValue("(O)", res);

    if (unlikely(!arglist)) { Py_DECREF(handle); return; }

    res = PyObject_CallObject(handle, arglist);

    Py_XDECREF(res);
    Py_DECREF(handle);
    Py_DECREF(arglist);

    if (unlikely(!res)) return;

finish_input:
    DEBUG_PRINT("Jump point:finish_input \n");
    // Copy the read python input string to the buffer
    #ifdef PY3
        bufstr = PyBytes_AsString(res);
    #else
        bufstr = PyString_AsString(res);
    #endif

    if(!bufstr){
      DEBUG_PRINT("buf str alloc failed \n");
      return;
    }
    printf("bufstr : %s\n", bufstr);
    *result = strlen(bufstr);
    memcpy(buf, bufstr, *result);

    // Close the read buffer if nothing is read. Marks the Python file object
    // as being closed from Python's point of view. This does not close the
    // associated C stream (which is not necessary here, otherwise use
    // "os.close(0)").
    if (!*result && PyObject_HasAttr(parser, py_attr_file_name)) {
        DEBUG_PRINT("hi\n");
        // don't mark the file as closed
        // set a marker that there is no more input
        PyObject *marker_handle = PyObject_GetAttr(parser, py_attr_input_marker);
        if (unlikely(!marker_handle)) return;
        // create a int object containing a '1'
        PyObject* po_long1 = PyLong_FromLong(1);
        // execute attribute setting
        int success = PyObject_SetAttr(parser, py_attr_input_marker, po_long1);
        if (success != 0)
            return;
        Py_DECREF(marker_handle);
        Py_DECREF(po_long1);

        // TODO: something went wrong while closing the buffer.
        if (unlikely(!res)) return;
        Py_XDECREF(res);
    }
    DEBUG_PRINT("input done\n");
}
