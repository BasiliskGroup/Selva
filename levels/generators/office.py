import basilisk as bsk
import glm
import random
from typing import Callable
from helper.type_hints import Game
from levels.level import Level
from levels.helper import rect_room
from levels.interactable import Interactable
from levels.functions.imports import *

def office(game: Game) -> Level:
    # create basic layout for bedroom level
    office = Level(game)
    office.add(*rect_room(0, 0, 5.75, 6.75, 4, game.materials['light_white']))
    
