"""
Builds bison python module
"""
from __future__ import absolute_import
from __future__ import print_function

import sys
import os
from os.path import basename, join, splitext
from glob import glob
from setuptools import find_packages, setup

# source: https://github.com/Blosc/bcolz/blob/master/setup.py#L34-L78
class LazyCommandClass(dict):
    """
    Lazy command class that defers operations requiring Cython and numpy until
    they've actually been downloaded and installed by setup_requires.
    """
    def __contains__(self, key):
        return (
            key == 'build_ext'
            or super(LazyCommandClass, self).__contains__(key)
        )

    def __setitem__(self, key, value):
        if key == 'build_ext':
            raise AssertionError("build_ext overridden!")
        super(LazyCommandClass, self).__setitem__(key, value)

    def __getitem__(self, key):
        if key != 'build_ext':
            return super(LazyCommandClass, self).__getitem__(key)

        from Cython.Distutils import build_ext as cython_build_ext
        from Cython.Compiler.Options import get_directive_defaults
        get_directive_defaults()['linetrace'] = True
        get_directive_defaults()['binding'] = True

        class build_ext(cython_build_ext):
            """
            Custom build_ext command that lazily adds numpy's include_dir to
            extensions.
            """
            def build_extensions(self):
                """
                Lazily append numpy's include directory to Extension includes.
                This is done here rather than at module scope because setup.py
                may be run before numpy has been installed, in which case
                importing numpy and calling `numpy.get_include()` will fail.
                """
                # numpy_incl = resource_filename('numpy', 'core/include')
                # for ext in self.extensions:
                #     ext.include_dirs.append(numpy_incl)

                # This explicitly calls the superclass method rather than the
                # usual super() invocation because distutils' build_class, of
                # which Cython's build_ext is a subclass, is an old-style class
                # in Python 2, which doesn't support `super`.
                cython_build_ext.build_extensions(self)
        return build_ext

from setuptools import Extension

version = '0.2'

package_data = []


if sys.platform == 'win32':
    libs = []
    extra_link_args = ['/debug', '/Zi']
    bison2pyscript = 'utils/bison2py'
    bisondynlibModule = 'src/bison/c/bisondynlib-win32.c'
    extra_compile_args = ['/Od', '/Zi', '-D__builtin_expect(a,b)=(a)', '/DCYTHON_TRACE=1']
    for root, dirs, files in os.walk('src/bison/winflexbison'):
        package_data.extend(join(root.replace('src/bison/', ''), f) for f in files)

elif sys.platform.startswith('linux'):
    libs = ['dl']
    extra_link_args = []
    extra_compile_args = []  # ['-DCYTHON_TRACE=1']
    bison2pyscript = 'utils/bison2py'
    bisondynlibModule = 'src/bison/c/bisondynlib-linux.c'

elif sys.platform.startswith('darwin'):
    libs = ['dl']
    extra_link_args = []
    extra_compile_args = []
    bison2pyscript = 'utils/bison2py'
    bisondynlibModule = 'src/bison/c/bisondynlib-linux.c'
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
    author='Visual Computing @ Johannes Gutenberg University <vc-infra@lists.uni-mainz.de>',
    url='https://github.com/JGU-VC/pybison',
    ext_modules=[
        Extension(
            'bison.bison_',
            [
                'src/bison/cython/bison_.pyx',
                'src/bison/c/bison_callback.c',
                bisondynlibModule
            ],
            extra_compile_args=extra_compile_args,
            libraries=libs,
            extra_link_args=extra_link_args,
            cython_compile_time_env={'PY3': sys.version_info.major >= 3},
        )
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    cmdclass=LazyCommandClass(),
    scripts=[bison2pyscript],
    install_requires=[
        "cython",
        "six",
        "setuptools"
    ],
    setup_requires=[
        'cython',
    ],
    include_package_data=True,
    package_data={
        'bison': package_data,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
