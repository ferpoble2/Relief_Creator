#  BEGIN GPL LICENSE BLOCK
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  END GPL LICENSE BLOCK

"""
Tests that check the logic of the utils module.
"""
import logging
import os
import unittest
import warnings

import numpy as np

from src.utils import dict_to_json, dict_to_serializable_dict, get_logger, is_clockwise, is_numeric, \
    json_to_dict


class TestIsClockwise(unittest.TestCase):

    def test_is_clockwise(self):
        points = [(1, 1), (1, 0), (0, 0)]
        self.assertTrue(is_clockwise(points))

    def test_not_clockwise(self):
        points = [(0, 0), (1, 0), (1, 1)]
        self.assertFalse(is_clockwise(points))

    def test_error_points(self):
        points = [(0, 0), (1, 1)]
        with self.assertRaises(AssertionError):
            is_clockwise(points)


class TestIsNumeric(unittest.TestCase):

    def test_string_numeric(self):
        self.assertTrue(is_numeric('10215'))
        self.assertTrue(is_numeric('10215.1257'))

    def test_string_not_numeric(self):
        self.assertFalse(is_numeric('10215notannumber'))
        self.assertFalse(is_numeric('not a number'))
        self.assertFalse(is_numeric('10215.1257 number'))
        self.assertFalse(is_numeric('eight'))
        self.assertFalse(is_numeric('0x1544'))


class TestLogger(unittest.TestCase):

    def setUp(self) -> None:
        """Logic executed before every test."""
        warnings.simplefilter("ignore", ResourceWarning)

    def test_log_only_listed_modules(self):
        log = get_logger(log_level=logging.DEBUG,
                         log_file_level=logging.DEBUG,
                         module='TEST_LOGGER_1',
                         directory='resources/test_resources/temp',
                         log_to_file=True,
                         log_to_console=False,
                         log_only_listed_modules=True,
                         log_list_modules=['TEST_LOGGER_1'])

        log2 = get_logger(log_level=logging.DEBUG,
                          log_file_level=logging.DEBUG,
                          module='TEST_LOGGER_2',
                          directory='resources/test_resources/temp',
                          log_to_file=True,
                          log_to_console=False,
                          log_only_listed_modules=True,
                          log_list_modules=['TEST_LOGGER_1'])

        log3 = get_logger(log_level=logging.DEBUG,
                          log_file_level=logging.DEBUG,
                          module='TEST_LOGGER_3',
                          directory='resources/test_resources/temp',
                          log_to_file=True,
                          log_to_console=False,
                          log_only_listed_modules=True,
                          log_list_modules=['TEST_LOGGER_1'])

        log.debug('test_logging_message_test_logger_1')
        log2.debug('test_logging_message_test_logger_2')
        log3.debug('test_logging_message_test_logger_3')

        for handler in log.handlers + log2.handlers + log3.handlers:
            handler.close()

        log1_file = open('resources/test_resources/temp/TEST_LOGGER_1.log', 'r')
        log2_file = open('resources/test_resources/temp/TEST_LOGGER_2.log', 'r')
        log3_file = open('resources/test_resources/temp/TEST_LOGGER_3.log', 'r')

        log1_lines = log1_file.readlines()
        log2_lines = log2_file.readlines()
        log3_lines = log3_file.readlines()

        log1_file.close()
        log2_file.close()
        log3_file.close()

        # check lines
        self.assertEqual(1, len(log1_lines))
        split_line = log1_lines[0].split(' - ')
        module = split_line[1]
        message = split_line[2]

        self.assertEqual('TEST_LOGGER_1', module)
        self.assertEqual('DEBUG: test_logging_message_test_logger_1\n', message)

        self.assertEqual([], log2_lines)
        self.assertEqual([], log3_lines)

        os.remove('resources/test_resources/temp/TEST_LOGGER_1.log')
        os.remove('resources/test_resources/temp/TEST_LOGGER_2.log')
        os.remove('resources/test_resources/temp/TEST_LOGGER_3.log')

    def test_logger_file(self):
        log = get_logger(log_level=logging.DEBUG,
                         log_file_level=logging.DEBUG,
                         module='TEST_LOGGER',
                         directory='resources/test_resources/temp',
                         log_to_file=True,
                         log_to_console=False,
                         log_only_listed_modules=False,
                         log_list_modules=[])

        log.debug('test_logging_message')
        log.error('test_logging_error')
        log.info('test_logging_info')

        # close handlers
        for handler in log.handlers:
            handler.close()

        log_file = open('resources/test_resources/temp/TEST_LOGGER.log', 'r')
        log_file_lines = log_file.readlines()
        log_file.close()

        # check lines
        debug_info = log_file_lines[0].split(' - ')
        self.assertEqual('TEST_LOGGER', debug_info[1])
        self.assertEqual('DEBUG: test_logging_message\n', debug_info[2])

        error_info = log_file_lines[1].split(' - ')
        self.assertEqual('TEST_LOGGER', error_info[1])
        self.assertEqual('ERROR: test_logging_error\n', error_info[2])

        info_info = log_file_lines[2].split(' - ')
        self.assertEqual('TEST_LOGGER', info_info[1])
        self.assertEqual('INFO: test_logging_info\n', info_info[2])

        # remove files
        os.remove('resources/test_resources/temp/TEST_LOGGER.log')


