from levels.level import Level
from levels.helper import rect_room
from helper.type_hints import Game


def bedroom(game: Game) -> Level:
    # create basic layout for bedroom level
    bedroom = Level(game)
    bedroom.add(*rect_room(0, 0, 8, 12, 6, game.materials['bible']))
    
    
    return bedroom