import basilisk as bsk
import glm
import random
from typing import Callable
from helper.type_hints import Game
from levels.level import Level
from levels.helper import rect_room
from levels.interactable import Interactable
from levels.functions.imports import *
from levels.generators.bedroom import decor
from player.held_items.held_item import HeldItem, PictureFrame

def bedroom2(game: Game) -> Level:
    bedroom = Level(game, 'bedroom2', glm.vec3(0, 0, 0))
    decor(bedroom)
    safe(bedroom)
    
    return bedroom

def safe(bedroom: Level) -> None:
    game = bedroom.game
    
    safe = bsk.Node(
        position = (1.5, 0.95, 4.6),
        rotation = glm.angleAxis(glm.pi(), (0, 1, 0)),
        scale = (0.7, 0.7, 0.7),
        mesh = game.meshes['safe'],
        material = game.materials['black']
    )
    
    handle = bsk.Node(
        position = (1.85, 0.95, 3.9),
        rotation = glm.angleAxis(glm.pi(), (0, 1, 0)),
        scale = (0.7, 0.7, 0.7),
        mesh = game.meshes['safe_door_handle'],
        material = game.materials['black']
    )
    
    door = bsk.Node(
        position = (1, 0.95, 3.5),
        rotation = glm.angleAxis(glm.pi()/2, (0, 1, 0)),
        scale = (0.7, 0.7, 0.7),
        mesh = game.meshes['safe_door'],
        material = game.materials['safe_door']
    )
    
    bedroom.add(safe, handle, door)
    
    for y in range(1, -2, -1):
        for x in range(1, -2, -1):
            position = glm.vec3(1.05, 0.95 - 0.1 * y, 3.6 - 0.1 * x)
            bedroom.add(bsk.Node(
                position = position,
                rotation = glm.angleAxis(glm.pi() / 2, (1, 0, 0)) * glm.angleAxis(glm.pi(), (0, 0, 1)) * glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
                scale = (0.8, 0.8, 0.8),
                mesh = game.meshes['keycap'],
                material = game.materials[f'key{(x + 2) + (y + 1) * 3}'],
            ))