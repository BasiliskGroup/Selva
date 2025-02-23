import basilisk as bsk
from helper.type_hints import Game
from levels.interactable import Interactable


class Level():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.scene = bsk.Scene(self.game.engine)
        
        self.interactables: dict[bsk.Node, Interactable] = {}
        
    def add(self, *args):
        """
        Add nodes and interactables to a scene. Args can also be lists of Nodes/Interactables
        """
        for arg in args: 
            if isinstance(arg, bsk.Node): self.scene.add(arg) # if Node, add Node to the scene as normal
            elif isinstance(arg, (list, tuple)): self.add(*arg) # if list, resurse
            elif isinstance(arg, Interactable): # if interactable, keep the remember which node goes to who for detemining who's being interacted with
                self.scene.add(arg.node)
                self.interactables[arg.node] = arg
            