#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv;

uniform sampler2D mainTexture;
uniform sampler2D portalTexture;
uniform sampler2D mainDepthTexture;
uniform sampler2D portalDepthTexture;

void main()
{ 
    vec3 mainColor    = texture(mainTexture, uv       ).rgb;
    vec3 portalColor  = texture(portalTexture, uv     ).rgb;
    float mainDepth   = texture(mainDepthTexture, uv  ).r;
    float portalDepth = texture(portalDepthTexture, uv).r;

    if (mainDepth < portalDepth) {
        fragColor = vec4(mainColor, 1.0);
    }
    else {
        fragColor = vec4(portalColor, 1.0);
    }
}