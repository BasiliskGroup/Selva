from dataclasses import dataclass
from levels.level import Level


@dataclass
class Memory():
    
    def __init__(self, level: Level, neighbors: list[str]) -> None:
        self.level = level
        self.neighbors = neighbors