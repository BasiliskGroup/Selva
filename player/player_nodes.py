from basilisk import Node
from helper.type_hints import Game

# this file will be used to reduce bloat from the Player class. 
# Nodes for the Player will be created here and imported into the Player's __init__ function

def player_nodes(game: Game) -> tuple[Node, Node]:
    body = Node(
        position = (0, 2, 0),
        scale = (1, 2, 1),
        collision = True,
        # physics = True
    )
    
    held = Node(
        position = (0.5, 1.5, -1)
    )
    # body.add(held) TODO fix children in basilisk engine 
    
    return body, held