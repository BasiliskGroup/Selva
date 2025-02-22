import basilisk as bsk
from helper.type_hints import Game


class Level():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.scene = bsk.Scene(self.game.engine)