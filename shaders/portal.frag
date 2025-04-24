#version 330 core

layout (location = 0) out vec4 fragColor;

uniform vec2 viewportDimensions;
uniform sampler2D otherTexture;

void main()
{ 
    vec2 uv = (gl_FragCoord.xy) / viewportDimensions;

    vec4 otherColor = texture(otherTexture, uv);

    fragColor = otherColor;
}