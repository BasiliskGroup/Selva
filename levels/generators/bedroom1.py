import basilisk as bsk
import glm
import random
from typing import Callable
from helper.type_hints import Game
from levels.level import Level
from levels.interactable import Interactable
from levels.functions.imports import *
from levels.generators.bedroom import decor
from player.held_items.held_item import HeldItem, PictureFrame

def bedroom1(game: Game) -> Level:
    # create basic layout for bedroom level
    bedroom = Level(game, 'bedroom1', glm.vec3(2, 0, 2))

    def note_func(dt: float) -> None: bsk.draw.blit(game.engine, game.images['bedroom_note1.png'], (0, 0, game.win_size.x, game.win_size.y))
    decor(bedroom, note_func)
    this_decor(bedroom)
    add_locked_box(bedroom)
    key_interact = key(bedroom)
    bedroom.add(key_interact)
    drawers(bedroom, key_interact)
    safe(bedroom)
    mug(bedroom)
    
    return bedroom

def mug(bedroom: Level) -> None:
    game = bedroom.game
    
    mug = Interactable(bedroom, bsk.Node(
        position = (2.5, 2.25, 4.35),
        scale = glm.vec3(0.1),
        mesh = game.meshes['mug'],
        tags = ['empty_mug']
    ))
    mug.active = pickup_function(mug, interact_to_hold(mug, HeldItem(game, mug.node)))
    bedroom.add(mug)

def this_decor(bedroom: Level) -> None:
    game = bedroom.game
    
    bedroom.add(bsk.Node(
        position = (4.75, 3.2, 0),
        scale = (0.01, 0.9, 1.4),
        rotation = glm.angleAxis(glm.pi() / 2, (1, 0, 0)),
        material = game.materials['fortune_dresser']
    ))

def add_locked_box(bedroom: Level) -> None:
    locked_box_interact = locked_box(bedroom)
    bedroom.add(locked_box_interact)
    wheels(bedroom, locked_box_interact)
    bedroom.add(locked_lid(bedroom, locked_box_interact))
    
def key(level: Level) -> Interactable:
    node = bsk.Node(
        position = (3.5, 2.4, -4.35),
        scale = (0.1, 0.1, 0.1),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)) * glm.angleAxis(glm.pi() / 2, (1, 0, 0)),
        mesh = level.game.meshes['key']
    )
    key = Interactable(level, node)
    key.active = pickup_function(key, interact_to_hold(key, HeldItem(level.game, key.node)))
    return key

def drawer(level: Level, position: glm.vec3, check_func: Callable=None) -> Interactable:
    node = bsk.Node(
        position = position,
        scale = (1, 0.8, 0.8),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh = level.game.meshes['drawer']
    )
    drawer = Interactable(level, node)
    
    drawer.passive = lerp_difference(drawer, time = 0.25, delta_position = (0, 0, 1))
    drawer.active = lerp_interact(drawer, check_func = check_func)
    return drawer

def drawers(bedroom: Level, key: Interactable) -> None:
    game = bedroom.game
    
    drawers: list[Interactable] = [
        drawer(bedroom, position) for position in (
            glm.vec3(1.55, 0.6, -4.4), # bottom left
            glm.vec3(3.45, 1.4, -4.4), # top right
            glm.vec3(3.45, 0.6, -4.4)  # bottom right
        )
    ]
    bedroom.add(drawers)
    
    # bottom right drawer 
    p = glm.vec3(-0.3, 0, 0.4)
    john = bsk.Node(
        position = (3.7, 0.6, -4.4) + p,
        scale = (0.1, 0.1, 0.1),
        mesh = bedroom.game.meshes['john'],
        material = bedroom.game.materials['john'],
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)) * glm.angleAxis(glm.pi() / 2, (1, 0, 0)) * glm.angleAxis(glm.pi() / 3, (0, 1, 0))
    )
    john_interact = Interactable(bedroom, john)
    drawers[2].node.add(john)
    bedroom.add(john_interact)
    
    # bottom left drawer
    for node in [bsk.Node(
        position = position + p,
        scale = (0.06, 0.06, 0.06),
        mesh = bedroom.game.meshes['sock'],
        material = bedroom.game.materials['red'],
        rotation = glm.angleAxis(angle, (0, 1, 0))
    ) for position, angle in (
        ((1.8, 0.6, -4.8), glm.pi() / 3),
        ((2.1, 0.6, -4.5), -glm.pi() / 3),
        ((1.6, 0.6, -4.3), glm.pi()),
    )]: 
        drawers[0].node.add(node)
    
    # top right drawer
    for node in [bsk.Node(
        position = position + p,
        scale = (0.03, 0.03, 0.03),
        mesh = bedroom.game.meshes['brick'],
        material = bedroom.game.materials['red'],
        rotation = glm.angleAxis(angle, (0, 1, 0))
    ) for position, angle in (
        ((3.8, 1.4, -4.4), random.uniform(0, 2 * glm.pi())),
        ((4, 1.4, -4.5), random.uniform(0, 2 * glm.pi())),
        ((3.7, 1.4, -4.3), random.uniform(0, 2 * glm.pi())),
        ((3.4, 1.4, -4.2), random.uniform(0, 2 * glm.pi())),
        ((3.6, 1.4, -4.7), random.uniform(0, 2 * glm.pi())),
        ((3.5, 1.4, -4.8), random.uniform(0, 2 * glm.pi())),
    )]: 
        drawers[1].node.add(node)
    
    # function for opening locked drawer
    def check_func() -> bool:
        if not bedroom.game.key_down(bsk.pg.K_e) or not bedroom.game.player.item_r or not bedroom.game.player.item_r.node == key.node: return False
        bedroom.game.player.item_r_ui.remove(bedroom.game.player.item_r) # removes key from the player's inventory
        return True

    locked_drawer = drawer(bedroom, glm.vec3(1.55, 1.4, -4.4), check_func = check_func)
    frame_node = bsk.Node(
        position = (1.55, 1.45, -3.9),
        mesh = game.meshes['picture_frame'], 
        material = game.materials['picture_frame'],
        scale = glm.vec3(0.25),
        rotation = glm.angleAxis(-glm.pi() / 2, (1, 0, 0)) * glm.angleAxis(glm.pi() / 2, (0, 1, 0))
    )
    frame = Interactable(bedroom, frame_node)
    
    def frame_passive(dt: float) -> None:
        frame.node.position.z = locked_drawer.node.position.z + 0.25
    
    frame_pickup = pickup_function(frame, interact_to_frame(frame, PictureFrame(game, 'office')))
    def frame_active(dt: float) -> None:
        frame.passive = None
        frame_pickup(dt)
    
    frame.active = frame_active
    frame.passive = frame_passive
    
    bedroom.add(frame, locked_drawer)

