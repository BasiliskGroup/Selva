import basilisk as bsk
from render.renderer import Renderer


class KuwaharaRenderer(Renderer):
    def __init__(self, scene):
        super().__init__(scene)

        self.kuwahara_shader = bsk.Shader(self.engine, 'shaders/frame.vert', 'shaders/kuwahara.frag')
        self.kuwahara_fbo    = bsk.Framebuffer(self.engine, self.kuwahara_shader)

    def render(self) -> None:
        """
        Renders the scene onto the fbo. Can access with Renderer.texture
        """
        
        self.scene.render(self.kuwahara_fbo)
        self.kuwahara_fbo.render(self.fbo)