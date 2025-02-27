import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable

def free(interact: Interactable, node: bsk.Node=None, sensitivity: float=0.35) -> Callable:
    """
    Generates a function that allows the user to spin the given node.
    interact requires the following attributes: timer
    """
    level = interact.level
    game = level.game
    node = node if node else interact.node
    
    def func() -> None:
        interact.timer += game.engine.delta_time
        rel_x, rel_y = game.engine.mouse.relative
        node.rotational_velocity = node.rotational_velocity * (1 - game.engine.delta_time) if glm.length2(node.rotational_velocity) > 1e-7 else glm.vec3(0, 0, 0)
        if not game.engine.mouse.left_down: return # TODO combine this with the next if statement
        if rel_x != 0 or rel_y != 0 or interact.timer > 0.1:
            node.rotational_velocity = level.scene.camera.rotation * glm.vec3(rel_y * sensitivity, rel_x * sensitivity, 0)
            interact.timer = 0
        
    return func

def free_y(interact: Interactable, node: bsk.Node=None, sensitivity: float=0.35) -> Callable: # TODO use free axis instead of this function
    """
    Generates a function that allows the user to spin the given node.
    interact requires the following attributes: timer
    """
    level = interact.level
    game = level.game
    node = node if node else interact.node
    
    def func() -> None:
        interact.timer += game.engine.delta_time
        rel_y = game.engine.mouse.relative_y
        node.rotational_velocity = node.rotational_velocity * (1 - game.engine.delta_time) if glm.length2(node.rotational_velocity) > 1e-7 else glm.vec3(0, 0, 0)
        if not game.engine.mouse.left_down: return # TODO combine this with the next if statement
        if rel_y != 0 or interact.timer > 0.1:
            node.rotational_velocity = level.scene.camera.rotation * glm.vec3(rel_y * sensitivity, 0, 0)
            interact.timer = 0
        
    return func