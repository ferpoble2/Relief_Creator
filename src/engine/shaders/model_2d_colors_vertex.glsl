/*
* BEGIN GPL LICENSE BLOCK
*
*     This program is free software: you can redistribute it and/or modify
*     it under the terms of the GNU General Public License as published by
*     the Free Software Foundation, either version 3 of the License, or
*     (at your option) any later version.
*
*     This program is distributed in the hope that it will be useful,
*     but WITHOUT ANY WARRANTY; without even the implied warranty of
*     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*     GNU General Public License for more details.
*
*     You should have received a copy of the GNU General Public License
*     along with this program.  If not, see <https://www.gnu.org/licenses/>.
*
* END GPL LICENSE BLOCK
*/
#version 330 core

layout (location = 0) in vec3 position;

uniform mat4 projection;

out float height_value;

void main()
{
    height_value = position.z;

    // OpenGL need the coordinated to be between (-1, 1). The projection matrix is the one in charge of converting the
    // coordinates of the points to the range (-1, 1) and to keep the aspect ratio of the viewport used.
    gl_Position = projection * vec4(position, 1.0f);
}