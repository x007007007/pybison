"""
Wrapper module for interfacing with Bison (yacc)

Written April 2004 by David McNab <david@freenet.org.nz>
Copyright (c) 2004 by David McNab, all rights reserved.

Released under the GNU General Public License, a copy of which should appear in
this distribution in the file called 'COPYING'. If this file is missing, then
you can obtain a copy of the GPL license document from the GNU website at
http://www.gnu.org.

This software is released with no warranty whatsoever. Use it at your own
risk.

If you wish to use this software in a commercial application, and wish to
depart from the GPL licensing requirements, please contact the author and apply
for a commercial license.
"""

__version__ = '0.2.9'
__uri__ = 'https://github.com/lukeparser/pybison'
__author__ = 'David McNab'
__maintainer__ = 'Lukeparser Team'
__license__ = 'GPLv2'

from .parse import (
    ParserEngine,
    BisonParser,
    BisonSyntaxError,
)

