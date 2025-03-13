from typing import Any
import basilisk as bsk
import glm
from helper.type_hints import Game
from levels.interactable import Interactable
from player.held_item import HeldItem
from levels.functions.imports import interact_to_hold, simulate_gravity_node


class HeldUI():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.node = bsk.Node()
        self.items: list[HeldItem] = []
        self.index = 0
        
        self.game.current_scene.add(self.node) # TODO Later change this to a specific UI scene
        
    def update(self, dt: float) -> None:
        """
        Updates the position of the held item and the function
        """
        if not self.item:
            self.node.position = glm.vec3(0, 1000, 0)
            return
        
        self.node.position = self.camera.position + self.item.offset.x * self.camera.right + self.item.offset.y * self.camera.up + self.item.offset.z * self.camera.forward
        self.node.rotation = self.item.rotation * glm.conjugate(self.camera.rotation)
        if self.item.func: self.item.func(dt)
        
    def add(self, item: HeldItem) -> None: self.items.append(item)
        
    def remove(self, item: HeldItem) -> None | HeldItem:
        """
        Removes item and preserves which item the player was holding if the item removed was not the one held
        """
        if item not in self.items: return
        index = self.items.index(item)
        self.items.remove(item)
        if index <= self.index: self -= 1
        return item
        
    def drop(self) -> Interactable:
        """
        Removes the item from the ui element and spawns a falling Interactable in the current scene
        """
        if not self.item: return # can't drop an item you don't have
        
        item = self.remove(self.item)
        interact = Interactable(level = self.game.current_level, node = item.node)
        
        # freeze interact node from any previous movement
        interact.node.position = self.game.camera.position - glm.vec3(0, 0.5, 0)
        interact.node.rotation = glm.quat()
        interact.node.velocity = glm.vec3()
        interact.node.rotational_velocity = glm.vec3()
        
        # define interact bahvior and add to level
        interact.active = interact_to_hold(interact, item)
        interact.passive = simulate_gravity_node(self.game, self.game.current_scene, interact, interact.node)
        self.game.current_level.add(interact)
        return interact
        
    def __iadd__(self, num: int) -> Any: 
        self.index = (self.index + num) % self.safe_len
        return self
    def __isub__(self, num: int) -> Any: 
        self.index = (self.index - num) % self.safe_len
        return self
        
    @property
    def item(self) -> None | HeldItem:
        if not len(self.items): return None
        return self.items[self.index]
    @item.setter
    def item(self, value: HeldItem):
        # search for held item in the list and change 
        if value in self.items: self.index = self.items.index(value)
        else:
            self.items.append(value)
            self.index = len(self.items) - 1
    
    # force index to be within bounds of the array
    @property
    def safe_len(self): return len(self.items) if len(self.items) else 1
    @property
    def index(self): return self._index
    @index.setter
    def index(self, value): 
        self._index = value % self.safe_len
        # update node properties
        if not len(self.items): return
        self.node.scale = self.item.node.scale
        self.node.mesh = self.item.node.mesh
        self.node.material = self.item.node.material
    
    # commonly properties derived from the game
    @property
    def player(self): return self.game.player
    @property
    def camera(self): return self.game.camera
        
    @property
    def position(self): return self.node.position
    @property
    def rotation(self): return self.node.position
    @property
    def scale(self): return self.node.scale
    
    @position.setter
    def position(self, value): self.node.position = value
    @rotation.setter
    def rotation(self, value): self.node.rotation = value
    @scale.setter
    def scale(self, value): self.node.scale = value