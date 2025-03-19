import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable
from levels.functions.imports import interact_to_hold

def place(interact: Interactable, position: glm.vec3=None, check_in_func: Callable=None, check_out_func: Callable=None, put_in_func: Callable=None, pull_out_func: Callable=None) -> Callable:
    """
    Places the player's held item into the interact
    """
    level = interact.level
    game = level.game
    player = game.player
    position = glm.vec3(position) if position else glm.vec3()
    setattr(interact, 'held_item', None)
    
    def func(dt: float) -> None:
        player_item = player.item_r
        
        # run custom and built-in checks
        if interact.held_item:
            if not game.player.item_r or (check_in_func and not check_in_func(dt)): return
            
            # add held item to scene
            interact.held_item = player_item
            player.item_r_ui.remove(player_item)
            placed = placed_interactable(interact, position, check_out_func, pull_out_func)
            level.add(placed) # NOTE this is not a child of the current interactable, change if needed
            
            if put_in_func: put_in_func(dt)
        else: take_back(dt, interact, check_out_func, pull_out_func)
        
    return func

def placed_interactable(interact: Interactable, position: glm.vec3=None, check_out_func: Callable=None, pull_out_func: Callable=None) -> Interactable:
    """
    Allows the player to pick their item back up without needing to click on the parent interact
    """
    level = interact.level
    game = level.game
    node = interact.held_item.node
    
    # create the interactable
    node.position = glm.vec3(position)
    def func(dt: float) -> None: take_back(dt, interact, check_out_func, pull_out_func)
    placed = Interactable(level, node)
    placed.active = func
    
    return placed

def take_back(dt: float, interact: Interactable, check_out_func: Callable=None, pull_out_func: Callable=None) -> Callable:
    """
    Performs the operations to give the picked up nodes back to the players. NOTE this is not a higher order function (But it could be)
    """
    player = interact.level.game.player
    if check_out_func and not check_out_func(dt): return
    # give held_item to player
    interact.node.node_handler.scene.remove(interact.node)
    interact.held_item = None
    player.item_r_ui.drop()
    player.item_r = interact.held_item
    # call pullout function
    if pull_out_func: pull_out_func(dt)
    