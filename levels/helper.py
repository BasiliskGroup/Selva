import glm
from basilisk import Node, Material, Shader
import random
    
def rect_room(centerx: float, centerz: float, width: float, depth: float, height: float, floor_material: Material=None, wall_material: Material=None, ceil_material: Material=None, shader: Shader=None) -> list[Node]:
    nodes = [Node(
        position = (data[0], height - 0.5, data[1]), 
        scale = (data[2], height, data[3]),
        collision = True,
        static = True,
        material = wall_material,
        shader = shader
    ) for data in (
        (centerx + width, centerz, 1, depth), 
        (centerx - width, centerz, 1, depth), 
        (centerx, centerz + depth, width, 1), 
        (centerx, centerz - depth, width, 1)
    )]
    
    nodes += [Node(
        scale = (width - 1, 1, depth - 1),
        collision = True,
        position=(centerx, y, centerz),
        material = floor_material if y == -1 else ceil_material,
        shader = shader
    ) for y in (-1, height * 2)]
    return nodes