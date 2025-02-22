import glm
from basilisk import Node
from type_hints import Game
from player.held_item import HeldItem


class Player():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        
        # constant variables
        self.HEIGHT = 2 # vertical scale of the node, 1x2x1
        
        # Main body used for stabilizing collisions on the camera
        self.body_node = Node(
            position = (0, 0, 0),
            scale = (1, 2, 1),
            collision = True,
            physics = True
        )
        self.held_node = Node(
            scale = (0.2, 0.2, 0.2),
            
        )
        self.body_node.add(self.held_node)
        
        self.items: list[HeldItem] = []
        
    def update(self, dt: float) -> None:
        """
        Updates the players movement, Nodes, and controls
        """
        # update user node to preserve direction
        self.body_node.rotation = self.game.camera.rotation
        self.body_node.rotational_velocity = glm.vec3(0, 0, 0)
        
        # syncronize held item's position to the player TODO replace this with children
        
        self.move(dt)
    
    def move(self, dt: float) -> None:
        """
        Controls the player movement from the input of the 
        """
        
        
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
    
    