def locked_box(level: Level) -> Interactable:
    node = bsk.Node(
        position = (3.5, 2.25, -4.35),
        scale = (0.5, 0.5, 0.5),
        mesh = level.game.meshes['box_three'],
        material = level.game.materials['box_three']
    )
    locked_box = Interactable(level, node)        
    return locked_box

def wheels(bedroom: Level, locked_box: Interactable) -> None:
    game = bedroom.game
    
    wheels = [bsk.Node(
        position = (3.5 + 0.15 * i, 2.25, -3.85),
        scale = (0.07, 0.07, 0.07),
        mesh = game.meshes['wheel_eight'],
        material = game.materials['wheel_eight']
    ) for i in range(-1, 2)]
    bedroom.add(wheels)
    
    locked_wheels = {wheel : free_axis_xy(locked_box, (1, 0, 0), wheel, sensitivity = 0.6) for wheel in wheels}
    setattr(locked_box, 'wheels', locked_wheels)
    setattr(locked_box, 'timer', 0)
    setattr(locked_box, 'selected', None)
    setattr(locked_box, 'prev_left_down', False)
    setattr(locked_box, 'code', [1, 1, 1])
    
    def loop_func(dt) -> None:
        if game.mouse.left_down:
            if not locked_box.prev_left_down:
                cast = game.current_scene.raycast_mouse(game.mouse.position, has_collisions=False)
                locked_box.selected = cast.node
            if locked_box.selected in locked_box.wheels:
                locked_box.wheels[locked_box.selected](dt)
        
        for index, wheel in enumerate(locked_box.wheels):
            wheel.rotational_velocity = wheel.rotational_velocity * (1 - game.engine.delta_time * 5) if glm.length2(wheel.rotational_velocity) > 1e-7 else glm.vec3(0, 0, 0)
            
            # compute and adjust the rotation angle for generating input code
            angle = glm.angle(wheel.rotation.data)
            if glm.axis(wheel.rotation.data).x < 1: angle -= 2 * glm.pi()
            angle = (abs(angle) - glm.pi() / 8) % (2 * glm.pi())
            
            # compute input code from angle
            locked_box.code[index] = 8 - int(angle / glm.pi() * 4)
        
        locked_box.prev_left_down = game.mouse.left_down
    
    locked_box.active = pan_loop(
        interact = locked_box, 
        time = 0.5, 
        position = locked_box.node.position.data + glm.vec3(0, 0, 1.5),
        rotation = glm.quat(),
        loop_func = loop_func
    )
    
def locked_lid(bedroom: Level, locked_box: Interactable) -> Interactable:
    parent = bsk.Node( # TODO make this invisible or a hinge
        position = locked_box.node.position.data + glm.vec3(0, 0.375, -0.4),
        scale = (0.1, 0.1, 0.1),
        rotation = glm.angleAxis(0.2, (1, 0, 0))
    )
    node = bsk.Node(
        position = parent.position + (0, 0.125, 0.425),
        scale = locked_box.node.scale,
        mesh = bedroom.game.meshes['box_three_lid'],
    )
    bedroom.add(parent)
    parent.add(node)
    locked_lid = Interactable(bedroom, node)
    
    def check_func() -> bool:
        return bedroom.game.key_down(bsk.pg.K_e) and locked_box.code == [3, 6, 1] #NOTE this is the code for the locked box
    
    locked_lid.passive = lerp_difference(locked_lid, node = parent, time = 0.25, delta_rotation = glm.angleAxis(glm.pi() / 2, (1, 0, 0)))
    locked_lid.active = lerp_interact(locked_lid, check_func = check_func)
    
    return locked_lid

