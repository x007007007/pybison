/*
 * Linux-specific dynamic library manipulation routines
 */
#include "log.h"
#include "bisondynlib.h"
#include <stdio.h>
#include <dlfcn.h>

void (*reset_flex_buffer)(void) = NULL;

void *bisondynlib_open(char *filename) {
    DEBUG_PRINT("bisondynlib_open: %s\n", filename);
    void *handle;

    handle = dlopen(filename, (RTLD_NOW|RTLD_GLOBAL));

    dlerror();

    if (!handle)
        return NULL;

    reset_flex_buffer = dlsym(handle, "reset_flex_buffer");

    dlerror();

    return handle;
}

int bisondynlib_close(void *handle) {
    DEBUG_PRINT("bisondynlib_close\n");
    return dlclose(handle);
}

void bisondynlib_reset(void) {
    DEBUG_PRINT("bisondynlib_reset\n");
    if (reset_flex_buffer) {
        reset_flex_buffer();
    }
}

char *bisondynlib_err() {
    DEBUG_PRINT("bisondynlib_err\n");
    return dlerror();
}

char *bisondynlib_lookup_hash(void *handle) {
    DEBUG_PRINT("bisondynlib_lookup_hash\n");
    char **hash;

    hash = dlsym(handle, "rules_hash");

    dlerror();

    return hash ? *hash : NULL;
}

PyObject *bisondynlib_run(void *handle, PyObject *parser, void *cb, void *in, int debug) {
    DEBUG_PRINT("bisondynlib_run\n");
    if(!handle) return NULL;

    PyObject *(*pparser)(PyObject *, void *, void *, int);

    pparser = bisondynlib_lookup_parser(handle);
    DEBUG_PRINT("bisondynlib_lookup_parser\n");
    if (!pparser) {
        PyErr_SetString(PyExc_RuntimeError, "bisondynlib_lookup_parser() returned NULL\n");
        return NULL;
    }
    DEBUG_PRINT("%p\n", pparser);
    (*pparser)(parser, cb, in, debug);

    // Do not ignore a raised exception, but pass the exception through.
    if (PyErr_Occurred()) {
        DEBUG_PRINT("ignore a raised exception\n");
        return NULL;
    }

    Py_INCREF(Py_None);
    DEBUG_PRINT("bisondynlib_run done\n");
    return Py_None;
}

/*
 * function(void *) returns a pointer to a function(PyObject *, char *)
 * returning PyObject*
 */
PyObject *(*bisondynlib_lookup_parser(void *handle))(PyObject *, void *, void *, int) {
    DEBUG_PRINT("bisondynlib_lookup_parser\n");
    PyObject *(*do_parse)(PyObject *, void *, void *, int) = dlsym(handle, "do_parse");

    dlerror();

    return do_parse;
}
