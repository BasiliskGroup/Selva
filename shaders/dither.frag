#version 330 core

layout (location = 0) out vec4 fragColor;


in vec2 uv;

uniform sampler2D screenTexture;
uniform vec2 textureSize;

const int n = 4;
const float s = 0.025;
mat4 bayerDither = mat4 (
    0, 8, 2, 10,
    12, 4, 14, 6,
    3, 11, 1, 9,
    15, 7, 13, 5
);

const int buckets = 16;

void main() {
    vec4 color = texture(screenTexture, uv);

    vec2 position = uv * textureSize;
    position = mod(position, n);
    float M = bayerDither[int(position.x)][int(position.y)] / (n * n) - 0.5;

    vec3 quantized = floor((color.rgb + s * M) * buckets) / buckets;

    fragColor = vec4(quantized, 1.0);
}