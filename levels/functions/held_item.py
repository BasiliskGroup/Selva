import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable
from player.held_item import HeldItem

def interact_to_hold(interact: Interactable, held: HeldItem) -> Callable:
    """
    Removes the Interactable from the scene and gives the player the held item
    """
    level = interact.level
    game = level.game
    
    def func(dt: float) -> None:
        if not game.key_down(bsk.pg.K_e): return
        level.scene.remove(interact.node)
        game.player.item_r = held
        
    return func