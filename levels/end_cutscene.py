import basilisk as bsk
import random


class EndCutscene:
    engine: bsk.Engine
    def __init__(self, game):
        self.game = game
        self.engine = game.engine

        # Create a new blank scene
        self.scene = bsk.Scene(self.engine)

    def make_scene(self):
        """
        Adds all the nodes to the scene
        """
        
        # Clears the scene in case we are returning to this menu
        self.scene.clear()

        # Set camera at origin
        self.scene.camera = bsk.StaticCamera((0, 0, 7.5))

        # Black void moment
        self.scene.sky = bsk.Sky(self.scene, './images/white.jpg')

        # Create the emissive material used
        self.mtl = bsk.Material(color=(0, 0, 0), emissive_color=(30, 30, 30))
        self.title_node = bsk.Node(position=(0, 0, 0), mesh=self.game.meshes['selva_title'], material=self.mtl, scale=1.5)
        self.scene.add(self.title_node)

    def update(self):
        """
        Updates the menu. Increments time. Checks for input. Adds particles. Handles start sequence.
        """

        self.time += self.engine.delta_time
        if self.time > 2: 
            self.running = False
            self.game.engine.running = False

    def start(self):
        """
        Starts the main menu, taking control of the game/engine
        """

        self.time = 0
        self.start_sequence = False
        self.make_scene()
        
        self.running = True
        while self.running and self.engine.running:
            self.update()

            self.scene.update()
            self.engine.update()