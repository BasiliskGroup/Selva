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
    office.add(*rect_room(0, 0, 8, 8, 4, game.materials['dirty_carpet'], game.materials['bright_wood'], game.materials['bright_wood']))
    
    desk(office)
    puzzle(office)
    coffee_table(office)
    
    return office
    
def puzzle(office: Level) -> None:
    game = office.game
    
    # computer
    computer = Interactable(office, bsk.Node(
        position = (0.5, 2.25, 0),
        scale    = glm.vec3(0.4),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        mesh     = game.meshes['crt'],
        material = game.materials['crt']
    ))
    setattr(computer, 'on', False)
    
    def computer_loop_func(dt: float) -> None: 
        if computer.on: 
            print('teleport')
            game.update = game.primary_update
    
    def computer_active(dt: float) -> None:
        pan_loop(computer, time = 0.5, position = (1.5, 2.25, 0), rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)), loop_func = computer_loop_func)(dt)
    
    computer.active = computer_active
    
    # add the battery into the scene
    battery = Interactable(office, bsk.Node(
        position = (0, 1, 3),
        scale    = glm.vec3(0.2),
        mesh     = game.meshes['battery'], # TODO enable when jonah figures out why its throwing errors
        material = game.materials['battery'],
        tags     = ['battery']
    ))
    battery.active = pickup_function(battery, interact_to_hold(battery, HeldItem(game, battery.node)))
    
    # add the battery box
    def check_out(dt: float) -> bool: return game.key_down(bsk.pg.K_e)
    def check_in(dt: float) -> bool:  return game.key_down(bsk.pg.K_e) and game.player.item_r and game.player.item_r.node.tags == ['battery']
    
    # left socket (computer)
    def left_in(dt: float) -> None:  computer.on = True
    def left_out(dt: float) -> None: computer.on = False
    
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
            mesh     = game.meshes['battery_box'],
            material = game.materials['battery_box']
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
        position = (0.5, 1.65, 0),
        scale    = glm.vec3(0.8),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        mesh     = game.meshes['work_desk'],
        material = game.materials['bright_wood']
    )
    
    drawers = [Interactable(office, bsk.Node(
        position = (0.7, 0.5 + i * 0.75, 0.8),
        scale    = glm.vec3(0.65),
        mesh     = game.meshes['drawer'],
        material = game.materials['light_wood']
    )) for i in range(2)]
    for drawer in drawers:
        drawer.passive = lerp_difference(drawer, time = 0.25, delta_position = (1, 0, 0))
        drawer.active  = lerp_interact(drawer)
    
    office.add(drawers)
    office.add(desk)
    
def coffee_table(office: Level) -> None:
    game = office.game
    
    table = bsk.Node(
        position = (-1.5, 1.65, 0),
        scale    = glm.vec3(0.8),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh     = game.meshes['desk'],
        material = game.materials['light_wood']
    )
    
    office.add(table)