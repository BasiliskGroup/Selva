import basilisk as bsk
from render.renderer import Renderer
import glm


class PixelRenderer(Renderer):
    def __init__(self, scene):
        super().__init__(scene)

        self.main_shader = bsk.Shader(self.engine, frag='shaders/blinnPhong.frag')
        self.other_shader = bsk.Shader(self.engine, frag='shaders/blinnPhongOther.frag')
        self.dither_shader = bsk.Shader(self.engine, 'shaders/frame.vert', 'shaders/dither.frag')

        # self.temp_fbo = bsk.Framebuffer(self.engine)
        self.low_res_fbo = bsk.Framebuffer(self.engine, scale=.2, linear_filter=False)
        self.dither_fbo = bsk.Framebuffer(self.engine, self.dither_shader, scale=.2, linear_filter=False)
        self.fbo   = bsk.Framebuffer(self.engine, scale=.2, linear_filter=False)


    def render(self) -> None:
        """
        Renders the scene onto the fbo. Can access with Renderer.texture
        """
        
        self.dither_shader.write(glm.vec2(self.engine.win_size) * .2, 'textureSize')
        self.scene.render(self.low_res_fbo)
        self.low_res_fbo.render(self.dither_fbo)
        self.dither_fbo.render(self.fbo)


class PixelQuantizedRenderer(PixelRenderer):
    def __init__(self, scene):
        super().__init__(scene)

        self.dither_shader = bsk.Shader(self.engine, 'shaders/frame.vert', 'shaders/ditherQuantized.frag')
        self.dither_fbo = bsk.Framebuffer(self.engine, self.dither_shader, scale=.2, linear_filter=False)