"""
File with the tests related to the import of polygons in shapefile files.
"""

import unittest
import json
import os

from src.input.shapefile_importer import ShapefileImporter

FILES_DIRECTORY = './test/input/files/'


class TestShapefileReading(unittest.TestCase):

    def test_no_polygons(self):
        with open(os.path.join(FILES_DIRECTORY, 'polygons', 'shapefile_data_no_polygons.json')) as f:
            data = json.load(f)

        shp_importer = ShapefileImporter()
        points, parameters = shp_importer.get_polygon_information(os.path.join(FILES_DIRECTORY,
                                                                               'polygons',
                                                                               'Shape_sin_poligono.shp'))

        self.assertEqual(data['points'], points)
        self.assertEqual(data['parameters'], parameters)

    def test_one_polygons(self):
        with open(os.path.join(FILES_DIRECTORY, 'polygons', 'shapefile_data_one_polygons.json')) as f:
            data = json.load(f)

        shp_importer = ShapefileImporter()
        points, parameters = shp_importer.get_polygon_information(os.path.join(FILES_DIRECTORY,
                                                                               'polygons',
                                                                               'Shape_Un_poligono.shp'))

        data_points = data['points']
        data_parameters = data['parameters']

        for polygon in data_points:
            for point_ind in range(len(polygon)):
                polygon[point_ind] = tuple(polygon[point_ind])

        self.assertEqual(data_points, points)
        self.assertEqual(data_parameters, parameters)

    def test_many_polygons(self):
        with open(os.path.join(FILES_DIRECTORY, 'polygons', 'shapefile_data_many_polygons.json')) as f:
            data = json.load(f)

        shp_importer = ShapefileImporter()
        points, parameters = shp_importer.get_polygon_information(os.path.join(FILES_DIRECTORY,
                                                                               'polygons',
                                                                               'Shape_muchos_poligono.shp'))

        data_points = data['points']
        data_parameters = data['parameters']

        for polygon in data_points:
            for point_ind in range(len(polygon)):
                polygon[point_ind] = tuple(polygon[point_ind])

        self.assertEqual(data_points, points)
        self.assertEqual(data_parameters, parameters)

    def test_odd_polygons(self):
        with open(os.path.join(FILES_DIRECTORY, 'polygons', 'shapefile_data_odd_polygons.json')) as f:
            data = json.load(f)

        shp_importer = ShapefileImporter()
        points, parameters = shp_importer.get_polygon_information(os.path.join(FILES_DIRECTORY,
                                                                               'polygons',
                                                                               'Shape_raros_poligono.shp'))

        data_points = data['points']
        data_parameters = data['parameters']

        for polygon in data_points:
            for point_ind in range(len(polygon)):
                polygon[point_ind] = tuple(polygon[point_ind])

        self.assertEqual(data_points, points)
        self.assertEqual(data_parameters, parameters)

    def test_polygons_parameters(self):
        with open(os.path.join(FILES_DIRECTORY, 'polygons', 'shapefile_data_parameters.json')) as f:
            data = json.load(f)

        shp_importer = ShapefileImporter()
        points, parameters = shp_importer.get_polygon_information(os.path.join(FILES_DIRECTORY,
                                                                               'polygons',
                                                                               'Shape_multiple_parameters.shp'))

        data_points = data['points']
        data_parameters = data['parameters']

        for polygon in data_points:
            for point_ind in range(len(polygon)):
                polygon[point_ind] = tuple(polygon[point_ind])

        self.assertEqual(data_points, points)
        self.assertEqual(data_parameters, parameters)


if __name__ == '__main__':
    unittest.main()
