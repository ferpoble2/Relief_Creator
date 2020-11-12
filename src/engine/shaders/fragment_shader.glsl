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