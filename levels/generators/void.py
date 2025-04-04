import basilisk as bsk
import glm
import random
from typing import Callable
from helper.transforms import connect
from helper.type_hints import Game
from levels.level import Level
from levels.helper import rect_room
from levels.interactable import Interactable
from levels.functions.imports import *
from player.held_items.held_item import HeldItem, PictureFrame

def void(game: Game) -> Level:
    void = Level(game)
    void.scene.sky = None
    
    picture_frame(void)
    
    return void
    
def picture_frame(void: Level) -> None:
    game = void.game
    
    starting_position = glm.vec3(0, 17, -20)
    pf = Interactable(void, bsk.Node(
        position = starting_position,
        scale = glm.vec3(0.7),
        rotation = glm.quat(),
        mesh = game.meshes['picture_frame'],
        material = game.materials['bloom_white']
    ))
    setattr(pf, 'fall_time', 0)
    
    def float_down(dt: float) -> None:
        pf.fall_time += dt * 2.3
        if pf.node.position.y < 0: return
        
        t = pf.fall_time
        pf.node.position = starting_position + (
            glm.sin(t) * 10 / t,
            -0.5 * glm.cos(2 * t) - 0.5 * t - 0.02 * t ** 2,
            glm.cos(t) * 10 / t
        )
        direction = glm.normalize((starting_position.x, pf.node.position.y + 1, starting_position.z) - pf.node.position.data)
        pf.node.rotation = glm.normalize(glm.conjugate(glm.quatLookAt(direction , (0, 1, 0)))) * glm.angleAxis(glm.pi(), (0, 1, 0))
    
    pf.passive = float_down
    pf.active = pickup_function(pf, interact_to_hold(pf, HeldItem(void, pf.node)))
    
    void.add(pf)