from helper.type_hints import Game
from levels.level import Level
from memories.memory import Memory


class MemoryHandler():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.graph: dict[str, Memory] = {}
        
    # functions for adding and accessing graphs
    def __getitem__(self, name: str) -> Memory: return self.graph[name]
    def __setitem__(self, name: str, memory: Memory) -> None: self.graph[name] = memory
    def add(self, name: str, level: Level, neighbors: list[str]) -> None: self[name] = Memory(level, neighbors)
    
    