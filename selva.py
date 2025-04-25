from game import Game

game = Game()

while game.engine.running:
    game.update()

# Fortnite

"""
improve fishing - difficulty
make pickup function look better (needs more scenes)
queue the player when picking up the first picture frame
add frame cycling with mouse scrolling
fix portal frame glitch (probably camera collision being bad)
"""