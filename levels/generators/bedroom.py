import basilisk as bsk
import glm
from levels.level import Level
from levels.helper import rect_room
from levels.interactable import Interactable
from helper.type_hints import Game
from levels.pickup import pickup_function, pickup_return_function


def bedroom(game: Game) -> Level:
    # create basic layout for bedroom level
    bedroom = Level(game)
    bedroom.add(*rect_room(0, 0, 6, 8, 6, game.materials['light_white']))
    bedroom.add(bsk.Node(
        position = (2.5, 1.5, -4.5),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh=game.meshes['dresser']
    ))
    
    bedroom.add(animated_box(bedroom))
    
    return bedroom

def animated_box(level: Level) -> Interactable:
    box = bsk.Node(
        mesh = level.game.meshes['wheel_eight'],
        material = level.game.materials['wheel_eight'],
        position = (0, 1.5, 0)
    )
    animated_box = Interactable(level, box)
    animated_box.func = pickup_function(animated_box, pickup_return_function(animated_box))
    return animated_box
    