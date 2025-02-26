import glm
import basilisk as bsk
from helper.type_hints import Game, Level
from player.held_item import HeldItem, PictureFrame
from player.player_nodes import player_nodes
import time


class Player():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        
        # constant variables
        self.HEIGHT = 2 # vertical scale of the node, 1x2x1
        self.SPEED = 5 # the velocity of the player's node when moving
        self.DECELERATION_COEFFICIENT = 10
        
        # Main body used for stabilizing collisions on the camera
        self.body_node, self.held_node = player_nodes(self.game)
        self.current_scene.add(self.body_node, self.held_node)
        
        # variables for controling the player's held items
        self.items: list[HeldItem] = [PictureFrame(self.game, None)] # TODO temporary, remove item and define behavior when the user has not item
        self.held_index = 0
        
        # game interaction variables
        self.control_disabled = False
        self.camera = self.current_scene.camera = bsk.FollowCamera(self.body_node, offset = (0, 1.5, 0)) # TODO ensure that this camera is passed between scenes depending on where the player is NOTE this will act as the main player camera
        
    def update(self, dt: float) -> None:
        """
        Updates the players movement, Nodes, and controls
        """
        if not self.control_disabled: 
            # player controls
            self.move(dt)
            self.use_held_item(dt)
            self.interact(dt)
        
        # update user node to preserve direction
        horizontal_quat = glm.conjugate(glm.quat((0, self.camera.yaw, self.camera.roll)))
        self.body_node.rotation = horizontal_quat
        self.body_node.rotational_velocity = glm.vec3(0, 0, 0)
    
    def move(self, dt: float) -> None:
        """
        Controls the player movement from the input of the 
        """
        # control player movement WASD
        proposed = glm.vec3(0, 0, 0)
        proposed += self.camera.horizontal * (self.game.keys[bsk.pg.K_w] - self.game.keys[bsk.pg.K_s]) 
        proposed += self.camera.right * (self.game.keys[bsk.pg.K_d] - self.game.keys[bsk.pg.K_a])
        
        if proposed == (0, 0, 0): self.body_node.velocity *= (1 - self.DECELERATION_COEFFICIENT * dt)
        else: self.body_node.velocity = self.SPEED * glm.normalize(proposed)
        
        # TODO add jumping once camera is stabilized
        
    def use_held_item(self, dt: float) -> None:
        """
        Determines if the player has a held item.
        If so, run the held item's function.
        """
        if not self.held_item: return
        self.held_node.position = self.camera.position + self.held_item.offset.x * self.camera.right + self.held_item.offset.y * self.camera.up + self.held_item.offset.z * self.camera.forward
        self.held_node.rotation = self.held_item.rotation * glm.conjugate(self.camera.rotation)
        self.held_item.func(dt)
        
    def interact(self, dt: float) -> None:
        """
        If the player is pressing E, interact with what they are looking at. 
        """
        # determine if the player is interacting with a valid object
        if not self.game.keys[bsk.pg.K_e]: return
        cast = self.current_scene.raycast(position = self.camera.position + self.camera.forward * 1.5) # will find the player's hitbox
        if not cast.node: return
        interactable = self.current_level[cast.node]
        if not interactable: return
        
        # use the Interactable's functionality
        if interactable.func: interactable.func(dt)

    @property
    def position(self): return self.body_node.position # TODO offset this position to be at the node's feet
    
    @property
    def velocity(self): return self.body_node.velocity
    
    @property
    def held_item(self):
        size = len(self.items)
        if not size: return None
        return self.items[self.held_index % size]
    
    @property
    def held_index(self): return self._held_index
    
    @property
    def current_scene(self): return self.game.current_scene
    
    @property
    def current_level(self) -> Level: return self.game.current_level
    
    @property
    def control_disabled(self): return self._control_disabled
    
    @position.setter
    def position(self, value: glm.vec3): self.body_node.position = value
    
    @velocity.setter
    def velocity(self, value: glm.vec3): self.body_node.velocity = value
    
    @held_item.setter
    def held_item(self, value: HeldItem): 
        # search for held item in the list and change 
        if value in self.items: self.held_index = self.items.index(value)
        else:
            self.items.append(value)
            self.held_index = len(self.items) - 1
        
    @held_index.setter
    def held_index(self, value: int):
        # if not items are held, do nothing
        if not len(self.items): 
            self._held_index = 0
            return
        
        value = value % len(self.items) 
        self._held_index = value
        
        # set properties for the held node that will not change until the held node is swapped
        self.held_node.scale = self.items[value].node.scale
        self.held_node.material = self.items[value].node.material
        self.held_node.mesh = self.items[value].node.mesh
        
    @control_disabled.setter
    def control_disabled(self, value: bool):
        self._control_disabled = value