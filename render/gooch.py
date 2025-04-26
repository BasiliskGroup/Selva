import basilisk as bsk
import moderngl as mgl
from render.renderer import Renderer


class GoochRenderer(Renderer):
    def __init__(self, scene):
        super().__init__(scene)

        self.main_shader = bsk.Shader(self.engine, frag='shaders/gooch.frag')
        self.other_shader = bsk.Shader(self.engine, frag='shaders/goochOther.frag')
        self.outline_shader = bsk.Shader(self.engine, 'shaders/frame.vert', 'shaders/outline.frag')
        self.combine_shader = bsk.Shader(self.engine, 'shaders/frame.vert', 'shaders/combineOutline.frag')

        # self.temp_fbo = bsk.Framebuffer(self.engine)
        self.edge_detect_fbo = bsk.Framebuffer(self.engine, self.outline_shader)
        self.outline_fbo     = bsk.Framebuffer(self.engine)
        self.gooch_fbo       = bsk.Framebuffer(self.engine)
        self.combine_fbo     = bsk.Framebuffer(self.engine, self.combine_shader)



    def render(self) -> None:
        """
        Renders the scene onto the fbo. Can access with Renderer.texture
        """
        
        self.scene.render(self.gooch_fbo)


        self.edge_detect_fbo.bind(self.scene.frame.input_buffer.depth, 'depthTexture', 0)
        self.edge_detect_fbo.bind(self.scene.frame.input_buffer.color_attachments[2], 'normalTexture', 1)
        self.edge_detect_fbo.render(self.outline_fbo, auto_bind=False)

        self.combine_fbo.bind(self.gooch_fbo.texture, 'mainTexture', 2)
        self.combine_fbo.bind(self.outline_fbo.texture, 'outlineTexture', 3)
        self.combine_fbo.render(self.fbo, auto_bind=False)
