import time
from typing import Any
import glm
import basilisk as bsk
from helper.transforms import plane_mirror
from helper.type_hints import Game, Level
from player.held_items.held_item import HeldItem, PictureFrame
from player.player_nodes import player_nodes
from player.held_items.held_ui import HeldUI
from levels.classes.fish import FishTracker


class Player():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        
        # constant variables
        self.HEIGHT = 2 # vertical scale of the node, 1x2x1
        self.SPEED = 5 # the velocity of the player's node when moving
        self.DECELERATION_COEFFICIENT = 10
        
        # Main body used for stabilizing collisions on the camera
        self.body_node, self.loader = player_nodes(self.game)
        self.current_scene.add(self.body_node, self.loader)
        
        # variables for controling the player's held items
        self.item_r_ui = HeldUI(self.game, glm.vec3(0.5, -0.4, 1.2))
        self.item_l_ui = HeldUI(self.game, glm.vec3(-0.5, -0.4, 1.2))
        
        # game interaction variables
        self.fish_tracker = FishTracker()
        
        self.gravity = glm.vec3(0, -9.8, 0)
        self.control_disabled = False
        
        # camera swapping
        self.game.hold_camera = self.current_scene.camera
        self.camera = self.game.current_scene.camera = bsk.FollowCamera(self.body_node, offset = (0, 1.5, 0))
        
        self.previous_position = glm.vec3(self.camera.position)
        
    def update(self, dt: float) -> None:
        """
        Updates the players movement, Nodes, and controls
        """
        self.loader.position = self.body_node.position
        
        # player controls
        if not self.control_disabled: 
            # player controls
            self.move(dt)
            self.item_r_ui.update(dt)
            self.item_l_ui.update(dt)
            self.interact(dt)
            self.debug()
            self.picture_swap(dt)
            if self.game.key_down(bsk.pg.K_q): self.item_r_ui.drop()
        
        # update user node to preserve direction
        self.body_node.rotation = self.horizontal_quat
        self.body_node.rotational_velocity = glm.vec3(0, 0, 0)
        
        # hover stabilizes camera and prevents player from falling
        self.position.y = 2.1
        self.velocity.y = 0
        
        if not self.item_l: return
        if self.game.current_level.name == self.item_l.level_name: self.item_l_ui.node.mesh = self.game.meshes['picture_frame']
        else: self.item_l_ui.node.mesh = self.game.meshes['empty_frame']
        
    def debug(self) -> None:
        if not self.game.engine.keys[bsk.pg.K_LSHIFT]: return
        if self.game.key_down(bsk.pg.K_1):
            self.item_r = HeldItem(self.game, bsk.Node(
                position = (3.5, 2.4, -4.35),
                scale = (0.1, 0.1, 0.1),
                rotation = glm.angleAxis(-glm.pi() / 2, (0, 1, 0)) * glm.angleAxis(glm.pi() / 2, (1, 0, 0)),
                mesh = self.game.meshes['key'],
                tags = ['color_key']
            ))
        if self.game.key_down(bsk.pg.K_2):
            self.item_r = HeldItem(self.game, bsk.Node(
                position = (1.5, 2.25, 4.35),
                scale = glm.vec3(0.1),
                mesh = self.game.meshes['mug'],
                tags = ['empty_mug']
            ))
        if self.game.key_down(bsk.pg.K_3):
            self.item_r = HeldItem(self.game, bsk.Node(
                position = (-0.3, 0.5, 0.9),
                scale = glm.vec3(0.03),
                mesh = self.game.meshes['wire'],
                material = self.game.materials['copper'],
                tags = ['copper_wire']
            ))
        if self.game.key_down(bsk.pg.K_4):
            self.item_r = HeldItem(self.game, bsk.Node(
                position = (-3, 1.9, -0.2),
                scale    = glm.vec3(0.2),
                rotation = glm.angleAxis(glm.pi() / 2, (0, 1, 0)),
                mesh     = self.game.meshes['battery'],
                material = self.game.materials['battery'],
                tags     = ['battery']
            ))
        
    def picture_swap(self, dt) -> None:
        """
        Swaps the portal in the player's hand
        """
        if not self.item_l: return
        
        current_level_name = self.item_l.level_name
        nums = [bsk.pg.K_1, bsk.pg.K_2, bsk.pg.K_3, bsk.pg.K_4, bsk.pg.K_5, bsk.pg.K_6, bsk.pg.K_7, bsk.pg.K_8, bsk.pg.K_9]
        for i, key in enumerate(nums): 
            if not self.game.key_down(key): continue
            self.item_l_ui.index = i
            break
        
        if current_level_name == self.item_l.level_name: return # portal was not changed
        self.game.close()
        # update portal exit
        self.game.portal_handler.set_levels(self.game.current_level, self.game.memory_handler[self.item_l.level_name])
        
    def teleport(self) -> None:
        """
        Teleports the player through a portal if they have collided with one between frames
        """
        # test if the player has gone through a portal
        position = glm.vec3(self.camera.position)
        if self.previous_position == position: return
        
        # checks for collision with a portal
        collision = self.collide()
        if not collision:
            self.previous_position = glm.vec3(position)
            return
        
        # transform position/rotation relative to portal
        pc, pl = (self.game.entry_portal, self.game.exit_portal) if self.game.entry_portal == collision.node else (self.game.exit_portal, self.game.entry_portal)
        position = plane_mirror(self.previous_position, pc.position.data, collision.normal)
        self.camera.position = position
        
        mc = pl.model_matrix * glm.inverse(pc.model_matrix) * self.camera_model_matrix
        position = glm.vec3(mc[3])
        self.position = glm.vec3(position)
        self.body_node.rotation = self.body_node.rotation * glm.inverse(pc.rotation.data) * pl.rotation.data
        
        self.swap_to_level(pl.tags[1], position)
    
    def swap_to_level(self, level_name: str, position: glm.vec3) -> None:
        # update player scene and possibly portal node scene
        self.game.current_scene.remove(self.body_node)
        self.game.current_scene.remove(self.loader)
        
        # swap scene and camera
        self.game.current_scene.camera = self.game.hold_camera
        self.game.memory_handler.current_level = self.game.memory_handler[level_name] # swaps game current scene
        self.game.hold_camera = self.game.current_scene.camera
        self.game.current_scene.camera = self.camera
        
        # add player back to scene
        self.game.current_scene.add(self.body_node)
        self.game.current_scene.add(self.loader)
        
        # swap rendering
        
        self.game.portal_handler.swap()
        
        # update for next frame
        self.previous_position = glm.vec3(position)
        self.position.y = 2.1
        
    def collide(self) -> None | Any:
        """
        Determines if the camera has collided with an object between frames 
        """
        diff = self.camera.position - self.previous_position
        direction, move_distance = glm.normalize(diff), glm.length(diff)
        cast = self.game.current_scene.raycast(position=self.previous_position, forward=direction)
        if not cast.node or len(cast.node.tags) != 2 or cast.node.tags[0] != 'portal': return
        
        cast_distance = glm.length(cast.position - self.previous_position)
        if cast_distance > move_distance: return
        return cast
    
    def move(self, dt: float) -> None:
        """
        Controls the player movement from the input of the 
        """
        # control player movement WASD
        proposed = glm.vec3(0, 0, 0)
        proposed += self.camera.horizontal * (self.game.keys[bsk.pg.K_w] - self.game.keys[bsk.pg.K_s]) 
        proposed += self.camera.right * (self.game.keys[bsk.pg.K_d] - self.game.keys[bsk.pg.K_a])
        
        if proposed == (0, 0, 0): self.body_node.velocity *= (1 - self.DECELERATION_COEFFICIENT * dt)
        else: self.body_node.velocity = self.SPEED * glm.normalize(proposed)
        
    def interact(self, dt: float) -> None:
        """
        If the player is pressing E, interact with what they are looking at. 
        """
        # determine if the player is interacting with a valid object
        cast = self.current_scene.raycast(has_collisions=False) # will find the player's hitbox
        if not cast.node: return
        interactable = self.current_level[cast.node]
        if not interactable: return
        bsk.draw.blit(self.game.engine, self.game.images['label_e.png'], (self.game.win_size.x // 2, self.game.win_size.y // 2, 20, 20))
        if not self.game.keys[bsk.pg.K_e]: return
        
        # use the Interactable's functionality
        if interactable.active: interactable.active(dt)

    @property
    def position(self): return self.body_node.position
    @property
    def velocity(self): return self.body_node.velocity
    @position.setter
    def position(self, value: glm.vec3): self.body_node.position = value
    @velocity.setter
    def velocity(self, value: glm.vec3): self.body_node.velocity = value
    
    @property
    def horizontal_quat(self) -> glm.quat: return glm.conjugate(glm.quat((0, self.camera.yaw, self.camera.roll)))
    
    # derived properties from the game
    @property
    def current_scene(self): return self.game.current_scene
    @property
    def current_level(self) -> Level: return self.game.current_level
    
    @property
    def control_disabled(self): return self._control_disabled
    @control_disabled.setter
    def control_disabled(self, value: bool):
        self._control_disabled = value
        
    # held items
    @property
    def item_r(self) -> HeldItem: return self.item_r_ui.item
    @item_r.setter
    def item_r(self, value) -> HeldItem: self.item_r_ui.item = value
    
    @property
    def item_l(self) -> HeldItem: return self.item_l_ui.item
    @item_l.setter
    def item_l(self, value) -> HeldItem: self.item_l_ui.item = value
    
    @property
    def camera_model_matrix(self) -> glm.mat4x4:
        m_mat = glm.translate(glm.mat4x4(1.0), self.camera.position)
        m_mat *= glm.mat4_cast(self.body_node.rotation.data)
        return m_mat