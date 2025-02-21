import basilisk as bsk
from dataclasses import dataclass
from typing import Callable


@dataclass
class Game():
    engine: bsk.Engine
    
    
@dataclass
class Player():
    game: Game
    
    
@dataclass
class HeldItem():
    node: bsk.Node
    down: Callable
    up: Callable