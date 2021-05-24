# BEGIN GPL LICENSE BLOCK
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# END GPL LICENSE BLOCK

"""
Files with the DashedLines class. Class is in charge of render dashed lines on the screen.
"""

from src.engine.scene.model.lines import Lines

import OpenGL.GL as GL


class DashedLines(Lines):
    """
    Class in charge of render dashed lines.
    """

    def __init__(self, scene):
        """
        Constructor of the class.

        Args:
            scene: Scene to use for rendering.
        """
        super().__init__(scene)

        self.transparency = 0.3
        self.dash_size = 10
        self.gap_size = 5

        self.__vertex_shader_file = './src/engine/shaders/dashed_lines_vertex.glsl'
        self.__fragment_shader_file = './src/engine/shaders/dashed_lines_fragment.glsl'

        line_color = self.get_line_color()
        border_color = self.get_border_color()

        self.set_line_color([line_color[0], line_color[1], line_color[2], self.transparency])
        self.set_border_color([border_color[0], border_color[1], border_color[2], self.transparency])

        self.set_shaders(self.__vertex_shader_file, self.__fragment_shader_file)

    def _update_uniforms(self) -> None:
        """
        Update the uniforms of the model

        Returns: None
        """
        super()._update_uniforms()

        u_resolution_location = GL.glGetUniformLocation(self.shader_program, "u_resolution")
        u_dashSize_location = GL.glGetUniformLocation(self.shader_program, "u_dashSize")
        u_gapSize_location = GL.glGetUniformLocation(self.shader_program, "u_gapSize")

        scene_settings = self.scene.get_scene_setting_data()
        GL.glUniform2f(u_resolution_location, scene_settings["SCENE_WIDTH_X"], scene_settings["SCENE_HEIGHT_Y"])
        GL.glUniform1f(u_dashSize_location, self.dash_size)
        GL.glUniform1f(u_gapSize_location, self.gap_size)

    def set_line_color(self, color: list) -> None:
        """
        Set the line color to draw.

        Args:
            color: Color in RGBA format.

        Returns: None
        """
        super().set_line_color([color[0], color[1], color[2], self.transparency])

    def set_border_color(self, color: list) -> None:
        """
        Set the color of the border of the line.

        Args:
            color: new color to use as border.

        Returns: None
        """
        super().set_border_color([color[0], color[1], color[2], self.transparency])
