#version 330 core

layout (location = 0) out vec4 fragColor;


in vec2 uv;

uniform sampler2D screenTexture;

const int n = 4;

vec3 palette[n] = vec3[n](
    vec3(255, 178, 0) / 255,
    vec3(235, 91, 0)  / 255,
    vec3(217, 22, 86) / 255,
    vec3(100, 13, 95) / 255
);


float grayscale(vec3 color) {
    return dot(color.rgb, vec3(0.299, 0.587, 0.114));
}

void main()
{
    vec4 color = texture(screenTexture, uv);
    float value = grayscale(color.rgb);

    fragColor = vec4(palette[n - int(floor((value) * n)) - 1], 1.0);
}