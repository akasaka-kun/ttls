import numpy
import pygame.sprite

import misc


class Vfx(pygame.sprite.Sprite):
    def __init__(self, effect_sprite_gen):
        super().__init__()
        self.gen = effect_sprite_gen
        self.image, self.rect = pygame.Surface([0, 0]), pygame.Rect([0, 0, 0, 0])

    def update(self, *args) -> None:
        gen_ = self.gen()
        if gen_ is not None:
            self.image, self.rect = gen_


