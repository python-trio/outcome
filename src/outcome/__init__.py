# coding: utf-8
"""Top-level package for outcome."""
from __future__ import absolute_import, division, print_function

from ._version import __version__

import sys

if sys.version_info >= (3, 5):
    from ._async import Error, Outcome, Value, acapture, capture
    __all__ = (
        'Error', 'Outcome', 'Value', 'acapture', 'capture', 'AlreadyUsedError'
    )
else:
    from ._sync import Error, Outcome, Value, capture
    __all__ = ('Error', 'Outcome', 'Value', 'capture', 'AlreadyUsedError')

from ._util import fixup_module_metadata, AlreadyUsedError
fixup_module_metadata(__name__, globals())
del fixup_module_metadata
