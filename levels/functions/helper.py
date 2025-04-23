import basilisk as bsk
from typing import Callable
from helper.type_hints import Game

def down(game: Game) -> Callable:
    def func() -> bool: return not game.key_down(bsk.pg.K_e)
    return func