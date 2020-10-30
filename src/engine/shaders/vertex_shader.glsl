#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in float height;

out vec4 color;

void main()
{

    if(height < 400){
        color = vec4(1,0,0,1);
    }
    else{
        color = vec4(0,1,0,1);
    }

    gl_Position = vec4(position, 1.0f);
}