import os


class LoadingScreen:
    def __init__(self, game):
        self.engine = game.engine

        self.progess = 0
        self.total = len(os.listdir('./meshes')) + len(os.listdir('./sounds')) + len(os.listdir('./images'))

    def update(self):
        self.engine