import glm


def connect(p1: glm.vec3, p2: glm.vec3, width: float=0.02) -> tuple[glm.vec3, glm.vec3, glm.quat]:
    """
    Calculates the transformations to connect the two given points by the default cube Node
    """
    # fallback if points are equal, no line should be drawn
    if p1 == p2: return p1, glm.vec3(), glm.quat()
    
    diff = p2 - p1
    direction, distance = glm.normalize(diff), glm.length(diff)
    
    position = (p1 + p2) / 2
    scale = glm.vec3(width, distance / 2, width)
    rotation = glm.normalize(glm.angleAxis(glm.pi() / 2, (1, 0, 0)) * glm.conjugate(glm.quatLookAt(direction, (0, 1, 0))))
    
    return position, scale, rotation

def plane_mirror(point: glm.vec3, plane_point: glm.vec3, plane_normal: glm.vec3) -> glm.vec3:
    """
    Mirrors the given point along the plane 
    """
    plane_normal = glm.normalize(plane_normal)
    proj = glm.dot(plane_point - point, plane_normal) * plane_normal
    return point + 2 * proj