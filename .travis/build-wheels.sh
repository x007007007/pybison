#!/bin/bash
set -e -x

# Install a system package required by our library
yum install -y atlas-devel

# Compile wheels
for PYBIN in /opt/python/*/bin; do
    "${PYBIN}/pip" install -r /io/requirements.txt
    "${PYBIN}/pip" wheel /io/ -w dist/
done

# Bundle external shared libraries into the wheels
for whl in dist/*.whl; do
    auditwheel repair "$whl" --plat $PLAT -w /io/dist/
done

# Install packages and test
for PYBIN in /opt/python/*/bin/; do
    echo "$PYBIN"
    "${PYBIN}/pip" install pybison --no-index -f /io/dist
    # (cd "$HOME"; "${PYBIN}/nosetests" pymanylinuxdemo)
done
