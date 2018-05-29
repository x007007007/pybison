"""
Builds bison python module
"""

from __future__ import absolute_import
from __future__ import print_function
version = '0.1.8'

from setuptools import setup, Extension
from Cython.Distutils import build_ext

import sys

if sys.platform == 'win32':
    print('No windows support at this time. PyBison won\'t work for you :(')
    libs = []
    extra_link_args = ['/debug','/Zi']
    bison2pyscript = 'utils/bison2py.py'
    bisondynlibModule = 'src/c/bisondynlib-win32.c'
    extra_compile_args = ['/Od','/Zi','-D__builtin_expect(a,b)=(a)']
elif sys.platform == 'linux':
    libs = ['dl']
    extra_link_args = []
    extra_compile_args = []
    bison2pyscript = 'utils/bison2py.py'
    bisondynlibModule = 'src/c/bisondynlib-linux.c'
else:
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
        Extension('bison_', [
            'src/cython/bison_.pyx',
            'src/c/bison_callback.c',
            bisondynlibModule
        ],
            extra_compile_args=extra_compile_args,
            libraries=libs,
            extra_link_args=extra_link_args,
        )
    ],
    include_package_data=True,
    packages=['bison'],
    package_dir={'bison': 'src/python'},
    cmdclass={'build_ext': build_ext},
    scripts=[bison2pyscript],
)
