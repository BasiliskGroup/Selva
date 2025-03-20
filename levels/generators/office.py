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
    office.add(*rect_room(0, 0, 8, 8, 4, game.materials['light_white']))
    
    desk(office)
    puzzle(office)
    
    return office
    
def puzzle(office: Level) -> None:
    game = office.game
    
    # computer
    computer = Interactable(office, bsk.Node(
        position = (0, 2.5, 0),
        scale = glm.vec3(0.5),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['crt'],
        material = game.materials['crt']
    ))
    setattr(computer, 'on', False)
    
    def computer_loop_func(dt: float) -> None: 
        if computer.on: game.update = game.primary_update
    
    def computer_active(dt: float) -> None:
        pan_loop(computer, time = 0.5, position = (1.5, 2.5, 0), rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)), loop_func = computer_loop_func)(dt)
    
    computer.active = computer_active
    
    # add the battery into the scene
    battery = Interactable(office, bsk.Node(
        position = (0, 1, 3),
        scale = glm.vec3(0.2),
        mesh = game.meshes['battery'], # TODO enable when jonah figures out why its throwing errors
        material = game.materials['battery'],
        tags = ['battery']
    ))
    battery.active = pickup_function(battery, interact_to_hold(battery, HeldItem(game, battery.node)))
    
    # add the battery box
    def check_out(dt: float) -> bool: return game.key_down(bsk.pg.K_e)
    def check_in(dt: float) -> bool:  return game.key_down(bsk.pg.K_e) and game.player.item_r and game.player.item_r.node.tags == ['battery']
    
    # left socket (computer)
    def left_in(dt: float) -> None:  ...
    def left_out(dt: float) -> None: ...
    
    # center socket (light) NOTE could be !game.day for both but separated for security
    def center_in(dt: float) -> None:  game.day = False
    def center_out(dt: float) -> None: game.day = True
    
    # right socket (coffee)
    def right_in(dt: float) -> None:  ...
    def right_out(dt: float) -> None: ...
    
    sockets = [Interactable(
        office,
        bsk.Node(
            position = (-2, 2.5, 0.25 * z),
            scale    = glm.vec3(0.2),
            rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
            mesh     = game.meshes['battery_box']
        )
    ) for z in range(-1, 2)]
    for socket, (put, pull) in zip(sockets, ((left_in, left_out), (center_in, center_out), (right_in, right_out))): 
        socket.active = place(socket, rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)), check_in_func = check_in, check_out_func = check_out, put_in_func = put, pull_out_func = pull)
    
    office.add(computer)
    office.add(battery)
    office.add(sockets)
    
def desk(office: Level) -> None:
    game = office.game
    
    desk = bsk.Node(
        position = (0, 2, 0),
        scale = glm.vec3(0.65),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['work_desk']
    )
    
    office.add(desk)