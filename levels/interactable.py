from basilisk import Node
from typing import Callable
from helper.type_hints import Level


class Interactable():
    
    def __init__(self, level: Level, node: Node, func: Callable=None, **kwargs) -> None:
        self.level = level
        self.node = node # this Node is added to the Level scene when this Interactable is added to the Level
        self.func = func
        
        # allows the user to set arguments of any type they want
        for key, value in kwargs.items(): setattr(self, str(key), value)
        