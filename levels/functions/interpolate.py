import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable

def lerp(interact: Interactable, node: bsk.Node=None, time: float=1, position: glm.vec3=None, rotation: glm.quat=None, end_func: Callable=None) -> Callable:
    """
    Linrealy interpolates between the original position/rotation to the final position/rotation.
    """
    setattr(interact, 'percent', 0)
    setattr(interact, 'step', -1) # step is negative so the animation doesn't play on start up
    node = node if node else interact.node
    original_position = glm.vec3(*node.position)
    original_rotation = glm.quat(*node.rotation)
    final_position = glm.vec3(position) if position else glm.vec3(*node.position)
    final_rotation = glm.quat(rotation) if rotation else glm.quat(*node.rotation)
    
    def func(dt: float) -> None:
        # play animation and store lerp value
        was1 = interact.percent == 1
        interact.percent = glm.clamp(interact.percent + dt * interact.step / time, 0, 1)
        node.position = glm.mix(original_position, final_position, interact.percent)
        node.rotation = glm.slerp(original_rotation, final_rotation, interact.percent)
        
        # interact with current scene if animation is at it's maximum
        if end_func and interact.percent == 1 and not was1: end_func(dt)
        
    return func

def lerp_difference(interact: Interactable, node: bsk.Node=None, time: float=1, delta_position: glm.vec3=None, delta_rotation: glm.vec3=None, end_func: Callable=None) -> Callable:
    """
    Generates a lerp function for an Interactable to the offset position and rotation. 
    """
    node = node if node else interact.node
    final_position = (glm.vec3(delta_position) if delta_position else glm.vec3()) + node.position.data
    final_rotation = (glm.quat(delta_rotation) if delta_rotation else glm.quat()) * node.rotation.data
    return lerp(interact, node, time, final_position, final_rotation, end_func)

# function used for activating a lerp
def lerp_interact(interact: Interactable, end_func: Callable=None, check_func: Callable=None, sound: str=None) -> Callable:
    """
    On keydown, toggles the lerp on an Interactable with the lerp function.
    """
    if not check_func:
        def check() -> bool: return interact.level.game.key_down(bsk.pg.K_e)
        check_func = check
            
    def func(dt: float) -> None:
        if not check_func(): return
        if sound: interact.level.game.sounds[sound].play()
        interact.step *= -1
        if end_func: end_func(dt)
        
    return func