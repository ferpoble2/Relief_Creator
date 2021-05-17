"""
File with tests related to the export functionality for poligons.
"""
import unittest
import warnings
import os
import time

from src.output.shapefile_exporter import ShapefileExporter
from src.input.shapefile_importer import ShapefileImporter
from src.engine.scene.model.polygon import Polygon
from src.engine.scene.scene import Scene
from src.engine.engine import Engine
from src.program.program import Program

FILES_DIRECTORY = './test/output/files/'


class TestExportPolygons(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

        # create program
        self.engine = Engine()
        self.program = Program(self.engine)

        # intialize variables
        self.engine.should_use_threads(False)
        self.engine.refresh_with_model_2d(os.path.join(FILES_DIRECTORY, 'shapefile', 'default.cpt'),
                                          os.path.join(FILES_DIRECTORY, 'shapefile', 'test_model.nc'))

    def test_create_and_export(self):
        warnings.simplefilter("ignore", ResourceWarning)

        pol = self.engine.create_new_polygon()
        importer = ShapefileImporter()

        # add points
        self.engine.set_active_polygon(pol)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 1)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, 1)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, 0)

        # export
        self.engine.export_polygon_with_id(pol, os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_export'))

        # import and read the file
        polygons, parameters = importer.get_polygon_information(
            os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_export.shp'))

        expected_value_polygons = [[(-1.3703703703703702, 2.074074074074074),
                                    (-1.3703703703703702, 2.071111111111111),
                                    (-1.3674074074074074, 2.071111111111111),
                                    (-1.3674074074074074, 2.074074074074074)]]

        expected_value_parameters = [{'name': 'Polygon 0'}]

        self.assertEqual(polygons, expected_value_polygons, 'Points stored in the polygon are not the expected value.')
        self.assertEqual(parameters, expected_value_parameters, 'Parameters stored are not the expected.')

        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_export.shp'))
        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_export.dbf'))
        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_export.shx'))

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

        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(2, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(3, 0)

        # export
        self.engine.export_polygon_with_id(pol, os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_parameters'))

        # import and testing
        importer = ShapefileImporter()
        polygons, parameters = importer.get_polygon_information(
            os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_parameters.shp'))

        expected_value_polygons = [[(-1.3703703703703702, 2.074074074074074), (-1.3674074074074074, 2.074074074074074),
                                    (-1.3644444444444443, 2.074074074074074), (-1.3614814814814813, 2.074074074074074)]]
        expected_value_parameters = [
            {'1': 'some_string', '2': 10.0, '3': 10.55487, '4': 205.5, '5': True, '6': False, 'name': 'Polygon 0'}]

        self.assertEqual(polygons, expected_value_polygons, 'Points stored in the polygon are not the expected value.')
        self.assertEqual(parameters, expected_value_parameters, 'Parameters stored are not the expected.')

        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_parameters.shp'))
        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_parameters.dbf'))
        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_parameters.shx'))

    def test_create_and_export_parameters(self):
        warnings.simplefilter("ignore", ResourceWarning)

        pol = self.engine.create_new_polygon()

        self.engine.set_active_polygon(pol)
        self.engine.set_new_parameter_to_polygon(pol, 'notcutted', 'some_string')
        self.engine.set_new_parameter_to_polygon(pol, 'thisnameshouldbecuttedsomewhere', 'A very interesting string')

        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 60)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, 60)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(2, 60)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(3, 60)

        # export
        self.engine.export_polygon_with_id(pol, os.path.join(FILES_DIRECTORY, 'shapefile',
                                                             'test_shapefile_parameters_long_names'))

        # import and testing
        importer = ShapefileImporter()
        polygons, parameters = importer.get_polygon_information(
            os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_parameters_long_names.shp'))

        expected_value_polygons = [
            [(-1.3703703703703702, 1.8962962962962964), (-1.3674074074074074, 1.8962962962962964),
             (-1.3644444444444443, 1.8962962962962964), (-1.3614814814814813, 1.8962962962962964)]]

        expected_value_parameters = [
            {'notcutted': 'some_string',
             'thisnamesh': 'A very interesting string',
             'name': 'Polygon 0'}]

        self.assertEqual(polygons, expected_value_polygons, 'Points stored in the polygon are not the expected value.')
        self.assertEqual(parameters, expected_value_parameters, 'Parameters stored are not the expected.')

        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_parameters_long_names.shp'))
        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_parameters_long_names.dbf'))
        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_parameters_long_names.shx'))

    def test_create_and_export_multiple(self):
        warnings.simplefilter("ignore", ResourceWarning)

        pol_1 = self.engine.create_new_polygon()
        pol_2 = self.engine.create_new_polygon()
        pol_3 = self.engine.create_new_polygon()
        importer = ShapefileImporter()

        # add points to the polygons
        self.engine.set_active_polygon(pol_1)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 1)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 2)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 3)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 4)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 5)

        self.engine.set_active_polygon(pol_2)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(2, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(3, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(4, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(5, 0)

        self.engine.set_active_polygon(pol_3)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(0, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, 1)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(2, 2)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(2, 0)
        self.engine.add_new_vertex_to_active_polygon_using_window_coords(1, 0.1)

        # export the polygons
        self.engine.export_polygon_list_id([pol_1, pol_2, pol_3],
                                           directory_filename=os.path.join(FILES_DIRECTORY, 'shapefile',
                                                                           'test_shapefile_export_multiple_1'))

        # import and read the file
        polygons, parameters = importer.get_polygon_information(
            os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_export_multiple_1.shp'))

        expected_value_polygons = [
            [(-1.3703703703703702, 2.074074074074074), (-1.3703703703703702, 2.071111111111111),
             (-1.3703703703703702, 2.0681481481481483), (-1.3703703703703702, 2.065185185185185),
             (-1.3703703703703702, 2.062222222222222), (-1.3703703703703702, 2.0592592592592593)],
            [(-1.3555555555555554, 2.074074074074074), (-1.3585185185185185, 2.074074074074074),
             (-1.3614814814814813, 2.074074074074074), (-1.3644444444444443, 2.074074074074074),
             (-1.3674074074074074, 2.074074074074074), (-1.3703703703703702, 2.074074074074074)],
            [(-1.3703703703703702, 2.074074074074074), (-1.3674074074074074, 2.071111111111111),
             (-1.3644444444444443, 2.0681481481481483), (-1.3644444444444443, 2.074074074074074),
             (-1.3674074074074074, 2.0737777777777775)]]

        expected_value_parameters = [{'name': 'Polygon 0'}, {'name': 'Polygon 1'}, {'name': 'Polygon 2'}]

        self.assertEqual(polygons, expected_value_polygons, 'Points stored in the polygon are not the expected value.')
        self.assertEqual(parameters, expected_value_parameters, 'Parameters stored are not the expected.')

        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_export_multiple_1.shp'))
        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_export_multiple_1.dbf'))
        os.remove(os.path.join(FILES_DIRECTORY, 'shapefile', 'test_shapefile_export_multiple_1.shx'))


if __name__ == '__main__':
    unittest.main()
