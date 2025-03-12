from dataclasses import dataclass
from typing import Iterator


@dataclass
class EdgeRowType():
    def keys(self) -> list[str]: ...
    def values(self) -> list[bool]: ...
    def items(self) -> list[tuple[str, bool]]: ...
    def __getitem__(self, key: str) -> bool: ...
    def __setitem__(self, key: str, value: bool) -> None: ...
    def __iter__(self) -> Iterator[str]: ...

class EdgeMatrix():
    
    def __init__(self) -> None:
        self.edges: set[str] = set()
        self.keys: set[str] = set()
        
    # assumes k1 and k2 have already been hashed
    def combo_key(self, key1: str, key2: str) -> str: return key1 + key2 if key1 < key2 else key2 + key1
        
    # internal functions should never be called by the user
    def get_internal(self, key1: str, key2: str) -> bool: return self.combo_key(key1, key2) in self.edges
        
    def set_internal(self, key1: str, key2: str, value: bool) -> None: 
        if key1 == key2: return # a node cannot connect to  itself in an edge graph
        combo = self.combo_key(key1, key2)
        if value == 0: 
            if combo in self.edges: self.edges.remove(combo) 
        elif value == 1: self.edges.add(combo)
        else: raise ValueError(f'EdgeMatrix cannot store a value of type {type(value)}')
        
    # get a whole row of the edge matrix
    def __getitem__(self, key: str) -> EdgeRowType: return EdgeRow(self, str(hash(key)))
    
    # set a row of the edge matrix to a single value (probably will never use)
    def __setitem__(self, key: str, value: bool) -> None:
        key = str(hash(key))
        self.keys.add(key)
        for k in self.keys: self.set_internal(key, k, value)
        
    def __iter__(self) -> None: raise RuntimeError('Cannot iterate through EdgeMatrix')
        
# should function exactly like a dictionary
class EdgeRow():
    
    def __init__(self, graph: EdgeMatrix, key: str) -> None:
        self.graph = graph
        self.key = key # should be hashed already
        
    def keys(self) -> list[str]: return list(self.graph.keys.difference([self.key]))
    def values(self) -> list[bool]: return [self.graph.get_internal(self.key, k) for k in self.keys()]
    def items(self) -> list[tuple[str, bool]]: return zip(self.keys(), self.values())
        
    def __getitem__(self, key: str) -> bool: return self.graph.get_internal(self.key, str(hash(key)))
    def __setitem__(self, key: str, value: bool) -> None:
        key = str(hash(key))
        self.graph.keys.add(key)
        self.graph.set_internal(self.key, key, value)
        
    def __iter__(self) -> Iterator[str]: return iter(self.keys())