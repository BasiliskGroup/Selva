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
    art = Level(game, 'art', glm.vec3(-1, 0, -1))
    
    room(art)
    painting_puzzle(art)
    paint_buckets(art)
    hints(art)
    
    paint_brush = Interactable(art, bsk.Node(
        position = (2.5, 2.25, 4.35),
        scale = glm.vec3(0.1),
        mesh = game.meshes['squid'],
        material = game.materials['squid'],
        tags = ['paint_brush', 'none']
    ))
    paint_brush.active = pickup_function(paint_brush, interact_to_hold(paint_brush, HeldItem(game, paint_brush.node)))
    art.add(paint_brush)
    
    return art
    
def paint_buckets(art: Level) -> None:
    game = art.game
    
    # adds paint buckets
    paint_buckets = {}
    for color, data in zip(['red', 'yellow', 'blue'], [
        ((-2, 1.7, -5.3), glm.vec3(0.4)),
        ((-2.7, 1.7, -4.8), glm.vec3(0.4)),
        ((-3.4, 1.7, -5.2), glm.vec3(0.4)),
    ]):
        bucket = Interactable(art, bsk.Node(
            position = data[0],
            scale = data[1],
            material = game.materials[f'paint_bucket_{color}'],
            mesh = game.meshes['paint_bucket']
        ))
        paint_buckets[color] = bucket
        
        def mix(dt: float, color = color) -> None:
            if not game.key_down(bsk.pg.K_e) or not game.player.item_r: return # enforce key press to interact
            held_node = game.player.item_r.node
            tags: list[str] = held_node.tags
            if not 'paint_brush' in tags: return
            color_index = tags[0] == 'paint_brush'
            if tags[color_index] == 'none': 
                held_node.material = game.materials[f'squid_{color}'] # set material of HeldItem
                game.player.item_r_ui.node.material = game.materials[f'squid_{color}'] # set material of Node
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
            held_node.material = game.materials[f'squid_{new_color}'] # set material of HeldItem
            game.player.item_r_ui.node.material = game.materials[f'squid_{new_color}'] # set material of Node
            held_node.tags[color_index] = new_color
            
        paint_buckets[color].active = mix
          
    art.add([b for b in paint_buckets.values()])
    
    # adds water
    water = Interactable(art, bsk.Node(
        position = (-1.7, 1.45, -4.8),
        scale = glm.vec3(0.15),
        material = game.materials['water_mug'],
        mesh = game.meshes['coffee_mug']
    ))
    
    def clear(dt: float) -> None:
        if not game.key_down(bsk.pg.K_e) or not game.player.item_r: return # enforce key press to interact
        held_node = game.player.item_r.node
        tags: list[str] = held_node.tags
        if not 'paint_brush' in tags: return
        color_index = tags[0] == 'paint_brush'
        held_node.material = game.materials['squid'] # set material of HeldItem
        game.player.item_r_ui.node.material = game.materials['squid'] # set material of Node
        held_node.tags[color_index] = 'none'
    water.active = clear  
    art.add(water)

def painting_puzzle(art: Level) -> None:
    game = art.game
    
    key = Interactable(art, bsk.Node(
        position = (0, 100, 0),
        scale = glm.vec3(0.1),
        mesh = game.meshes['key'],
        material = game.materials['key_color'],
        tags = ['color_key']
    ))
    key.active = pickup_function(key, interact_to_hold(key, HeldItem(game, key.node)))
    art.add(key)
    
    # the painting nodes
    painting_interacts: dict[str, Interactable] = {}
    s = 0.03
    position = glm.vec3(-4.775, 2.75, -1.825)
    for color, data in zip(['red', 'orange', 'yellow', 'green', 'blue', 'purple'], [
        ((0, 0, 0), glm.vec3(0.1), glm.quat(), 'half_torus'),
        ((0, 0, 0), glm.vec3(0.1), glm.quat(), 'other_half_torus'),
        ((0, 0, -5.5*s), glm.vec3(s, 2.5*s, s), glm.angleAxis(glm.pi() / 2, (1, 0, 0)), 'cylinder'),
        ((0, -1.5*s, -8*s), glm.vec3(s), glm.quat(), 'cylinder'),
        ((0, 0, -10.5*s), glm.vec3(s, 2.5*s, s), glm.angleAxis(glm.pi() / 2, (1, 0, 0)), 'cylinder'),
        ((0, -2*s, -11*s), glm.vec3(s, 1.5*s, s), glm.quat(), 'cylinder'),
    ]):
        paint_part = Interactable(art, bsk.Node(
            position = position + data[0],
            scale = data[1],
            rotation = data[2],
            material = game.materials['white'],
            mesh = game.meshes[data[3]]
        ))
        painting_interacts[color] = paint_part
        setattr(paint_part, 'happy', False)
        
        def coloring(dt: float, paint_part = paint_part, color = color) -> None:
            if not game.player.item_r: return
            tags: list[str] = game.player.item_r.node.tags
            if not 'paint_brush' in tags: return
            brush_color = tags[0] if tags[1] == 'paint_brush' else tags[1]
            if brush_color == 'none': return
            paint_part.node.material = game.materials[brush_color]
            paint_part.happy = brush_color == color
            
            # when puzzle has been completed
            if all([p.happy for p in painting_interacts.values()]):
                for p in painting_interacts.values(): p.node.position.y = 100 # remove from scene
                
                # summon key
                key.node.position = position + glm.vec3(0.05, 0, -0.2)
                key.passive = simulate_gravity_node(game, art.scene, key, key.node)
            
        paint_part.active = coloring
    
    art.add([p for p in painting_interacts.values()])
    
    # easel
    art.add(bsk.Node(
        position = (-5, 1.5, -2),
        scale = glm.vec3(0.6),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)),
        mesh = game.meshes['easel'],
        material = game.materials['light_wood']
    ))
    art.add(bsk.Node(
        position = (-5, 2, -2),
        scale = glm.vec3(0.3, 2, 1),
        collision = True,
        static = True,
        shader = game.shaders['invisible']
    ))
    
    # canvas
    art.add(bsk.Node(
        position = (-4.85, 2.75, -2),
        scale = (0.05, 1.2, 0.7),
        material = game.materials['light_white']
    ))
    
    # paint stand
    art.add(bsk.Node(
        position = (-2.5, 1.2, -5),
        scale = glm.vec3(0.7),
        mesh = game.meshes['desk'],
        material = game.materials['dark_wood']
    ))
    art.add(bsk.Node(
        position = (-2.5, 0.6, -5),
        scale = glm.vec3(1.4, 0.6, 0.7),
        collision = True,
        static = True,
        shader = game.shaders['invisible']
    ))
    
