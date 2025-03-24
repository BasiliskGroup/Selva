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
from levels.classes.fish import FishTracker

def boat(game: Game) -> Level:
    level = Level(game)
    
    fishing(level)
    load_boat(level)
    bucket(level)
    
    return level

def fishing(level: Level) -> None:
    game = level.game
    
    # add water for the ocean
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
    
    # add the fishing rod and minigame
    tip_pos = glm.vec3(-1.25, 4.5, 13.5)
    handle_pos = glm.vec3(-2.75, 1.5, 6.5)
    ortho_vector = glm.normalize(glm.cross(tip_pos - handle_pos, (0, 1, 0)))
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
        position = glm.normalize(tip_pos - handle_pos) * 1.3 + handle_pos - glm.vec3(0, 0.2, 0) - ortho_vector * 0.15,
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
    def rod_pull_out(dt: float) -> None: rod.stage = 'bait'
    def rod_lerp_end_func(dt: float) -> None: 
        rod_node: bsk.Node = rod.held_item.node
        rod.step = -1
        rod.node.remove(rod_node)
        game.current_scene.add(rod_node)
        rod_node.physics = True
        rod_node.velocity = glm.vec3(0, 3, 15)
        rod.time = 0
    
    free_reel = free_axis(rod, ortho_vector, fishing_reel)
        
    def rod_loop(dt: float, rod = rod) -> None:
        # print(rod.held_item)
        rod_node: bsk.Node = rod.held_item.node if rod.held_item else None
        
        # control the fishing line
        if rod_node and rod.stage in ['cast', 'reel']:
            pos, sca, rot = connect(rod_node.position.data, tip_tracker.position.data, 0.025)
            fishing_line.position = pos
            fishing_line.scale = sca
            fishing_line.rotation = rot
        
        rod_lerp(dt)
        match rod.stage:
            case 'bait': ...
            case 'ready':
                if not rod.held_item:
                    rod.stage = 'bait'
                    return
                rod.stage = 'cast'
                rod.step = 1
                rod.node.add(rod_node)
            case 'cast':
                rod.time += dt
                if rod_node.position.y < water.node.position.y + 1:
                    rod_node.physics = False
                    rod_node.velocity = glm.vec3(0)
                    print('hit')
                    rod.stage = 'reel'
                    rod.time = 0
            case 'reel': 
                # fishing minigame
                rod.time += dt
                rod_node.position.y = water.node.position.y + 1
                # get player fishing movement
                rot_start = glm.quat(fishing_reel.rotation.data)
                free_reel(dt)
                rot_end = glm.quat(fishing_reel.rotation.data)
                a = glm.angle(rot_start) if glm.dot(glm.axis(rot_start), ortho_vector) > 0 else -glm.angle(rot_start)
                b = glm.angle(rot_end) if glm.dot(glm.axis(rot_end), ortho_vector) > 0 else -glm.angle(rot_end)
                reeled = b - a if a > b and a * b > 0 else 0
                # control bait movement in the water plus fighting the fish
                fish_velocity = rod.time * 0.2 - glm.cos(rod.time) + 0.5
                rod_node.position.z += reeled + dt * fish_velocity
                
                # when the fish is successfully caught
                if glm.length(rod_node.position.data - game.camera.position) < 8: # NOTE playtest this number
                    rod.stage = 'end'
            case 'end':
                # give the player their fish
                bait_tag = rod.held_item.node.tags[0]
                if False: ...
                else:
                    fish = game.player.fish_tracker.get_fish()
                    new_record = game.player.fish_tracker.log(fish)
                    print(new_record, fish)
                
                # remove bait from rod
                rod.held_item = None
                level.scene.node_handler.remove(rod.held_interact.node)
                rod.held_interact = None
                    
                rod.stage = 'bait'
        if rod.stage == 'ready': 
            ...
        
    rod_lerp = lerp(rod, rod_pivot, time = 0.3, rotation = glm.angleAxis(glm.pi() / 3, (1, 0, 0)), end_func = rod_lerp_end_func)
    rod_place = place(rod, tip_pos, check_in_func = rod_check_in, put_in_func = rod_put_in, pull_out_func = rod_pull_out)
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

def bucket(level: Level) -> None:
    game = level.game
    
    bucket = Interactable(level, bsk.Node(
        position = (-8, 1.5, 6.5),
        scale = glm.vec3(0.8),
        material = game.materials['green'],
        mesh = game.meshes['tuna']
    ))
    
    worm_node = bsk.Node(
        position = glm.vec3(0, -100, 0),
        scale = glm.vec3(0.1),
        material = game.materials['red'],
        tags = ['worm']
    )
    bucket.active = interact_give_hold(bucket, HeldItem(game, worm_node))
    
    level.add(bucket, worm_node)