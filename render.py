from typing import List
from abc import ABC

import numpy
import pygame

from vfx import Vfx
from config import size, playfield_size


# noinspection SpellCheckingInspection
class Renderable(ABC):
    x: int
    y: int
    surface: pygame.Surface


def render(objects: List[Renderable | Vfx]):
    try:
        S = pygame.Surface(size).convert_alpha()
        S.fill((0, 0, 0, 0))
        for i in objects:
            if isinstance(i, Vfx):
                S.blit(i.image, i.rect.topleft)
            else:
                S.blit(pygame.transform.scale(i.surface, numpy.divide(i.surface.get_size(), playfield_size) * size), (i.x / playfield_size[0] * size[0], i.y / playfield_size[1] * size[1]))
    finally:
        pass
    return S
