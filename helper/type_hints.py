import basilisk as bsk
import glm
from dataclasses import dataclass
from typing import Callable

# this file contains abstract classes for all classes in Selva. 
# They can be used to provide type hinting to child classes without circular importing


@dataclass
class Game():
    engine: bsk.Engine
    # NOTE level is a child class
    camera: bsk.FreeCamera
    keys: list[bool]
    previous_keys: list[bool]
    mouse: bsk.engine.Mouse
    current_scene: bsk.Scene
    materials: dict[str : bsk.Material]
    
    def update(self) -> None: ...
    

@dataclass
class Level():
    game: Game
    scene: bsk.Scene
    add: Callable
    
    
@dataclass
class HeldItem():
    node: bsk.Node
    func: Callable
    
    
@dataclass
class Player():
    # NOTE game is a parent class
    HEIGHT: float
    body_node: bsk.Node
    held_node: bsk.Node
    position: glm.vec3
    velocity: glm.vec3
    items: list[HeldItem]
    
    def update(self, dt: float) -> None: ...
    # NOTE move(self, dt:float) -> None: should not be exposed