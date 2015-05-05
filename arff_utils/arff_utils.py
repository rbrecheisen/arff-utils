# -*- coding: utf-8 -*-
__author__ = 'Ralph'

import arff
import numpy as np
import pandas as pd


class ARFF(object):

    @staticmethod
    def read(file_name, missing=None):
        """
        Loads ARFF file into data dictionary. Missing values indicated
        by '?' are automatically converted to None. If you want some
        other value to be treated as missing, specify them in the
        missing parameter.
        :param file_name: File name
        :param missing: List of missing value representations
        :return: Data dictionary
        """
        data = arff.load(open(file_name))
        if not missing == None:
            for i in range(len(data['data'])):
                for j in range(len(data['data'][i])):
                    if type(missing) is str:
                        if data['data'][i][j] == missing:
                            data['data'][i][j] = None
                    elif type(missing) is list:
                        for m in missing:
                            if data['data'][i][j] == m:
                                data['data'][i][j] = None                                
                    else:
                        raise RuntimeError('Invalid type for \'missing\' parameter ' + str(type(missing)))
        return data

    @staticmethod
    def read_from_csv(file_name):
        """
        Loads CSV file and converts it to an ARFF data dictionary. This 
        function assumes the following:
        (1) First line contains a header with column names
        (2) First column contains IDs (interpreted as string values)
        (3) Remaining columns contain numeric values
        :param file_name: CSV file path
        """
        attributes = []
        f = open(file_name, 'r')
        header = f.readline().strip().split(',')
        header = [item.strip() for item in header]
        attributes.append((header[0], 'STRING'))
        for item in header[1:]:
            attributes.append((item, 'NUMERIC'))
        data = []
        for line in f.readlines():
            line = line.strip()
            if line.startswith('#') or line == '':
                continue
            parts = line.split(',')
            parts = [part.strip() for part in parts]
            parts[0]  = str(parts[0])
            parts[1:] = [float(part) for part in parts[1:]]
            data.append(parts)
        f.close()

        return {
            'relation': 'unknown',
            'attributes': attributes,
            'data': data,
            'description': ''
        }
        

    @staticmethod
    def to_data_frame(data, index_col=None):
        """
        Converts ARFF data dictionary to Pandas data frame.
        :param data: Data dictionary
        :param index_col: Column name to use as index
        :return: Data frame
        """
        # Create data frame by by taking rows and attributes from 
        # ARFF data. Data types should be automatically inferred
        rows = data['data']
        columns = [attribute[0] for attribute in data['attributes']]
        data_frame = pd.DataFrame(rows, columns=columns)

        # If index column specified, set it
        if not index_col is None:
            if not index_col in data_frame.columns:
                raise RuntimeError('Index column ' + index_col + ' not found')
            data_frame.set_index(index_col, drop=True, inplace=True, verify_integrity=True)

        return data_frame

    @staticmethod
    def from_data_frame(relation, attributes, data_frame, description=''):
        """
        Converts Pandas data frame to ARFF dictionary. This is only possible
        if the data frame was previously converted from ARFF data because we
        need the specific attribute information.
        :param relation: Relation
        :param attributes: ARFF attributes
        :param data_frame: Data frame
        :param description: Optional description
        :return: ARFF data dictionary
        """
        data = []
        for row in data_frame.to_records(index=False):
            data.append(list(row))

        return {
            'relation': relation,
            'attributes': attributes,
            'data': data,
            'description': description
        }

    @staticmethod
    def write(file_name, data):
        """
        Writes ARFF data dictionary to file.
        :param file_name: File name
        :param data: Data dictionary
        :return:
        """
        f = open(file_name, 'w')
        arff.dump(data, f)
        f.close()

    @staticmethod
    def write_csv(file_name, data):
        """
        Writes ARFF data dictionary to CSV file. Note that this will
        cause loss of attribute type information. The approach we take
        here is to first convert to a Pandas data frame and then use the
        Pandas built-in function to export to CSV.
        :param file_name: CSV file name
        :param data: Data dictionary
        :return:
        """
        data_frame = ARFF.to_data_frame(data)
        data_frame.to_csv(file_name, na_rep='?', header=True, index=False, sep=',')

    @staticmethod
    def append(data1, data2):
        """
        Appends contents of ARFF data dictionary 'data2' to the contents
        of data dictionary 'data1'. Obviously, the attributes and types
        must correspond exactly.
        :param data1: Base data dictionary.
        :param data2: Dictionary to append
        :return: Updated dictionary
        """
        # Use description of data1
        description = data1['description']

        # Check whether we have matching attributes
        attributes1 = data1['attributes']
        attributes2 = data2['attributes']
        if not len(attributes1) == len(attributes2):
            raise RuntimeError('Mismatch number of attributes')
        for i in range(len(attributes1)):
            attribute1 = attributes1[i]
            attribute2 = attributes2[i]
            if not len(attribute1) == 2:
                raise RuntimeError('Number of attribute1 items != 2')
            if not len(attribute2) == 2:
                raise RuntimeError('Number of attribute2 items != 2')
            if not unicode(attribute1[0]) == unicode(attribute2[0]):
                raise RuntimeError('Mismatching names at ' + str(i) + ' (' + attribute1[0] + ' vs ' + attribute2[0] + ')')
            if type(attribute1[1]) is list and type(attribute2[1]) is list:
                for j in range(len(attribute1[1])):
                    if not unicode(attribute1[1][j]) == unicode(attribute2[1][j]):
                        raise RuntimeError('Mismatching nominal values at (' + str(i) + ',' + str(j) + ') (' + unicode(attribute1[1][j]) + ' vs ' + unicode(attribute2[1][j]) + ')')
            elif not unicode(attribute1[1]) == unicode(attribute2[1]):
                raise RuntimeError('Mismatching attribute types (' + unicode(attribute1[1]) + ' vs ' +  unicode(attribute2[1]) + ')')

        # Append rows of data2 to rows of data1
        data = []
        data.extend(data1['data'])
        data.extend(data2['data'])

        return {
            'relation': relation1,
            'attributes': attributes1,
            'data': data,
            'description': description
        }

    @staticmethod
    def merge(data1, data2, join_by, attributes):
        """
        Merges two data sets by appending the columns of data2 associated
        with given attributes to data1. Rows are matched based on the
        join_by attribute.
        :param data1: Original data set
        :param data2: Data set whose columns to add
        :param join_by: Attribute for matching data rows
        :param attributes: Attributes to add
        :return: New data set
        """
        # Check that both data sets have the merge attribute otherwise we
        # can never match rows from one with rows from the other
        if not ARFF.contains(data1, join_by):
            raise RuntimeError('Attribute ' + join_by + ' missing from data1')
        if not ARFF.contains(data2, join_by):
            raise RuntimeError('Attribute ' + join_by + ' missing from data2')

        # Check that data2 has the given attributes
        for attribute in attributes:
            if not ARFF.contains(data2, attribute):
                raise RuntimeError('Attribute ' + attribute + ' missing from data2')

        # Check that data1 does not have the given attributes
        for attribute in attributes:
            if ARFF.contains(data1, attribute):
                raise RuntimeError('Attribute ' + attribute + ' already exists in data1')

        # Get index of join_by attribute in both data sets. Then, create a
        # lookup table for data2 based on join_by attribute as key. This
        # allows quick access to data rows of data2. If we iterate through
        # the rows of data1, we can get the join_by attribute value using
        # the join_idx1 index. Using the attribute value we can then lookup
        # the corresponding data row in data2.
        join_idx1 = ARFF.index_of(data1, join_by)
        join_idx2 = ARFF.index_of(data2, join_by)
        data2_lookup = {}
        for data_row1 in data2['data']:
            data2_lookup[data_row1[join_idx2]] = data_row1

        # Get indexes associated with given attributes in data2. We need this
        # to efficiently access specific values in the rows of data2
        attribute_indexes = []
        for attribute in attributes:
            attribute_indexes.append(ARFF.index_of(data2, attribute))

        # Create new attribute set by appending the attributes of
        # data set data2. We already checked there are no duplicates.
        attributes_extended = data1['attributes']
        for i in attribute_indexes:
            attribute = data2['attributes'][i]
            attributes_extended.append(attribute)

        # Create new data rows by taking the original data row and
        # appending the values corresponding to the attribute columns from
        # data2. We can do this efficiently because of the lookup table we
        # created earlier. 
        data = []
        for i in range(len(data1['data'])):
            data_row = data1['data'][i]
            key = data_row[join_idx1]
            if not key in data2_lookup:
            	print('WARNING: row with id {} not present in data2'.format(key))
            	continue
            data_row2 = data2_lookup[data_row[join_idx1]]
            for j in attribute_indexes:
                data_row.append(data_row2[j])
            data.append(data_row)

        return {
            'relation': data1['relation'],
            'attributes': attributes_extended,
            'data': data,
            'description': ''
        }

    @staticmethod
    def dummy_encode(data, attribute):
        """
        Applies a 1-of-k dummy encoding to the given attribute and replaces
        the associated column with two or more dummy columns.
        :param data: ARFF data dictionary
        :param attribute: Nominal attribute
        :return: Dummy encoded data dictionary
        """
        # Check that the attribute is actually nominal. If not, just
        # return the data unchanged
        if not ARFF.is_nominal(data, attribute):
            return data

        # Get index of given attribute. We need it when we insert
        # additional dummy columns.
        idx = ARFF.index_of(data, attribute)

        # Get attribute values
        attr_values = data['attributes'][idx][1]

        # Next, delete the original attribute and insert new attributes
        # for each attribute value we encounter
        del data['attributes'][idx]
        for attr_value in reversed(attr_values):
            data['attributes'].insert(idx, (attr_value, 'NUMERIC'))

        # Insert dummy values into each data row depending on its
        # original value in the attribute column
        data_rows = data['data']
        for i in range(len(data_rows)):
            value = data_rows[i][idx]
            first = True
            for attr_value in reversed(attr_values):
                if first:
                    data_rows[i][idx] = 0
                    first = False
                else:
                    data_rows[i].insert(idx, 0)
                if value == attr_value:
                    data_rows[i][idx] = 1

        # Return both the dummy-encoded data as well as the newly
        # created attributes
        return data, attr_values

    @staticmethod
    def contains(data, attribute):
        """
        Checks whether given attribute is in data dictionary.
        :param data: Data dictionary
        :param attribute: Attribute to check
        :return: True/False
        """
        return ARFF.index_of(data, attribute) > -1

    @staticmethod
    def index_of(data, attribute):
        """
        Returns index of given attribute or -1 if not found.
        :param data: Data dictionary
        :param attribute: Attribute to search
        :return: Index or -1
        """
        for i in range(len(data['attributes'])):
            item = data['attributes'][i][0]
            if item == attribute:
                return i
        return -1

    @staticmethod
    def type_of(data, attribute):
        """
        Returns type of given attribute or None if attribute is
        of nominal type. In that case, use labels_of()
        :param data: Data dictionary
        :param attribute: Attribute to return type of
        :return: Attribute type
        """
        i = ARFF.index_of(data, attribute)
        if i < 0:
            return None
        attribute_value = data['attributes'][i][1]
        if isinstance(attribute_value, list):
            print('WARNING: attribute value is nominal')
            return None
        else:
            return attribute_value

    @staticmethod
    def labels_of(data, attribute):
        """
        Returns labels of given nominal attribute or None if
        attribute is not of nominal type.
        :param data: Data dictionary
        :param attribute: Attribute to return labels of
        :return: Labels
        """
        i = ARFF.index_of(data, attribute)
        if i < 0:
            return None
        attribute_values = data['attributes'][i][1]
        if not isinstance(attribute_values, list):
            print('WARNING: attribute value is not of type nominal')
            return None        
        else:
            return attribute_values

    @staticmethod
    def sort_by(data, attribute):
        """
        Sorts data by given attribute.
        :param data: ARFF data dictionary
        :param attribute: Attribute to sort by
        :return: Sorted dictionary
        """
        i = ARFF.index_of(data, attribute)
        if i < 0:
            raise RuntimeError('Attribute not found')
        data['data'].sort(key=lambda tup: tup[i])
        return data

    @staticmethod
    def is_nominal(data, attribute):
    	"""
    	Checks whether given attribute name corresponds to
    	nominal attribute or not.
    	:param data: ARFF data dictionary
    	:param attribute: Attribute to check
    	"""
    	i = ARFF.index_of(data, attribute)
    	if i < 0:
    		raise RuntimeError('Attribute not found')
    	attribute_value = data['attributes'][i][1]
    	if type(attribute_value) is list:
    		return True
    	return False