def room(art: Level) -> None:
    game = art.game
    
    # box
    art.add(rect_room(0, 0, 10, 12, 5.5, floor_material = game.materials['bright_wood'], wall_material = game.materials['art_wall'], ceil_material = game.materials['art_ceiling']))
    
    # desks
    def add_table(pos: glm.vec3, rot: float = 0) -> None:
        # add table and collider
        table_position = pos + glm.vec3(0, 1, 0)
        art.add(bsk.Node(
            position = table_position,
            scale = glm.vec3(1.5),
            rotation = glm.angleAxis(rot + glm.pi() / 4, (0, 1, 0)),
            mesh = game.meshes['art_table'],
            material = game.materials['art_table']
        ))
        art.add(bsk.Node(
            position = table_position,
            scale = glm.vec3(3, 1, 3),
            collision = True,
            static = True,
            mesh = game.meshes['cylinder'],
            shader = game.shaders['invisible']
        ))
        
        table_horizontal = glm.vec3(table_position.x, 0, table_position.z)
        for i in range(4):
            r = 3
            position = pos + glm.vec3(r * glm.cos(glm.pi() * i / 2 + rot), 0.85, r * glm.sin(glm.pi() * i / 2 + rot))
            horizontal = glm.vec3(position.x, 0, position.z)
            
            art.add(bsk.Node(
                position = position,
                scale = glm.vec3(0.7),
                rotation = glm.conjugate(glm.quatLookAt(glm.normalize(table_horizontal - horizontal), (0, 1, 0))) * glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
                mesh = game.meshes['bear_chair'],
                material = game.materials['bear_chair']
            ))
        
    add_table(glm.vec3(5, 0, 5), rot = 0.2)
    add_table(glm.vec3(-5, 0, 5), rot = 0.7)
    add_table(glm.vec3(5, 0, -5), rot = 1)

    # floor colors
    center = glm.vec3(-2, 0, -4)
    scale = 1.5
    for x in range(-1, 2):
        for z in range(-1, 2):
            color = random.choice(['red', 'orange', 'yellow', 'green', 'blue', 'purple'])
            art.add(bsk.Node(
                position = center + glm.vec3(2 * scale * x, 0, 2 * scale * z),
                scale = (scale, 0.025, scale),
                material = game.materials[color]
            ))
            
    art.add(bsk.Node(
        position = (0, 3.5, 11),
        scale = glm.vec3(0.9),
        rotation = glm.angleAxis(glm.pi(), (0, 1, 0)),
        mesh = game.meshes['fake_door'],
        material = game.materials['fake_door']
    ))
    
    # add window
    for z in range(-1, 2):
        art.add(bsk.Node(
            position = (8.85, 5, 6 * z),
            scale = glm.vec3(1.75),
            rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
            mesh = game.meshes['window_two_pane'],
            material = game.materials['window_two_pane']
        ))
        
def hints(art: Level) -> None:
    game = art.game
    
    height, w, l, h = 2, 1, 1, 0.01
    
    art.add(bsk.Node(
        position = glm.vec3(4, height, 4),
        scale = (w, h, l),
        rotation = glm.angleAxis(2.1, (0, 1, 0)),
        material = game.materials['color_key']
    ))
    
    art.add(bsk.Node(
        position = glm.vec3(-5, height, 3.5),
        scale = (w, h, l),
        rotation = glm.angleAxis(glm.pi(), (0, 1, 0)),
        material = game.materials['color_combos']
    ))
    
    art.add(bsk.Node(
        position = glm.vec3(4, height, -4),
        scale = (w, h, l),
        rotation = glm.angleAxis(0.6, (0, 1, 0)),
        material = game.materials['key_key']
    ))