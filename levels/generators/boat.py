import basilisk as bsk
import glm
import random
from typing import Callable
from player.held_items.held_item import HeldItem, PictureFrame
from helper.type_hints import Game
from levels.level import Level
from levels.helper import rect_room
from levels.interactable import Interactable
from levels.functions.imports import *
from helper.transforms import connect
from levels.classes.fish import FishTracker
from images.images import images
from ui.effects import ImageBounce
from render.pixel import PixelRenderer, PixelQuantizedRenderer


def boat(game: Game) -> Level:
    level = Level(game, 'boat', glm.vec3(0, -100, 0), PixelRenderer, PixelQuantizedRenderer)
    
    loading_node(level)
    fishing(level)
    load_boat(level)
    bucket(level)
    fish_book(level)
    
    return level

def loading_node(level) -> None:
    level.add(bsk.Node(
        position = glm.vec3(-6.5, -97.45, 0),
        scale = glm.vec3(1, 4, 3),
        rotation = glm.angleAxis(-glm.pi() / 2, (1, 0, 0)),
        material = level.game.materials['fish_master_2002']
    ))

def fish_book(level: Level) -> None:
    game = level.game
    engine = game.engine
    images = game.images
    
    fish_book = Interactable(level, bsk.Node(
        position = glm.vec3(3, 1.4, 3),
        scale = (0.75, 0.1, 0.75),
        mesh = game.meshes['paper'],
        material = game.materials['paper']
    ))
    
    def p1(dt: float) -> None: bsk.draw.blit(engine, images['fishopedia1.png'], (0, 0, game.win_size.x, game.win_size.y)) # repeated so win_size is updated on engine change
    def p2(dt: float) -> None: bsk.draw.blit(engine, images['fishopedia2.png'], (0, 0, game.win_size.x, game.win_size.y))
    def p3(dt: float) -> None: bsk.draw.blit(engine, images['fishopedia3.png'], (0, 0, game.win_size.x, game.win_size.y))
    def p4(dt: float) -> None: bsk.draw.blit(engine, images['fishopedia4.png'], (0, 0, game.win_size.x, game.win_size.y))
    def p5(dt: float) -> None: bsk.draw.blit(engine, images['fishopedia5.png'], (0, 0, game.win_size.x, game.win_size.y))

    pages = [p1, p2, p3, p4, p5]
    fish_book.active = book(fish_book, pages)
    
    level.add(fish_book)

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
        shader = game.shaders['invisible']
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
        position = (0, -100, 0),
        mesh = game.meshes['cylinder'],
        material = game.materials['white']
    )
    fishing_reel = bsk.Node(
        position = glm.normalize(tip_pos - handle_pos) * -6 + handle_pos - glm.vec3(0, 0.2, 0) - ortho_vector * 0.4,
        scale = glm.vec3(0.5),
        rotation = glm.conjugate(glm.quatLookAt(ortho_vector, (0, 1, 0))),
        mesh = game.meshes['crank'],
        material = game.materials['crank_cw'],
        relative_scale=False
    )
    rod.node.add(fishing_reel)
    rod.node.add(tip_tracker)
    setattr(rod, 'stage', 'bait')
    setattr(rod, 'time', 0)
    setattr(rod, 'bobber_pos', glm.vec3(tip_pos))
    rod_pivot.add(rod.node)
    
    def rod_check_in(dt: float) -> bool: return bool(game.player.item_r) and len(game.player.item_r.node.tags) > 0 and game.player.item_r.node.tags[0] in ['worm', 'copper_wire', 'paint_brush']
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
                    rod.stage = 'reel'
                    rod.time = 0
                    game.sounds['placeholder'].play()
                    
                    # spawn reel icon
                    game.ui.add(ImageBounce(game.ui, game.images['reel.png'], position1 = glm.vec2(100, 100), scale1 = glm.vec2(75, 125), position2 = glm.vec2(100, 100), scale2 = glm.vec2(150, 250), effect_time = 2))
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
                fish_velocity = rod.time * 0.1 - glm.cos(rod.time) + 1
                rod_node.position.z += reeled + dt * fish_velocity
                
                # when the fish is successfully caught
                distance = glm.length(rod_node.position.data - game.camera.position)
                if distance < 8: rod.stage = 'win'
                elif distance > 50: rod.stage = 'lose'
                    
            case 'win':
                # give the player their fish
                bait_tag = rod.held_item.node.tags[0]
                
                if bait_tag == 'copper_wire': 
                    caught = Interactable(level, bsk.Node(
                        position = (-2, 1.8, 3),
                        scale    = glm.vec3(0.2),
                        mesh     = game.meshes['battery'],
                        material = game.materials['battery'],
                        tags     = ['battery']
                    ))
                elif bait_tag == 'paint_brush':
                    caught = Interactable(level, bsk.Node( # TODO swap to picture frame
                        position = (-2, 1.8, 3),
                        scale    = glm.vec3(0.2),
                        mesh     = game.meshes['picture_frame'],
                        material = game.materials['picture_frame'],
                    ))
                elif not game.day:
                    caught = Interactable(level, bsk.Node(
                        scale = glm.vec3(0.1),
                        mesh = game.meshes['squid'],
                        material = game.materials['squid'],
                        tags = ['paint_brush', 'none'],
                    ))
                else:
                    # give the player a fish
                    fish = game.player.fish_tracker.get_fish()
                    new_record = game.player.fish_tracker.log(fish)
                    
                    caught = Interactable(level, bsk.Node(
                        scale = glm.vec3(fish.length),
                        mesh = game.meshes[fish.kind],
                        material = game.materials[fish.kind],
                        tags = [fish.kind, 'new_record' if new_record else '']
                    ))
                
                def always_false() -> bool: return False
                
                if caught.node.mesh == game.meshes['picture_frame']: pickup_function(caught, interact_to_frame(caught, PictureFrame(game, 'art')), always_false)(dt)
                else: 
                    bottom_text = None
                    overlay_distance = 1
                    match caught.node.tags[0]:
                        case 'battery': top_text = 'battery'
                        case 'paint_brush': top_text = 'pyjama_squid'
                        case _: 
                            top_text = caught.node.tags[0]
                            bottom_text = caught.node.tags[1] if caught.node.tags[1] == 'new_record' else None
                            overlay_distance = caught.node.scale.x * 2.5
                    pickup_function(caught, interact_to_hold(caught, HeldItem(game, caught.node)), always_false, distance = overlay_distance, rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)), top_text = top_text, bottom_text = bottom_text)(dt)
                
                # remove bait from rod
                rod.held_item = None
                level.scene.node_handler.remove(rod.held_interact.node)
                rod.held_interact = None
                fishing_line.position = (0, -100, 0)
                    
                rod.stage = 'bait'
                rod.percent_lerp = 0
                rod.step_lerp = -1
                game.player.control_disabled = False
                game.player.camera.rotation = glm.conjugate(glm.quatLookAt((0, 0, 1), (0, 1, 0)))
                game.sounds['placeholder'].play() # TODO win sound
            
            case 'lose':
                rod_node.position = tip_pos
                fishing_line.position = (0, -100, 0)
                rod.stage = 'bait'
                rod.percent_lerp = 0
                rod.step_lerp = -1
                game.player.control_disabled = False
                game.player.camera.rotation = glm.conjugate(glm.quatLookAt((0, 0, 1), (0, 1, 0)))
                game.sounds['placeholder'].play() # TODO lose sound
            
    def rod_loop_check_func(dt: float) -> None: return rod.stage in ['bait']
        
    rod_lerp = lerp(rod, rod_pivot, time = 0.25, rotation = glm.angleAxis(glm.pi() / 3, (1, 0, 0)), end_func = rod_lerp_end_func)
    rod_place = place(rod, tip_pos, check_in_func = rod_check_in, put_in_func = rod_put_in, pull_out_func = rod_pull_out)
    rod_pan_loop = pan_loop(rod, time = 0.5, position = glm.vec3(-1.75, 2, 6), rotation = glm.angleAxis(glm.pi(), (0, 1, 0)), loop_func = rod_loop, leave_check_func = rod_loop_check_func)
    
    def rod_active(dt: float) -> None:
        if rod.held_item: rod.stage = 'ready'
        match rod.stage:
            case 'bait': rod_place(dt)
            case 'ready': rod_pan_loop(dt)
    
    rod.active = rod_active
    
    level.add(rod_pivot, rod, fishing_line)

def load_boat(level: Level) -> None:
    game = level.game
    
    boat = bsk.Node(
        position = (0, -0.9, 2),
        scale = glm.vec3(1),
        rotation = glm.quat(),
        mesh = game.meshes['boat'],
        material = game.materials['boat']
    )
    level.add(boat)
    
    # add colliders
    level.add(rect_room(0, 0, 4, 8.5, 4, shader = game.shaders['invisible']))

def bucket(level: Level) -> None:
    game = level.game
    
    bucket = Interactable(level, bsk.Node(
        position = (-3, 1.75, 4.75),
        scale = glm.vec3(0.6),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        material = game.materials['bait_bucket'],
        mesh = game.meshes['bait_bucket']
    ))
    
    worm_node = bsk.Node(
        position = glm.vec3(0, -100, 0),
        scale = glm.vec3(0.075),
        material = game.materials['worm'],
        mesh = game.meshes['worm'],
        tags = ['worm']
    )
    bucket.active = interact_give_hold(bucket, HeldItem(game, worm_node))
    
    level.add(bucket, worm_node)