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

from src.utils import get_logger, interpolate, is_clockwise, is_numeric


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

    def test_log_only_listed_modules(self):
        warnings.simplefilter("ignore", ResourceWarning)

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
        warnings.simplefilter("ignore", ResourceWarning)

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


class TestInterpolation(unittest.TestCase):

    def test_simple_values(self):
        self.assertEqual(50, interpolate(5, 0, 10, 0, 100, True))

    def test_border_case(self):
        # initial interval is just one value
        self.assertEqual(50,
                         interpolate(5, 5, 5, 0, 100, True),
                         'Interpolate function does not return average of target values when initial interval'
                         'is just one value.')

        # parameters are given in incorrect order
        self.assertEqual(50,
                         interpolate(5, 10, 0, 100, 0, True),
                         'Interpolate function does not return correct value when intervals are given in different'
                         'order (max store min values and min store maximum values)')


if __name__ == '__main__':
    unittest.main()
