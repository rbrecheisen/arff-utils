# -*- coding: utf-8 -*-

__author__ = 'Ralph Brecheisen'
__date__ = '2015-01-01'
__email__ = 'ralph.brecheisen@gmail.com'
__license__ = "LGPL v3"
__maintainer__ = "Ralph Brecheisen"

VERSION = '0.1.0'
VERSION_NUMBER_PARTS = ()
VERSION_STATUS = ''

_items = VERSION.split('-')                                           
VERSION_NUMBER_PARTS = tuple(int(i) for i in _items[0].split('.'))
if len(_items) > 1:
	VERSION_STATUS = _items[1]
__version__ = VERSION

from arff_utils import ARFF
