import abc
import math
from typing import Tuple

import pygame

import GLOBAL
import config


class projectile(abc.ABC, pygame.sprite.Sprite):
    """please implement ALL class attributes in your subclasses"""
    surface: pygame.Surface
    collider: Tuple[str, ...]

    def __init__(self, pos, size=None):
        super().__init__()
        self.pos = pos
        self.size = [10, 10] if size is None else size
        self.rect = pygame.Rect(*self.pos, *self.size)

    @staticmethod
    def on_collision():  # for most cases you can leave this as is
        return "delete"


class Danmaku(pygame.sprite.Group):
    """
    turns out in old testing, having projectiles as separated projectile fields per projectile type was more efficient
    """

    def __init__(self, faction, default_collider=(pygame.sprite.collide_circle, 10)):
        super().__init__()
        self.default_collider = default_collider
        self.bullet_field = []

        self.faction = faction  # for now, just determines if it collides with the player or the enemies
        self.x, self.y = 0, 0
        GLOBAL.TO_UPDATE.append(self)
        GLOBAL.PROJECTILE_GROUPS.append(self)

    def update(self, dt):
        super().update(dt)

    def add(self, *sprites: projectile) -> None:
        super().add(*sprites)
