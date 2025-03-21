import basilisk as bsk
import glm
import random
from typing import Callable
from player.held_item import HeldItem
from helper.type_hints import Game
from levels.level import Level
from levels.helper import rect_room
from levels.interactable import Interactable
from levels.functions.imports import *
from helper.transforms import connect

def boat(game: Game) -> Level:
    level = Level(game)
    
    fishing(level)
    load_boat(level)
    ocean(level)
    
    return level

def fishing(level: Level) -> None:
    game = level.game
    
    pos, sca, rot = connect(glm.vec3(-2.5, 1.5, 6.5), glm.vec3(-1.5, 4.5, 13.5), 3)
    rod = Interactable(level, bsk.Node(
        position = pos,
        scale = sca,
        rotation = rot,
        mesh = game.meshes['fishing_rod'],
        material = game.materials['fishing_rod']
    ))
    
    level.add(rod)

def load_boat(level: Level) -> None:
    game = level.game
    
    floor = bsk.Node(
        position = (0, -1, 0),
        scale = (5, 1, 7.5),
        collision = True
    )
    boat = bsk.Node(
        position = (0, -0.9, 2),
        scale = glm.vec3(1),
        rotation = glm.quat(),
        mesh = game.meshes['boat'],
        material = game.materials['boat']
    )
    
    level.add(floor, boat)

def ocean(level: Level) -> None:
    game = level.game
    
    water = Interactable(level, bsk.Node(
        position = (0, -1, 0),
        scale = (500, 0.5, 500),
        material = game.materials['ocean']
    ))
    setattr(water, 't', 0)
    def water_passive(dt: float) -> None:
        water.t += dt
        water.node.position.y = glm.sin(water.t) * 0.45 - 1
    water.passive = water_passive
    
    level.add(water)