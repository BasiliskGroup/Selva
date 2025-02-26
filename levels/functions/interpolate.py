import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable

def lerp(interact: Interactable, time: float=1, position: glm.vec3=None, rotation: glm.quat=None, end_func: Callable=None) -> Callable:
    """
    Linrealy interpolates between the original position/rotation to the final position/rotation.
    """
    setattr(interact, 'percent', 0)
    setattr(interact, 'step', -1 / time) # step is negative so the animation doesn't play on start up
    original_position = glm.vec3(*interact.node.position)
    original_rotation = glm.quat(*interact.node.rotation)
    final_position = glm.vec3(position) if position else glm.vec3(*interact.node.position)
    final_rotation = glm.quat(rotation) if rotation else glm.quat(*interact.node.rotation)
    
    def func(dt: float) -> None:
        # play animation and store lerp value
        was1 = interact.percent == 1
        interact.percent = glm.clamp(interact.percent + dt * interact.step, 0, 1)
        interact.node.position = glm.mix(original_position, final_position, interact.percent)
        interact.node.rotation = glm.slerp(original_rotation, final_rotation, interact.percent)
        
        # interact with current scene if animation is at it's maximum
        if end_func and interact.percent == 1 and not was1: end_func()
        
    return func

def lerp_difference(interact: Interactable, time: float=1, delta_position: glm.vec3=None, delta_rotation: glm.vec3=None, end_func: Callable=None) -> Callable:
    """
    Generates a lerp function for an Interactable to the offset position and rotation. 
    """
    final_position = (glm.vec3(delta_position) if delta_position else glm.vec3()) + interact.node.position.data
    final_rotation = (glm.quat(delta_rotation) if delta_rotation else glm.quat()) * interact.node.rotation.data
    return lerp(interact, time, final_position, final_rotation, end_func)

def lerp_interact(interact: Interactable, end_func: Callable=None) -> Callable:
    """
    On keydown, toggles the lerp on an Interactable with the lerp function.
    """
    def func(dt: float) -> None:
        if not interact.level.game.key_down(bsk.pg.K_e): return
        interact.step *= -1
        if end_func: end_func()
        
    return func