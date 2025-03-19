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

def office(game: Game) -> Level:
    # create basic layout for bedroom level
    office = Level(game)
    office.add(*rect_room(0, 0, 8, 8, 5, game.materials['light_white']))
    
    battery_box(office)
    
    return office
    
def battery_box(office: Level) -> None:
    game = office.game
    
    # add the battery into the scene
    battery = Interactable(office, bsk.Node(
        position = (0, 1, 2),
        scale = glm.vec3(0.2),
        # mesh = game.meshes['battery']
    ))
    battery.active = pickup_function(battery, interact_to_hold(battery, HeldItem(game, battery.node)))
    office.add(battery)
    
    # add the battery box
    def check_in(dt: float) -> bool: return game.key_down(bsk.pg.K_e)
    
    sockets = [Interactable(
        office,
        bsk.Node(
            position = (-2, 2, 0.25 * z),
            scale = glm.vec3(0.2),
            rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
            mesh = game.meshes['battery_box']
        )
    ) for z in range(-1, 2)]
    for socket in sockets: socket.active = place(socket, rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)), check_in_func = check_in, check_out_func = check_in, put_in_func = None, pull_out_func = None)
    
    office.add(sockets)