import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable

def pan_loop(interact: Interactable, time: float=1, position: glm.vec3=None, rotation: glm.quat=None, loop_func: Callable=None, leave_check_func: Callable=None) -> Callable:
    """
    Lerps camera to desires position and rotation and starts main loop with func.
    Exits on pressing E.
    Lerps camera back to player position
    """
    # attributes created dynamically so that they can be accessed outside function call
    camera = bsk.StaticCamera() # position and rotation do not matter for init
    setattr(interact, 'percent_lerp', 0)
    setattr(interact, 'step_lerp', 1)
    level = interact.level
    game = level.game
    
    def func(dt: float) -> None:
        # prepare variables for lerp
        if not game.key_down(bsk.pg.K_e): return
        original_position = camera.position = glm.vec3(*game.camera.position)
        original_rotation = camera.rotation = glm.quat(*game.camera.rotation)
        final_position = glm.vec3(position) if position else original_position
        final_rotation = glm.quat(rotation) if rotation else original_rotation
        game.camera = camera
        game.player.velocity = glm.vec3() # reset player velocity to prevent player sliding away
        interact.step_lerp = 1 # reset steps from previous calls of this function
        game.mouse.position = glm.vec2(game.engine.win_size) // 2
        forced_stay = True # force the player to stay in the lerp for one frame to prevent instant leaving bug

        # generate update function for the game
        def update():
            nonlocal forced_stay
            interact.percent_lerp = glm.clamp(interact.percent_lerp + game.engine.delta_time / time * interact.step_lerp, 0, 1)
            game.camera.position = glm.mix(original_position, final_position, interact.percent_lerp)
            game.camera.rotation = glm.slerp(original_rotation, final_rotation, interact.percent_lerp)

            if interact.percent_lerp == 1 and game.key_down(bsk.pg.K_e): interact.step_lerp = -1 # initiate reverse lerp
            if not (interact.percent_lerp == 0 and interact.step_lerp == -1) or forced_stay or (leave_check_func and not leave_check_func(dt)): game.update = update # "recurse" through this function if not exiting
            else: game.camera = game.player.camera # reapply the player camera when fully exited
            if loop_func and interact.percent_lerp == 1 and interact.step_lerp == 1: loop_func(dt) # placed after game.update reset to allow breaking without panning out

            forced_stay = False
            level.update()
            bsk.draw.blit(game.engine, game.images['mouse.png'], (*game.mouse.position, 20, 20))
            game.engine.update()
        
        # exit procedure for pan
        game.update = update
            
    return func