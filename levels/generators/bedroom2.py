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
    
    return bedroom
    