from typing import Callable
from helper.type_hints import Game
from levels.level import Level
from memories.edge_matrix import EdgeMatrix


class MemoryHandler():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.nodes: dict[str, Level] = {}
        self.edges = EdgeMatrix()
        self.current_level: Level = None
        
    # functions for adding and accessing graphs
    def add_first(func: Callable) -> Callable:
        """
        Decorates adding functions and ensures that the first level add is handled properly
        """
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            if len(self.nodes) == 1: self.current_level = list(self.nodes.values())[0]
        return wrapper
    
    @add_first
    def add(self, name: str, level: Level) -> None: self[name] = level
    
    @add_first
    def __setitem__(self, name: str, level: Level) -> None: self.nodes[name] = level
    def __getitem__(self, name: str) -> Level: return self.nodes[name]
    
    
    
