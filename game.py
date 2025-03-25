import os
import basilisk as bsk
from levels.level import Level
from levels.generators.imports import *

from player.player import Player
from materials.images import images
from memories.memory_handler import MemoryHandler


class Game():
    
    def __init__(self) -> None:
        # Basilisk Engine overhead
        self.engine = bsk.Engine()
        self.ui_scene = bsk.Scene(self.engine) # scene to contain player UI like held items
        self.overlay_scene = bsk.Scene(self.engine) # this scene will render over 
        self.day = True
        
        # game components
        self.images = images
        self.load_materials()
        self.load_meshes()
        self.load_sounds()
        
        # level layout
        self.memory_handler = MemoryHandler(self)
        # self.memory_handler['boat'] = boat(self)
        # self.memory_handler['office'] = office(self)
        self.memory_handler['bedroom'] = bedroom(self)
        
        # player
        self.player = Player(self)
        
        # frame by frame updating
        self.left_mouse_time = self.right_mouse_time = 0
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
        saturation = 70
        self.materials = {
            # textured
            'battery' : bsk.Material(texture = images['battery.png']),
            'crt' : bsk.Material(texture = images['crt.png']),
            'picture_frame' : bsk.Material(texture = images['uv_map.png']),
            'john' : bsk.Material(texture = images['john.png']),
            'wheel_eight' : bsk.Material(texture = images['wheel_eight.png']),
            'box_three' : bsk.Material(texture = images['box_three.png']),
            'suits' : bsk.Material(texture = images['suits.png']),
            'battery_box' : bsk.Material(texture = images['battery_box.png']),
            'office_window' : bsk.Material(texture = images['office_window.png']),
            'coffee_maker' : bsk.Material(texture = images['coffee_maker.png']),
            'boat' : bsk.Material(texture = images['boat.png']),
            'ocean' : bsk.Material(texture = images['ocean.jpg']),
            'fishing_rod' : bsk.Material(texture = images['fishing_rod.png']),
            'flounder' : bsk.Material(texture = images['flounder.png']),
            'tuna' : bsk.Material(texture = images['tuna.png']),
            'tilapia' : bsk.Material(texture = images['tilapia.png']),
            'herring' : bsk.Material(texture = images['herring.png']),
            'bass' : bsk.Material(texture = images['bass.png']),
            # pure colors
            'white' : bsk.Material(color = (220, 220, 220)),
            'red' : bsk.Material(color = (255, saturation, saturation)),
            'green' : bsk.Material(color = (saturation, 255, saturation)),
            'blue' : bsk.Material(color = (saturation, saturation, 255)),
            'light_white' : bsk.Material(color = [240 for _ in range(3)]),
            'bright_wood' : bsk.Material(color = (183, 170, 131)),
            'light_wood' : bsk.Material(color = (142, 124, 94)),
            'dark_wood' : bsk.Material(color = (59, 34, 24)),
            'dry_wall' : bsk.Material(color = (181, 190, 179)),
            'dirty_carpet' : bsk.Material(color = (90, 70, 35))
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
        
    def load_sounds(self) -> None:
        """
        Loads all sounds from the sounds folder
        """
        self.sounds = {
            file_name[:-4] : bsk.Sound(f'./sounds/{file_name}') 
            for file_name in os.listdir('./sounds') 
            if file_name.endswith('.mp3')
        }
    
    def primary_update(self) -> None:
        """
        Updates all adjacent scenes and the engine
        """
         # update player data and actions
        self.player.update(self.engine.delta_time)
        
        # render and tick physics # TODO Jonah, I'm guessing you're going to need to separate a lot of stuff for render portals, 
        bsk.draw.circle(self.engine, (0, 0, 0), (self.engine.win_size[0] / 2, self.engine.win_size[1] / 2), radius = 2)
        for level in self.adjacent_levels(self.current_level): level.update()
        
        self.track_io_holds()
        self.ui_scene.update()
        self.overlay_scene.update()
        self.engine.update()
        
    def track_io_holds(self) -> None:
        """
        Tracks the in-game time that certain io elements have stayed on
        """
        self.right_mouse_time = self.engine.delta_time + self.right_mouse_time if self.engine.mouse.right_down else 0
        self.left_mouse_time = self.engine.delta_time + self.left_mouse_time if self.engine.mouse.left_down else 0
        
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
    def current_level(self) -> Level: return self.memory_handler.current_level
    
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
        
    