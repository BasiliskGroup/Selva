import basilisk as bsk
from levels.level import Level
from levels.helper import rect_room
from levels.interactable import Interactable
from helper.type_hints import Game


def bedroom(game: Game) -> Level:
    # create basic layout for bedroom level
    bedroom = Level(game)
    bedroom.add(*rect_room(0, 0, 8, 12, 6, game.materials['red']))
    
    bedroom.add(animated_box(bedroom))
    
    return bedroom

def animated_box(level: Level) -> Interactable:
    box = bsk.Node()
    
    animated_box = Interactable(level, box)
    
    def func(dt: float) -> None:
        box.position += (0, 1, 0)
    
    animated_box.func = func
    
    return animated_box
    