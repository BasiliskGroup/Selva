import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable
from levels.functions.tactile import free
from levels.functions.helper import down

def pickup_function(interact: Interactable, end_func: Callable=None, check_func: Callable=None, rotation: glm.quat=None, distance: float=1, top_text: str=None, bottom_text: str=None) -> Callable:
    """
    Generates a "pick up" function for the given interactable.
    func will be activated when the player closes the pick up menu in the accept termination.
    """
    setattr(interact, 'timer', 0)
    setattr(interact, 'pickup_overlay_timer', 0)
    level = interact.level
    game = level.game
    actions = free(interact, camera=game.overlay_scene.camera)
    force_stay = True
    
    check = check_func if check_func else down(game)

    def update() -> None:
        nonlocal force_stay
        actions(game.engine.delta_time)
        bsk.draw.blit(game.engine, game.images['mouse.png'], (*game.mouse.position, 20, 20))
        if top_text: bsk.draw.blit(game.engine, game.images[f'label_{top_text}.png'], (game.win_size.x // 8 * 3, game.win_size.y // 10, game.win_size.x // 4, game.win_size.y // 10))
        if bottom_text: bsk.draw.blit(game.engine, game.images[f'label_{bottom_text}.png'], (game.win_size.x // 8 * 3, game.win_size.y // 10 * 8, game.win_size.x // 4, game.win_size.y // 10))
        game.player.control_disabled = True
        
        interact.pickup_overlay_timer += game.engine.delta_time
        if interact.pickup_overlay_timer < 1:
            for node in game.overlay_scene.nodes: 
                if node.material == game.materials['bloom_yellow']: node.scale = glm.vec3(interact.pickup_overlay_timer)  
                elif node.material == game.materials['bloom_copper']: node.scale = glm.vec3(interact.pickup_overlay_timer / 2 * 3)
        
        # TODO grey out background
        
        # if the function is exiting
        if game.key_down(bsk.pg.K_e) and not force_stay: 
            game.camera = game.player.camera
            game.overlay_scene.remove(interact.node)
            game.overlay_on = False
            game.player.control_disabled = False
            if end_func: end_func(game.engine.delta_time)
        else: 
            game.update = update
            force_stay = False
        
        game.main_update()
        
    def func(dt: float) -> None:
        if check(): return # only allow the user to call this function on a full left click
        for node in game.overlay_scene.nodes: node.scale = glm.vec3(0)
        interact.pickup_overlay_timer = 0
        
        # prevent the player from moving camera and position
        game.camera = bsk.StaticCamera(
            position = game.camera.position,
            rotation = game.camera.rotation
        )
        game.player.velocity = glm.vec3()
        game.overlay_on = True
        game.player.control_disabled = True
        
        interact.node.position = glm.vec3(0, 0, 20 - distance)
        interact.node.rotation = (rotation if rotation else glm.quat()) * glm.conjugate(game.camera.rotation)
        level.scene.remove(interact.node)
        game.overlay_scene.add(interact.node)
        # game.sounds['placeholder'].play() # get item sound
        game.update = update
        
    return func

def pickup_return_function(interact: Interactable, end_func: Callable=None) -> Callable:
    """
    Generates the standard function for returning a picked up item to its original position
    """
    position = glm.vec3(interact.node.position.data)
    rotation = glm.quat(interact.node.rotation.data)
    
    def func(dt: float) -> None:
        interact.node.position = position
        interact.node.rotation = rotation
        interact.node.rotational_velocity = glm.vec3(0, 0, 0)
        if end_func: end_func(interact.level.game.engine.delta_time)
        
    return func