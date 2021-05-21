#version 330 core

in float height_value;
in float max_height_value;
in float min_height_value;

uniform int length;
uniform float height_color[500];
uniform vec3 colors[500];

out vec4 outColor;

void main()
{
    vec3 color;
    float intepolation_height;

    if (height_value < height_color[0]){
        color = colors[0];
    }

    if (height_value > height_color[length - 1]){
        color = colors[length - 1];
    }

    for (int index = 0; index < length - 1; index++){
        if (height_value >= height_color[index] && height_value < height_color[index + 1]){
            intepolation_height = (height_value - height_color[index])/(height_color[index+1] - height_color[index]);
            color = (colors[index]*(1 - intepolation_height) + colors[index + 1]*(intepolation_height))/255;
            break;
        }
    }

    outColor = vec4(color, 1);
}
