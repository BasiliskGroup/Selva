import glm
import basilisk as bsk
from typing import Callable
from levels.interactable import Interactable

def book(interact: Interactable, pages: list[Callable]) -> Callable:
    """
    Displays drawing on the screen until the player hits e to exit
    """
    level = interact.level
    game = level.game
    setattr(interact, 'page_number', 0)
    
    def func(dt: float) -> None:
        if not game.key_down(bsk.pg.K_e): return
        game.mouse.position = glm.vec2(game.engine.win_size) // 2
        
        def update():
            if not game.key_down(bsk.pg.K_e): game.update = update
            pages[interact.page_number](dt)
            level.update()
            game.engine.update()
            
        game.update = update
        
    return func