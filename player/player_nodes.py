from basilisk import Node
from helper.type_hints import Game
import glm

# this file will be used to reduce bloat from the Player class. 
# Nodes for the Player will be created here and imported into the Player's __init__ function

def player_nodes(game: Game) -> tuple[Node, Node]:
    body = Node(
        position = (0, 2, 0),
        scale = (1, 1.5, 1),
        collision = True,
        physics = True,
        shader = game.shaders['invisible']
    )
    loader = Node(
        scale = glm.vec3(0.1),
        mesh = game.meshes['john'],
        shader = game.shaders['invisible']
    )
    
    return body, loader