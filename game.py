import basilisk as bsk
from levels.level import Level
from player.player import Player


class Game():
    
    def __init__(self) -> None:
        self.engine = bsk.Engine()
        self.current_level = Level(self) # this is the current scene that the player is in
        player = Player(self)
        
    def update(self) -> None:
        """
        Updates all adjacent scenes and the engine
        """
        for level in self.adjacent_levels(): level.scene.update()
        self.engine.update()
        
    def adjacent_levels(self) -> set[Level]:
        """
        Determines all "adjacent" scenes connected by portals
        """
        return set([self.current_level])
    
    def key_down(self, key: int) -> bool:
        """
        Determiones if a key has been pressed by the user
        """
        return self.keys[key] and not self.previous_keys[key]
        
    @property
    def camera(self): return self.current_level.scene.camera
    
    @property
    def keys(self): return self.engine.keys
    @property
    def previous_keys(self): return self.engine.previous_keys