"""
Builds bison python module
"""

from __future__ import absolute_import
from __future__ import print_function

from setuptools import setup
from setuptools import Extension
from Cython.Distutils import build_ext

import sys

version = '0.1'

if sys.platform == 'win32':
    print('No windows support at this time. PyBison won\'t work for you :(')
    libs = []
    extra_link_args = []
    bison2pyscript = 'utils/bison2py.py'
    bisondynlibModule = 'src/c/bisondynlib-win32.c'
elif sys.platform.startswith('linux'):
    libs = ['dl']
    extra_link_args = []
    bison2pyscript = 'utils/bison2py'
    bisondynlibModule = 'src/c/bisondynlib-linux.c'
elif sys.platform.startswith('darwin'):
    libs = ['dl']
    extra_link_args = []
    bison2pyscript = 'utils/bison2py'
    bisondynlibModule = 'src/c/bisondynlib-linux.c'
    from distutils import sysconfig
    v = sysconfig.get_config_vars()
    v['LDSHARED'] = v['LDSHARED'].replace('-bundle', '-dynamiclib')
else:
    print('Sorry, your platform is not supported.')
    sys.exit(1)

setup(
    name='bison',
    version=version,
    description='Python bindings for bison/flex parser engine',
    author='David McNab <david@freenet.org.nz>',
    url='http://www.freenet.org.nz/python/pybison',
    ext_modules=[
        Extension(
            'bison_',
            [
                'src/pyrex/bison_.pyx',
                'src/c/bison_callback.c',
                bisondynlibModule
            ],
            libraries=libs,
            extra_compile_args=['-Wall', '-Wextra']
        )
    ],
    packages=['bison'],
    package_dir={'': 'src'},
    cmdclass={'build_ext': build_ext},
    scripts=[bison2pyscript],
    install_requires=[
        "cython",
        "six"
    ]
)
