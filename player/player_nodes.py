from basilisk import Node

# this file will be used to reduce bloat from the Player class. 
# Nodes for the Player will be created here and imported into the Player's __init__ function

def player_nodes() -> tuple[Node]:
    body = Node(
        position = (0, 0, 0),
        scale = (1, 2, 1),
        collision = True,
        # physics = True
    )
    
    held = Node(
        scale = (0.2, 0.2, 0.2),
    )
    body.add(held)
    
    return body, held