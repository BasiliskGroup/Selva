import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable
from math import atan2

def free(interact: Interactable, node: bsk.Node=None, sensitivity: float=0.35) -> Callable:
    """
    Generates a function that allows the user to spin the given node.
    interact requires the following attributes: timer
    """
    setattr(interact, 'timer', 0)
    level = interact.level
    game = level.game
    node = node if node else interact.node
    
    def func() -> None:
        interact.timer += game.engine.delta_time
        rel_x, rel_y = game.engine.mouse.relative
        node.rotational_velocity = node.rotational_velocity * (1 - game.engine.delta_time) if glm.length2(node.rotational_velocity) > 1e-7 else glm.vec3(0, 0, 0)
        if not game.engine.mouse.left_down and (rel_x != 0 or rel_y != 0 or interact.timer > 0.1):
            node.rotational_velocity = level.scene.camera.rotation * glm.vec3(rel_y * sensitivity, rel_x * sensitivity, 0)
            interact.timer = 0
        
    return func

def free_axis(interact: Interactable, axis :glm.vec3, node: bsk.Node=None, sensitivity: float=0.35) -> Callable: # TODO use free axis instead of this function
    """
    Generates a function that allows the user to spin the given node around the specified axis.
    interact requires the following attributes: timer
    """
    setattr(interact, 'timer', 0)
    level = interact.level
    game = level.game
    node = node if node else interact.node
    axis = glm.normalize(axis)
    
    def func() -> None:
        # get relative x and y components
        interact.timer += game.engine.delta_time
        rel_x, rel_y = game.engine.mouse.relative
        node.rotational_velocity = node.rotational_velocity * (1 - game.engine.delta_time) if glm.length2(node.rotational_velocity) > 1e-7 else glm.vec3(0, 0, 0) # apply deceleration
        
        # get relative z component
        clip = game.camera.m_proj * game.camera.m_view * glm.vec4(*node.position, 1.0)
        prev_pos = glm.vec2(game.engine.mouse.position) - game.engine.mouse.relative
        if clip.w == 0 or prev_pos == game.engine.mouse.position: rel_z = 0
        else:
            # get node position on screen
            ndc_pos = glm.vec3(clip) / clip.w
            node_pos = glm.vec2((ndc_pos.x + 1.0) * 0.5 * game.engine.win_size[0], (1.0 - ndc_pos.y) * 0.5 * game.engine.win_size[1])
            
            # get angle
            ca = prev_pos - node_pos
            cb = game.engine.mouse.position - node_pos
            rel_z = glm.degrees(atan2(ca.x * cb.y - ca.y * cb.x, glm.dot(ca, cb))) * 6
        
        # apply rotation to node
        if game.engine.mouse.left_down and (rel_x != 0 or rel_y != 0 or interact.timer > 0.1):
            rotation = game.camera.right * rel_y + game.camera.up * rel_x  + game.camera.forward * rel_z
            node.rotational_velocity = axis * glm.dot(rotation, axis) * sensitivity
            interact.timer = 0
        
    return func