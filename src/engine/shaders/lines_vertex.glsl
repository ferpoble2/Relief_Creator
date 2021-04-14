#version 330 core

layout (location = 0) in vec3 position;

uniform mat4 projection;
uniform float z_offset;

void main()
{
    gl_Position = projection * vec4(position.xy, position.z + z_offset, 1.0f);
}