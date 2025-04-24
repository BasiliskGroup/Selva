import os
import basilisk as bsk


class LoadingScreen:
    engine: bsk.Engine
    def __init__(self, game):
        self.engine = game.engine

        self.banner = bsk.Image('images/basilisk_banner.png', flip_y=False)

        self.progess = 0
        self.total = len(os.listdir('./meshes')) + len(os.listdir('./sounds')) + len(os.listdir('./images')) + 1

        self.update()

    def update(self):
        """
        Increments the progress bar and draws the screen
        """
        
        # Increment the progress bar
        self.progess += 1

        # Get display variables
        win_size = self.engine.win_size
        x, y, w, h = win_size[0] / 4, win_size[1] / 4 * 3, win_size[0] / 2, 50

        # Draw the basilisk banner
        width, height = 500, 250
        bsk.draw.blit(self.engine, self.banner, ((win_size[0] - width) / 2, 200, width, height))

        # Draw the progress
        p = 2
        bsk.draw.rect(self.engine, (255, 255, 255), (x - p, y - p, w + p * 2, h + p * 2))
        bsk.draw.rect(self.engine, (0, 0, 0), (x, y, w, h))
        bsk.draw.rect(self.engine, (255, 255, 255), (x + p, y + p, w / self.total * self.progess - p * 2, h - p * 2))

        self.engine.update()