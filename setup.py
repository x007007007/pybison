"""
Builds bison python module
"""

from __future__ import absolute_import
from __future__ import print_function
version = '0.1.8'

import sys
from setuptools import setup
from Cython.Distutils.extension import Extension
from Cython.Distutils import build_ext

import sys

if sys.platform == 'win32':
    libs = []
    extra_link_args = ['/debug','/Zi']
    bison2pyscript = 'utils/bison2py.py'
    bisondynlibModule = 'src/c/bisondynlib-win32.c'
    extra_compile_args = ['/Od','/Zi','-D__builtin_expect(a,b)=(a)']
elif sys.platform.startswith('linux'):
    libs = ['dl']
    extra_link_args = []
    extra_compile_args = []
    bison2pyscript = 'utils/bison2py.py'
    bisondynlibModule = 'src/c/bisondynlib-linux.c'
else:  # TODO: maybe support darwin?
    print('Sorry, your platform is presently unsupported.')
    sys.exit(1)

setup(
    name='pybison',
    version=version,
    description='Python bindings for bison/flex parser engine',
    author='Christoph Sarnowski',
    author_email='cs@chrisonpython.com',
    url='https://github.com/csarn/pybison',
    ext_modules=[
        Extension(
            'bison_',
            sources=[
                'src/cython/bison_.pyx',
                'src/c/bison_callback.c',
                bisondynlibModule
            ],
            extra_compile_args=extra_compile_args,
            libraries=libs,
            extra_link_args=extra_link_args,
            cython_compile_time_env={'PY3': sys.version_info.major >= 3},
        )
    ],
    include_package_data=True,
    packages=['bison'],
    package_dir={'bison': 'src/python'},
    cmdclass={'build_ext': build_ext},
    scripts=[bison2pyscript],
)
