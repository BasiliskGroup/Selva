import basilisk as bsk
from levels.level import Level
from levels.helper import rect_room
from levels.interactable import Interactable
from helper.type_hints import Game
from levels.pickup import pickup_function, pickup_return_function


def bedroom(game: Game) -> Level:
    # create basic layout for bedroom level
    bedroom = Level(game)
    bedroom.add(*rect_room(0, 0, 8, 12, 6, game.materials['red']))
    
    bedroom.add(animated_box(bedroom))
    
    return bedroom

def animated_box(level: Level) -> Interactable:
    box = bsk.Node(
        mesh = level.game.meshes['picture_frame'],
        material = level.game.materials['picture_frame'],
        position = (0, 1.5, 0)
    )
    animated_box = Interactable(level, box)
    animated_box.func = pickup_function(animated_box, pickup_return_function(animated_box))
    return animated_box
    