def safe(level: Level) -> None:
    game = level.game
    
    safe = Interactable(level, bsk.Node(
        position = (1.5, 0.95, 4.6),
        rotation = glm.angleAxis(glm.pi(), (0, 1, 0)),
        scale = (0.7, 0.7, 0.7),
        mesh = game.meshes['safe'],
        material = game.materials['black']
    ))
    setattr(safe, 'buttons', [])
    setattr(safe, 'code', [0 for _ in range(4)])
    setattr(safe, 'locked', True)
    setattr(safe, 'holding_handle', False)
    
    safe_handle = Interactable(level, bsk.Node(
        position = (1.85, 0.95, 3.9),
        rotation = glm.angleAxis(glm.pi(), (0, 1, 0)),
        scale = (0.7, 0.7, 0.7),
        mesh = game.meshes['safe_door_handle'],
        material = game.materials['black']
    ))
    setattr(safe_handle, 'open', False)
    setattr(safe, 'handle', safe_handle)
    
    handle_rotate = free_axis(safe_handle, (0, 0, 1), safe_handle.node)
    
    def loop_func(dt: float) -> None:
        safe_handle.node.rotational_velocity = safe_handle.node.rotational_velocity * (1 - game.engine.delta_time) if glm.length2(safe_handle.node.rotational_velocity) > 1e-7 else glm.vec3(0, 0, 0)
        safe_handle.open = glm.dot(glm.axis(safe_handle.node.rotation.data), (-0.68, 0.72, 0)) > 0.9 or glm.dot(glm.axis(safe_handle.node.rotation.data), (0.68, -0.72, 0)) > 0.9
        if not game.mouse.left_down: 
            safe.holding_handle = False
            return
        cast = game.current_scene.raycast_mouse(game.mouse.position, has_collisions=False)
        if game.mouse.left_down and (cast.node == safe.handle.node or safe.holding_handle) and not safe.locked:
            safe.holding_handle = True
            handle_rotate(dt)
        else: safe.holding_handle = False
        if not game.mouse.left_click: return
        if cast.node in [i.node for i in safe.buttons]: 
            button = safe.buttons[[i.node for i in safe.buttons].index(cast.node)]
            if button.percent == 0: button.step = 1
            game.sounds['keycap'].play()
        safe.locked = safe.code != [2, 1, 6, 9]
    
    safe.active = pan_loop(safe, rotation = glm.quatLookAt((0, 0, 1), (0, 1, 0)), position = (1.5, 0.95, 2), time = 0.5, loop_func = loop_func)
    
    safe_door = Interactable(level, bsk.Node(
        position = (1.5, 0.95, 4),
        rotation = glm.angleAxis(glm.pi(), (0, 1, 0)),
        scale = (0.7, 0.7, 0.7),
        mesh = game.meshes['safe_door'],
        material = game.materials['safe_door']
    ))
    hinge = bsk.Node(
        position = (1, 0.95, 4),
        scale = (0.02, 0.02, 0.02)
    )
    safe_door.passive = lerp_difference(safe_door, hinge, 0.5, delta_rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)))

    def door_func(dt: float) -> None:
        if not safe_handle.open: safe.active(dt)
        else: 
            for button in safe.buttons: button.passive = empty
            safe_door.step = 1
        
    safe_door.active = door_func
    hinge.add(safe_door.node)
    hinge.add(safe_handle.node)
    
    for y in range(1, -2, -1):
        for x in range(1, -2, -1):
            position = glm.vec3(1.3 - 0.1 * x, 0.95 - 0.1 * y, 3.9)
            keycap = Interactable(level, bsk.Node(
                position = position,
                rotation = glm.angleAxis(glm.pi() / 2, (1, 0, 0)) * glm.angleAxis(glm.pi(), (0, 0, 1)),
                scale = (0.8, 0.8, 0.8),
                mesh = game.meshes['keycap'],
                material = game.materials[f'key{(x + 2) + (y + 1) * 3}'],
            ))
            setattr(keycap, 'safe', safe)
            setattr(keycap, 'number', (x + 2) + (y + 1) * 3)
            
            def end_func(dt: float, keycap=keycap) -> None:
                keycap.step = -1
                safe.code.pop(0)
                safe.code.append(keycap.number)
                print(keycap.number)
                
            keycap.passive = lerp_difference(interact = keycap, node = keycap.node, time = 0.05, delta_position = glm.vec3(0, 0, 0.05), end_func = end_func)
            safe.buttons.append(keycap)
            hinge.add(keycap.node)
            level.add(keycap)
    
    level.add(hinge)
    level.add(safe_handle)
    level.add(safe)
    level.add(safe_door)
    

