import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable

SENSITIVITY = 0.35

def pickup_function(interact: Interactable, end_func: Callable=None) -> Callable:
    """
    Generates a "pick up" function for the given interactable.
    func will be activated when the player closes the pick up menu in the accept termination.
    """
    level = interact.level
    game = level.game
    
    def actions() -> None:
        """
        Controls the player's ability to spin the object around on the screen. 
        """
        rel_x, rel_y = game.engine.mouse.relative
        interact.node.rotational_velocity = interact.node.rotational_velocity * (1 - game.engine.delta_time) if glm.length2(interact.node.rotational_velocity) > 1e-7 else glm.vec3(0, 0, 0)
        if not (game.engine.mouse.left_down and (rel_x != 0 or rel_y != 0)): return
        interact.node.rotational_velocity = level.scene.camera.rotation * glm.vec3(rel_y * SENSITIVITY, rel_x * SENSITIVITY, 0)
    
    def update() -> None:
        """
        This function will replace the game's primary update function. 
        """
        actions()
        
        # TODO grey out background
        
        # if the function is not exiting
        if game.key_down(bsk.pg.K_e): 
            game.camera = game.player.camera
            if end_func: end_func()
        else: game.update = update
        
        level.scene.update() # TODO change this to only update HUD scene and render background scenes
        game.engine.update()
        
    def func(dt: float) -> None:
        """
        The function that will be called when "picking up" an Interactable
        """
        if not game.key_down(bsk.pg.K_e): return # only allow the user to call this function on a full left click
        
        # prevent the player from moving camera and position
        game.camera = bsk.StaticCamera(
            position = game.camera.position,
            rotation = game.camera.rotation
        )
        
        # set node's position to infront of the player # TODO this will require the same shader that Emulsion used to render HUD elements over everything else
        
        interact.node.position = game.camera.position + game.camera.forward * 5 # TODO make the distance scalable
        interact.node.rotation = game.camera.rotation
        
        game.update = update
        
    return func

def pickup_return_function(interact: Interactable, end_func: Callable=None) -> Callable:
    """
    Generates the standard function for returning a picked up item to its original position
    """
    position = glm.vec3(interact.node.position.data)
    rotation = glm.quat(interact.node.rotation.data)
    
    def func() -> None:
        """
        Returns the node to its original location
        """
        interact.node.position = position
        interact.node.rotation = rotation
        interact.node.rotational_velocity = glm.vec3(0, 0, 0)
        if end_func: end_func()
        
    return func