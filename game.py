import basilisk as bsk
from levels.level import Level


class Game():
    
    def __init__(self) -> None:
        self.engine = bsk.Engine()
        self.current_level = Level(self) # this is the current scene that the player is in
        
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
        
    @property
    def camera(self): return self.current_level.scene.camera