"""
File with the tests related to the functionality that imports CPT files into the program.
"""
import unittest
import warnings
import os
import json

from src.input.CTP import read_file

FILES_DIRECTORY = './test/input/files/'


class TestReadCPTFile(unittest.TestCase):

    def test_reading_normal_files(self):
        warnings.simplefilter("ignore", ResourceWarning)

        with open(os.path.join(FILES_DIRECTORY, 'cpt/test_data_CPT_1.json')) as f:
            data_1 = json.load(f)
            data_read = read_file(os.path.join(FILES_DIRECTORY, 'cpt/test_cpt_1.cpt'))
            self.assertEqual(data_1, data_read, 'Data read from CPT file is not what is expected.')

        with open(os.path.join(FILES_DIRECTORY, 'cpt/test_data_CPT_2.json')) as f:
            data_2 = json.load(f)
            data_read = read_file(os.path.join(FILES_DIRECTORY, 'cpt/test_cpt_2.cpt'))
            self.assertEqual(data_2, data_read, 'Data read from CPT file is not what is expected.')


if __name__ == '__main__':
    unittest.main()
