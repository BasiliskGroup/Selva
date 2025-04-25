import basilisk as bsk
import glm
import random
from player.held_items.held_item import HeldItem
from player.held_items.interpolate import lerp_held
from helper.type_hints import Game
from levels.level import Level
from levels.helper import rect_room
from levels.interactable import Interactable
from levels.functions.imports import *
from helper.transforms import connect

def generate_chain(level: Level, positions: list[glm.vec3]) -> list[bsk.Node]:
    positions = [glm.vec3(p) for p in positions]
    nodes = []
    for i in range(len(positions) - 1):
        pos, sca, rot = connect(positions[i], positions[i + 1])
        nodes.append(bsk.Node(
            position = pos,
            scale = sca,
            rotation = rot,
            material = level.game.materials['black']
        ))
    return nodes

def office(game: Game) -> Level:
    # create basic layout for bedroom level
    office = Level(game, 'office', glm.vec3(0, 0, 3))
    office.add(*rect_room(0, 0, 8, 8, 4, game.materials['dirty_carpet'], game.materials['bright_wood'], game.materials['bright_wood']))
    
    desk(office)
    puzzle(office)
    coffee_table(office)
    decor(office)
    wires(office)
    note(office)
    
    return office
    
def puzzle(office: Level) -> None:
    game = office.game
    
    # computer
    computer = Interactable(office, bsk.Node(
        position = (-0.5, 2.4, 0),
        scale    = glm.vec3(0.4),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        mesh     = game.meshes['crt'],
        material = game.materials['crt']
    ))
    setattr(computer, 'on', False)
    setattr(computer, 'stage', 'off')
    
    def computer_leave_check_func(dt: float) -> bool:
        return not computer.on
    
    def computer_loop_func(dt: float) -> None: 
        if not computer.on: return
        match computer.stage:
            case 'off':
                # create portal
                game.close()
                game.open(game.memory_handler['boat'])
                # game.portal_handler.portal.scale = glm.vec3()
                computer.stage = 'opening'
            case 'opening':
                # grow portal to edges of screen
                # game.portal_handler.portal.scale = 
                computer.stage = 'teleport'
            case 'teleport':
                # teleport the player
                # exit loop with variables
                computer.stage = 'off'
    
    def computer_active(dt: float) -> None:
        pan_loop(computer, time = 0.5, position = (0.5, 2.4, 0), rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)), loop_func = computer_loop_func, leave_check_func = computer_leave_check_func)(dt)
    
    computer.active = computer_active
    
    # coffee maker
    coffee_maker = Interactable(office, bsk.Node(
        position = (-2.8, 2.25, 0.6),
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
    
    top = glm.vec3(-2.85, 2.5, 0.6)
    bottom = glm.vec3(-2.85, 2, 0.6)
    vel = glm.vec3(0, 1, 0)
    
    def coffee_check_out(dt: float) -> bool: return game.key_down(bsk.pg.K_e) and coffee_maker.stage == 'done'
    def coffee_check_in(dt: float) -> bool:  return game.key_down(bsk.pg.K_e) and coffee_maker.stage == 'done' and game.player.item_r and game.player.item_r.node.tags == ['empty_mug']
    def coffee_passive(dt: float) -> None:
        pos, sca, rot = connect(coffee_maker.top, coffee_maker.bottom, coffee_maker.width)
        coffee_node.position = pos
        coffee_node.scale = sca
        coffee_node.rotation = rot
        if not coffee_maker.held_item: return
        match coffee_maker.stage:
            case 'done': 
                if not coffee_maker.held_item.node.tags == ['empty_mug'] or not coffee_maker.on: return
                coffee_maker.stage = 'starting'
                coffee_maker.time = 0
                coffee_maker.top = glm.vec3(top)
                coffee_maker.bottom = top - (0, 0.01, 0)
            case 'starting': 
                coffee_maker.time += dt
                coffee_maker.width += 0.01 * dt
                coffee_maker.bottom -= vel * dt
                if coffee_maker.time < 0.8: return 
                coffee_maker.stage = 'filling'
                coffee_maker.time = 0
            case 'filling':
                coffee_maker.time += dt
                coffee_maker.width = 0.01 + 0.005 * glm.sin(coffee_maker.time)
                if coffee_maker.time > 2: 
                    coffee_maker.stage = 'stopping'
                    coffee_maker.time = 0
                    held_item = coffee_maker.held_item
                    held_item.node.material = game.materials['coffee_mug']
                    held_item.node.mesh = game.meshes['coffee_mug']
            case 'stopping':
                coffee_maker.time += dt
                coffee_maker.width -= 0.01 * dt
                coffee_maker.top -= vel * dt
                if coffee_maker.time < 0.8: return 
                
                coffee_maker.stage = 'done'
                coffee_maker.time = 0
                coffee_maker.top = glm.vec3(0, 100, 0)
                coffee_maker.bottom = glm.vec3(0, 99, 0)
                
                # set mug to coffee mug
                held_item = coffee_maker.held_item
                held_item.node.tags = ['coffee_mug']
                setattr(held_item, 'coffee_remaining', 2)
                held_item.offset = glm.vec3(0)
                held_item.rotation = glm.quat()
                
                def coffee_mug_end_func(dt: float) -> None:
                    # TODO play slerp sound effect
                    print(game.player.item_r.coffee_remaining)
                    game.player.item_r.coffee_remaining -= dt
                    if game.player.item_r.coffee_remaining > 0: return
                    game.player.item_r.node.mesh = game.meshes['mug']
                    game.player.item_r.node.material = game.materials['white']
                    game.player.item_r.node.tags = ['empty_mug']
                    
                    game.player.item_r_ui.node.mesh = game.meshes['mug']
                    game.player.item_r_ui.node.material = game.materials['white']
                    game.player.item_r_ui.node.tags = ['empty_mug']
                
                mug_lerp = lerp_held(held_item, time = 0.2, position = glm.vec3(-0.42, -0.05, -0.6), rotation = glm.angleAxis(-glm.pi() / 4, (1, 0, 0)), end_func = coffee_mug_end_func)
                def coffee_mug_func(dt: float) -> None:
                    mug_lerp(dt)
                    
                held_item.func = coffee_mug_func
    
    coffee_maker.active = place(coffee_maker, coffee_maker.node.position.data + glm.vec3(-0.1, -0.25, 0), check_in_func = coffee_check_in, check_out_func = coffee_check_out, put_in_func = None, pull_out_func = None)
    coffee_maker.passive = coffee_passive # TODO make coffee
    
    coffee_icon = bsk.Node(
        position = (-3.125, 2.675, 0.6),
        scale = glm.vec3(0.05),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['coffee_icon'],
        material = game.materials['red']
    )
    
    # add the battery into the scene
    battery = Interactable(office, bsk.Node(
        position = (-3, 1.8, 3),
        scale    = glm.vec3(0.2),
        mesh     = game.meshes['battery'],
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
            position = (-2.8, 2.1, 0.25 * z - 1),
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
        position = (-0.5, 1.75, 0),
        scale    = glm.vec3(0.85),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        mesh     = game.meshes['work_desk'],
        material = game.materials['bright_wood']
    )
    
    # add drawers
    bottom_drawer = Interactable(office, bsk.Node(
        position = (-0.3, 0.5, 0.9),
        scale    = glm.vec3(0.65),
        mesh     = game.meshes['drawer'],
        material = game.materials['light_wood']
    ))
    bottom_drawer.passive = lerp_difference(bottom_drawer, time = 0.25, delta_position = (1, 0, 0))
    bottom_drawer.active = lerp_interact(bottom_drawer)
    
    def lock_drawer_check(dt: float=0) -> bool:
        if not game.key_down(bsk.pg.K_e) or not game.player.item_r or not game.player.item_r.node.tags == ['color_key']: return False
        game.player.item_r_ui.remove(game.player.item_r)
        return True
        
    top_drawer = Interactable(office, bsk.Node(
        position = (-0.3, 1.3, 0.9),
        scale    = glm.vec3(0.65),
        mesh     = game.meshes['drawer'],
        material = game.materials['drawer_color']
    ))
    top_drawer.passive = lerp_difference(top_drawer, time = 0.25, delta_position = (1, 0, 0))
    top_drawer.active = lerp_interact(top_drawer, check_func = lock_drawer_check)
    
    # add copper wire
    wire = Interactable(office, bsk.Node(
        position = (-0.3, 0.5, 0.9),
        scale = glm.vec3(0.3),
        mesh = game.meshes['wire'],
        material = game.materials['copper'],
        tags = ['copper_wire']
    ))
    wire_pickup = pickup_function(wire, interact_to_hold(wire, HeldItem(game, wire.node)))
    def wire_active(dt: float) -> None:
        wire.passive = None
        wire_pickup(dt)
    
    def wire_passive(dt: float) -> None: wire.node.position.x = bottom_drawer.node.position.x + 0.25
    wire.passive = wire_passive
    wire.active = wire_active
    
    office.add(desk, bottom_drawer, top_drawer, wire)
    
def coffee_table(office: Level) -> None:
    game = office.game
    
    table = bsk.Node(
        position = (-2.5, 1.65, 0),
        scale    = glm.vec3(0.8),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh     = game.meshes['desk'],
        material = game.materials['light_wood']
    )
    
    office.add(table)
    
def decor(office: Level) -> None:
    game = office.game
    
    windows = [bsk.Node(
        position = (6.9, 3.5, 1.8 * i),
        scale = glm.vec3(0.85),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['office_window'],
        material = game.materials['office_window']
    ) for i in range(-1, 2)] + [bsk.Node(
        position = (-6.9, 3.5, 1.8 * i),
        scale = glm.vec3(0.85),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['office_window'],
        material = game.materials['office_window']
    ) for i in range(-1, 2)]
    
    # cubicle and colliders
    cubicle = bsk.Node(
        position = (0, 1.5, 0),
        scale = glm.vec3(0.65),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['cubicle'],
        material = game.materials['dark_wood']
    )
    cubicle_colliders = [
        bsk.Node(
            position = (-1.5, 1.5, 0),
            scale = (0.1, 2.5, 2),
            collision = True,
            static = True,
            shader = game.shaders['invisible']
        ),
        bsk.Node(
            position = (0, 1.5, 2),
            scale = (1.5, 2.5, 0.1),
            collision = True,
            static = True,
            shader = game.shaders['invisible']
        ),
        bsk.Node(
            position = (0, 1.5, -2),
            scale = (1.5, 2.5, 0.1),
            collision = True,
            static = True,
            shader = game.shaders['invisible']
        ),
        bsk.Node(
            position = (-1.5, 0.75, 0),
            scale = (2, 1, 2),
            collision = True,
            static = True,
            shader = game.shaders['invisible']
        )
    ]
    
    posters = [
        bsk.Node(
            position = (2, 4, 7),
            scale = (1.25, 0.75, 0.002),
            rotation = glm.angleAxis(glm.pi() / 2, (0, 0, 1)),
            material = game.materials['hang_in_there']
        ),
        bsk.Node(
            position = (-3.5, 3.5, 7),
            scale = (1.25, 0.75, 0.002),
            rotation = glm.angleAxis(glm.pi() / 2, (0, 0, 1)),
            material = game.materials['scan_me']
        ),
        bsk.Node(
            position = (-1, 4, 7),
            scale = (0.75, 1.25, 0.002),
            rotation = glm.angleAxis(glm.pi() / 2, (0, 0, 1)),
            material = game.materials['i_love_barcodes']
        ),
    ]
    
    calendar = bsk.Node(
        position = (3.5, 3, 7),
        scale = (0.333, 0.5, 0.002),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 0, 1)),
        material = game.materials['calendar']
    )
    
    door = bsk.Node(
        position = (0, 2.65, -7),
        scale = glm.vec3(0.65),
        rotation = glm.angleAxis(0, (0, 1, 0)),
        mesh = game.meshes['fake_door'],
        material = game.materials['fake_door']
    )
    
    office.add(windows, cubicle, posters, door, calendar, cubicle_colliders)
    
    # add bulb
    office.add(bsk.Node(
        position = (0, 4.9, 0),
        scale = glm.vec3(0.1),
        rotation = glm.angleAxis(glm.pi(), (1, 0, 0)),
        material = game.materials['bulb'],
        mesh = game.meshes['bulb']
    ))
    
    # chair
    office.add(bsk.Node(
        position = (1.1, 0.75, -1),
        scale = glm.vec3(0.4),
        rotation = glm.angleAxis(0.7, (0, 1, 0)),
        mesh = game.meshes['office_chair'],
        material = game.materials['black']
    ))
    
def wires(office: Level) -> None:
    chains = [
        # computer
        [(-2.65, 1.8, -1.25), (-2.65, 1.8, -1.62), (-2.65, 0.1, -1.62), (-2.65, 0.1, -2.3), (1.85, 0.1, -2.3), (1.85, 0.1, -1.8), (-0.5, 0.1, -1.8), (-0.5, 1.9, -1.8), (-0.5, 1.9, 0)],
        # light
        [(-2.65, 1.8, -1), (-2.45, 1.8, -1), (-2.45, 7, -1), (0, 7, -1), (0, 7, 0), (0, 5, 0)],
        # coffee
        [(-2.65, 1.8, -0.75), (-2.65, 1.8, 0.8)],
    ]
    
    for chain in chains: office.add(generate_chain(office, chain))

def note(level: Level) -> None:
    game = level.game
    engine = game.engine
    
    note = Interactable(level, bsk.Node(
        position = glm.vec3(-0.3, 1.9, 1),
        scale = (0.4, 0.01, 0.5),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        material = game.materials['paper'],
        mesh = game.meshes['paper']
    ))
    
    def p1(dt: float) -> None: 
        def p1(dt: float) -> None: bsk.draw.blit(engine, game.images['office_ad.png'], (0, 0, game.win_size.x, game.win_size.y))

    pages = [p1]
    note.active = book(note, pages)
    
    level.add(note)