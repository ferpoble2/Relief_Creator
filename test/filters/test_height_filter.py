"""
File with the tests related to the functionality that applies height filters to the polygons.
"""
import unittest
import warnings
import os

from src.engine.engine import Engine
from src.program.program import Program
from src.input.NetCDF import read_info


class TestHeightGreaterFilter(unittest.TestCase):

    def setUp(self) -> None:
        """
        Code executed before every test. Initializes a program to work with.
        """

        # create program
        self.engine = Engine()
        self.program = Program(self.engine)

        # initialize variables
        self.engine.should_use_threads(False)

    # TODO: Test case when polygon does not use all the map
    # TODO: Test case when polygon is outside of map

    def test_normal_application(self):
        warnings.simplefilter("ignore", ResourceWarning)

        self.engine.refresh_with_model_2d('resources/test_resources/cpt/colors_0_100_200.cpt',
                                          'resources/test_resources/netcdf/test_file_50_50.nc')

        # load polygon
        self.engine.load_polygon_from_shapefile('resources/test_resources/polygons/shape_one_polygon_1.shp')

        # create polygon to modify the scene.
        self.engine.transform_points(polygon_id=self.engine.get_active_polygon_id(),
                                     model_id=self.engine.get_active_model_id(),
                                     min_height=100,
                                     max_height=200,
                                     transformation_type='linear',
                                     filters=[('height_greater_than', 50)])

        # export model to compare data
        self.engine.export_model_as_netcdf(self.engine.get_active_model_id(),
                                           'resources/test_resources/temp/temp_filter_1')

        # read data and compare
        info_written = read_info('resources/test_resources/temp/temp_filter_1.nc')
        info_expected = read_info('resources/test_resources/expected_data/netcdf/expected_filter_1.nc')

        self.assertTrue((info_written[0] == info_expected[0]).all())
        self.assertTrue((info_written[1] == info_expected[1]).all())
        self.assertTrue((info_written[2] == info_expected[2]).all())

        os.remove('resources/test_resources/temp/temp_filter_1.nc')

if __name__ == '__main__':
    unittest.main()
