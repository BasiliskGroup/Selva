import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable
from player.held_items.held_item import HeldItem

def interact_to_hold(interact: Interactable, held: HeldItem) -> Callable:
    """
    Removes the Interactable from the scene and gives the player the held item
    """
    level = interact.level
    game = level.game
    
    def func(dt: float) -> None:
        if not game.key_down(bsk.pg.K_e): return
        interact.node.node_handler.scene.remove(interact.node)
        game.player.item_r_ui.drop()
        game.player.item_r = held
        
    return func

def interact_give_hold(interact: Interactable, held: HeldItem) -> Callable:
    """
    Gives the player the held item
    """
    level = interact.level
    game = level.game
    
    def func(dt: float) -> None:
        if not game.key_down(bsk.pg.K_e): return
        game.player.item_r_ui.drop()
        held_copy = held
        held_copy.node = held.node.deep_copy()
        game.player.item_r = held_copy
        
    return func

def interact_to_frame(interact: Interactable, held: HeldItem) -> Callable:
    """
    Removes the Interactable from the scene and gives the player the held item
    """
    level = interact.level
    game = level.game
    
    def func(dt: float) -> None:
        if not game.key_down(bsk.pg.K_e): return
        interact.node.node_handler.scene.remove(interact.node)
        game.player.item_l = held
        
    return func