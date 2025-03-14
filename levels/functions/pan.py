import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable

def pan_loop(interact: Interactable, time: float=1, position: glm.vec3=None, rotation: glm.quat=None, loop_func: Callable=None) -> Callable:
    """
    Lerps camera to desires position and rotation and starts main loop with func.
    Exits on pressing E.
    Lerps camera back to player position
    """
    setattr(interact, 'camera', bsk.StaticCamera()) # position and rotation do not matter for init
    setattr(interact, 'percent', 0)
    setattr(interact, 'step', 1)
    level = interact.level
    game = level.game
    
    def func(dt: float) -> None:
        # prepare variables for lerp
        if not game.key_down(bsk.pg.K_e): return
        original_position = interact.camera.position = glm.vec3(*game.camera.position)
        original_rotation = interact.camera.rotation = glm.quat(*game.camera.rotation)
        final_position = glm.vec3(position) if position else original_position
        final_rotation = glm.quat(rotation) if rotation else original_rotation
        game.camera = interact.camera
        game.player.velocity = glm.vec3() # reset player velocity to prevent player sliding away
        interact.step = 1 # reset steps from previous calls of this function

        # generate update function for the game
        def update():
            interact.percent = glm.clamp(interact.percent + game.engine.delta_time / time * interact.step, 0, 1)
            game.camera.position = glm.mix(original_position, final_position, interact.percent)
            game.camera.rotation = glm.slerp(original_rotation, final_rotation, interact.percent)

            if interact.percent == 1 and game.key_down(bsk.pg.K_e): interact.step = -1 # initiate reverse lerp
            if loop_func and interact.percent == 1 and interact.step == 1: loop_func(dt)
            if not (interact.percent == 0 and interact.step == -1): game.update = update # "recurse" through this function if not exiting
            else: game.camera = game.player.camera # reapply the player camera when fully exited

            level.update()
            game.engine.update()
        
        # exit procedure for pan
        game.update = update
            
    return func