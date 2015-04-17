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

DIR = os.path.abspath('./tests')
IN_FILE = DIR + '/data/data.arff'
OUT_FILE = DIR + '/data/data_out.arff'


class TestArffUtils(unittest.TestCase):

    def setUp(self):

    	# Get file names test data sets
        self._data_dir = os.path.abspath('./tests/data')

        self._iris  = self._data_dir + '/iris.arff'
        self._labor = self._data_dir + '/labor.arff'
        self._temp  = self._data_dir + '/temp.arff'

    def testIO(self):
        
        # Read iris data
        data = ARFF.read(self._iris)
        ARFF.write(self._temp, data)
        data = ARFF.read(self._temp)

        # Read labor data
        data = ARFF.read(self._labor)
        ARFF.write(self._temp, data)
        data = ARFF.read(self._temp)

    def testToDataFrame(self):

    	# Convert ARFF data to Pandas data frame
    	data = ARFF.read(self._iris)
    	data_frame = ARFF.to_data_frame(data)

    def tearDown(self):
        
        # Clean up intermediate files
        if os.path.isfile(self._temp):
        	os.remove(self._temp)


if __name__ == '__main__':

    unittest.main()
