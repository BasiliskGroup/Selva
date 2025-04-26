import glm
from basilisk import Node, FollowCamera, Material
from typing import Callable, Any
from helper.transforms import connect
from helper.type_hints import Game, Level, Player


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
    
    def __init__(self, game: Game, level_name: str, material: Material=None, end_func: Callable=None):
        # Information for creating portals
        self.level_name = level_name
        self.portal = Node(
            scale = (1, 2.5, 0.01),
            material = game.materials['red']
        )
        
        def default_end_func() -> None: self.game.open(self.level)
        self.end_func = end_func if end_func else default_end_func
        
        # variables to be sent to the parent
        node = Node(
            scale = (0.2, 0.2, 0.2),
            material = material if material else game.materials['picture_frame'],
            mesh = game.meshes['empty_frame']
        )
        
        super().__init__(game, node, self.func, rotation = glm.angleAxis(glm.pi(), (0, 1, 0)))
        
        # ANIMATION variables
        self.percent_moved = 0
        self.ANIMATION_TIME = 0.5
        self.SPAWN_DISTANCE = 0.1
        
        self.original_offset = glm.vec3(self.offset) # left hand offset (-0.45, -0.25, 1.2)
        self.original_rotation = glm.quat(self.rotation)
        self.final_offset = glm.vec3(0, 0, 0.3) - glm.vec3(-0.7, -0.5, 1.2)
        self.final_rotation = glm.quat(self.rotation)
        
    def func(self, dt: float) -> None:
        """
        Mouse Left Down - holds the frame in front of the user for a short period of time, shakes, plays portal opening sound effect, and opens a portal
        Mouse Left Up - moves the frame back to starting position
        """
        # dynamically compute offset
        bl, tl, br, tr = self.view_corners
        blv, tlv, brv, trv = self.corner_vectors
        
        s = 0.333 / (glm.length(tl - bl) + 2 * glm.dot(tlv, self.camera.right))
        self.final_offset = -s * glm.dot(self.camera.forward, tlv) * glm.vec3(0, 0, 1) - glm.vec3(-0.7, -0.5, 1.2)
        
        # play ANIMATION and store lerp value
        was1 = self.percent_moved == 1
        was0 = self.percent_moved == 0
        self.percent_moved = glm.clamp(self.percent_moved + dt / self.ANIMATION_TIME * (2 * self.game.mouse.left_down - 1), 0, 1)
        self.offset = glm.mix(self.original_offset, self.final_offset, self.percent_moved)
        self.rotation = glm.slerp(self.original_rotation, self.final_rotation, self.percent_moved)
        
        # interact with current scene if ANIMATION is at it's maximum
        if was0 and self.percent_moved != 0: self.game.close()
        if self.percent_moved == 1 and not was1: self.end_func()
        
    @property
    def player(self) -> Player: return self.game.player
    @property
    def camera(self) -> FollowCamera: return self.game.camera
    @property
    def inv_proj(self) -> glm.mat4x4: return glm.inverse(self.camera.m_proj)
    @property
    def inv_view(self) -> glm.mat4x4: return glm.inverse(self.camera.m_view)
    @property
    def view_corners(self) -> list[glm.vec3]:
        """
        Gets the near clip plane coordinates of the camera in world space
        """
        player_corners: list[glm.vec4] = [glm.vec4(a, b, -1, 1) for a in (-1, 1) for b in (-1, 1)] # BL TL BR TR
        
        world_corners = []
        for corner in player_corners:
            view_pos = self.inv_proj * corner
            view_pos /= view_pos.w
            world_pos = self.inv_view * view_pos
            world_corners.append(glm.vec3(world_pos))
            
        return world_corners
    
    @property
    def corner_vectors(self) -> list[glm.vec3]:
        """
        Gets the vectors of the corners of the screen projects from the camera
        """
        player_corners = [glm.vec2(a, b) for a in (0, self.game.win_size.x) for b in (self.game.win_size.y, 0)]
        
        vectors = []
        for corner in player_corners:
            ndc = glm.vec4(2 * corner.x / self.game.win_size.x - 1, 1 - 2 * corner.y / self.game.win_size.y, 1, 1)
            point = self.inv_proj * ndc
            point /= point.w
            forward = glm.normalize(glm.vec3(self.inv_view * glm.vec4(point.x, point.y, point.z, 0)))
            vectors.append(forward)
            
        return vectors
    
    @property
    def level(self) -> Level: return self.game.memory_handler[self.level_name]