#version 330 core

layout (location = 0) out vec4 fragColor;


in vec2 uv;

uniform sampler2D screenTexture;
uniform vec2 viewportDimensions;

const int size = 10;
const int skip = 2;


float grayscale(vec3 color) {
    return dot(color.rgb, vec3(0.299, 0.587, 0.114));
}

// Calcualte the average color of the pixels in a quadrant
vec3 quadrantMean (vec2 offset, int size) {
    vec3 total = vec3(0.0);

    for (int x = 0; x < size; x+=skip) {
        for (int y = 0; y < size; y+=skip) {
            total += texture(screenTexture, uv + vec2(x, y) * offset).rgb;
        }
    }

    total /= size * size / skip / skip;
    return total;
}

// Calcualte the standard deviation of the grayscale pixels in a quadrant
float quadrantStandardDeviation (vec3 color, vec2 offset, int size) {
    float mean = grayscale(color);

    float total = 0.0;
    for (int x = 0; x < size; x+=skip) {
        for (int y = 0; y < size; y+=skip) {
            float diff = grayscale(texture(screenTexture, uv + vec2(x, y) * offset).rgb) - mean;
            total += diff * diff;
        }
    }

    total /= size * size / skip / skip;
    total = sqrt(total);
    return total;
}


void main()
{
    vec2 offset = 1.0 / viewportDimensions;

    vec3 c1 = quadrantMean(offset * vec2( 1.0,  1.0), size);
    vec3 c2 = quadrantMean(offset * vec2(-1.0,  1.0), size);
    vec3 c3 = quadrantMean(offset * vec2( 1.0, -1.0), size);
    vec3 c4 = quadrantMean(offset * vec2(-1.0, -1.0), size);

    float q1 = quadrantStandardDeviation(c1, offset * vec2( 1.0,  1.0), size);
    float q2 = quadrantStandardDeviation(c2, offset * vec2(-1.0,  1.0), size);
    float q3 = quadrantStandardDeviation(c3, offset * vec2( 1.0, -1.0), size);
    float q4 = quadrantStandardDeviation(c4, offset * vec2(-1.0, -1.0), size);

    float smallest = min(min(q1, q2), min(q3, q4));

    vec3 color = vec3(0.0);
    if      (q1 == smallest) {color = c1;}
    else if (q2 == smallest) {color = c2;}
    else if (q3 == smallest) {color = c3;}
    else if (q4 == smallest) {color = c4;}

    fragColor = vec4(color, 1.0);
}