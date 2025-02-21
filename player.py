from basilisk import Node
from type_hints import Game

class Player():
    
    def __init__(self, game: Game):
        self.game = game
        