"""
Builds bison python module
"""
import codecs
import os
import re
import sys
from os.path import join
from setuptools import find_packages, setup

# put the right setup.py into the sdist directory
if os.path.isfile("setup.py"):
    os.remove("setup.py")
os.symlink("setup-runtime.py", "setup.py")


###################################################################
#                             META DATA                           #
###################################################################

NAME = "pybison-runtime"
DESCRIPTION='Python bindings for bison/flex parser engine'
PACKAGES = find_packages(where="src")
META_PATH = os.path.join("src", "bison", "__init__.py")
KEYWORDS = []
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    'Operating System :: Unix',
    'Operating System :: POSIX',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Text Processing'
]
INSTALL_REQUIRES = [
    "six",
    "setuptools"
]



###################################################################

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()



META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))



# check availability for system
if sys.platform == 'win32' or sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
    pass
else:
    print('Sorry, your platform is not supported. Please compile pybison instead.')
    sys.exit(1)



if __name__ == "__main__":
    setup(
        name=NAME,
        description=DESCRIPTION,
        author=find_meta("author"),
        maintainer=find_meta("maintainer"),
        license=find_meta("license"),
        url=find_meta("uri"),
        version=find_meta("version"),
        keywords=KEYWORDS,
        long_description=read("README.md"),
        long_description_content_type="text/markdown",
        packages=PACKAGES,
        package_dir={"": "src"},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        package_data={"bison": [
            "bison_.cpython-37m-x86_64-linux-gnu.so"
        ]},
    )

