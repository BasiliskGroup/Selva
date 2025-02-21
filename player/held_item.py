from basilisk import Node
from typing import Callable, Any


class HeldItem():
    
    def __init__(self, node: Node, down: Callable, up: Callable, **kwargs) -> None:
        self.node = node # NOTE never added to the scnee, only used to store data
        
        # functions that will activate on key up/down
        self.down = down
        self.up = up
        
        # allows the user to set arguments of any type they want
        for key, value in kwargs.items(): setattr(self, str(key), value)