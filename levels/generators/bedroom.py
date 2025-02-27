import basilisk as bsk
import glm
from levels.level import Level
from levels.helper import rect_room
from levels.interactable import Interactable
from helper.type_hints import Game
from levels.functions.pickup import pickup_function, pickup_return_function
from levels.functions.interpolate import lerp, lerp_interact, lerp_difference
from levels.functions.pan import pan_loop


def bedroom(game: Game) -> Level:
    # create basic layout for bedroom level
    bedroom = Level(game)
    bedroom.add(*rect_room(0, 0, 5.75, 6.75, 4, game.materials['light_white']))
    
    # dresser
    bedroom.add(bsk.Node(
        position = (2.5, 1, -4.5),
        scale = (1, 0.8, 1),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh=game.meshes['dresser']
    ))
    
    for position in (glm.vec3(1.55, 0.6, -4.4), glm.vec3(3.45, 1.4, -4.4), glm.vec3(3.45, 0.6, -4.4)): bedroom.add(drawer(bedroom, position))
    
    bedroom.add(locked_box(bedroom))
    bedroom.add(key(bedroom))
    bedroom.add(animated_box(bedroom))
    
    return bedroom

def animated_box(level: Level) -> Interactable:
    box = bsk.Node(
        mesh = level.game.meshes['john'],
        scale = (0.25, 0.25, 0.25),
        material = level.game.materials['john'],
        position = (0, 1.5, 0)
    )
    animated_box = Interactable(level, box)
    animated_box.active = pickup_function(animated_box, pickup_return_function(animated_box))
    return animated_box
    
def key(level: Level) -> Interactable:
    node = bsk.Node(
        position = (3.5, 2.4, -4.35),
        scale = (0.1, 0.1, 0.1),
        rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)) * glm.angleAxis(glm.pi() / 2, (1, 0, 0)),
        mesh = level.game.meshes['key']
    )
    key = Interactable(level, node)
    key.active = pickup_function(key, pickup_return_function(key))
    return key

def drawer(level: Level, position: glm.vec3) -> Interactable:
    node = bsk.Node(
        position = position,
        scale = (1, 0.8, 0.8),
        rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
        mesh = level.game.meshes['drawer']
    )
    drawer = Interactable(level, node)
    drawer.passive = lerp_difference(drawer, time = 0.25, delta_position = (0, 0, 1))
    drawer.active = lerp_interact(drawer)
    return drawer

def locked_box(level: Level) -> Interactable:
    node = bsk.Node(
        position = (3.5, 2.25, -4.35),
        scale = (0.5, 0.5, 0.5),
        mesh = level.game.meshes['box_three']
    )
    locked_box = Interactable(level, node)
    
    def active(dt: float) -> None:
        """
        1. Camera lerps to box
        2. Player is allowed control (Moving wheels and exiting with e)
        3. On exit, camera lerps to player position
        """
    
    locked_box.active = pan_loop(
        interact = locked_box, 
        time = 0.5, 
        position = node.position.data + glm.vec3(0, 0, 1.5),
        rotation = glm.quat(),
        loop_func = None
    )
    
    return locked_box