import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable
import time

def free(interact: Interactable, node: bsk.Node=None, sensitivity: float=0.35) -> Callable:
    """
    Generates a function that allows the user to spin the given node.
    interact requires the following attributes: timer
    """
    setattr(interact, 'timer', 0)
    level = interact.level
    game = level.game
    node = node if node else interact.node
    
    def func(dt: float) -> None:
        interact.timer += dt
        rel_x, rel_y = game.engine.mouse.relative
        node.rotational_velocity = node.rotational_velocity * (1 - dt) if glm.length2(node.rotational_velocity) > 1e-7 else glm.vec3(0, 0, 0)
        if game.engine.mouse.left_down and (rel_x != 0 or rel_y != 0 or interact.timer > 0.1):
            node.rotational_velocity = level.scene.camera.rotation * glm.vec3(rel_y * sensitivity, rel_x * sensitivity, 0)
            interact.timer = 0
        
    return func

def free_axis_xy(interact: Interactable, axis :glm.vec3, node: bsk.Node=None, sensitivity: float=0.35) -> Callable: # TODO use free axis instead of this function
    """
    Generates a function that allows the user to spin the given node around the specified axis.
    interact requires the following attributes: timer
    """
    setattr(interact, 'timer', 0)
    level = interact.level
    game = level.game
    node = node if node else interact.node
    axis = glm.normalize(axis)
    
    def func(dt: float) -> None:
        # get relative x and y components
        interact.timer += dt
        rel_x, rel_y = game.engine.mouse.relative
        node.rotational_velocity = node.rotational_velocity * (1 - dt) if glm.length2(node.rotational_velocity) > 1e-7 else glm.vec3(0, 0, 0) # apply deceleration
        
        # apply rotation to node
        if game.engine.mouse.left_down and (rel_x != 0 or rel_y != 0 or interact.timer > 0.1):
            rotation = game.camera.right * rel_y + game.camera.up * rel_x
            node.rotational_velocity = axis * glm.dot(rotation, axis) * sensitivity
            interact.timer = 0
        
    return func

def free_axis(interact: Interactable, axis :glm.vec3, node: bsk.Node=None) -> Callable: # TODO use free axis instead of this function
    """
    Generates a function that allows the user to spin the given node around the specified axis.
    interact requires the following attributes: timer
    """
    setattr(interact, 'timer', 0)
    setattr(interact, 'positions', [None, None])
    setattr(interact, 'last_time_registered', 0)
    level = interact.level
    game = level.game
    node = node if node else interact.node
    axis = glm.normalize(axis)
    
    capture_time = 0.1
    
    # TODO add functionality for planes perpendicular to the camera's forward axis
    def func(dt: float) -> None:
        if not game.mouse.left_down or time.time() - interact.last_time_registered > capture_time: 
            interact.last_time_registered = time.time()
            interact.positions = [None, None]
            interact.timer = 0 # TODO add rotational velocity at the end
            return
        interact.last_time_registered = time.time()
        
        # get mouse position every x time
        # interact.timer += dt
        # if interact.timer < capture_time: return
        # interact.timer = 0
        
        # compute world space of the mouse
        position = game.engine.mouse.position
        inv_proj, inv_view = glm.inverse(game.camera.m_proj), glm.inverse(game.camera.m_view)
        ndc = glm.vec4(2 * position[0] / game.engine.win_size[0] - 1, 1 - 2 * position[1] / game.engine.win_size[1], 1, 1)
        position: glm.vec4 = inv_proj * ndc
        position /= position.w
        forward = glm.normalize(glm.vec3(inv_view * glm.vec4(position.x, position.y, position.z, 0)))
        
        # get mouse point on the plane
        d = glm.dot(node.position.data - game.camera.position, axis) / glm.dot(forward, axis)
        position = game.camera.position + d * forward
        
        interact.positions.pop(0)
        interact.positions.append(position)
        
        if not interact.positions[0]: return # no change in position has been detected
        v1, v2 = interact.positions[0] - node.position.data, interact.positions[1] - node.position.data
        cross = glm.cross(v2, v1)
        dot = glm.dot(v1, v2)
        dq = glm.angleAxis(glm.atan2(glm.length(cross), dot) * glm.sign(glm.dot(axis, cross)), axis)
        node.rotation *= dq
        
    return func