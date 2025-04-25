import basilisk as bsk
import glm
from levels.level import Level
from levels.helper import rect_room
from levels.functions.imports import *
from typing import Callable
from levels.interactable import Interactable

def decor(bedroom: Level, note_func: Callable) -> None:
    game = bedroom.game
    bedroom.add(*rect_room(0, 0, 5.75, 6.75, 4, floor_material = game.materials['bedroom_floor'], wall_material = game.materials['bedroom_wall'], ceil_material = game.materials['light_white']))
    # bed
    bedroom.add(bsk.Node(
        position = (-2.5, 1, -2.5),
        mesh = game.meshes['bed'],
        material = game.materials['bed']
    ))
    bedroom.add(bsk.Node(
        position = (-2.5, 1, -2.5),
        scale = (2, 1, 3),
        collision = True,
        static = True,
        shader = game.shaders['invisible']
    ))
    
    # lamp
    bedroom.add(bsk.Node(
        position = (1, 2.25, -4.35),
        scale = (0.7, 0.7, 0.7),
        mesh = game.meshes['lamp'],
        material = game.materials['lamp']
    ))
    
    # desk
    bedroom.add(bsk.Node(
        position = (2.5, 2, 4.5),
        mesh = game.meshes['desk'],
        material = game.materials['light_wood']
    ))
    bedroom.add(bsk.Node(
        position = (2.5, 1, 4.5),
        scale = (2, 1, 1),
        collision = True,
        static = True,
        shader = game.shaders['invisible']
    ))
    
    # door
    bedroom.add(bsk.Node(
        position = (-4.75, 2.65, 3),
        scale = glm.vec3(0.65),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['fake_door'],
        material = game.materials['fake_door']
    ))
    
    # dresser
    bedroom.add(bsk.Node(
        position = (2.5, 1, -4.5),
        scale = (1, 0.8, 1),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['dresser'],
        material = game.materials['bright_wood']
    ))
    bedroom.add(bsk.Node(
        position = (2.5, 1, -4.5),
        scale = (2, 1, 1),
        collision = True,
        static = True,
        shader = game.shaders['invisible']
    ))
    
    # note
    note = Interactable(bedroom, bsk.Node(
        position = (3.75, 2.1, 4.35),
        scale = glm.vec3(0.5),
        rotation = glm.quat(),
        mesh = game.meshes['paper'],
        material = game.materials['paper']
    ))
    note.active = book(note, [note_func])
    bedroom.add(note)