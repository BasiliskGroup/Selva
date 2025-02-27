import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable
from player.held_item import HeldItem

def interact_to_hold(interact: Interactable, node: bsk.Node, held_func: Callable=None, offset: glm.vec3=None, rotation: glm.quat=None, **kwargs) -> Callable:
    """
    Removes the Interactable from the scene and gives the player the held item
    """
    level = interact.level
    game = level.game
    
    # precreate the held item
    node.mesh = interact.node.mesh
    node.material = interact.node.material
    held_item = HeldItem(
        game = game,
        node = node,
        func = held_func,
        offset = offset,
        rotation = rotation,
        kwargs = kwargs
    )
    
    def func(dt: float) -> None:
        if not game.key_down(bsk.pg.K_e): return
        level.scene.remove(interact.node)
        game.player.held_item = held_item
        
    return func