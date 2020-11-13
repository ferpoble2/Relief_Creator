#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in float height;

uniform float max_height;
uniform float min_height;
uniform mat4 projection;

out float height_value;
out float max_height_value;
out float min_height_value;

void main()
{
    height_value = height;
    max_height_value = max_height;
    min_height_value = min_height;

    gl_Position = projection * vec4(position, 1.0f);
}