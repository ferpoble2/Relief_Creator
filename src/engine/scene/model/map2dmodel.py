"""
Class in charge of managing the models of the maps in 2 dimensions.
"""

import ctypes as ctypes

import OpenGL.GL as GL
import numpy as np

from src.engine.scene.model.model import Model
from src.engine.scene.model.tranformations.transformations import ortho
from src.input.CTP import read_file
from src.utils import get_logger

log = get_logger(module='Map2DModel')


# noinspection PyMethodMayBeStatic
class Map2DModel(Model):
    """
    Class that manage all things related to the 2D representation of the maps.

    Open GL variables:
        glVertexAttributePointer 1: Heights of the vertices.

    """

    def __init__(self, scene=None):
        """
        Constructor of the model class.
        """
        super().__init__(scene)

        # Color file used. (if not color file, then None)
        self.__color_file = None
        self.__colors = []
        self.__height_limit = []

        # grid values
        self.__x = None
        self.__y = None
        self.__z = None

        # vertices values (used in the buffer)
        self.__vertices = []

        # indices of the model (used in the buffer)
        self.__indices = []

        # height values
        self.__height_array = np.array([])
        self.__max_height = None
        self.__min_height = None

        # height buffer object
        self.hbo = GL.glGenBuffers(1)

        # projection matrix
        self.__projection = None
        self.__left_coordinate = None
        self.__right_coordinate = None
        self.__top_coordinate = None
        self.__bottom_coordinate = None

        # utilities variables
        self.__triangles_to_delete = np.array([])  # triangles overlapped to delete when optimizing memory
        self.__new_indices = None  # new indices of triangles calculated using parallelism

    def __add_triangles_inside_zone_to_delete_list(self,
                                                   left_coordinate: float,
                                                   right_coordinate: float,
                                                   top_coordinate: float,
                                                   bottom_coordinate: float) -> None:
        """
        Delete all the indices of the the triangles that are inside the zone from the
        list of indices.

        Args:
            left_coordinate: Left coordinate to check
            right_coordinate: Right coordinate to check
            top_coordinate: Top coordinate to check
            bottom_coordinate: Bottom coordinate to check

        Returns: None
        """
        log.debug('Add triangles inside zone to delete list...')

        # Get the variables and matrix to use
        # --------------------------

        log.debug('Converting array in array')
        indices_array = np.array(self.__indices)
        log.debug('Finished converting array in array')

        indices_array = indices_array.reshape(-1)
        vertices_array = self.get_vertices_array().reshape((-1, 3))

        log.debug('Apply of masks and reshape')
        indices_with_coords_array = vertices_array[indices_array]  # time consuming
        indices_with_coords_array = indices_with_coords_array.reshape((-1, 3, 3))
        log.debug('End of applying masks and reshape')

        # find out the indices with triangles inside the zone using masks
        # ---------------------------------------------------------------
        indices_with_coords_array = indices_with_coords_array.reshape((-1, 9)).transpose()

        log.debug('Generating mask with values')
        mask = np.ones(len(indices_with_coords_array[0]), dtype=bool)

        mask[np.where(indices_with_coords_array[0] < left_coordinate)[0]] = False
        mask[np.where(indices_with_coords_array[3] < left_coordinate)[0]] = False
        mask[np.where(indices_with_coords_array[6] < left_coordinate)[0]] = False

        mask[np.where(indices_with_coords_array[0] > right_coordinate)[0]] = False
        mask[np.where(indices_with_coords_array[3] > right_coordinate)[0]] = False
        mask[np.where(indices_with_coords_array[6] > right_coordinate)[0]] = False

        mask[np.where(indices_with_coords_array[1] < bottom_coordinate)[0]] = False
        mask[np.where(indices_with_coords_array[4] < bottom_coordinate)[0]] = False
        mask[np.where(indices_with_coords_array[7] < bottom_coordinate)[0]] = False

        mask[np.where(indices_with_coords_array[1] > top_coordinate)[0]] = False
        mask[np.where(indices_with_coords_array[4] > top_coordinate)[0]] = False
        mask[np.where(indices_with_coords_array[7] > top_coordinate)[0]] = False

        inside = np.where(mask == True)[0]  # noqa
        log.debug('Finished creation of mask with values')

        # Deprecated Code (using intersection instead of masks)
        # -----------------------------------------------------
        # index_out_1 = np.where(indices_with_coords_array[0] > left_coordinate)[0]
        # index_out_2 = np.where(indices_with_coords_array[3] > left_coordinate)[0]
        # index_out_3 = np.where(indices_with_coords_array[6] > left_coordinate)[0]
        # all_right = np.intersect1d(np.intersect1d(index_out_1, index_out_2), index_out_3)
        #
        # index_out_1 = np.where(indices_with_coords_array[0] < right_coordinate)[0]
        # index_out_2 = np.where(indices_with_coords_array[3] < right_coordinate)[0]
        # index_out_3 = np.where(indices_with_coords_array[6] < right_coordinate)[0]
        # all_left = np.intersect1d(np.intersect1d(index_out_1, index_out_2), index_out_3)
        #
        # index_out_1 = np.where(indices_with_coords_array[1] < top_coordinate)[0]
        # index_out_2 = np.where(indices_with_coords_array[4] < top_coordinate)[0]
        # index_out_3 = np.where(indices_with_coords_array[7] < top_coordinate)[0]
        # all_bottom = np.intersect1d(np.intersect1d(index_out_1, index_out_2), index_out_3)
        #
        # index_out_1 = np.where(indices_with_coords_array[1] > bottom_coordinate)[0]
        # index_out_2 = np.where(indices_with_coords_array[4] > bottom_coordinate)[0]
        # index_out_3 = np.where(indices_with_coords_array[7] > bottom_coordinate)[0]
        # all_top = np.intersect1d(np.intersect1d(index_out_1, index_out_2), index_out_3)
        #
        # inside = np.intersect1d(np.intersect1d(np.intersect1d(all_left, all_right), all_bottom), all_top)

        log.debug('Converting array to list')
        # to_delete = list(inside)
        to_delete = inside
        # log.debug('Finished conversion')

        # Deprecated Code
        # ---------------
        # print(f'Triangles added using numpy with time: {time.time() - initial}')
        #
        # initial = time.time()
        #
        # index_array = np.array(self.__indices)
        # index_array = index_array.reshape((-1, 3))
        #
        # for index in range(len(index_array)):
        #     triangle = index_array[index]
        #     if self.__is_triangle_inside_zone(triangle, left_coordinate, right_coordinate, top_coordinate,
        #                                       bottom_coordinate):
        #         to_delete.append(index)
        # print(f'Triangles added with time: {time.time() - initial}')

        log.debug(f"Triangles to delete added: {len(to_delete)}")

        # Add triangles to delete to the list of the model
        # ------------------------------------------------
        log.debug('Concatenating arrays')
        self.__triangles_to_delete = np.concatenate((self.__triangles_to_delete, to_delete))
        log.debug('Ended concatenating arrays')

    def __generate_index_list(self,
                              step_x: int,
                              step_y: int,
                              left_coordinate: float = -180,
                              right_coordinate: float = 180,
                              top_coordinate: float = 90,
                              bottom_coordinate: float = -90) -> np.ndarray:
        """
        Generate an index list given an already loaded list of vertices. Method use the list of vertices
        stored in the self.__vertices variable.

        Vertices are expected to be given as in the output of the __generate_vertices_list method.

        The coordinates values are used to generate the index of just a part of the total of the vertices.

        Args:
            left_coordinate: Left coordinate to cut the map.
            right_coordinate: Right coordinate to cut the map.
            top_coordinate: Top coordinate to cut the map.
            bottom_coordinate: Bottom coordinate to cut the map.
            step_x: Number of vertices in the x axis
            step_y: Number of elements in the y axis

        Returns: List of index
        """

        step_x = max(1, step_x)
        step_y = max(1, step_y)

        # Get the index of the vertices to generate the indexes
        # -----------------------------------------------------
        index_minimum_x = self.__get_index_closest_value(self.__x, left_coordinate)
        index_maximum_x = self.__get_index_closest_value(self.__x, right_coordinate)
        index_minimum_y = self.__get_index_closest_value(self.__y, bottom_coordinate)
        index_maximum_y = self.__get_index_closest_value(self.__y, top_coordinate)

        # Sort the result from the calculus
        # ---------------------------------
        new_index_minimum_y = min(index_maximum_y, index_minimum_y)
        new_index_maximum_y = max(index_maximum_y, index_minimum_y)
        new_index_maximum_x = max(index_maximum_x, index_minimum_x)
        new_index_minimum_x = min(index_maximum_x, index_minimum_x)

        # Assign the correct values to the variables
        # ------------------------------------------
        index_minimum_y = new_index_minimum_y
        index_maximum_y = new_index_maximum_y
        index_maximum_x = new_index_maximum_x
        index_minimum_x = new_index_minimum_x

        log.debug(f"index_minimum_x: {index_minimum_x}")
        log.debug(f"index_maximum_x: {index_maximum_x}")
        log.debug(f"index_minimum_y: {index_minimum_y}")
        log.debug(f"index_maximum_y: {index_maximum_y}")
        log.debug(f"len x {len(self.__x)}")
        log.debug(f"len y {len(self.__y)}")

        # calculate the indices to add to the program using numpy
        # -------------------------------------------------------
        rows = range(len(self.__y))[index_minimum_y:index_maximum_y + 1:step_y]
        cols = range(len(self.__x))[index_minimum_x:index_maximum_x + 1:step_x]
        len_rows = len(rows)
        len_cols = len(cols)

        rows = np.tile(np.array(rows), (len_cols, 1)).transpose()
        cols = np.tile(np.array(cols), (len_rows, 1))

        other_cols = cols[:-1, :-1]
        other_rows = rows[:-1, :-1]

        # first part of the triangles
        # ---------------------------

        # noinspection PyTypeChecker
        index_1: np.ndarray = self.__get_vertex_index(other_cols, other_rows)
        # noinspection PyTypeChecker
        index_2: np.ndarray = self.__get_vertex_index(other_cols + step_x, other_rows)
        # noinspection PyTypeChecker
        index_3: np.ndarray = self.__get_vertex_index(other_cols, other_rows + step_y)

        index_1 = index_1.reshape(-1)
        index_2 = index_2.reshape(-1)
        index_3 = index_3.reshape(-1)

        # second part of the triangles
        # ---------------------------
        # noinspection PyTypeChecker
        index_4: np.ndarray = self.__get_vertex_index(other_cols + step_x, other_rows)
        # noinspection PyTypeChecker
        index_5: np.ndarray = self.__get_vertex_index(other_cols + step_x, other_rows + step_y)
        # noinspection PyTypeChecker
        index_6: np.ndarray = self.__get_vertex_index(other_cols, other_rows + step_y)

        index_4 = index_4.reshape(-1)
        index_5 = index_5.reshape(-1)
        index_6 = index_6.reshape(-1)

        # add the indices
        # ---------------
        # DEPRECATED CODE
        # for ind in range(len(index_1)):
        #     indices.append(index_1[ind])
        #     indices.append(index_2[ind])
        #     indices.append(index_3[ind])
        #     indices.append(index_4[ind])
        #     indices.append(index_5[ind])
        #     indices.append(index_6[ind])

        log.debug('Joining indices calculated into one array')
        indices = np.zeros((len(index_1), 6))
        indices[:, 0] = index_1
        indices[:, 1] = index_2
        indices[:, 2] = index_3
        indices[:, 3] = index_4
        indices[:, 4] = index_5
        indices[:, 5] = index_6
        indices = indices.reshape(-1).astype(np.uint32)

        # Deprecated Code
        # ---------------
        # import time
        # time_before = time.time()
        #
        # for row in range(len(self.__y))[index_minimum_y:index_maximum_y + 1:step_y]:
        #     for col in range(len(self.__x))[index_minimum_x:index_maximum_x + 1:step_x]:
        #         if col + step_x < len(self.__x) and row + step_y < len(self.__y):
        #             indices.append(self.__get_vertex_index(col, row))
        #             indices.append(self.__get_vertex_index(col + step_x, row))
        #             indices.append(self.__get_vertex_index(col, row + step_y))
        #
        #             indices.append(self.__get_vertex_index(col + step_x, row))
        #             indices.append(self.__get_vertex_index(col + step_x, row + step_y))
        #             indices.append(self.__get_vertex_index(col, row + step_y))
        #             pass
        #
        # print(f'Duration of indices: {time.time() - time_before}')

        return indices

    def __generate_vertices_list(self, x: np.ndarray, y: np.ndarray, z: np.ndarray, z_value: int = 0) -> np.ndarray:
        """
        Generate a list of vertices given the data of a 3D grid.
        The z value of the vertices is set to 0.

        Args:
            x: X-axis values
            y: Y-axis values
            z: Height values

        Returns: List with the vertices.
        """

        # log.debug('Old for cycle')
        # vertices = []
        # for row_index in range(len(z)):
        #     for col_index in range(len(z[0])):
        #         vertices.append(x[col_index])
        #         vertices.append(y[row_index])
        #         vertices.append(z_value)
        # log.debug('End of old for cycle')

        log.debug('Creating array of vertices...')
        x = np.tile(x, (z.shape[0], 1))
        y = np.tile(y, (z.shape[1], 1))
        y = y.transpose()

        vertices = np.zeros((z.shape[0], z.shape[1], 3))
        vertices[:, :, 0] = x
        vertices[:, :, 1] = y
        vertices[:, :, 2] = z_value
        vertices = vertices.reshape(-1)
        log.debug('End of creation array of vertices')
        return vertices

    # noinspection PyUnresolvedReferences
    def __get_index_closest_value(self, list_to_evaluate: list, value: float) -> 'ndarray[int]':
        """
        Get the index of the closest element in the array to the value.

        Args:
            list_to_evaluate: List with numeric elements
            value: Value to search for

        Returns: Index of the closest value in the array.
        """
        return np.argmin(np.abs(np.array(list_to_evaluate) - value))

    def __get_vertex_index(self, x_pos: int, y_pos: int) -> int:
        """
        Get the vertex index in the buffer given the x and y position.

        The positions are given as in a cartesian plane.
        The 0,0 exist.

        Args:
            x_pos: Position X of the vertex
            y_pos: Position Y of the vertex

        Returns: Index of the vertex in the buffer.
        """
        return y_pos * len(self.__x) + x_pos

    def __is_triangle_inside_zone(self,
                                  index_triangle: list,
                                  left_coordinate: float,
                                  right_coordinate: float,
                                  top_coordinate: float,
                                  bottom_coordinate: float) -> bool:
        """
        Checks if a triangle is contained inside a certain zone given their indices.

        Args:
            index_triangle: Indices of the vertices of the triangle. List of 3 elements.
            left_coordinate: Left coordinate to check
            right_coordinate: Right coordinate to check
            top_coordinate: Top coordinate to check
            bottom_coordinate: Bottom coordinate to check

        Returns: Boolean indicating if the triangle is contained in the zone.
        """
        # Check the vertices given the indices
        # :::: Remember that vertices are composed of 3 values, thus, we need to
        # :::: multiply the index value by 3
        # ---------------------------------------------------------------------
        for coordinate in index_triangle:
            if self.__vertices[coordinate * 3] < left_coordinate or \
                    self.__vertices[coordinate * 3] > right_coordinate or \
                    self.__vertices[coordinate * 3 + 1] < bottom_coordinate or \
                    self.__vertices[coordinate * 3 + 1] > top_coordinate:
                return False

        # Return true if triangle is inside
        # ---------------------------------
        return True

    def __print_indices(self) -> None:
        """
        Print the indices of the model.
        Returns: None
        """

        for i in range(int(len(self.__indices) / 3)):
            print(f"I{i}: " + "".join(str(self.__indices[i * 3:(i + 1) * 3])))

    def __print_vertices(self) -> None:
        """
        Print the vertices of the model.
        Returns: None
        """
        print(f"Total Vertices: {len(self.__vertices)}")
        for i in range(int(len(self.__vertices) / 3)):
            print(f"P{i}: " + "".join(str(self.__vertices[i * 3:(i + 1) * 3])))

    def __set_height_buffer(self) -> None:
        """
        Set the buffer object for the heights to be used in the shaders.

        IMPORTANT:
            Uses the index 1 of the attributes pointers.

        Returns: None

        """
        height = np.array(self.__height_array, dtype=np.float32)

        # Set the buffer data in the buffer
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.hbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        len(height) * self.scene.get_float_bytes(),
                        height,
                        GL.GL_STATIC_DRAW)

        # Enable the data to the shaders
        GL.glVertexAttribPointer(1, 1, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(1)

        return

    def _update_uniforms(self) -> None:
        """
        Update the uniforms in the model.

        Set the maximum and minimum height of the vertices.
        Returns: None
        """
        # get the location
        max_height_location = GL.glGetUniformLocation(self.shader_program, "max_height")
        min_height_location = GL.glGetUniformLocation(self.shader_program, "min_height")
        projection_location = GL.glGetUniformLocation(self.shader_program, "projection")

        # set the value
        GL.glUniform1f(max_height_location, float(self.__max_height))
        GL.glUniform1f(min_height_location, float(self.__min_height))
        GL.glUniformMatrix4fv(projection_location, 1, GL.GL_TRUE, self.__projection)

        # set colors if using
        if self.__color_file is not None:
            colors_location = GL.glGetUniformLocation(self.shader_program, "colors")
            height_color_location = GL.glGetUniformLocation(self.shader_program, "height_color")
            length_location = GL.glGetUniformLocation(self.shader_program, "length")

            GL.glUniform3fv(colors_location, len(self.__colors), self.__colors)
            GL.glUniform1fv(height_color_location, len(self.__height_limit), self.__height_limit)
            GL.glUniform1i(length_location, len(self.__colors))

    def calculate_projection_matrix(self, scene_data: dict, zoom_level: float = 1) -> None:
        """
        Set the projection matrix to show the model in the scene.
        Must be called before drawing.

        The projection matrix is in charge of cutting what things fit and what dont fit on the scene.

        Args:
            scene_data: Height and width of the scene.
            zoom_level: level of zoom in the scene.

        Returns: None
        """
        log.debug("Changing the projection matrix")
        width = scene_data['SCENE_WIDTH_X']
        height = scene_data['SCENE_HEIGHT_Y']
        proportion_panoramic = width / float(height)
        proportion_portrait = height / float(width)

        min_x = min(self.__x)
        max_x = max(self.__x)
        min_y = min(self.__y)
        max_y = max(self.__y)
        log.debug(f"Model measures: X: {min_x} - {max_x} Y: {min_y} - {max_y}")

        x_width = max_x - min_x
        y_height = max_y - min_y

        # CASE PANORAMIC DATA
        # -------------------
        if x_width > y_height:
            calculated_height_viewport = x_width / proportion_panoramic

            projection_min_y = (max_y + min_y) / 2 - calculated_height_viewport / 2
            projection_max_y = (max_y + min_y) / 2 + calculated_height_viewport / 2

            zoom_difference_x = (x_width - (x_width / zoom_level)) / 2
            zoom_difference_y = (calculated_height_viewport - (calculated_height_viewport / zoom_level)) / 2

            log.debug(f"Calculated height viewport: {calculated_height_viewport}")
            log.debug(f"Zoom differences: x:{zoom_difference_x} y:{zoom_difference_y}")

            self.__left_coordinate = min_x + zoom_difference_x
            self.__right_coordinate = max_x - zoom_difference_x
            self.__bottom_coordinate = projection_min_y + zoom_difference_y
            self.__top_coordinate = projection_max_y - zoom_difference_y

        # CASE PORTRAIT DATA
        # -------------------
        else:
            calculated_width_viewport = y_height / proportion_portrait

            projection_min_x = (max_x + min_x) / 2 - calculated_width_viewport / 2
            projection_max_x = (max_x + min_x) / 2 + calculated_width_viewport / 2

            zoom_difference_y = (y_height - (y_height / zoom_level)) / 2
            zoom_difference_x = (calculated_width_viewport - (calculated_width_viewport / zoom_level)) / 2

            self.__left_coordinate = projection_min_x + zoom_difference_x
            self.__right_coordinate = projection_max_x - zoom_difference_x
            self.__bottom_coordinate = min_y + zoom_difference_y
            self.__top_coordinate = max_y - zoom_difference_y

        self.__left_coordinate -= self.position[0]
        self.__right_coordinate -= self.position[0]
        self.__top_coordinate -= self.position[1]
        self.__bottom_coordinate -= self.position[1]

        self.__projection = ortho(self.__left_coordinate,
                                  self.__right_coordinate,
                                  self.__bottom_coordinate,
                                  self.__top_coordinate,
                                  -1,
                                  1)

    def get_height_array(self) -> np.ndarray:
        """
        Get the array used to set the height buffer in the object.

        Returns: numpy array with the values of the buffer.
        """
        return self.__height_array

    def get_projection_matrix(self) -> 'np.array':
        """
        Get the projection matrix being used by the model.

        Returns: Projection matrix being used by the model
        """
        return self.__projection

    def get_showed_limits(self) -> dict:
        """
        Get a dictionary with the limits of the model being showed on the screen.

        Returns: Dictionary with the limits showing on the scene
        """
        return {
            'left': self.__left_coordinate,
            'right': self.__right_coordinate,
            'top': self.__top_coordinate,
            'bottom': self.__bottom_coordinate
        }

    def get_vertices_shape(self) -> tuple:
        """
        get the shape of the vertices of the model.

        Returns: Tuple with the shape of the vertices.
        """
        return len(self.__y), len(self.__x), 3

    def move(self, x_movement: int, y_movement: int) -> None:
        """
        Move the model view on the scene changing the projection matrix used.

        Args:
            x_movement: Movement in the x-axis
            y_movement: Movement in the y-axis

        Returns: None
        """

        width_scene = self.scene.get_scene_setting_data()['SCENE_WIDTH_X']
        height_scene = self.scene.get_scene_setting_data()['SCENE_HEIGHT_Y']

        self.position[0] += (x_movement * (self.__right_coordinate - self.__left_coordinate)) / width_scene
        self.position[1] += (y_movement * (self.__top_coordinate - self.__bottom_coordinate)) / height_scene

        # tell the program our new position
        self.scene.set_map_position(self.position)

        # recalculate projection matrix
        self.calculate_projection_matrix(self.scene.get_scene_setting_data(), self.scene.get_zoom_level())

    def optimize_gpu_memory_async(self, then: callable) -> None:
        """
        Optimize the memory allocated in the GPU deleting the triangles stored in the
        list self.__triangles_to_delete.

        The triangles on the list are the ones that are bellow another triangle rendered after them (this is,
        the triangles that overlap with other triangles rendered over them).

        Args:
            then: Routine to execute after the deleting.

        Returns: None
        """
        log.debug("Optimizing gpu memory of the model deleting triangles")

        # noinspection PyMissingOrEmptyDocstring
        def parallel_routine():
            # Delete the triangles from the list
            log.debug("Deleting repeated triangles")
            self.__triangles_to_delete = list(set(self.__triangles_to_delete))

            log.debug("Generating list of indices")

            triangles_array = np.array(self.__triangles_to_delete)
            vertex_1 = triangles_array * 3
            vertex_2 = triangles_array * 3 + 1
            vertex_3 = triangles_array * 3 + 2

            indices_to_delete = np.concatenate((vertex_1, vertex_2, vertex_3)).astype(int)

            # deprecated code
            # ---------------
            # indices_to_delete = []
            # for index_to_delete in self.__triangles_to_delete:
            #     indices_to_delete.append(index_to_delete * 3)
            #     indices_to_delete.append(index_to_delete * 3 + 1)
            #     indices_to_delete.append(index_to_delete * 3 + 2)

            log.debug("Generating mask for the indices")
            mask = np.ones(len(self.__indices), dtype=bool)
            mask[indices_to_delete] = False

            log.debug("Applying mask to the indices")

            # Deprecated code
            # arr_indices = np.array(self.__indices)  # time consuming (must optimize)
            # new_indices = arr_indices[mask]
            # self.__indices = new_indices.tolist()  # time consuming (must optimize)

            # noinspection PyTypeChecker
            self.__indices = self.__indices[mask]
            log.debug('Ended applying mask to indices')

            self.__triangles_to_delete = np.array([])

        # noinspection PyMissingOrEmptyDocstring
        def then_routine():
            # Set the new vertices on the engine
            self.set_indices(np.array(self.__indices, dtype=np.uint32))
            then()

        self.scene.set_thread_task(parallel_task=parallel_routine, then=then_routine)

    def recalculate_vertices_from_grid_async(self, quality: int = 2, then=lambda: None) -> None:
        """
        Recalculate vertices from grid.

        Recalculate the vertices with a new definition given the zoom level and the borders used in the
        projection matrix.

        Returns: None

        Args:
            then: Routine to execute after the parallel tasks.
            quality: quality of the rendering process.
        """
        self.__new_indices = None

        # noinspection PyMissingOrEmptyDocstring
        def parallel_tasks():
            log.debug("Coordinates actually showing on the screen:")
            log.debug(f"left: {self.__left_coordinate}")
            log.debug(f"right: {self.__right_coordinate}")
            log.debug(f"top:{self.__top_coordinate} ")
            log.debug(f"bottom: {self.__bottom_coordinate}")

            # Calculate the definition to use in the reload
            # ---------------------------------------------
            elements_on_screen_x = abs(self.__get_index_closest_value(self.__x, self.__right_coordinate) -
                                       self.__get_index_closest_value(self.__x, self.__left_coordinate))
            elements_on_screen_y = abs(self.__get_index_closest_value(self.__y, self.__top_coordinate) -
                                       self.__get_index_closest_value(self.__y, self.__bottom_coordinate))

            log.debug(f"Number of vertices on screen axis X: {elements_on_screen_x}")
            log.debug(f"Number of vertices on screen axis Y: {elements_on_screen_y}")

            scene_data = self.scene.get_scene_setting_data()
            step_x = int(elements_on_screen_x / scene_data['SCENE_WIDTH_X'])  # + 2
            step_y = int(elements_on_screen_y / scene_data['SCENE_HEIGHT_Y'])  # + 2

            log.debug(f"Step used to generate index list on x axis {step_x}")
            log.debug(f"Step used to generate index list on y axis {step_y}")

            # Generate new list of triangles to add to the model
            # --------------------------------------------------
            self.scene.set_loading_message("Generating new indices...")
            self.__new_indices = self.__generate_index_list(step_x + quality,
                                                            step_y + quality,
                                                            self.__left_coordinate,
                                                            self.__right_coordinate,
                                                            self.__top_coordinate,
                                                            self.__bottom_coordinate)

            # Delete old triangles that are in the same place as the new ones
            # ---------------------------------------------------------------
            self.scene.set_loading_message("Recalculating triangles...")
            self.__add_triangles_inside_zone_to_delete_list(self.__left_coordinate,
                                                            self.__right_coordinate,
                                                            self.__top_coordinate,
                                                            self.__bottom_coordinate)

        # noinspection PyMissingOrEmptyDocstring
        def then_routine():
            # Set the new indices
            # -------------------
            self.__indices = np.concatenate((self.__indices, self.__new_indices))
            self.set_indices(np.array(self.__indices, dtype=np.uint32))

            # call the then routine
            then()

        self.scene.set_thread_task(parallel_tasks, then_routine)

    def set_color_file(self, filename: str) -> None:
        """

        Args:
            filename: File to use for the colors.

        Returns: None

        """
        log.debug('Setting colors from file')
        if len(self.__vertices) == 0:
            raise AssertionError('Did you forget to set the vertices? (set_vertices_from_grid)')

        # set the shaders
        self.set_shaders('./engine/shaders/model_2d_colors_vertex.glsl',
                         './engine/shaders/model_2d_colors_fragment.glsl')
        self.__color_file = filename

        file_data = read_file(filename)
        colors = []
        height_limit = []

        for element in file_data:
            colors.append(element['color'])
            height_limit.append(element['height'])

        # send error in case too many colors are passed
        if len(colors) > 500:
            raise BufferError('Shader used does not support more than 500 colors in the file.')

        self.__colors = np.array(colors, dtype=np.float32)
        self.__height_limit = np.array(height_limit, dtype=np.float32)

    def set_height_buffer(self, new_height: np.ndarray) -> None:
        """
        Change the values of the height buffer.

        Args:
            new_height: Numpy array with the new height values.

        Returns: None
        """

        self.__height_array = new_height.reshape(-1)
        self.__max_height = np.nanmax(self.__height_array)
        self.__min_height = np.nanmin(self.__height_array)
        self.__set_height_buffer()

    def set_vertices_from_grid_async(self, x, y, z, quality=1, then=lambda: None) -> None:
        """
        Set the vertices of the model from a grid.

        This method:
         - Store in the class variables the original values of the grid loaded.
         - Set the vertices of the model after applying a decimation algorithm over them to reduce the number
           of vertices to render.
         - Set the height buffer with the height of the vertices.

        Args:
            then: Task too do after the thread execution
            quality: Quality of the grid to render. 1 for max quality, 2 or more for less quality.
            x: X values of the grid to use.
            y: Y values of the grid.
            z: Z values of the grid.

        Returns: None

        """

        # store the data for future operations.
        self.__x = x
        self.__y = y
        self.__z = z

        def parallel_routine():
            """
            Routine to be executed in parallel
            """

            # Set the vertices in the buffer
            log.debug("Loading buffers")
            self.scene.set_loading_message("Loading vertices...")
            self.__vertices = self.__generate_vertices_list(x, y, z)

            log.debug("Generating Indices")
            self.scene.set_loading_message("Generating polygons...")
            scene_data = self.scene.get_scene_setting_data()
            self.__indices = self.__generate_index_list(int(len(self.__x) / scene_data['SCENE_WIDTH_X']) + quality,
                                                        int(len(self.__y) / scene_data['SCENE_HEIGHT_Y']) + quality)

            self.scene.set_loading_message("Drawing model on screen...")

        def then_routine():
            """
            Routine to be executed after the parallel routine
            """
            self.set_vertices(
                np.array(
                    self.__vertices,
                    dtype=np.float32,
                )
            )
            self.set_indices(np.array(self.__indices, dtype=np.uint32))

            # Only select this shader if there is no shader selected.
            if self.shader_program is None:
                self.set_shaders(
                    "./engine/shaders/model_2d_vertex.glsl", "./engine/shaders/model_2d_fragment.glsl"
                )

            # set the height buffer for rendering and store height values
            self.set_height_buffer(np.array(z))

            # call the then routine
            then()

        self.scene.set_thread_task(parallel_routine, then_routine)
