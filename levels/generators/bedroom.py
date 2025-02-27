import basilisk as bsk
import glm
import random
from typing import Callable
from helper.type_hints import Game
from levels.level import Level
from levels.helper import rect_room
from levels.interactable import Interactable
from levels.functions.pickup import pickup_function, pickup_return_function
from levels.functions.interpolate import lerp, lerp_interact, lerp_difference
from levels.functions.pan import pan_loop
from levels.functions.tactile import free, free_y
from levels.functions.held_item import interact_to_hold


def bedroom(game: Game) -> Level:
    # create basic layout for bedroom level
    bedroom = Level(game)
    bedroom.add(*rect_room(0, 0, 5.75, 6.75, 4, game.materials['light_white']))
    
    # poster
    bedroom.add(bsk.Node(
        position = (4.75, 5, -2),
        scale = (0.01, 1.2, 1.7),
        rotation = glm.angleAxis(glm.pi() / 2, (1, 0, 0)),
        material = game.materials['suits']
    ))

    # locked box
    locked_box_interact = locked_box(bedroom)
    bedroom.add(locked_box_interact)
    wheels(bedroom, locked_box_interact)
    key_interact = key(bedroom)
    bedroom.add(key_interact)
    bedroom.add(locked_lid(bedroom, locked_box_interact))
    
    # dresser
    bedroom.add(bsk.Node(
        position = (2.5, 1, -4.5),
        scale = (1, 0.8, 1),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh=game.meshes['dresser']
    ))
    drawers(bedroom, key_interact)
    
    return bedroom
    
def key(level: Level) -> Interactable:
    node = bsk.Node(
        position = (3.5, 2.4, -4.35),
        scale = (0.1, 0.1, 0.1),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)) * glm.angleAxis(glm.pi() / 2, (1, 0, 0)),
        mesh = level.game.meshes['key']
    )
    key = Interactable(level, node)
    key.active = pickup_function(key, interact_to_hold(key, key.node))
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
    drawers: list[Interactable] = [
        drawer(bedroom, position) for position in (
            glm.vec3(1.55, 0.6, -4.4), # bottom left
            glm.vec3(3.45, 1.4, -4.4), # top right
            glm.vec3(3.45, 0.6, -4.4)  # bottom right
        )
    ]
    bedroom.add(drawers)
    
    # bottom right drawer 
    john = bsk.Node(
        position = (3.7, 0.6, -4.4),
        scale = (0.1, 0.1, 0.1),
        mesh = bedroom.game.meshes['john'],
        material = bedroom.game.materials['john'],
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)) * glm.angleAxis(glm.pi() / 2, (1, 0, 0)) * glm.angleAxis(glm.pi() / 3, (0, 1, 0))
    )
    # john_interact = Interactable(bedroom, john)
    # john_interact.active = pickup_function(john_interact, pickup_return_function(john_interact))
    drawers[2].node.add(john)
    # bedroom.add(john_interact)
    
    # bottom left drawer
    for node in [bsk.Node(
        position = position,
        scale = (0.06, 0.06, 0.06),
        mesh = bedroom.game.meshes['sock'],
        material = bedroom.game.materials['red'],
        rotation = glm.angleAxis(angle, (0, 1, 0))
    ) for position, angle in (
        ((1.8, 0.6, -4.4), glm.pi() / 3),
        ((2, 0.6, -4.5), -glm.pi() / 3),
        ((1.7, 0.6, -4.3), glm.pi()),
    )]: 
        drawers[0].node.add(node)
    
    # top right drawer
    for node in [bsk.Node(
        position = position,
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
        if not bedroom.game.key_down(bsk.pg.K_e) or not bedroom.game.player.held_item or not bedroom.game.player.held_item.node == key.node: return False
        bedroom.game.player.items.remove(bedroom.game.player.held_item) # removes key from the player's inventory
        return True
    
    locked_drawer = drawer(bedroom, glm.vec3(1.55, 1.4, -4.4), check_func = check_func)
    bedroom.add(locked_drawer)

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
    
    locked_wheels = {wheel : free_y(locked_box, wheel, sensitivity = 0.7) for wheel in wheels}
    setattr(locked_box, 'wheels', locked_wheels)
    setattr(locked_box, 'timer', 0)
    setattr(locked_box, 'selected', None)
    setattr(locked_box, 'prev_left_down', False)
    setattr(locked_box, 'code', [1, 1, 1])
    
    def loop_func() -> None:
        if game.mouse.left_down:
            if not locked_box.prev_left_down:
                cast = game.current_scene.raycast_mouse(game.mouse.position, has_collisions=False)
                locked_box.selected = cast.node
            if locked_box.selected in locked_box.wheels:
                locked_box.wheels[locked_box.selected]()
        
        for index, wheel in enumerate(locked_box.wheels):
            wheel.rotational_velocity = wheel.rotational_velocity * (1 - game.engine.delta_time * 5) if glm.length2(wheel.rotational_velocity) > 1e-7 else glm.vec3(0, 0, 0)
            
            # compute and adjust the rotation angle for generating input code
            angle = glm.angle(wheel.rotation.data)
            if glm.axis(wheel.rotation.data).x < 1: angle -= 2 * glm.pi()
            angle = (abs(angle) - glm.pi() / 8) % (2 * glm.pi())
            
            # compute input code from angle
            locked_box.code[index] = 8 - int(angle / glm.pi() * 4)
        
        locked_box.prev_left_down = game.mouse.left_down
        # print(locked_box.code)
    
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
    )
    node = bsk.Node(
        position = glm.vec3(0.35, 0.375, -0.075) * 10,
        scale = locked_box.node.scale,
        mesh = bedroom.game.meshes['box_three_lid'],
    )
    bedroom.add(parent)
    parent.add(node)
    locked_lid = Interactable(bedroom, node)
    
    def check_func() -> bool:
        return bedroom.game.key_down(bsk.pg.K_e) and locked_box.code == [1, 6, 3]
    
    locked_lid.passive = lerp_difference(locked_lid, node = parent, time = 0.25, delta_rotation = glm.angleAxis(glm.pi() / 2, (1, 0, 0)))
    locked_lid.active = lerp_interact(locked_lid, check_func = check_func)
    
    return locked_lid