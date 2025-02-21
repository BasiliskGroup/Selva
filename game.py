import basilisk as bsk
from levels.level import Level


class Game():
    
    def __init__(self) -> None:
        self.engine = bsk.Engine()
        self.level = Level(self) # TODO find good/clean way to create scenes
        
    def update(self) -> None:
        self.level.scene.update()
        self.engine.update()
        
    @property
    def camera(self): return self.level.scene.camera