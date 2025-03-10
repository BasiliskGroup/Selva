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
    scale = glm.vec3(width, width, distance / 2)
    rotation = glm.quatLookAt(direction, (0, 1, 0))
    
    return position, scale, rotation