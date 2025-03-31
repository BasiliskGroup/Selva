import glm
from typing import Callable
from player.held_items.held_item import HeldItem

def lerp_held(held_item: HeldItem, time: float=1, position: glm.vec3=None, rotation: glm.quat=None, end_func: Callable=None) -> Callable:
    print(f'Held Item: {held_item}')
    setattr(held_item, 'percent_moved', 0)
    original_offset = glm.vec3(held_item.offset)
    original_rotation = glm.quat(held_item.rotation)
    game = held_item.game
    
    def func(dt: float) -> None:
        held_item.percent_moved = glm.clamp(held_item.percent_moved + dt / time * (2 * game.mouse.left_down - 1), 0, 1)
        held_item.offset = glm.mix(original_offset, position, held_item.percent_moved)
        held_item.rotation = glm.slerp(original_rotation, rotation, held_item.percent_moved)
        if held_item.percent_moved == 1 and end_func: end_func(dt)
        
    return func