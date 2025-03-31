import glm
from basilisk import Node
from typing import Callable, Any
from helper.type_hints import Game, Level


class HeldItem():
    
    def __init__(self, game: Game, node: Node, func: Callable=None, offset: glm.vec3=None, rotation: glm.quat=None, **kwargs) -> None:
        self.game = game
        self.node = node # NOTE never added to the scnee, only used to store data like material, mesh, and scale
        self.func = func
        self.offset = glm.vec3(offset) if offset else glm.vec3() # camera right, up, forward
        self.rotation = glm.quat(rotation) if rotation else glm.quat()
        
        # allows the user to set arguments of any type they want
        for key, value in kwargs.items(): setattr(self, str(key), value)
        
    
class PictureFrame(HeldItem):
    
    def __init__(self, game: Game, level: Level):
        # Information for creating portals
        self.level = level
        
        # variables to be sent to the parent
        node = Node(
            scale = (0.2, 0.2, 0.2),
            material = game.materials['picture_frame'],
            mesh = game.meshes['picture_frame']
        )
        super().__init__(game, node, self.func, rotation = glm.angleAxis(glm.pi(), (0, 1, 0)))
        
        # ANIMATION variables
        self.percent_moved = 0
        self.ANIMATION_TIME = 0.5
        
        self.original_offset = glm.vec3(self.offset) # left hand offset (-0.45, -0.25, 1.2)
        self.original_rotation = glm.quat(self.rotation)
        self.final_offset = glm.vec3(0, 0, 0.3) - glm.vec3(-0.45, -0.25, 1.2)
        self.final_rotation = glm.quat(self.rotation)
        
    def func(self, dt: float) -> None:
        """
        Mouse Left Down - holds the frame in front of the user for a short period of time, shakes, plays portal opening sound effect, and opens a portal
        Mouse Left Up - moves the frame back to starting position
        """
        # play ANIMATION and store lerp value
        was1 = self.percent_moved == 1
        self.percent_moved = glm.clamp(self.percent_moved + dt / self.ANIMATION_TIME * (2 * self.game.mouse.left_down - 1), 0, 1)
        self.offset = glm.mix(self.original_offset, self.final_offset, self.percent_moved)
        self.rotation = glm.slerp(self.original_rotation, self.final_rotation, self.percent_moved)
        
        # interact with current scene if ANIMATION is at it's maximum
        if self.percent_moved == 1 and not was1: print('*farts*')
        
        