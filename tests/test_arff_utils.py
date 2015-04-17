#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_arff_utils
----------------------------------

Tests for `arff_utils` module.
"""

import os
import unittest
from arff_utils import ARFF

IN_FILE = 'data/data.arff'
OUT_FILE = 'data/data_out.arff'


class TestArffUtils(unittest.TestCase):

    def setUp(self):
        pass

    def testIO(self):
        
        # Read test data, write it to new file and read it back in
        data = ARFF.read(IN_FILE)
        ARFF.write(OUT_FILE, data)
        data = ARFF.read(OUT_FILE)

    def testToDataFrame():

    	data = ARFF.read(IN_FILE)
    	data_frame = ARFF.to_data_frame(data)

    def tearDown(self):
        
        # Clean up intermediate files
        if os.path.isfile(OUT_FILE):
        	os.remove(OUT_FILE)


if __name__ == '__main__':

    unittest.main()
