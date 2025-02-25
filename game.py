import time
import os
import basilisk as bsk
from levels.level import Level
from levels.generators.bedroom import bedroom
from player.player import Player
from materials.images import images


class Game():
    
    def __init__(self) -> None:
        # Basilisk Engine overhead
        self.engine = bsk.Engine()
        self.load_materials()
        self.load_meshes()
        self.current_level = bedroom(self) # this is the current scene that the player is in
        self.player = Player(self)
        
        # frame by frame updating
        self.update = self.primary_update
        
    def adjacent_levels(self, origin_level: Level) -> set[Level]:
        """
        Determines all "adjacent" scenes connected by portals
        """
        return set([origin_level])
    
    def key_down(self, key: int) -> bool:
        """
        Determiones if a key has been pressed by the user
        """
        return self.keys[key] and not self.previous_keys[key]
    
    def load_materials(self) -> None:
        """
        Loads all materials for the game from images and basic colors
        """
        self.materials = {
            'bible' : bsk.Material(texture = images['bibleapp.png']),
            'red' : bsk.Material(color = (255, 0, 0)),
            'green' : bsk.Material(color = (0, 255, 0)),
            'blue' : bsk.Material(color = (0, 0, 255))
        }
        
    def load_meshes(self) -> None:
        """
        Loads all meshes from the meshes folder
        """
        self.meshes = {
            file_name[:-4] : bsk.Mesh(f'./meshes/{file_name}') 
            for file_name in os.listdir('./meshes') 
            if file_name.endswith('.obj')
        }
    
    def primary_update(self) -> None:
        """
        Updates all adjacent scenes and the engine
        """
        # update player data and actions
        self.player.update(self.engine.delta_time)
        
        # render and tick physics # TODO Jonah, I'm guessing you're going to need to separate a lot of stuff for render portals, 
        for level in self.adjacent_levels(self.current_level): level.scene.update()
        self.engine.update()
        
    @property
    def camera(self): return self.current_scene.camera
    @property
    def current_scene(self): return self.current_level.scene
    
    # reduce some typing for IO
    @property
    def keys(self): return self.engine.keys
    @property
    def previous_keys(self): return self.engine.previous_keys
    @property
    def mouse(self): return self.engine.mouse
    
    @property
    def update(self):
        # assumes that the update function has been overridden
        cur_update = self._update
        self._update = self.primary_update
        return cur_update
    
    @camera.setter
    def camera(self, value): self.current_scene.camera = value
    
    @update.setter
    def update(self, value):
        self._update = value