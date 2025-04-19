import os
import basilisk as bsk
from levels.level import Level
from levels.generators.imports import *

from player.player import Player
from images.images import images
from memories.memory_handler import MemoryHandler
from ui.effects import *


class Game():
    
    def __init__(self) -> None:
        # Basilisk Engine overhead
        self.engine = bsk.Engine()    
        self.ui_scene = bsk.Scene(self.engine) # scene to contain player UI like held items
        self.ui_scene.sky = None
        self.overlay_scene = bsk.Scene(self.engine) # this scene will render over 
        self.overlay_scene.sky = None
        self.overlay_scene.add(bsk.Node(scale = (1, 10, 1)))

        # global puzzle variables
        self.day = True
        
        # game components
        self.images = images
        self.load_materials()
        self.load_meshes()
        self.load_sounds()
        self.load_shaders()
        self.load_fbos()
        
        # portals
        self.entry_portal = bsk.Node(
            scale = (1, 2.5, 0.001),
            tags = ['portal', ''],
            material = self.materials['red']
        )
        
        self.exit_portal = bsk.Node(
            scale = (1, 2.5, 0.001),
            tags = ['portal', ''],
            material = self.materials['red']
        )
        
        # ui
        self.ui = UI(self)
        
        # level layout
        self.memory_handler = MemoryHandler(self)
        # self.memory_handler['void'] = void(self)
        # self.memory_handler['bedroom1'] = bedroom1(self)
        # self.memory_handler['office'] = office(self)
        # self.memory_handler['boat'] = boat(self)
        # self.memory_handler['art'] = art(self)
        self.memory_handler['bedroom2'] = bedroom2(self)
        
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
        
        png_names = [
            'john', 'wheel_eight', 'box_three', 'picture_frame', 'fortune_dresser', 'fake_door', 'paper',
            'crt', 'hang_in_there', 'battery_box', 'office_window', 'coffee_maker', 'battery', 'coffee_mug', 'bulb', 'calendar',
            'boat', 'fishing_rod', 'flounder', 'tuna', 'tilapia', 'herring', 'bass', 'bait_bucket', 'worm', 'squid', 'squid_red', 'squid_orange', 'squid_yellow', 'squid_green', 'squid_blue', 'squid_purple',
            'art_table', 'bear_chair', 'art_wall', 'art_ceiling', 'paint_bucket_red', 'paint_bucket_blue', 'paint_bucket_green', 'window_two_pane', 'color_combos', 'color_key', 'key_key',
        ] + [f'key{i}' for i in range(1, 10)]
        
        self.materials = {name : bsk.Material(texture = images[f'{name}.png']) for name in png_names}
        self.materials['ocean'] = bsk.Material(texture = images['ocean.jpg'])
        self.materials['white'] = bsk.Material(color = (220, 220, 220))
        self.materials['black'] = bsk.Material(color = (20, 20, 20))
        self.materials['red'] = bsk.Material(color = (255, saturation, saturation))
        self.materials['green'] = bsk.Material(color = (saturation, 255, saturation))
        self.materials['blue'] = bsk.Material(color = (saturation, saturation, 255))
        self.materials['purple'] = bsk.Material(color = (117, 45, 112))
        self.materials['orange'] = bsk.Material(color = (223, 114, 60))
        self.materials['yellow'] = bsk.Material(color = (211, 198, 74))
        self.materials['light_white'] = bsk.Material(color = [240 for _ in range(3)])
        self.materials['bright_wood'] = bsk.Material(color = (183, 170, 131))
        self.materials['light_wood'] = bsk.Material(color = (142, 124, 94))
        self.materials['dark_wood'] = bsk.Material(color = (59, 34, 24))
        self.materials['dry_wall'] = bsk.Material(color = (181, 190, 179))
        self.materials['dirty_carpet'] = bsk.Material(color = (90, 70, 35))
        self.materials['bloom_white'] = bsk.Material(color = (255, 255, 255), emissive_color=(300, 300, 300))
        self.materials['cooper'] = bsk.Material(color = (209, 131, 85))
        
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
    
    def load_shaders(self) -> None:
        """
        Loads all shaders from the shaders folder
        """
        self.shaders = {
            'kuwahara' : bsk.Shader(self.engine, vert="shaders/frame.vert", frag="shaders/kuwahara.frag")
        }
        
    def load_fbos(self) -> None:
        """
        
        """
        self.fbos = {
            'kuwahara' : bsk.Framebuffer(self.engine, self.shaders['kuwahara'])
        }
    
    def primary_update(self) -> None:
        """
        Updates all adjacent scenes and the engine
        """
        # tick physics and interact updates
        for level in self.adjacent_levels(self.current_level): level.update(render=False)
        
        # update player data and actions
        self.player.update(self.engine.delta_time)
        self.track_io_holds()
        
        # standard ui
        bsk.draw.circle(self.engine, (0, 0, 0), (self.engine.win_size[0] / 2, self.engine.win_size[1] / 2), radius = 2)
        self.ui.update(self.engine.delta_time)
        
        # render all levels
        for level in self.adjacent_levels(self.current_level): level.render(self.fbos['kuwahara']) # 
        
        self.ui_scene.update()
        self.overlay_scene.update()
        self.overlay_scene.render(self.fbos['kuwahara'])
        
        self.fbos['kuwahara'].render()
        
        self.engine.update(render=True)
        
    def track_io_holds(self) -> None:
        """
        Tracks the in-game time that certain io elements have stayed on
        """
        self.right_mouse_time = self.engine.delta_time + self.right_mouse_time if self.engine.mouse.right_down else 0
        self.left_mouse_time = self.engine.delta_time + self.left_mouse_time if self.engine.mouse.left_down else 0
        
    def open(self, exit: Level) -> None:
        """
        Despawns current portals and opens them in new scenes
        """
        entry = self.current_level
        
        # do this if it is not the first time spawning a portal
        if self.entry_portal.node_handler: 
            self.entry_portal.node_handler.scene.remove(self.entry_portal)
            self.exit_portal.node_handler.scene.remove(self.exit_portal)
            
        # prevent opening a portal in the same scene
        # if entry == exit: return TODO uncomment
        rotation = glm.conjugate(glm.quatLookAt(self.camera.horizontal, (0, 1, 0)))
            
        # add entry portal at player location
        self.entry_portal.position = self.player.position + self.camera.forward * 0.2
        self.entry_portal.rotation = rotation
        self.entry_portal.tags[1] = entry.name
        self.current_level.add(self.entry_portal)
        
        # add portal at destination level
        self.exit_portal.position = exit.portal_position + glm.vec3(0, 2, 0)
        self.exit_portal.rotation = rotation
        self.exit_portal.tags[1] = exit.name
        exit.add(self.exit_portal)
        
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
        
    @property
    def win_size(self) -> glm.vec2: return glm.vec2(self.engine.win_size)