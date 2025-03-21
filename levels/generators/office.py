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

def office(game: Game) -> Level:
    # create basic layout for bedroom level
    office = Level(game)
    office.add(*rect_room(0, 0, 8, 8, 4, game.materials['dirty_carpet'], game.materials['bright_wood'], game.materials['bright_wood']))
    
    desk(office)
    puzzle(office)
    coffee_table(office)
    decor(office)
    
    # TODO temporary
    mug = Interactable(office, bsk.Node(
        position = (3.5, 2.25, 4.35),
        scale = glm.vec3(0.1),
        # mesh = game.meshes['mug'],
        tags = ['empty_mug']
    ))
    mug.active = pickup_function(mug, interact_to_hold(mug, HeldItem(game, mug.node)))
    office.add(mug)
    
    return office
    
def puzzle(office: Level) -> None:
    game = office.game
    
    # computer
    computer = Interactable(office, bsk.Node(
        position = (0.5, 2.4, 0),
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
        pan_loop(computer, time = 0.5, position = (1.5, 2.4, 0), rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)), loop_func = computer_loop_func)(dt)
    
    computer.active = computer_active
    
    # coffee maker
    coffee_maker = Interactable(office, bsk.Node(
        position = (-1.8, 2.25, 0.6),
        scale = glm.vec3(0.5),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['coffee_maker'],
        material = game.materials['coffee_maker']
    ))
    coffee_node = bsk.Node(
        position = (0, 100, 0),
        mesh = game.meshes['cylinder'],
        material = game.materials['dark_wood']
    )
    setattr(coffee_maker, 'on', False)
    setattr(coffee_maker, 'stage', 'done')
    setattr(coffee_maker, 'time', 0)
    setattr(coffee_maker, 'top', glm.vec3(0, 100, 0))
    setattr(coffee_maker, 'bottom', glm.vec3(0, 99, 0))
    setattr(coffee_maker, 'width', 0.001)
    
    top = glm.vec3(-1.8, 2.5, 0.6)
    bottom = glm.vec3(-1.8, 2, 0.6)
    vel = glm.vec3(0, 10, 0)
    
    def coffee_check_out(dt: float) -> bool: return game.key_down(bsk.pg.K_e) and coffee_maker.stage == 'done'
    def coffee_check_in(dt: float) -> bool:  return game.key_down(bsk.pg.K_e) and coffee_maker.stage == 'done' and game.player.item_r and game.player.item_r.node.tags == ['empty_mug']
    def coffee_passive(dt: float) -> None:
        pos, sca, rot = connect(coffee_maker.top, coffee_maker.bottom, coffee_maker.width)
        print(sca)
        coffee_node.position = pos
        coffee_node.scale = sca
        coffee_node.rotation = rot
        if not coffee_maker.held_item: return
        match coffee_maker.stage:
            case 'done': 
                print('done')
                if not coffee_maker.held_item.node.tags == ['empty_mug'] or not coffee_maker.on: return
                coffee_maker.stage = 'starting'
                coffee_maker.time = 0
                coffee_maker.top = glm.vec3(top)
                coffee_maker.bottom = top - (0, 0.01, 0)
            case 'starting': 
                print('starting')
                coffee_maker.time += dt
                coffee_maker.width += 0.1 * dt
                coffee_maker.bottom -= vel * dt
                if coffee_maker.time < 0.1: return 
                coffee_maker.stage = 'filling'
                coffee_maker.time = 0
            case 'filling':
                coffee_maker.stage = 'stopping'
            case 'stopping':
                print('stopping')
                coffee_maker.time += dt
                coffee_maker.width -= 0.1 * dt
                coffee_maker.top -= vel * dt
                if coffee_maker.time < 0.1: return 
                coffee_maker.stage = 'done'
                coffee_maker.time = 0
                coffee_maker.top = glm.vec3(0, 100, 0)
                coffee_maker.bottom = glm.vec3(0, 99, 0)
    
    coffee_maker.active = place(coffee_maker, coffee_maker.node.position.data + glm.vec3(-0.1, -0.25, 0), check_in_func = coffee_check_in, check_out_func = coffee_check_out, put_in_func = None, pull_out_func = None)
    coffee_maker.passive = coffee_passive # TODO make coffee
    
    coffee_icon = bsk.Node(
        position = (-2.125, 2.675, 0.6),
        scale = glm.vec3(0.05),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['coffee_icon'],
        material = game.materials['red']
    )
    
    # add the battery into the scene
    battery = Interactable(office, bsk.Node(
        position = (-2, 1.8, 3),
        scale    = glm.vec3(0.2),
        # mesh     = game.meshes['battery'], # TODO enable when jonah figures out why its throwing errors
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
    def right_in(dt: float) -> None:  
        coffee_maker.on = True
        coffee_icon.material = game.materials['green']
    def right_out(dt: float) -> None: 
        coffee_maker.on = False
        coffee_icon.material = game.materials['red']
    
    sockets = [Interactable(
        office,
        bsk.Node(
            position = (-1.8, 2.1, 0.25 * z - 1),
            scale    = glm.vec3(0.2),
            rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
            mesh     = game.meshes['battery_box'],
            material = game.materials['battery_box']
        )
    ) for z in range(-1, 2)]
    for socket, (put, pull) in zip(sockets, ((left_in, left_out), (center_in, center_out), (right_in, right_out))): 
        socket.active = place(socket, rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)), check_in_func = check_in, check_out_func = check_out, put_in_func = put, pull_out_func = pull)
    
    office.add(coffee_maker, coffee_icon, computer, battery, sockets, coffee_node)
    
def desk(office: Level) -> None:
    game = office.game
    
    desk = bsk.Node(
        position = (0.5, 1.75, 0),
        scale    = glm.vec3(0.85),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        mesh     = game.meshes['work_desk'],
        material = game.materials['bright_wood']
    )
    
    drawers = [Interactable(office, bsk.Node(
        position = (0.7, 0.5 + i * 0.8, 0.9),
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
    
def decor(office: Level) -> None:
    game = office.game
    
    window = bsk.Node(
        position = (6.9, 3.5, 0),
        scale = glm.vec3(0.85),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['office_window'],
        material = game.materials['office_window']
    )
    
    cubicle = bsk.Node(
        position = (1, 1.5, 0),
        scale = glm.vec3(0.65),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['cubicle'],
        material = game.materials['dark_wood']
    )
    
    
    
    office.add(window, cubicle)