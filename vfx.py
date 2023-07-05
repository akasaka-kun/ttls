import pygame.sprite


class Vfx(pygame.sprite.Sprite):
    def __init__(self, effect_sprite_gen):
        super().__init__()
        self.gen = effect_sprite_gen
        self.image, self.rect = self.gen()

    def update(self, *args) -> None:
        self.image, self.rect = self.gen()


