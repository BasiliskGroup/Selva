import glm
import basilisk as bsk
from helper.type_hints import Game
from player.held_item import HeldItem
from player.player_nodes import player_nodes


class Player():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        
        # constant variables
        self.HEIGHT = 2 # vertical scale of the node, 1x2x1
        self.SPEED = 3 # the velocity of the player's node when moving
        self.DECELERATION_COEFFICIENT = 10
        
        # Main body used for stabilizing collisions on the camera
        self.body_node, self.held_node = player_nodes()
        
        
        # variables for controling the player's held items
        self.items: list[HeldItem] = []
        
    def update(self, dt: float) -> None:
        """
        Updates the players movement, Nodes, and controls
        """
        # update user node to preserve direction
        self.body_node.rotation = self.game.camera.rotation
        self.body_node.rotational_velocity = glm.vec3(0, 0, 0)
        
        # syncronize held item's position to the player TODO replace this with children
        
        # TODO sync game camera position with player head
        
        self.move(dt)
        self.actions(dt)
    
    def move(self, dt: float) -> None:
        """
        Controls the player movement from the input of the 
        """
        # control player movement WASD
        proposed = glm.vec3(0, 0, 0)
        proposed += self.game.camera.horizontal * (self.game.keys[bsk.pg.K_w] - self.game.keys[bsk.pg.K_s]) 
        proposed += self.game.camera.right * (self.game.keys[bsk.pg.K_d] - self.game.keys[bsk.pg.K_a])
        
        if proposed == (0, 0, 0): self.body_node.velocity *= (1 - self.DECELERATION_COEFFICIENT * dt)
        else: self.body_node.velocity = self.SPEED * glm.normalize(proposed)
        
        # TODO add jumping once camera is stabilized
        
    def actions(self, dt: float) -> None:
        """
        Controls the player's actions that affect the world around them (i.e. not movement)
        """
        
        # control held item functionality
        if not len(self.items): return
    
    @property
    def position(self): return self.body_node.position # TODO offset this position to be at the node's feet
    
    @property
    def velocity(self): return self.body_node.velocity
    
    @position.setter
    def position(self, value): self.body_node.position = value
    
    @velocity.setter
    def velocity(self, value): self.body_node.velocity = value
    
    