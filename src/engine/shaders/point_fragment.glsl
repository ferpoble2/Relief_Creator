#version 330 core

in vec4 point_color;

out vec4 outColor;

void main()
{
    outColor = vec4(point_color);
}