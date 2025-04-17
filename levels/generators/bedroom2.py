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

def safe(level: Level) -> None:
    game = level.game
    
    safe = Interactable(level, bsk.Node( 
        position = (1.5, 0.95, 4.6),
        rotation = glm.angleAxis(glm.pi(), (0, 1, 0)),
        scale = (0.7, 0.7, 0.7),
        mesh = game.meshes['safe'],
        material = game.materials['red']
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
        material = game.materials['red']
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
        safe.locked = safe.code != [1, 2, 3, 4]
    
    safe.active = pan_loop(safe, rotation = glm.quatLookAt((0, 0, 1), (0, 1, 0)), position = (1.5, 0.95, 2), time = 0.5, loop_func = loop_func)
    
    safe_door = Interactable(level, bsk.Node(
        position = (1.5, 0.95, 4),
        rotation = glm.angleAxis(glm.pi(), (0, 1, 0)),
        scale = (0.7, 0.7, 0.7),
        mesh = game.meshes['safe_door']
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
                rotation = glm.angleAxis(glm.pi() / 2, (1, 0, 0)),
                scale = (0.8, 0.8, 0.8),
                mesh = game.meshes['keycap'],
                material = game.materials['red'],
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