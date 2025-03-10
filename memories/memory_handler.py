from typing import Callable
from helper.type_hints import Game
from levels.level import Level
from memories.memory import Memory


class MemoryHandler():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.graph: dict[str, Memory] = {}
        self.current_memory: Memory = None
        
    # functions for adding and accessing graphs
    def add_first(func: Callable) -> Callable:
        """
        Decorates adding functions and ensures that the first level add is handled properly
        """
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            if len(self.graph) == 1: self.current_memory = list(self.graph.values())[0]
        return wrapper
    
    @add_first
    def add(self, name: str, level: Level, neighbors: list[str]) -> None: self[name] = Memory(level, neighbors)
    
    @add_first
    def __setitem__(self, name: str, memory: Memory) -> None: self.graph[name] = memory
    def __getitem__(self, name: str) -> Memory: return self.graph[name]
    
    
    
