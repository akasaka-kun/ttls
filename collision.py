import pygame


class collider_sprite(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.rect = pygame.Rect([0, 0, size, size])