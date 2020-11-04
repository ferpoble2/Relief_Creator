#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in float height;

uniform float max_height;
uniform float min_height;

out vec4 color;

void main()
{

    float R = (height - min_height)/(max_height - min_height);

    color = vec4(clamp(vec3(R, R, R), 0.0, 1.0), 1);

    gl_Position = vec4(position, 1.0f);
}