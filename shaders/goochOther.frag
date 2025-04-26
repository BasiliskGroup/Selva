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

uniform vec3 cameraPosition;
const int    maxDirLights = 5;
uniform      DirectionalLight dirLights[maxDirLights];
uniform int  numDirLights;
uniform      textArray textureArrays[5];

// Gooch Parameters
const float b     = 0.4;
const float y     = 0.4;
const float alpha = 0.2;
const float beta  = 0.6;

const vec3 k_blue   = vec3(0.0, 0.0, b  );
const vec3 k_yellow = vec3(y  , y  , 0.0);


// Theory from Amy Gooch's 1998 paper: https://users.cs.northwestern.edu/~ago820/SIG98/gooch98.pdf
LightResult GoochLight(DirectionalLight light, Material mtl, vec3 albedo, vec3 N, vec3 V) {

    LightResult result;

    vec3 L = normalize(-light.direction);  // light direction
    vec3 H = normalize(L + V);             // half vector
    float cos_theta_l = clamp(dot(N, L), 0.0, 1.0);
    float ndoth = dot(N, H);

    // Gooch calculations using expanded lambertian
    vec3 k_cool = k_blue + alpha * albedo;
    vec3 k_warm = k_yellow + beta  * albedo;
    float diff = (0.5 + dot(N, L) / 2.0);

    result.diffuse  = diff * k_warm + (1 - diff) * k_cool;
    result.specular = clamp(vec3(pow(ndoth, 32) * cos_theta_l), 0.0, 1.0) / 3.0;

    return result;
}

vec3 getAlbedo(Material mtl, vec2 uv, float gamma) {
    vec3 albedo = mtl.color;
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
    vec3 viewDir = vec3(normalize(cameraPosition - position));

    // Get lighting vectors
    vec3 albedo = getAlbedo(mtl, uv, gamma);
    vec3 normal = getNormal(mtl, TBN);

    // Lighting variables
    vec3 N = normalize(normal);                     // normal
    vec3 V = normalize(cameraPosition - position);  // view vector

    LightResult lightResult;
    lightResult.diffuse  = vec3(0.0);
    lightResult.specular = vec3(0.0);

    // Add result from each directional light in the scene
    for (int i = 0; i < numDirLights; i++) {
        // Caculate the light for the directional light
        LightResult dirLightResult = GoochLight(dirLights[i], mtl, albedo, N, V);
        vec3 lightFactor = dirLights[i].intensity * dirLights[i].color;
        // Add each lobe
        lightResult.diffuse  += dirLightResult.diffuse  * lightFactor;
        lightResult.specular += dirLightResult.specular * lightFactor;
    }

    // Output fragment color
    vec3 finalColor = min(lightResult.diffuse + lightResult.specular, 1.0);

    // No bloom currently
    float brightness = dot(finalColor, vec3(0.2126, 0.7152, 0.0722)) + dot(mtl.emissiveColor, vec3(1));
    fragColor = vec4(finalColor + mtl.emissiveColor, 1.0);

    // Filter out bright pixels for bloom
    bloomColor = vec4(albedo / 20 / brightness, 1.0);
    normalTexture = vec4(abs(N), 1.0);
}