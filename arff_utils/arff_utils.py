# -*- coding: utf-8 -*-
__author__ = 'Ralph'

import arff
import numpy as np
import pandas as pd


class ARFF(object):

    @staticmethod
    def read(file_name, missing='?'):
        """
        Loads ARFF file into data dictionary. Missing values indicated
        by '?' are automatically converted to None. If you want some
        other value to be treated as missing, specify them in the
        missing parameter.
        :param file_name: File name
        :param missing: Missing value expression
        :return: Data dictionary
        """
        data = arff.load(open(file_name))
        if not missing == '?':
            for i in range(len(data['data'])):
                for j in range(len(data['data'][i])):
                    if data['data'][i][j] == missing:
                        data['data'][i][j] = None
        return data

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

        return ARFF.create(relation, attributes, data, description)

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
    def create(relation, attributes, data, description=''):
        """
        Creates new ARFF data dictionary from given parameters. Note that
        string values will be automatically converted to Unicode
        :param relation: Relation
        :param attributes: Attributes
        :param data: Data rows
        :param description: Optional description
        :return: New data dictionary
        """
        # data_new = dict()
        # data_new[unicode('description')] = unicode(description)
        # data_new[unicode('relation')] = unicode(relation)
        attributes_new = []
        for i in range(len(attributes)):
            attribute_name = unicode(attributes[i][0])
            if type(attributes[i][1]) is list():
                attribute_type = []
                for j in range(len(attributes[i][1])):
                    attribute_type.append(unicode(attributes[i][1][j]))
            else:
                attribute_type = unicode(attributes[i][1])
            attributes_new.append((attribute_name, attribute_type))
        data_new = []
        for i in range(len(data)):
            data_row_new = []
            for j in range(len(data[i])):
                if type(data[i][j]) is str:
                    data_row_new.append(unicode(data[i][j]))
                else:
                    data_row_new.append(data[i][j])
            data_new.append(data_row_new)

        return {
            unicode('description'): unicode(description),
            unicode('relation'): unicode(relation),
            unicode('attributes'): attributes_new,
            unicode('data'): data_new,
        }

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
        # Figure out which description to use. Show a warning message
        # if descriptions are different. We'll use the first one
        description = ''
        if 'description' in data1.keys() and 'description' in data2.keys():
            if not unicode(data1['description']) == unicode(data2['description']):
                print('WARNING: mismatching descriptions, taking data1')
            description = data1['description']
        elif 'description' in data1.keys():
            description = data1['description']
        elif 'description' in data2.keys():
            description = data2['description']

        # Check whether relation is the same
        relation1 = data1['relation']
        relation2 = data2['relation']
        if not unicode(relation1) == unicode(relation2):
            raise RuntimeError('Mismatching relations')

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

        return ARFF.create(relation1, attributes1, data, description)

    @staticmethod
    def merge(data1, data2, attribute):
        """
        Merges contents of dictionaries 'data1' and 'data2' based on
        the given common attribute. In this case, the number of data
        rows must be identical.
        :param data1: First dictionary
        :param data2: Second dictionary
        :param attribute: Merge attribute
        :return: New dictionary
        """
        # Check that both data sets have the merge attribute otherwise we
        # can never match rows from one with rows from the other
        if not ARFF.contains(data1, attribute):
            raise RuntimeError('Attribute ' + attribute + ' missing from data1')
        if not ARFF.contains(data2, attribute):
            raise RuntimeError('Attribute ' + attribute + ' missing from data2')

        # Check that both data sets have the same number of data rows
        len1 = len(data1['data'])
        len2 = len(data2['data'])
        if not len1 == len2:
            raise RuntimeError('Mismatching number of data rows (' + str(len1) + ' vs ' + str(len2) + ')')

        relation = data1['relation'] + '_' + data2['relation']

        attributes1 = data1['attributes']
        attributes2 = data2['attributes']
        attributes3 = attributes1

        # Figure out which attributes in data2 are not yet in data1 and add
        # them to data1's attributes. Also, store the corresponding indexes
        # in data2 so we can also add the corresponding data values.
        indexes = []
        attributes_names = [x[0] for x in attributes1]
        for i in range(len(attributes2)):
            attribute_name = attributes2[i][0]
            if attributes_names.__contains__(attribute_name):
                attribute_type = attributes2[i][1]
                attributes3.append((attribute_name, attribute_type))
                indexes.append(i)

        # Add the data values from data2 as well
        data_rows1 = data1['data']
        data_rows2 = data2['data']
        data = []

        # Create new data rows by first appending all items of data1 and
        # then appending the selected items of data2 based on the indexes
        # calculated previously
        for i in range(len(data_rows1)):
            data_row = data_rows1[i]
            for j in indexes:
                data_row.append(data_rows2[i][j])
            data.append(data_row)

        return ARFF.create(relation, attributes3, data)

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