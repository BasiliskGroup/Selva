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

def art(game: Game) -> Level:
    art = Level(game)
    
    room(art)
    painting_puzzle(art)
    paint_buckets(art)
    
    paint_brush = Interactable(art, bsk.Node(
        position = (2.5, 2.25, 4.35),
        scale = glm.vec3(0.1),
        tags = ['paint_brush', 'none']
    ))
    paint_brush.active = pickup_function(paint_brush, interact_to_hold(paint_brush, HeldItem(game, paint_brush.node)))
    art.add(paint_brush)
    
    return art

def room(art: Level) -> None:
    art.add(rect_room(0, 0, 6, 6, 4, floor_material = None, wall_material = None, ceil_material = None))
    
def paint_buckets(art: Level) -> None:
    game = art.game
    
    # adds paint buckets
    paint_buckets = {}
    for color, data in zip(['red', 'yellow', 'blue'], [
        ((4, 1, 0), glm.vec3(0.5)),
        ((4, 1, 1), glm.vec3(0.5)),
        ((4, 1, -1), glm.vec3(0.5)),
    ]):
        bucket = Interactable(art, bsk.Node(
            position = data[0],
            scale = data[1],
            material = game.materials[color],
            mesh = game.meshes['cylinder']
        ))
        paint_buckets[color] = bucket
        
        def mix(dt: float, color = color) -> None:
            if not game.key_down(bsk.pg.K_e): return # enforce key press to interact
            held_node = game.player.item_r.node
            tags: list[str] = held_node.tags
            if not 'paint_brush' in tags: return
            color_index = tags[0] == 'paint_brush'
            if tags[color_index] == 'none': 
                held_node.material = game.materials[color] # set material of HeldItem
                game.player.item_r_ui.node.material = game.materials[color] # set material of Node
                held_node.tags[color_index] = color
                return
            
            # if color is mixed or identical ignore
            if tags[color_index] in (color, 'orange', 'purple', 'green'): return # ignore double same color
            colors = (color, tags[color_index])
            new_color = None
            
            # mixing colors
            if 'red' in colors and 'blue' in colors: new_color = 'purple'
            elif 'red' in colors and 'yellow' in colors: new_color = 'orange'
            elif 'blue' in colors and 'yellow' in colors: new_color = 'green'
            held_node.material = game.materials[new_color] # set material of HeldItem
            game.player.item_r_ui.node.material = game.materials[new_color] # set material of Node
            held_node.tags[color_index] = new_color
            
        paint_buckets[color].active = mix
          
    art.add([b for b in paint_buckets.values()])
    
    # adds water
    water = Interactable(art, bsk.Node(
        position = (4, 1, -2),
        scale = glm.vec3(0.3),
        material = game.materials['dark_wood'],
        mesh = game.meshes['mug']
    ))
    
    def clear(dt: float) -> None:
        if not game.key_down(bsk.pg.K_e): return # enforce key press to interact
        held_node = game.player.item_r.node
        tags: list[str] = held_node.tags
        if not 'paint_brush' in tags: return
        color_index = tags[0] == 'paint_brush'
        held_node.material = game.materials['white'] # set material of HeldItem
        game.player.item_r_ui.node.material = game.materials['white'] # set material of Node
        held_node.tags[color_index] = 'none'
    water.active = clear  
    art.add(water)

def painting_puzzle(art: Level) -> None:
    game = art.game
    
    # the painting nodes
    painting_interacts = {}
    for color, data in zip(['red', 'orange', 'yellow', 'green', 'blue', 'purple'], [
        ((3, 3, 3), glm.vec3(0.5)),
        ((2, 2, 2), glm.vec3(0.5)),
        ((1, 1, 1), glm.vec3(0.5)),
        ((0, 1, 0), glm.vec3(0.5)),
        ((-1, 2, -1), glm.vec3(0.5)),
        ((-2, 3, -2), glm.vec3(0.5)),
    ]):
        paint_part = Interactable(art, bsk.Node(
            position = data[0],
            scale = data[1],
            material = game.materials['white']
        ))
        painting_interacts[color] = paint_part
        setattr(paint_part, 'happy', False)
        
        def coloring(dt: float, paint_part = paint_part, color = color) -> None:
            tags: list[str] = game.player.item_r.node.tags
            if not 'paint_brush' in tags: return
            brush_color = tags[0] if tags[1] == 'paint_brush' else tags[1]
            if brush_color == 'none': return
            paint_part.node.material = game.materials[brush_color]
            paint_part.happy = brush_color == color
            print([p.happy for p in painting_interacts.values()])
            
        paint_part.active = coloring
    
    art.add([p for p in painting_interacts.values()])
    
    