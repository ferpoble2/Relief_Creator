#version 330 core

layout (location = 0) in vec3 position;

flat out vec3 startPos;
out vec3 vertPos;

uniform mat4 projection;

void main()
{
    vec4 pos = projection * vec4(position, 1.0f);
    vertPos     = pos.xyz / pos.w;
    startPos    = vertPos;
    gl_Position = pos;
}