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

in float height_value;
in float max_height_value;
in float min_height_value;

out vec4 outColor;

void main()
{
    float color = (height_value - min_height_value)/(max_height_value - min_height_value);
    outColor = vec4(clamp(vec3(color, color, color), 0.0, 1.0), 1);
}