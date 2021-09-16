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
File with tests related to the export functionality for polygons.
"""
import os
import unittest
import warnings

from src.error.export_error import ExportError
from src.input.shapefile_importer import ShapefileImporter
from src.output.shapefile_exporter import ShapefileExporter
from src.program.program import Program


class TestExportPolygons(unittest.TestCase):

    def setUp(self):
        """
        Method executed before every test.
        """
        warnings.simplefilter("ignore", ResourceWarning)

        # create program
        self.program = Program()
        self.engine = self.program.engine

        # initialize variables
        self.engine.should_use_threads(False)
        self.engine.load_netcdf_file('resources/test_resources/cpt/cpt_1.cpt',
                                     'resources/test_resources/netcdf/test_model_2.nc')

    def tearDown(self) -> None:
        """
        Delete all temporary files created by the program on the setup or testing processes.

        Returns: None
        """
        self.program.close()

    def test_create_and_export(self):
        warnings.simplefilter("ignore", ResourceWarning)

        pol = self.engine.create_new_polygon()
        importer = ShapefileImporter()

        # add points
        self.engine.set_active_polygon(pol)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 1)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 1)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 0)

        # export
        self.engine.export_polygon_with_id(pol, 'resources/test_resources/temp/test_shapefile_export')

        # import and read the file
        polygons, parameters = importer.get_polygon_information('resources/test_resources/temp/'
                                                                'test_shapefile_export.shp')

        expected_value_polygons = [[(1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]]

        expected_value_parameters = [{'name': 'Polygon 0'}]

        self.assertEqual(polygons, expected_value_polygons, 'Points stored in the polygon are not the expected value.')
        self.assertEqual(parameters, expected_value_parameters, 'Parameters stored are not the expected.')

        os.remove('resources/test_resources/temp/test_shapefile_export.shp')
        os.remove('resources/test_resources/temp/test_shapefile_export.dbf')
        os.remove('resources/test_resources/temp/test_shapefile_export.shx')

    def test_create_and_export_parameters(self):
        warnings.simplefilter("ignore", ResourceWarning)

        pol = self.engine.create_new_polygon()

        self.engine.set_active_polygon(pol)
        self.engine.set_new_parameter_to_polygon(pol, '1', 'some_string')
        self.engine.set_new_parameter_to_polygon(pol, '2', int(10))
        self.engine.set_new_parameter_to_polygon(pol, '3', float(10.55487))
        self.engine.set_new_parameter_to_polygon(pol, '4', float(205.5))
        self.engine.set_new_parameter_to_polygon(pol, '5', True)
        self.engine.set_new_parameter_to_polygon(pol, '6', False)
        self.engine.set_new_parameter_to_polygon(pol, '7', None)

        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(2, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(3, 0)

        # export
        self.engine.export_polygon_with_id(pol, 'resources/test_resources/temp/'
                                                'test_shapefile_parameters')

        # import and testing
        importer = ShapefileImporter()
        polygons, parameters = importer.get_polygon_information(
            'resources/test_resources/temp/test_shapefile_parameters.shp')

        expected_value_polygons = [[(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0)]]
        expected_value_parameters = [
            {'1': 'some_string', '2': 10.0, '3': 10.55487, '4': 205.5, '5': True, '6': False, '7': 'None',
             'name': 'Polygon 0'}]

        self.assertEqual(polygons, expected_value_polygons, 'Points stored in the polygon are not the expected value.')
        self.assertEqual(parameters, expected_value_parameters, 'Parameters stored are not the expected.')

        os.remove('resources/test_resources/temp/test_shapefile_parameters.shp')
        os.remove('resources/test_resources/temp/test_shapefile_parameters.dbf')
        os.remove('resources/test_resources/temp/test_shapefile_parameters.shx')

    def test_create_and_export_string_parameters(self):
        warnings.simplefilter("ignore", ResourceWarning)

        pol = self.engine.create_new_polygon()

        self.engine.set_active_polygon(pol)
        self.engine.set_new_parameter_to_polygon(pol, 'notcutted', 'some_string')
        self.engine.set_new_parameter_to_polygon(pol, 'thisnameshouldbecuttedsomewhere', 'A very interesting string')

        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 60)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 60)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(2, 60)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(3, 60)

        # export
        self.engine.export_polygon_with_id(pol, 'resources/test_resources/temp/'
                                                'test_shapefile_parameters_long_names')

        # import and testing
        importer = ShapefileImporter()
        polygons, parameters = importer.get_polygon_information('resources/test_resources/temp/'
                                                                'test_shapefile_parameters_long_names.shp')

        expected_value_polygons = [[(0.0, 60.0), (1.0, 60.0), (2.0, 60.0), (3.0, 60.0)]]

        expected_value_parameters = [
            {'notcutted': 'some_string',
             'thisnamesh': 'A very interesting string',
             'name': 'Polygon 0'}]

        self.assertEqual(polygons, expected_value_polygons, 'Points stored in the polygon are not the expected value.')
        self.assertEqual(parameters, expected_value_parameters, 'Parameters stored are not the expected.')

        os.remove('resources/test_resources/temp/test_shapefile_parameters_long_names.shp')
        os.remove('resources/test_resources/temp/test_shapefile_parameters_long_names.dbf')
        os.remove('resources/test_resources/temp/test_shapefile_parameters_long_names.shx')

    def test_create_and_export_multiple(self):
        warnings.simplefilter("ignore", ResourceWarning)

        pol_1 = self.engine.create_new_polygon()
        pol_2 = self.engine.create_new_polygon()
        pol_3 = self.engine.create_new_polygon()
        importer = ShapefileImporter()

        # add points to the polygons
        self.engine.set_active_polygon(pol_1)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 1)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 2)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 3)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 4)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 5)

        self.engine.set_active_polygon(pol_2)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(2, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(3, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(4, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(5, 0)

        self.engine.set_active_polygon(pol_3)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 1)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(2, 2)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(2, 0)
        self.engine.add_new_vertex_to_active_polygon_using_real_coords(1, 0.1)
        self.engine.set_new_parameter_to_polygon(pol_3, 'float_val', 15.567)
        self.engine.set_new_parameter_to_polygon(pol_3, 'bool_val', True)
        self.engine.set_new_parameter_to_polygon(pol_3, 'other_val', None)
        self.engine.set_new_parameter_to_polygon(pol_3, 'int_val', 18)

        # export the polygons
        self.engine.export_polygon_list_id([pol_1, pol_2, pol_3],
                                           directory_filename='resources/test_resources/temp/'
                                                              'test_shapefile_export_multiple_1')

        # import and read the file
        polygons, parameters = importer.get_polygon_information('resources/test_resources/temp/'
                                                                'test_shapefile_export_multiple_1.shp')

        expected_value_polygons = [[(0.0, 0.0), (0.0, 1.0), (0.0, 2.0), (0.0, 3.0), (0.0, 4.0), (0.0, 5.0)],
                                   [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0), (4.0, 0.0), (5.0, 0.0)],
                                   [(1.0, 0.1), (2.0, 0.0), (2.0, 2.0), (1.0, 1.0), (0.0, 0.0)]]

        expected_value_parameters = [{'name': 'Polygon 0',
                                      'float_val': '',
                                      'bool_val': '',
                                      'other_val': '',
                                      'int_val': ''},

                                     {'name': 'Polygon 1',
                                      'float_val': '',
                                      'bool_val': '',
                                      'other_val': '',
                                      'int_val': ''},

                                     {'name': 'Polygon 2',
                                      'float_val': 15.567,
                                      'bool_val': True,
                                      'other_val': 'None',
                                      'int_val': 18}]

        self.assertEqual(polygons, expected_value_polygons, 'Points stored in the polygon are not the expected value.')
        self.assertEqual(parameters, expected_value_parameters, 'Parameters stored are not the expected.')

        os.remove('resources/test_resources/temp/test_shapefile_export_multiple_1.shp')
        os.remove('resources/test_resources/temp/test_shapefile_export_multiple_1.dbf')
        os.remove('resources/test_resources/temp/test_shapefile_export_multiple_1.shx')

    def test_export_polygon_error(self):
        exporter = ShapefileExporter()

        # Test error when exporting only one polygon
        with self.assertRaises(ExportError):
            exporter.export_polygon_to_shapefile(list_of_points=None,
                                                 directory='',
                                                 polygon_name='',
                                                 parameters=None)

        # Test error when exporting multiple polygons
        with self.assertRaises(ExportError):
            exporter.export_list_of_polygons([[0, 0], [0, 0], [0, 0]],
                                             [{}, {}, {}],
                                             ['pol_1', 'pol_2', 'pol_3'],
                                             'resources/test_resources/temp/should_not_export.shp'
                                             )


if __name__ == '__main__':
    unittest.main()
