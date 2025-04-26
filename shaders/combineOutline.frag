#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv;

uniform sampler2D mainTexture;
uniform sampler2D outlineTexture;

void main()
{ 
    vec3 color    = texture(mainTexture, uv).rgb;
    vec3 outline  = texture(outlineTexture, uv).rgb;

    fragColor = vec4(color * outline, 1.0);
}