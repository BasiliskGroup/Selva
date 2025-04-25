import basilisk as bsk
import glm
from helper.type_hints import Game
from levels.level import Level
from levels.interactable import Interactable
from levels.functions.imports import *
from player.held_items.held_item import HeldItem, PictureFrame

def void(game: Game) -> Level:
    void = Level(game, 'void', glm.vec3(0, 0, 0))
    void.scene.sky = None
    
    picture_frame(void)
    
    return void
    
def picture_frame(void: Level) -> None:
    game = void.game
    
    starting_position = glm.vec3(0, 25.65, -20)
    pf = Interactable(void, bsk.Node(
        position = starting_position,
        scale = glm.vec3(0.7),
        rotation = glm.quat(),
        mesh = game.meshes['picture_frame'],
        material = game.materials['bloom_white']
    ))
    setattr(pf, 'fall_time', 0)
    setattr(pf, 'falling', True)
    
    def float_down(dt: float, pf=pf) -> None:
        if not pf.falling: return
        if pf.node.position.y < 0: 
            pf.falling = False
            return
        pf.fall_time += dt * 3
        
        t = pf.fall_time
        pf.node.position = starting_position + (
            glm.sin(t) * 10 / t,
            -0.5 * glm.cos(2 * t) - 0.5 * t - 0.02 * t ** 2,
            glm.cos(t) * 10 / t
        )
        direction = glm.normalize((starting_position.x, pf.node.position.y + 1, starting_position.z) - pf.node.position.data)
        pf.node.rotation = glm.normalize(glm.conjugate(glm.quatLookAt(direction , (0, 1, 0)))) * glm.angleAxis(glm.pi(), (0, 1, 0))
    
    pf.passive = float_down
    pf.active = pickup_function(pf, interact_to_frame(pf, PictureFrame(game, 'bedroom1')), rotation=glm.angleAxis(glm.pi(), (0, 1, 0)), distance=4)
    
    void.add(pf)