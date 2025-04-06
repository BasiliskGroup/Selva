import basilisk as bsk
import glm
from helper.type_hints import Game

class UI():
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.effects: list[Effect] = []
        
    def update(self, dt: float) -> None:
        """
        Updates all effects in the UI (Probably blit to screen)
        """
        for effect in self.effects: effect.update(dt)
        
    def add(self, effect) -> None:
        """
        Adds an effect to the UI list
        """
        self.effects.append(effect)
    
    @property
    def engine(self) -> bsk.Engine: return self.game.engine
    
class Effect():
    
    def __init__(self, ui: UI, position: glm.vec2) -> None:
        self.ui = ui
        self.position = position
        
    def destroy(self) -> None:
        """
        Removes this ui element from the UI
        """
        if self in self.ui.effects: self.ui.effects.remove(self)
        
    @property
    def game(self) -> Game: return self.ui.game
    
    @property
    def engine(self) -> bsk.Engine: return self.ui.engine
    
class Image(Effect):
    
    def __init__(self, ui: UI, image: bsk.Image, position: glm.vec2, scale: glm.vec2) -> None:
        super().__init__(ui = ui, position = position)
        self.image = image
        self.scale = scale
        
    def update(self, dt: float) -> None:
        """
        Blit image to screen (delta time is unused)
        """
        bsk.draw.blit(self.engine, self.image, tuple((*self.position, *self.scale)))
        
class ImageLerp(Image):
    
    def __init__(self, ui: UI, image: bsk.Image, position1: glm.vec2, scale1: glm.vec2, position2: glm.vec2=None, scale2: glm.vec2=None, effect_time: float=1) -> None:
        super().__init__(ui = ui, image = image, position = position1, scale = scale1)
        self.original_position = glm.vec2(position1)
        self.original_scale = glm.vec2(scale1)
        self.final_position = glm.vec2(position2) if position2 else glm.vec2(position1)
        self.final_scale = glm.vec2(scale2) if scale2 else glm.vec2(scale1)
        self.effect_time = effect_time
        self.time = 0
        
    def update(self, dt: float) -> None:
        """
        Blits image to screen and lerps towards target position and scale. Kills itself once it has finished.
        """
        self.time += dt
        percent = glm.clamp(self.time / self.effect_time, 0, 1)
        
        self.position = glm.mix(self.original_position, self.final_position, percent)
        self.scale = glm.mix(self.original_scale, self.final_scale, percent)
        
        bsk.draw.blit(self.engine, self.image, tuple((*self.position, *self.scale)))
        
        if percent == 1: self.destroy()
        
class ImageBounce(ImageLerp):
    
    def __init__(self, ui: UI, image: bsk.Image, position1: glm.vec2, scale1: glm.vec2, position2: glm.vec2=None, scale2: glm.vec2=None, effect_time: float=1) -> None:
        super().__init__(ui = ui, image = image, position1 = position1, scale1 = scale1, position2 = position2, scale2 = scale2, effect_time = effect_time)
        self.step = 1
        
    def update(self, dt: float) -> None:
        """
        Performs full lerp then does so in reverse
        """
        self.time += dt * self.step
        percent = glm.clamp(self.time * 2 / self.effect_time, 0, 1) # time is multiplied by 2 since both a forward and backward lerp happen
        
        self.position = glm.mix(self.original_position, self.final_position, percent)
        self.scale = glm.mix(self.original_scale, self.final_scale, percent)
        
        bsk.draw.blit(self.engine, self.image, tuple((*self.position, *self.scale)))
        
        if percent == 1: self.step = -1
        elif percent == 0 and self.step == -1: self.destroy()
    