import basilisk as bsk
import glm
from levels.level import Level
from levels.helper import rect_room
from levels.functions.imports import *

def decor(bedroom: Level) -> None:
    game = bedroom.game
    bedroom.add(*rect_room(0, 0, 5.75, 6.75, 4, game.materials['light_white']))
    # decorations
    bedroom.add(bsk.Node(
        position = (-2.5, 1, -2.5),
        mesh = game.meshes['bed']
    ))
    bedroom.add(bsk.Node(
        position = (1, 2.25, -4.35),
        scale = (0.7, 0.7, 0.7),
        mesh = game.meshes['lamp']
    ))
    bedroom.add(bsk.Node(
        position = (2.5, 2, 4.5),
        mesh = game.meshes['desk']
    ))
    bedroom.add(bsk.Node(
        position = (-4.75, 2.65, 3),
        scale = glm.vec3(0.65),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['fake_door']
    ))
    bedroom.add(bsk.Node(
        position = (4.75, 3.2, 0),
        scale = (0.01, 0.9, 1.4),
        rotation = glm.angleAxis(glm.pi() / 2, (1, 0, 0)),
        material = game.materials['fortune_dresser']
    ))
    bedroom.add(bsk.Node(
        position = (2.5, 1, -4.5),
        scale = (1, 0.8, 1),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['dresser']
    ))