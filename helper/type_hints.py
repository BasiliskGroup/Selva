import basilisk as bsk
import glm
from dataclasses import dataclass
from typing import Callable, Any

# this file contains abstract classes for all classes in Selva. 
# They can be used to provide type hinting to child classes without circular importing


@dataclass
class Game():
    engine: bsk.Engine
    materials: dict[str : bsk.Material]
    meshes: dict[str : bsk.Mesh]
    current_level: Any
    player: Any
    update: Callable
    camera: bsk.FreeCamera
    current_scene: bsk.Scene
    keys: list[bool]
    previous_keys: list[bool]
    mouse: bsk.engine.Mouse
    
    def adjacent_levels(self, origin_level: Any) -> set[Any]: ...
    def key_down(self, key: int) -> bool: ...
    def key_down(self, key: int) -> bool: ...
    def load_materials(self) -> None: ...
    def primary_update(self) -> None: ...
    

@dataclass
class Interactable():
    level: Any
    node: bsk.Node
    active: Callable
    passive: Callable
    
    def update(self) -> None: ...
    

@dataclass
class Level():
    game: Game
    scene: bsk.Scene
    interactables: list[Interactable]
    
    def add(self, *args) -> None: ...
    def __getitem__(self, node: bsk.Node) -> Interactable: ...
    
    
@dataclass
class HeldItem():
    game: Game
    node: bsk.Node
    func: Callable
    offset: glm.vec3
    rotation: glm.quat
    

@dataclass
class PictureFrame(HeldItem):
    level: Level
    percent_moved: float
    ANIMATION_TIME: float
    original_offset: glm.vec3
    original_rotation: glm.quat
    final_offset: glm.vec3
    final_rotation: glm.quat
    
    
@dataclass
class Player():
    # NOTE game is a parent class
    HEIGHT: float
    SPEED: float
    DECELERATION_CONSTANT: float
    body_node: bsk.Node
    held_node: bsk.Node
    items: list[HeldItem]
    held_index: int
    control_disabled: bool
    camera: bsk.FollowCamera
    
    position: glm.vec3
    velocity: glm.vec3
    
    
    def update(self, dt: float) -> None: ...
    
