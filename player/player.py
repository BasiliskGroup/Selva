import glm
import basilisk as bsk
from helper.type_hints import Game
from player.held_item import HeldItem, PictureFrame
from player.player_nodes import player_nodes


class Player():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        
        # constant variables
        self.HEIGHT = 2 # vertical scale of the node, 1x2x1
        self.SPEED = 5 # the velocity of the player's node when moving
        self.DECELERATION_COEFFICIENT = 10
        
        # Main body used for stabilizing collisions on the camera
        self.body_node, self.held_node = player_nodes(self.game)
        self.current_scene = self.game.current_scene 
        self.current_scene.add(self.body_node, self.held_node)
        self.camera = bsk.FollowCamera(self.body_node, offset = (0, 1.5, 0))
        self.game.current_scene.camera = self.camera # TODO ensure that this camera is passed between scenes depending on where the player is NOTE this will act as the main player camera
        
        # variables for controling the player's held items
        self.items: list[HeldItem] = [PictureFrame(self.game, None)] # TODO temporary, remove item and define behavior when the user has not item
        self.held_index = 0
        
    def update(self, dt: float) -> None:
        """
        Updates the players movement, Nodes, and controls
        """
        # update user node to preserve direction
        horizontal_quat = glm.conjugate(glm.quat((0, self.camera.yaw, self.camera.roll)))
        self.body_node.rotation = horizontal_quat
        self.body_node.rotational_velocity = glm.vec3(0, 0, 0)
        
        self.move(dt)
        self.actions(dt)
    
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
        
    def actions(self, dt: float) -> None:
        """
        Controls the player's actions that affect the world around them (i.e. not movement)
        """
        
        # control held item functionality
        if not self.held_item: return
        
        self.held_node.position = self.camera.position + self.held_item.offset.x * self.camera.right + self.held_item.offset.y * self.camera.up + self.held_item.offset.z * self.camera.forward
        self.held_node.rotation = self.held_item.rotation * glm.conjugate(self.camera.rotation)
        self.held_item.func(dt)
    
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
        self._held_index = value
        
        # set properties for the held node that will not change until the held node is swapped
        self.held_node.scale = self.items[value].node.scale
        self.held_node.material = self.items[value].node.material