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
    bucket(level)
    
    return level

def fishing(level: Level) -> None:
    game = level.game
    
    tip_pos = glm.vec3(-1.5, 4.5, 13.5)
    handle_pos = glm.vec3(-2.5, 1.5, 6.5)
    rod_pivot = bsk.Node(
        position = glm.normalize(tip_pos - handle_pos) * 0.3 + handle_pos,
        scale = glm.vec3(0.1),
    )
    pos, sca, rot = connect(handle_pos, tip_pos, 3)
    rod = Interactable(level, bsk.Node(
        position = pos,
        scale = sca,
        rotation = rot,
        mesh = game.meshes['fishing_rod'],
        material = game.materials['fishing_rod']
    ))
    tip_tracker = bsk.Node(position = tip_pos, scale = glm.vec3(0.01))
    fishing_line = bsk.Node( # TODO amke this disappear when not being used
        mesh = game.meshes['cylinder'],
        material = game.materials['green']
    )
    fishing_reel = bsk.Node(
        position = glm.normalize(tip_pos - handle_pos) * 1.3 + handle_pos - glm.vec3(0, 0.2, 0),
        scale = glm.vec3(0.1),
    )
    rod.node.add(fishing_reel)
    rod.node.add(tip_tracker)
    setattr(rod, 'stage', 'bait')
    setattr(rod, 'time', 0)
    setattr(rod, 'bobber_pos', glm.vec3(tip_pos))
    rod_pivot.add(rod.node)
    
    def rod_check_in(dt: float) -> bool: return game.player.item_r and game.player.item_r.node.tags in [['worm'], ['place holder']] # must be type list[list[str]]
    def rod_put_in(dt: float) -> None: rod.stage = 'ready'
    def rod_lerp_end_func(dt: float) -> None: 
        rod_node: bsk.Node = rod.held_item.node
        rod.step = -1
        rod.node.remove(rod_node)
        game.current_scene.add(rod_node)
        rod_node.physics = True
        rod_node.velocity = glm.vec3(0, 3, 15)
        rod.time = 0
        
    free_reel = free_axis(rod, glm.normalize(glm.cross(tip_pos - handle_pos, (0, 1, 0))), fishing_reel)
        
    def rod_loop(dt: float, rod = rod) -> None:
        rod_node: bsk.Node = rod.held_item.node
        rod_lerp(dt)
        match rod.stage:
            case 'bait': ...
            case 'ready':
                rod.stage = 'cast'
                rod.step = 1
                rod.node.add(rod_node)
            case 'cast':
                pos, sca, rot = connect(rod_node.position.data, tip_tracker.position.data, 0.025)
                # fishing_line.position = pos
                # fishing_line.scale = sca
                # fishing_line.rotation = rot
                rod.time += dt
                if rod.time > 2.35:
                    rod_node.physics = False
                    rod_node.velocity = glm.vec3(0)
                    print('hit')
                    rod.stage = 'reel'
            case 'reel': free_reel(dt)
            case 'end': ...
        if rod.stage == 'ready': 
            ...
        
    rod_lerp = lerp(rod, rod_pivot, time = 0.3, rotation = glm.angleAxis(glm.pi() / 3, (1, 0, 0)), end_func = rod_lerp_end_func)
    rod_place = place(rod, tip_pos, check_in_func = rod_check_in, put_in_func = rod_put_in)
    rod_pan_loop = pan_loop(rod, time = 0.5, position = glm.vec3(-1.75, 2, 6), rotation = glm.angleAxis(glm.pi(), (0, 1, 0)), loop_func = rod_loop)
    
    def rod_active(dt: float) -> None:
        match rod.stage:
            case 'bait': rod_place(dt)
            case 'ready': rod_pan_loop(dt)
    
    rod.active = rod_active
    
    level.add(rod_pivot, rod, fishing_line)

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
    
def bucket(level: Level) -> None:
    game = level.game
    
    bucket = Interactable(level, bsk.Node(
        position = (-8, 1.5, 6.5),
        scale = glm.vec3(0.8),
        material = game.materials['green']
    ))
    
    worm_node = bsk.Node(
        position = glm.vec3(0, -100, 0),
        scale = glm.vec3(0.1),
        material = game.materials['red'],
        tags = ['worm']
    )
    bucket.active = interact_give_hold(bucket, HeldItem(game, worm_node))
    
    level.add(bucket, worm_node)