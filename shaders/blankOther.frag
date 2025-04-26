#version 330 core

layout (location = 0) out vec4 fragColor;
layout (location = 1) out vec4 bloomColor;
layout (location = 2) out vec4 normalTexture;


// Structs needed for the shader
struct textArray {
    sampler2DArray array;
};

struct DirectionalLight {
    vec3 direction;
    float intensity;
    vec3 color;
    float ambient;
};  

// Material struct sent to fragment shader
struct Material {
    vec3  color;
    vec3  emissiveColor;
    float roughness;
    float subsurface;
    float sheen;
    float sheenTint;
    float anisotropic;
    float specular;
    float metallicness;
    float specularTint;
    float clearcoat;
    float clearcoatGloss;
    
    int   hasAlbedoMap;
    vec2  albedoMap;
    int   hasNormalMap;
    vec2  normalMap;
    int   hasRoughnessMap;
    vec2  roughnessMap;
    int   hasAoMap;
    vec2  aoMap;
};

struct LightResult {
    vec3 diffuse;
    vec3 specular;
};

in vec2 uv;
in vec3 position;
in mat3 TBN;

// Material attributes
flat in Material mtl;

// Uniforms
uniform vec2 viewportDimensions;
uniform sampler2D depthTexture;

uniform      textArray textureArrays[5];


vec3 getAlbedo(Material mtl, vec2 uv, float gamma) {
    vec3 albedo = vec3(1.0);
    if (bool(mtl.hasAlbedoMap)){
        albedo *= pow(texture(textureArrays[int(round(mtl.albedoMap.x))].array, vec3(uv, round(mtl.albedoMap.y))).rgb, vec3(gamma));
    }
    return albedo;
}

vec3 getNormal(Material mtl, mat3 TBN){
    // Isolate the normal vector from the TBN basis
    vec3 normal = TBN[2];
    // Apply normal map if the material has one
    if (bool(mtl.hasNormalMap)) {
        normal = texture(textureArrays[int(round(mtl.normalMap.x))].array, vec3(uv, round(mtl.normalMap.y))).rgb * 2.0 - 1.0;
        normal = normalize(TBN * normal); 
    }
    // Return vector
    return normal;
}

void main() {
    vec2 screenuv = (gl_FragCoord.xy) / viewportDimensions;
    float portalDepth = texture(depthTexture, screenuv).r;
    float fragDepth = gl_FragCoord.z;

    if (fragDepth < portalDepth) {
        fragColor = vec4(0.0, 0.0, 0.0, 0.0);
        discard;
    }

    float gamma = 2.2;

    // Get lighting vectors
    vec3 albedo = getAlbedo(mtl, uv, gamma);
    vec3 normal = getNormal(mtl, TBN);

    // Lighting variables
    vec3 N = normalize(normal);                     // normal

    fragColor = vec4(albedo, 1.0);
    bloomColor = vec4(0.0);
    normalTexture = vec4(abs(N), 1.0);
}