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

out vec4 outColor;

flat in vec3 startPos;
in vec3 vertPos;

// Color of the line
uniform vec4 lines_color;

// Uniforms that store data for the dashed logic
uniform vec2  u_resolution;
uniform float u_dashSize;
uniform float u_gapSize;

void main()
{
    // Calcualte the direction and the distance of the line to be drawed
    vec2  dir  = (vertPos.xy-startPos.xy) * u_resolution/2.0;
    float dist = length(dir);

    // Discard fragments to create the effect of the dashed line
    if (fract(dist / (u_dashSize + u_gapSize)) > u_dashSize/(u_dashSize + u_gapSize)){
        discard;
    }

    outColor = vec4(lines_color);
}