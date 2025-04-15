import glm
import basilisk as bsk
from helper.type_hints import Game
from levels.interactable import Interactable


class Level():
    
    def __init__(self, game: Game, name: str, portal_position: glm.vec3) -> None:
        self.game = game
        self.name = name
        self.scene = bsk.Scene(self.game.engine)
        self.scene.physics_engine.accelerations = [glm.vec3(0, -25, 0)]
        
        self.interactables: dict[bsk.Node, Interactable] = {}
        
        self.portal_position = glm.vec3(portal_position)
        
    def update(self, render: bool=True, nodes: bool=True, particles: bool=True, collisions: bool=True) -> None:
        """
        Updates the scene as normal and all interactables in the level
        """
        self.scene.update(render, nodes, particles, collisions)
        for interactable in self.interactables.values():
            if interactable.passive: interactable.passive(self.game.engine.delta_time)
        
    def add(self, *args) -> None:
        """
        Add nodes and interactables to a scene. Args can also be lists of Nodes/Interactables
        """
        for arg in args: 
            if isinstance(arg, bsk.Node): self.scene.add(arg) # if Node, add Node to the scene as normal
            elif isinstance(arg, (list, tuple)): self.add(*arg) # if list, resurse
            elif isinstance(arg, Interactable): # if interactable, keep the remember which node goes to who for detemining who's being interacted with
                self.scene.add(arg.node)
                self.interactables[arg.node] = arg
    
    def __getitem__(self, node: bsk.Node) -> Interactable:
        """
        Gets the ineractable from the given Node if that Node is associated with an Interactable.
        If there is no Interactable, then return None
        """
        if node not in self.interactables: return None
        return self.interactables[node]
            
    def render(self, target): self.scene.render(target)