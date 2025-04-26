import basilisk as bsk
import moderngl as mgl


class Renderer:
    scene: bsk.Scene
    fbo: bsk.Framebuffer

    def __init__(self, scene: bsk.Scene) -> None:
        """
        Wrapper for scene rendering pipeline for portal rendering. Allows for custom pipelines.
        """
        
        self.scene = scene
        self.engine = scene.engine

        # Load the two used shaders
        # These should be essentially the same, but the other shader culls when behind the portal
        self.main_shader  = bsk.Shader(self.engine)
        self.other_shader = bsk.Shader(self.engine, 'shaders/other.vert', 'shaders/other.frag')

        self.sample_sky = bsk.Sky(self.scene, 'images/black.png')

        # Load an FBO
        self.fbo   = bsk.Framebuffer(self.engine)

    def update(self) -> None:
        """
        Updates the scene of the renderer without rendering the scene
        """
        
        self.scene.update(render=False)

    def render(self) -> None:
        """
        Renders the scene onto the fbo. Can access with Renderer.texture
        """
        
        self.scene.render(self.fbo)

    def bind(self) -> None:
        if 'skyboxTexture' in self.scene.shader.uniforms:
            if not self.scene.sky:
                self.scene.sky = self.sample_sky
                self.scene.sky.write()
                self.scene.sky = None
            else:
                self.scene.sky.write()

    def set_main(self) -> None:
        """
        Sets this renderer as a renderer for a main scene.
        """
        
        self.bind()
        self.scene.shader = self.main_shader

    def set_other(self) -> None:
        """
        Sets this renderer as a renderer for an other scene.
        """

        self.bind()
        self.scene.shader = self.other_shader

    @property
    def texture(self) -> mgl.Texture:
        return self.fbo.texture
    
    @property
    def depth(self) -> mgl.Texture:
        return self.fbo.depth