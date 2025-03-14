import glm
import basilisk as bsk
from typing import Callable, Any
from levels.interactable import Interactable
from helper.type_hints import Game

def simulate_gravity_node(game: Game, scene: bsk.Scene, parent: Any, node: bsk.Node, end_func: Callable=None, epsilon=1e-3) -> Callable: # TODO possibly add "resting" check to simplify calculations
    """
    Simulates gravity on a node to collide with floors without using collision pipeline, saves on performance
    """
    setattr(parent, 'resting', False)
    
    def func(dt: float) -> None:
        if parent.resting: return
        # manually apply gravity to the node to bypass physics engine 
        gravity: glm.vec3 = game.player.gravity
        gravity_dir = glm.normalize(gravity)
        base = node.position.data - node.mesh.half_dimensions * node.scale.data + gravity * epsilon
        node.velocity += gravity * dt
        
        cast = scene.raycast(base, gravity_dir)
        if not cast.node: return # nothing to break fall, shouldn't happen but this should avoid errors

        # anticipate next physics step and check if there is a collision
        if glm.length(cast.position - base) / 2 > glm.length(node.velocity) * dt + epsilon: return # fall distance > amount fallen next frame
        parent.resting = True
        node.position = cast.position - base + node.position
        node.velocity -= gravity_dir * glm.dot(node.velocity, gravity_dir)
        if end_func: end_func(dt)
        
    return func