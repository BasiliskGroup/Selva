import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable

def book(interact: Interactable, pages: list[Callable]) -> Callable:
    """
    Displays drawing on the screen until the player hits e to exit
    """
    setattr(interact, 'page_number', 0)
    level = interact.level
    game = level.game
    camera = bsk.StaticCamera()
    
    def func(dt: float, engine = game.engine) -> None:
        if not game.key_down(bsk.pg.K_e): return
        game.mouse.position = glm.vec2(game.engine.win_size) // 2
        camera.position = game.camera.position
        camera.rotation = game.camera.rotation
        game.camera = camera
        game.player.body_node.velocity = glm.vec3(0)
        
        def update():
            # update every frame
            win_size = glm.vec2(engine.win_size)
            margin = 15
            transforms = {
                'left' : (1 * win_size.x // margin, (margin - 2) * win_size.y // margin, win_size.x // 10, win_size.x // 20),
                'right': ((margin - 2) * win_size.x // margin, (margin - 2) * win_size.y // margin, win_size.x // 10, win_size.x // 20),
                'exit' : (1 * win_size.x // margin, 1 * win_size.y // margin, win_size.x // 20, win_size.x // 20),
            }
            mouse = engine.mouse.position
            
            def button(image: str, trans: str, func: Callable) -> None:
                if is_hovering(*transforms[trans], *mouse): 
                    bsk.draw.blit(engine, game.images[f'{image}_green.png'], transforms[trans])
                    if engine.mouse.left_click: func()
                else: bsk.draw.blit(engine, game.images[f'{image}.png'], transforms[trans])
            
            # page buttons
            def decr(): interact.page_number -= 1
            def incr(): interact.page_number += 1
            if interact.page_number: button('left_arrow', 'left', decr)
            if interact.page_number < len(pages) - 1: button('right_arrow', 'right', incr)
                
            # exit button
            exit = False
            def set_exit(): 
                nonlocal exit
                exit = True
            button('circled_x', 'exit', set_exit)
            
            # continue/exit function
            if not game.key_down(bsk.pg.K_e) and not exit: game.update = update
            else: game.camera = game.player.camera
            
            # update page and game
            pages[interact.page_number](dt)
            bsk.draw.blit(game.engine, game.images['mouse.png'], (*game.mouse.position, 20, 20))
            level.update()
            game.engine.update()
            
        game.update = update
        
    return func

def is_hovering(x: int, y: int, w: int, h: int, mx: int, my: int) -> bool: return x <= mx <= x + w and y <= my <= y + h