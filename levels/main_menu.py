import basilisk as bsk
import random


class MainMenu:
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
        self.scene.sky = None

        # Create the emissive material used
        self.mtl = bsk.Material(color=(255, 255, 255), emissive_color=(150, 150, 150))

        self.title_node   = bsk.Node(position=(0, 1, 0), mesh=self.game.meshes['selva_title'], material=self.mtl, scale=1.5)
        self.start_node   = bsk.Node(position=(0, -.5, 0), mesh=self.game.meshes['start'], material=self.mtl)

        self.scene.add(self.title_node, self.start_node)

    def add_particle(self):
        """
        Adds a random particle to the menu
        """

        if self.time <= 0.01: return
        self.time = 0
        
        padding = 4
        speed = random.randrange(0, 10) / 30
        
        
        side = random.randint(1, 4)
        if side == 1:
            # From left
            pos = (padding, random.randrange(-padding, padding), -.5)
            vel = [-speed, random.randrange(-1, 2) * speed, -.5]
        elif side == 2:
            # From left
            pos = (-padding, random.randrange(-padding, padding), -.5)
            vel = [speed, random.randrange(-1, 2) * speed, -.5]
        elif side == 3:
            # From left
            pos = (random.randrange(-padding, padding), padding, -.5)
            vel = [random.randrange(-1, 2) * speed, -speed, -.5]
        else:
            # From left
            pos = (random.randrange(-padding, padding), -padding, -.5)
            vel = [random.randrange(-1, 2) * speed, speed, -.5]

        # Get the acceleration base on the mouse position
        w, h = self.engine.win_size
        mouse_pos = self.engine.mouse.position
        mouse_pos = mouse_pos[0] / w - 0.5, mouse_pos[1] / h - 0.5

        accel = [random.randrange(-10, 11) / 40 for i in range(3)]
        vel[0] -= mouse_pos[0] * 1.5
        vel[1] += mouse_pos[1] * 1.5

        self.scene.particle.add(position=pos, scale=.02/3, life=6, velocity=vel, acceleration=accel, material=self.mtl)

    def update(self):
        """
        Updates the menu. Increments time. Checks for input. Adds particles. Handles start sequence.
        """

        self.time += self.engine.delta_time

        if self.engine.mouse.click and not self.start_sequence:
            self.time = 0
            self.start_sequence = True

        if not self.start_sequence:
            self.add_particle()
            return
        
        self.title_node.velocity.y   += 1 * self.engine.delta_time
        self.start_node.velocity.y   += 1 * self.engine.delta_time

        if self.time > 7: 
            print('stop')
            self.running = False

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