class TestSerializeDict(unittest.TestCase):

    def test_serialize_json(self):
        dict_to_serialize = {'test_1': 125346,
                             'test_2': np.zeros((3, 3)),
                             'test_3': {
                                 'test_3_1': 1645,
                                 'test_3_2': 'someString',
                                 'test_3_3': np.zeros((1, 1)),
                                 'test_3_4': {
                                     'test_3_4_1': np.zeros((2, 2))
                                 }
                             }}

        self.assertEqual({'test_1': 125346,
                          'test_2': [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
                          'test_3': {'test_3_1': 1645,
                                     'test_3_2': 'someString',
                                     'test_3_3': [[0.0]],
                                     'test_3_4': {'test_3_4_1': [[0.0, 0.0],
                                                                 [0.0, 0.0]]}}},
                         dict_to_serializable_dict(dict_to_serialize),
                         'Dictionary was not serialized  correctly.')


class TestSaveDictToJson(unittest.TestCase):

    def test_read_json_data(self):
        self.assertEqual({'test_1': 1234,
                          'test_2': 'some string',
                          'test_3': [1, 2, 3, 4, 5]},
                         json_to_dict('resources/test_resources/expected_data/json_data/random_data.json'),
                         'The information read is not equal to the expected.')

    def test_save_json_file(self):
        dict_to_save = {'test_1': 'some string',
                        'test_2': 17463,
                        'test_3': [1, 2, 3, 4, 5],
                        'test_4': np.zeros((2, 2)),
                        'test_5': {
                            'test_5_1': np.zeros((1, 1)),
                            'test_5_2': 'some string 2',
                            'test_5_3': [np.zeros((2, 2)), np.ones((1, 1))],
                            'test_5_4': (np.zeros((2, 2)), np.ones((1, 1)))
                        }}
        dict_to_json(dict_to_save, 'resources/test_resources/temp/json_temp_data.json')

        self.assertEqual({'test_1': 'some string',
                          'test_2': 17463,
                          'test_3': [1, 2, 3, 4, 5],
                          'test_4': [[0, 0], [0, 0]],
                          'test_5': {
                              'test_5_1': [[0]],
                              'test_5_2': 'some string 2',
                              'test_5_3': [[[0, 0], [0, 0]], [[1]]],
                              'test_5_4': [[[0, 0], [0, 0]], [[1]]]
                          }},
                         json_to_dict('resources/test_resources/temp/json_temp_data.json'),
                         'Data stored in the file is not equal to the original data.')

        os.remove('resources/test_resources/temp/json_temp_data.json')


if __name__ == '__main__':
    unittest.main()
