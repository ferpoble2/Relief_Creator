#version 330 core

layout (location = 0) in vec3 position;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

out vec4 newColor;

void main()
{
//    gl_Position = projection * view * model * vec4(position, 1.0f);
    gl_Position = projection * view * model * vec4(position, 1);
    newColor = vec4(1, 0, 0, 1);
}