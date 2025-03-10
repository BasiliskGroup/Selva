import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable
from levels.functions.tactile import free

def pickup_function(interact: Interactable, end_func: Callable=None) -> Callable:
    """
    Generates a "pick up" function for the given interactable.
    func will be activated when the player closes the pick up menu in the accept termination.
    """
    setattr(interact, 'timer', 0)
    level = interact.level
    game = level.game
    actions = free(interact)

    def update() -> None:
        actions()
        
        # TODO grey out background
        
        # if the function is not exiting
        if game.key_down(bsk.pg.K_e): 
            game.camera = game.player.camera
            if end_func: end_func(game.engine.delta_time)
        else: game.update = update
        
        level.update() # TODO change this to only update HUD scene and render background scenes
        game.engine.update()
        
    def func(dt: float) -> None:
        if not game.key_down(bsk.pg.K_e): return # only allow the user to call this function on a full left click
        
        # prevent the player from moving camera and position
        game.camera = bsk.StaticCamera(
            position = game.camera.position,
            rotation = game.camera.rotation
        )
        game.player.velocity = glm.vec3()
        
        # set node's position to infront of the player # TODO this will require the same shader that Emulsion used to render HUD elements over everything else
        
        interact.node.position = game.camera.position + game.camera.forward * 1 # TODO make the distance scalable
        interact.node.rotation = glm.conjugate(game.camera.rotation)
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