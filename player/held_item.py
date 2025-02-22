from basilisk import Node
from typing import Callable, Any


class HeldItem():
    
    def __init__(self, node: Node, func: Callable, **kwargs) -> None:
        self.node = node # NOTE never added to the scnee, only used to store data
        self.func = func
        
        # allows the user to set arguments of any type they want
        for key, value in kwargs.items(): setattr(self, str(key), value)