import time
from typing import Any
import glm
import basilisk as bsk
from helper.transforms import plane_mirror
from helper.type_hints import Game, Level
from player.held_items.held_item import HeldItem, PictureFrame
from player.player_nodes import player_nodes
from player.held_items.held_ui import HeldUI
from levels.functions.imports import simulate_gravity_node
from levels.classes.fish import FishTracker


class Player():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        
        # constant variables
        self.HEIGHT = 2 # vertical scale of the node, 1x2x1
        self.SPEED = 5 # the velocity of the player's node when moving
        self.DECELERATION_COEFFICIENT = 10
        
        # Main body used for stabilizing collisions on the camera
        self.body_node = player_nodes(self.game)
        self.current_scene.add(self.body_node)
        
        # variables for controling the player's held items
        self.item_r_ui = HeldUI(self.game, glm.vec3(0.45, -0.25, 1.2))
        self.item_l_ui = HeldUI(self.game, glm.vec3(-0.45, -0.25, 1.2))
        
        # game interaction variables
        self.fish_tracker = FishTracker()
        
        self.gravity = glm.vec3(0, -9.8, 0)
        self.control_disabled = False
        self.camera = self.current_scene.camera = bsk.FollowCamera(self.body_node, offset = (0, 1.5, 0)) # TODO ensure that this camera is passed between scenes depending on where the player is NOTE this will act as the main player camera
        
        self.previous_position = glm.vec3(self.camera.position)
        
    def update(self, dt: float) -> None:
        """
        Updates the players movement, Nodes, and controls
        """
        self.teleport()
        
        # player controls
        if not self.control_disabled: 
            # player controls
            self.move(dt)
            self.item_r_ui.update(dt)
            self.item_l_ui.update(dt)
            self.interact(dt)
            if self.game.right_mouse_time > 1.5: self.item_r_ui.drop()
        
        # update user node to preserve direction
        self.body_node.rotation = self.horizontal_quat
        self.body_node.rotational_velocity = glm.vec3(0, 0, 0)
        
        # hover stabilizes camera and prevents player from falling
        self.position.y = 2.1
        self.velocity.y = 0
        
    def teleport(self) -> None: # TODO enable with multiple scenes
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
        
        # update player position based on collision
        level: Level = self.game.memory_handler[collision.node.tags[1]]
        
        
        print('teleporting', time.time())
        
        # transform position/rotation relative to portal
        pc, pl = (self.game.entry_portal, self.game.exit_portal) if self.game.entry_portal == collision.node else (self.game.exit_portal, self.game.entry_portal)
        position = plane_mirror(self.previous_position, pc.position.data, collision.normal)
        
        mc = pl.model_matrix * glm.inverse(pc.model_matrix) * self.camera_model_matrix
        position = glm.vec3(mc[3])
        self.position = glm.vec3(position)
        self.body_node.rotation = self.body_node.rotation * glm.inverse(pc.rotation.data) * pl.rotation.data
        
        print(position)
        
        # update for next frame
        self.previous_position = glm.vec3(position)
        
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
        
        # TODO add jumping once camera is stabilized
        
    def interact(self, dt: float) -> None:
        """
        If the player is pressing E, interact with what they are looking at. 
        """
        # determine if the player is interacting with a valid object
        if not self.game.keys[bsk.pg.K_e]: return
        cast = self.current_scene.raycast(has_collisions=False) # will find the player's hitbox
        if not cast.node: return
        interactable = self.current_level[cast.node]
        if not interactable: return
        
        # use the Interactable's functionality
        if interactable.active: interactable.active(dt)

    @property
    def position(self): return self.body_node.position # TODO offset this position to be at the node's feet
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
    
    # TODO check if this is needed for the game
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