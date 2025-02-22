import glm
from basilisk import Node, Scene


class RoomItem():
    
    def __init__(self, scene: Scene, node: Node) -> None:
        self.scene = scene
        self.node = node
        self.room_position = glm.vec3(*self.node.position)
        self.room_rotation = glm.quat(*self.node.rotation)
    