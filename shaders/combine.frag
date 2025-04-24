#version 330 core

layout (location = 0) out vec4 fragColor;

uniform vec2 viewportDimensions;
uniform sampler2D mainTexture;
uniform sampler2D portalTexture;
uniform sampler2D mainDepthTexture;
uniform sampler2D portalDepthTexture;

void main()
{ 
    vec2 uv = (gl_FragCoord.xy) / viewportDimensions;

    vec4 mainColor    = texture(mainTexture, uv       );
    vec4 portalColor  = texture(portalTexture, uv     );
    float mainDepth   = texture(mainDepthTexture, uv  ).r;
    float portalDepth = texture(portalDepthTexture, uv).r;

    if (mainDepth < portalDepth) {
        fragColor = mainColor;
    }
    else {
        fragColor = portalColor;
    }
}